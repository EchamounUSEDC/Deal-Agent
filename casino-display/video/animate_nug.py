#!/usr/bin/env python3
"""Render a LIP-SYNCED talking Nug, one .mov per scene.

His ACTUAL mouth moves: the real lower face (below the mouth line) is stretched
downward by an amount driven by the scene audio's loudness — a jaw drop using
his own pixels. Eyes blink, eyebrows react to emphasis. Features are centered on
his real eyes/mouth. Output: nug_<key>.mov (QuickTime-RLE, real alpha).
"""
import os, math, json, wave, subprocess
import numpy as np
from collections import deque
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'realimg2', 'New folder', 'NUG.png')
FRAMES = os.path.join(HERE, 'nug_frames')
FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 30
DELAY = 0.30        # narration is delayed 300ms in the scene clip
PAD = 1.0           # scene clip = audio_dur + PAD (matches build_video)

# Feature coords in NUG.png space (cropped to y<=1090). Measured from a grid.
EL, ER, EYE_R = (452, 712), (600, 705), 42
MX, MY, MW = 510, 915, 82          # mouth center + half width
LIP = 910                          # split line: above stays, below drops
MAX_OPEN = 46

def base_cutout():
    im = Image.open(SRC).convert('RGB')
    w, h = im.size
    im = im.crop((0, 0, w, 1090))
    a = np.asarray(im).astype(np.int32)
    R, G, Bl = a[..., 0], a[..., 1], a[..., 2]
    bright = 0.299*R + 0.587*G + 0.114*Bl
    bg = (Bl > R + 6) & (bright < 135)
    alpha = np.where(bg, 0, 255).astype(np.uint8)
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
    gy, gx = np.where((R>150)&(G>110)&(Bl<120)&(keep>0))
    gold = (int(np.median(a[gy,gx,0])), int(np.median(a[gy,gx,1])), int(np.median(a[gy,gx,2])))
    return img, alpha, gold

def envelope(wav_path, nframes):
    w = wave.open(wav_path); sr = w.getframerate(); n = w.getnframes()
    data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float64)
    if w.getnchannels() == 2:
        data = data.reshape(-1, 2).mean(1)
    data /= 32768.0
    hop = sr / FPS
    env = np.zeros(nframes)
    for i in range(nframes):
        t = i / FPS - DELAY          # align with the 300ms narration delay
        if t < 0:
            continue
        s = int(t * sr); e = int(s + hop)
        seg = data[s:e]
        if len(seg):
            env[i] = math.sqrt(float(np.mean(seg**2)))
    if env.max() > 0:
        env /= env.max()
    env = np.clip(env, 0, 1) ** 0.6
    # light smoothing
    k = np.array([0.25, 0.5, 0.25])
    env = np.convolve(env, k, mode='same')
    return env

def blink(t):
    p = t % 2.4
    if p < 0.18:
        return math.sin(math.pi * (p / 0.18))
    return 0.0

def render_scene(key, wav_path, dur, base, alpha, gold):
    bbox = Image.fromarray(alpha, 'L').getbbox()
    gdark = tuple(max(0, c-55) for c in gold)
    nframes = int(round(dur * FPS))
    env = envelope(wav_path, nframes)
    bw, bh = base.size
    lower = base.crop((0, LIP, bw, bh))
    lower_h = bh - LIP

    os.makedirs(FRAMES, exist_ok=True)
    for f in os.listdir(FRAMES):
        os.remove(os.path.join(FRAMES, f))

    for i in range(nframes):
        t = i / FPS
        op = float(env[i])
        openH = int(6 + MAX_OPEN * op)

        im = base.copy()
        # --- actual mouth opens: stretch real lower face down by openH ---
        scaled = lower.resize((bw, lower_h + openH), Image.LANCZOS)
        # darken the newly-opened gap so it reads as an open mouth cavity
        d0 = ImageDraw.Draw(im, 'RGBA')
        d0.ellipse([MX-MW, LIP-4, MX+MW, LIP+openH+6], fill=(45, 20, 16, 255))
        if openH > 16:
            d0.rectangle([MX-MW+12, LIP-2, MX+MW-12, LIP+max(5, openH//4)], fill=(240,235,225,255))  # upper teeth
            d0.chord([MX-MW*0.6, LIP+openH-14, MX+MW*0.6, LIP+openH+10], 10, 170, fill=(180,70,70,255))  # tongue
        im.paste(scaled, (0, LIP), scaled)

        d = ImageDraw.Draw(im, 'RGBA')
        # --- eyebrows: raise with emphasis ---
        raise_px = int(8 + 18 * op)
        for (ex, ey) in (EL, ER):
            by = ey - 60 - raise_px
            d.line([(ex-EYE_R+2, by+10), (ex, by-8), (ex+EYE_R-2, by+10)],
                   fill=(55, 32, 8, 255), width=15, joint='curve')

        # --- blink ---
        bl = blink(t)
        if bl > 0.05:
            for (ex, ey) in (EL, ER):
                eh = max(2, int(EYE_R * bl))
                d.ellipse([ex-EYE_R-4, ey-eh, ex+EYE_R+4, ey+eh], fill=gold+(255,))
                if bl > 0.6:
                    d.line([(ex-EYE_R, ey), (ex+EYE_R, ey)], fill=gdark+(255,), width=6)

        im.crop(bbox).save(os.path.join(FRAMES, f'f_{i:04d}.png'))

    out = os.path.join(HERE, f'nug_{key}.mov')
    subprocess.run([FF, '-y', '-hide_banner', '-loglevel', 'error', '-framerate', str(FPS),
                    '-i', os.path.join(FRAMES, 'f_%04d.png'),
                    '-c:v', 'qtrle', '-pix_fmt', 'argb', '-an', out], check=True)
    print(f'  {key}: {nframes} frames -> {os.path.basename(out)}')

if __name__ == '__main__':
    base, alpha, gold = base_cutout()
    print('gold', gold, 'bbox', Image.fromarray(alpha,'L').getbbox())
    scenes = json.load(open(os.path.join(HERE, 'scenes.json')))
    for s in scenes:
        dur = round(s['dur'] + PAD, 2)
        render_scene(s['key'], os.path.join(HERE, s['audio']), dur, base, alpha, gold)
    print('all scene animations done')
