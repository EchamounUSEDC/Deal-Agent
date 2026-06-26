#!/usr/bin/env python3
"""Turn the static Nug photo into a talking puppet:
   - mouth opens/closes (talking)
   - eyes blink
   - eyebrows raise/lower
Renders a seamless loop of transparent PNG frames and encodes a VP9/alpha webm
(nug_anim.webm) that build_video.py overlays onto each scene.
"""
import os, math, numpy as np
from collections import deque
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'realimg2', 'New folder', 'NUG.png')
FRAMES = os.path.join(HERE, 'nug_frames'); os.makedirs(FRAMES, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS, DUR = 24, 4.0
N = int(FPS * DUR)

# ---------------------------------------------------------------- base cutout
def base_cutout():
    im = Image.open(SRC).convert('RGB')
    w, h = im.size
    im = im.crop((0, 0, w, 1090))                 # keep full nugget, drop reflection
    a = np.asarray(im).astype(np.int32)
    R, G, Bl = a[..., 0], a[..., 1], a[..., 2]
    bright = 0.299*R + 0.587*G + 0.114*Bl
    bg = (Bl > R + 6) & (bright < 135)
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    # largest connected opaque blob
    keep = np.zeros_like(alpha); H0, W0 = alpha.shape
    ys, xs = np.where(alpha > 0); cy, cx = int(ys.mean()), int(xs.mean())
    dq = deque([(cy, cx)]); keep[cy, cx] = 1
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny, nx = y+dy, x+dx
            if 0 <= ny < H0 and 0 <= nx < W0 and keep[ny,nx]==0 and alpha[ny,nx]>0:
                keep[ny,nx]=1; dq.append((ny,nx))
    alpha = (keep*255).astype(np.uint8)
    img = im.convert('RGBA')
    img.putalpha(Image.fromarray(alpha,'L').filter(ImageFilter.GaussianBlur(1.0)))
    return img, alpha

def detect(img, alpha):
    # Coordinates read off the coordinate-grid render of NUG.png (original space,
    # cropped to 1023x1090). Auto-detection was unreliable (gold highlights read
    # as "eyes"), so these are hand-placed.
    a = np.asarray(img).astype(np.int32)
    R,G,Bl,A = a[...,0],a[...,1],a[...,2],a[...,3]
    op = A > 30
    gold = op & (R>150)&(G>110)&(Bl<120)
    gy,gx = np.where(gold)
    gcol = (int(np.median(a[gy,gx,0])), int(np.median(a[gy,gx,1])), int(np.median(a[gy,gx,2])))
    return {'el':(435,695), 'er':(615,700), 'eye_r':46,
            'mouth':(535,855), 'mw':100, 'gold':gcol}

def smooth_blink(t):
    # blink ~ every 2.0s, ~0.12s long
    period = 2.0
    p = t % period
    if p < 0.18:
        x = p/0.18          # 0..1
        return math.sin(math.pi*x)   # 0->1->0 close fraction
    return 0.0

def talk(t):
    # lively talking: fast flap modulated by slower envelope + a couple of pauses
    env = 0.55 + 0.45*math.sin(2*math.pi*0.7*t + 1.0)
    flap = 0.5 + 0.5*math.sin(2*math.pi*5.5*t)
    val = flap*env
    # brief closed pauses
    if (t % 4.0) > 3.4:
        val *= 0.15
    return max(0.0, min(1.0, val))

def brow(t):
    return 0.5 + 0.5*math.sin(2*math.pi*0.5*t)   # 0..1 raise amount

def render():
    base, alpha = base_cutout()
    bbox = Image.fromarray(alpha, 'L').getbbox()   # tight crop to the nugget
    F = detect(base, alpha)
    el, er, eye_r = F['el'], F['er'], F['eye_r']
    mcx, mcy = F['mouth']; mw = F['mw']; gold = F['gold']
    gdark = tuple(max(0,c-55) for c in gold)
    print('features', F)

    for i in range(N):
        t = i/FPS
        im = base.copy(); d = ImageDraw.Draw(im, 'RGBA')

        # ---- eyebrows (raise/lower) ----
        raise_px = int(22*brow(t))
        for (ex, ey) in (el, er):
            by = ey - int(eye_r*1.25) - raise_px
            d.line([(ex-eye_r+2, by+10), (ex, by-8), (ex+eye_r-2, by+10)],
                   fill=(55,32,8,255), width=16, joint='curve')

        # ---- mouth: cover old, draw animated ----
        op = talk(t)
        # cover existing mouth with gold patch (blended)
        d.ellipse([mcx-mw*0.85, mcy-58, mcx+mw*0.85, mcy+70], fill=gold+(255,))
        d.ellipse([mcx-mw*0.85, mcy-58, mcx+mw*0.85, mcy-10], fill=tuple(min(255,c+25) for c in gold)+(120,))
        oh = int(8 + op*52)             # mouth opening height
        ow = int(mw*0.75)
        if op < 0.08:
            d.arc([mcx-ow, mcy-30, mcx+ow, mcy+50], start=20, end=160, fill=(70,35,15,255), width=12)
        else:
            d.ellipse([mcx-ow, mcy-oh, mcx+ow, mcy+oh], fill=(60,28,22,255))   # mouth cavity
            # upper teeth
            d.rectangle([mcx-ow+10, mcy-oh, mcx+ow-10, mcy-oh+max(6,oh//3)], fill=(245,240,230,255))
            # tongue
            d.chord([mcx-ow*0.6, mcy, mcx+ow*0.6, mcy+oh+6], start=10, end=170, fill=(180,70,70,255))
        # gold lip outline
        d.arc([mcx-ow-4, mcy-oh-6, mcx+ow+4, mcy+oh+6], start=0, end=360, fill=gdark+(180,), width=6)

        # ---- blink: gold eyelid squints the eye shut ----
        bl = smooth_blink(t)
        if bl > 0.05:
            for (ex, ey) in (el, er):
                eh = max(2, int(eye_r*bl))          # half-height of the gold lid band
                d.ellipse([ex-eye_r-4, ey-eh, ex+eye_r+4, ey+eh], fill=gold+(255,))
                if bl > 0.6:                         # closed: lash line
                    d.line([(ex-eye_r, ey), (ex+eye_r, ey)], fill=gdark+(255,), width=6)

        im.crop(bbox).save(os.path.join(FRAMES, f'f_{i:04d}.png'))
    print(f'rendered {N} frames')

    # QuickTime-RLE carries a real alpha channel and overlays reliably (VP9
    # alpha was being dropped). Lossless; size is fine for a short loop.
    out = os.path.join(HERE, 'nug_anim.mov')
    subprocess.run([FF,'-y','-hide_banner','-loglevel','error','-framerate',str(FPS),
                    '-i', os.path.join(FRAMES,'f_%04d.png'),
                    '-c:v','qtrle','-pix_fmt','argb','-an', out], check=True)
    print('wrote', out, os.path.getsize(out)//1024, 'KB')

if __name__ == '__main__':
    render()
