#!/usr/bin/env python3
"""Assemble Nug's rough-draft video.

  python3 build_video.py scenes              # build the 5 Nug scene clips
  python3 build_video.py final <cards.mp4>   # build intro from cards + concat all

Per scene: illustrated background + Nug "walking" across (bob) + bottom caption
of his line + his narration audio. Then concat after a cards-falling intro.
"""
import os, sys, json, math, subprocess, textwrap
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
AST = os.path.join(HERE, 'assets')
CLIPS = os.path.join(HERE, 'clips'); os.makedirs(CLIPS, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1920, 1080
INTRO_SEC = 7.0
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

SCENE_BG = {'s1_intro': 'bg_s1.png', 's2_town': 'bg_s2.png', 's3_history': 'bg_s3.png',
            's4_main': 'bg_s4.png', 's5_outro': 'bg_s5.png'}

def run(args):
    subprocess.run(args, check=True)

def make_caption(text, path):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 46)
    lines = textwrap.wrap(text, width=58)
    lh = 60
    box_h = lh * len(lines) + 40
    y0 = H - box_h - 40
    d.rectangle([60, y0, W - 60, y0 + box_h], fill=(0, 0, 0, 150))
    y = y0 + 20
    for ln in lines:
        w = d.textlength(ln, font=f)
        x = (W - w) / 2
        d.text((x + 2, y + 2), ln, font=f, fill=(0, 0, 0, 220))   # shadow
        d.text((x, y), ln, font=f, fill=(255, 244, 214, 255))
        y += lh
    img.save(path)

def build_scene(idx, scene):
    key = scene['key']
    dur = round(scene['dur'] + 1.0, 2)
    bg = os.path.join(AST, SCENE_BG[key])
    nug_anim = os.path.join(HERE, f'nug_{key}.mov')   # per-scene lip-synced Nug (alpha)
    aud = os.path.join(HERE, scene['audio'])
    out = os.path.join(CLIPS, f'{key}.mp4')

    # Nug walks across; direction alternates; gentle vertical bob. No captions.
    nug_scale = 520
    if idx % 2 == 0:
        x_expr = f'(W-w)*t/{dur}'
    else:
        x_expr = f'(W-w)*(1-t/{dur})'
    y_expr = f'H*0.34+26*sin(2*PI*1.3*t)'
    fc = (f"[1:v]scale={nug_scale}:-1[n];"
          f"[0:v][n]overlay=x='{x_expr}':y='{y_expr}':eval=frame:format=auto[v];"
          f"[2:a]adelay=300|300,apad[au]")
    run([FF, '-y', '-hide_banner', '-loglevel', 'error',
         '-loop', '1', '-i', bg,
         '-i', nug_anim,
         '-i', aud,
         '-filter_complex', fc,
         '-map', '[v]', '-map', '[au]', '-t', str(dur), '-r', '30',
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-ar', '44100', '-ac', '2', out])
    print(f'  {key}: {dur}s -> {os.path.basename(out)}')
    return out

def build_intro(cards_mp4):
    out = os.path.join(CLIPS, 'intro.mp4')
    run([FF, '-y', '-hide_banner', '-loglevel', 'error',
         '-t', str(INTRO_SEC), '-i', cards_mp4,
         '-f', 'lavfi', '-t', str(INTRO_SEC), '-i', 'anullsrc=r=44100:cl=stereo',
         '-vf', 'scale=1920:1080:flags=lanczos,setsar=1', '-r', '30',
         '-map', '0:v', '-map', '1:a',
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-ar', '44100', '-ac', '2', out])
    print(f'  intro: {INTRO_SEC}s -> intro.mp4')
    return out

def concat(parts, out):
    lst = os.path.join(CLIPS, 'concat.txt')
    with open(lst, 'w') as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    # re-encode concat (robust against tiny param diffs)
    inputs = []
    for p in parts:
        inputs += ['-i', p]
    n = len(parts)
    fc = ''.join(f'[{i}:v][{i}:a]' for i in range(n)) + f'concat=n={n}:v=1:a=1[v][a]'
    run([FF, '-y', '-hide_banner', '-loglevel', 'error', *inputs,
         '-filter_complex', fc, '-map', '[v]', '-map', '[a]',
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-movflags', '+faststart', out])

def add_music(video, music, out):
    # mix Wild-West music quietly under the narration for the whole video
    fc = ("[1:a]volume=0.14,afade=t=in:st=0:d=1.5[m];"
          "[0:a][m]amix=inputs=2:duration=first:dropout_transition=0,"
          "dynaudnorm=f=200[a]")
    run([FF, '-y', '-hide_banner', '-loglevel', 'error', '-i', video, '-i', music,
         '-filter_complex', fc, '-map', '0:v', '-map', '[a]',
         '-c:v', 'copy', '-c:a', 'aac', '-movflags', '+faststart', out])

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'scenes'
    scenes = json.load(open(os.path.join(HERE, 'scenes.json')))
    if mode == 'scenes':
        print('Building scene clips...')
        for i, s in enumerate(scenes):
            build_scene(i, s)
        print('scene clips done')
    elif mode == 'final':
        cards = sys.argv[2]
        print('Building intro + concatenating...')
        intro = build_intro(cards)
        parts = [intro] + [os.path.join(CLIPS, f"{s['key']}.mp4") for s in scenes]
        tmp = os.path.join(CLIPS, '_concat.mp4')
        concat(parts, tmp)
        out = os.path.join(HERE, 'nug_rough_draft.mp4')
        music = os.path.join(HERE, 'music.wav')
        if os.path.exists(music):
            add_music(tmp, music, out)
        else:
            os.replace(tmp, out)
        print(f'DONE -> {out}')
