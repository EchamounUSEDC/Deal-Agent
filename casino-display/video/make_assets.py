#!/usr/bin/env python3
"""Generate PLACEHOLDER art for the Nug rough draft:
   - nug.png         : a cartoon gold-nugget character (transparent)
   - bg_s1..s5.png   : illustrated stand-in scenes (1920x1080)
These are swapped for the user's real photos later.
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
AST = os.path.join(HERE, 'assets'); os.makedirs(AST, exist_ok=True)
W, H = 1920, 1080
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF = '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'

def font(path, size):
    return ImageFont.truetype(path, size)

def vgrad(w, h, top, bot):
    img = Image.new('RGB', (w, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        px_row = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = px_row
    return img

# ----------------------------------------------------------------------------- Nug
def make_nug():
    S = 700
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2 + 20
    # blobby body from overlapping circles
    random.seed(7)
    blobs = [(cx, cy, 200), (cx-90, cy-60, 120), (cx+95, cy-50, 120),
             (cx-70, cy+110, 110), (cx+80, cy+110, 110), (cx, cy-120, 120),
             (cx-150, cy+30, 80), (cx+150, cy+30, 80)]
    body = Image.new('L', (S, S), 0)
    bd = ImageDraw.Draw(body)
    for (x, y, r) in blobs:
        bd.ellipse([x-r, y-r, x+r, y+r], fill=255)
    body = body.filter(ImageFilter.GaussianBlur(6))
    body = body.point(lambda v: 255 if v > 90 else 0)
    # gold gradient fill masked by body
    gold = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    gp = gold.load()
    for y in range(S):
        for x in range(S):
            if body.getpixel((x, y)) > 0:
                # radial-ish shading
                dx, dy = (x - (cx-60)) / S, (y - (cy-80)) / S
                shade = max(0.0, 1.0 - (dx*dx + dy*dy) * 2.2)
                r = int(180 + 75 * shade); g = int(140 + 70 * shade); b = int(20 + 40 * shade)
                gp[x, y] = (min(255, r+40), min(255, g+40), b, 255)
    img = Image.alpha_composite(img, gold)
    d = ImageDraw.Draw(img)
    # nuggety texture: random darker/lighter specks
    for _ in range(900):
        x = random.randint(cx-190, cx+190); y = random.randint(cy-200, cy+220)
        if body.getpixel((max(0,min(S-1,x)), max(0,min(S-1,y)))) > 0:
            c = random.choice([(255, 230, 120, 90), (150, 110, 20, 90)])
            rr = random.randint(2, 6)
            d.ellipse([x-rr, y-rr, x+rr, y+rr], fill=c)
    # eyes
    for ex in (cx-70, cx+70):
        d.ellipse([ex-52, cy-90, ex+52, cy+14], fill=(255, 255, 255, 255), outline=(60,40,0,255), width=4)
        d.ellipse([ex-22, cy-58, ex+30, cy-6], fill=(60, 40, 20, 255))   # iris
        d.ellipse([ex+2, cy-50, ex+18, cy-34], fill=(255, 255, 255, 255))  # glint
    # smile
    d.arc([cx-90, cy-20, cx+90, cy+150], start=15, end=165, fill=(80, 40, 10, 255), width=14)
    d.chord([cx-60, cy+40, cx+60, cy+120], start=20, end=160, fill=(150, 40, 40, 255))  # tongue
    # little waving hand
    d.ellipse([cx+150, cy-150, cx+230, cy-70], fill=(230, 180, 40, 255), outline=(150,110,20,255), width=3)
    img.save(os.path.join(AST, 'nug.png'))
    print('nug.png')

# ----------------------------------------------------------------------------- scenes
def label(img, text, sub=None):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 110], fill=(0, 0, 0))
    d.text((60, 26), text, font=font(SERIF, 58), fill=(233, 196, 106))
    d.rectangle([0, H-4, W, H], fill=(233, 196, 106))
    if sub:
        d.text((60, H-150), sub, font=font(FONT, 30), fill=(255, 255, 255))

def scene_intro():
    img = vgrad(W, H, (16, 26, 64), (4, 6, 18)).convert('RGBA')
    d = ImageDraw.Draw(img)
    # spotlight
    glow = Image.new('RGBA', (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W//2-500, H//2-380, W//2+500, H//2+380], fill=(60, 90, 160, 120))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(120)))
    label(img, 'Meet Nug!  —  PLACEHOLDER (swap real images)')
    img.convert('RGB').save(os.path.join(AST, 'bg_s1.png')); print('bg_s1')

def scene_town():
    img = vgrad(W, H, (120, 170, 225), (210, 230, 245)).convert('RGBA')
    d = ImageDraw.Draw(img)
    # snowy hill
    d.polygon([(0, 520), (500, 300), (1100, 380), (1500, 260), (1920, 360), (1920, H), (0, H)], fill=(238, 244, 250))
    # pine specks
    for _ in range(140):
        x = random.randint(0, W); y = random.randint(300, 560)
        d.polygon([(x, y), (x-7, y+16), (x+7, y+16)], fill=(40, 80, 50))
    # rows of little colorful houses
    random.seed(3)
    cols = [(176,58,46),(214,178,90),(90,140,170),(200,120,80),(120,160,120),(225,225,225)]
    for row in range(3):
        by = 640 + row*120
        for i in range(14):
            x = 80 + i*135 + row*30
            c = random.choice(cols)
            d.rectangle([x, by, x+95, by+85], fill=c, outline=(60,50,45), width=2)
            d.polygon([(x-6, by), (x+101, by), (x+47, by-34)], fill=(245,245,248))  # snowy roof
    label(img, 'Central City, Colorado', 'PLACEHOLDER scene — your snowy aerial photo goes here')
    img.convert('RGB').save(os.path.join(AST, 'bg_s2.png')); print('bg_s2')

def scene_history():
    img = vgrad(W, H, (196, 184, 158), (120, 108, 88)).convert('RGBA')
    d = ImageDraw.Draw(img)
    d.polygon([(0, 480), (700, 300), (1300, 360), (1920, 300), (1920, H), (0, H)], fill=(150, 138, 112))
    random.seed(9)
    for i in range(40):
        x = random.randint(60, W-160); y = random.randint(560, 980)
        w = random.randint(50, 120); h = random.randint(50, 110)
        d.rectangle([x, y, x+w, y+h], fill=(92, 76, 56), outline=(40,30,20), width=2)
        d.polygon([(x-4, y), (x+w+4, y), (x+w//2, y-26)], fill=(70, 58, 42))
    label(img, '1859 — The Gold Rush', 'PLACEHOLDER — your historic black & white photo goes here')
    # sepia tint
    img = img.convert('RGB')
    sep = Image.new('RGB', (W, H), (112, 90, 60))
    img = Image.blend(img, sep, 0.18)
    img.save(os.path.join(AST, 'bg_s3.png')); print('bg_s3')

def scene_main():
    img = vgrad(W, H, (150, 180, 210), (205, 215, 225)).convert('RGBA')
    d = ImageDraw.Draw(img)
    # row of brick buildings
    random.seed(5)
    x = 0
    cols = [(150,52,40),(176,72,52),(120,90,70),(190,150,90),(160,60,48)]
    while x < W:
        bw = random.randint(180, 280); bh = random.randint(360, 520)
        top = H - bh
        c = random.choice(cols)
        d.rectangle([x, top, x+bw, H], fill=c, outline=(50,30,25), width=3)
        # windows
        for wy in range(top+50, H-120, 90):
            for wx in range(x+25, x+bw-40, 70):
                d.rectangle([wx, wy, wx+38, wy+58], fill=(180, 200, 220), outline=(40,30,25), width=2)
        # awning
        d.rectangle([x+10, H-110, x+bw-10, H-70], fill=(140, 30, 30))
        x += bw + 8
    # casino sign
    d.rectangle([W//2-180, 150, W//2+180, 250], fill=(20,20,20), outline=(233,196,106), width=6)
    d.text((W//2-150, 168), 'CASINO', font=font(FONT, 70), fill=(233,196,106))
    label(img, 'Main Street Today', 'PLACEHOLDER — your Bonanza Casino street photo goes here')
    img.convert('RGB').save(os.path.join(AST, 'bg_s4.png')); print('bg_s4')

def scene_outro():
    img = vgrad(W, H, (250, 210, 110), (200, 140, 40)).convert('RGBA')
    d = ImageDraw.Draw(img)
    # sunburst
    cx, cy = W//2, H//2
    for a in range(0, 360, 12):
        x2 = cx + math.cos(math.radians(a)) * 1400
        y2 = cy + math.sin(math.radians(a)) * 1400
        d.line([cx, cy, x2, y2], fill=(255, 235, 160), width=10)
    d.polygon([(0, 760), (500, 640), (1100, 700), (1920, 640), (1920, H), (0, H)], fill=(120, 80, 30))
    label(img, 'Come Visit Central City!  —  Happy Trails')
    img.convert('RGB').save(os.path.join(AST, 'bg_s5.png')); print('bg_s5')

if __name__ == '__main__':
    make_nug()
    scene_intro(); scene_town(); scene_history(); scene_main(); scene_outro()
    print('assets done')
