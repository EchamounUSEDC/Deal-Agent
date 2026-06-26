#!/usr/bin/env python3
"""Prepare the user's REAL images for the video:
   - cut Nug out of his dark-blue background  -> assets/nug.png (transparent)
   - fit each Central City photo to 1920x1080 with a title bar -> assets/bg_s*.png
Overwrites the placeholder assets so build_video.py picks up the real images.
"""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'realimg2', 'New folder')
AST = os.path.join(HERE, 'assets'); os.makedirs(AST, exist_ok=True)
W, H = 1920, 1080
SERIF = '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'

NUG = os.path.join(SRC, 'NUG.png')
PANO   = os.path.join(SRC, 'image-1782500699112.webp')  # sepia panorama
SNOW   = os.path.join(SRC, 'image-1782500706018.webp')  # snowy aerial
BW     = os.path.join(SRC, 'image-1782500708495.webp')  # b&w mining camp
STREET = os.path.join(SRC, 'image-1782500702844.webp')  # main street

# ---- cut Nug out of the blue background --------------------------------------
def cut_nug():
    im = Image.open(NUG).convert('RGB')
    w, h = im.size
    im = im.crop((0, 0, w, int(h * 0.66)))   # drop the mirror reflection below
    a = np.asarray(im).astype(np.int32)
    R, G, Bl = a[..., 0], a[..., 1], a[..., 2]
    bright = 0.299 * R + 0.587 * G + 0.114 * Bl
    # background = bluish AND not bright; Nug is gold (R>B) / eyes are bright
    bg = (Bl > R + 6) & (bright < 135)
    alpha = np.where(bg, 0, 255).astype(np.uint8)

    # keep only the largest blob (drop stray specks) via simple flood from center
    from collections import deque
    keep = np.zeros_like(alpha)
    ys, xs = np.where(alpha > 0)
    if len(xs):
        cy, cx = int(ys.mean()), int(xs.mean())
        # nearest opaque seed to centroid
        seed = None
        for r in range(0, 200, 5):
            yy = np.clip(cy + 0, 0, alpha.shape[0]-1)
            if alpha[yy, np.clip(cx, 0, alpha.shape[1]-1)] > 0:
                seed = (yy, np.clip(cx, 0, alpha.shape[1]-1)); break
        if seed is None:
            seed = (ys[0], xs[0])
        H0, W0 = alpha.shape
        dq = deque([seed]); keep[seed] = 1
        while dq:
            y, x = dq.popleft()
            for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                ny, nx = y+dy, x+dx
                if 0 <= ny < H0 and 0 <= nx < W0 and keep[ny, nx] == 0 and alpha[ny, nx] > 0:
                    keep[ny, nx] = 1; dq.append((ny, nx))
        alpha = (keep * 255).astype(np.uint8)

    out = im.convert('RGBA')
    am = Image.fromarray(alpha, 'L').filter(ImageFilter.GaussianBlur(1.2))
    out.putalpha(am)
    # autocrop to content
    bbox = out.getbbox()
    out = out.crop(bbox)
    out.save(os.path.join(AST, 'nug.png'))
    print('nug.png cut ->', out.size)

# ---- fit a photo to 1920x1080 (cover) + title bar ---------------------------
def scene(src, title, dst, darken=0.0):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    s = max(W / w, H / h)
    im = im.resize((int(w * s + 1), int(h * s + 1)), Image.LANCZOS)
    x = (im.width - W) // 2; y = (im.height - H) // 2
    im = im.crop((x, y, x + W, y + H))
    if darken:
        im = Image.eval(im, lambda v: int(v * (1 - darken)))
    # No title bar / no caption — clean full-bleed photo (per user request).
    im.save(dst)
    print('bg ->', os.path.basename(dst))

if __name__ == '__main__':
    cut_nug()
    scene(PANO,   'Meet Nug!',                  os.path.join(AST, 'bg_s1.png'), darken=0.35)
    scene(SNOW,   'Central City, Colorado',     os.path.join(AST, 'bg_s2.png'))
    scene(BW,     '1859 — The Gold Rush',       os.path.join(AST, 'bg_s3.png'))
    scene(STREET, 'Main Street Today',          os.path.join(AST, 'bg_s4.png'))
    scene(SNOW,   'Come Visit Central City!',   os.path.join(AST, 'bg_s5.png'))
    print('real assets ready')
