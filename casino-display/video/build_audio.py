#!/usr/bin/env python3
"""Generate Nug's per-scene narration WAVs and a friendlier-sounding version.

Robotic espeak output is post-processed with ffmpeg: a slight upward pitch
shift + gentle high cut to warm it, then loudness-normalized. Writes a
scenes.json manifest with each line's audio path and duration.
"""
import os, json, subprocess, wave
import imageio_ffmpeg
from tts_espeak import synth

FF = imageio_ffmpeg.get_ffmpeg_exe()
OUT = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(OUT, 'audio'); os.makedirs(AUD, exist_ok=True)

SCENES = [
    ("s1_intro",  "Well, howdy there, partners! I'm Nug, a little gold nugget with a big old story to tell. Come along with me to one of Colorado's most famous mountain towns!"),
    ("s2_town",   "This here is Central City, Colorado, tucked high in the Rocky Mountains at over eight thousand five hundred feet. Folks once called it the Richest Square Mile on Earth!"),
    ("s3_history","Way back in eighteen fifty nine, a prospector named John Gregory struck gold right here in Gregory Gulch. Word spread like wildfire, and thousands of miners rushed in, building this whole town almost overnight!"),
    ("s4_main",   "Today, Central City's historic Main Street is alive again! You can try your luck at the casinos, catch a show at the grand old Opera House, and stroll past beautiful buildings from the gold rush days."),
    ("s5_outro",  "So come on up and visit Central City, where Colorado's golden history still shines bright! This is Nug, wishin' you good luck, and happy trails!"),
]

def wav_dur(p):
    with wave.open(p) as w:
        return w.getnframes() / w.getframerate()

manifest = []
for key, line in SCENES:
    raw = os.path.join(AUD, f'{key}_raw.wav')
    fin = os.path.join(AUD, f'{key}.wav')
    synth(line, raw, pitch=68, rate=158, voice='en-us+m3', rng=72)
    # warm it up: pitch +8%, keep tempo, soften highs, normalize
    af = ("asetrate=22050*1.08,aresample=22050,atempo=1/1.08,"
          "highshelf=g=-3:f=3500,acompressor=ratio=3,loudnorm=I=-16:TP=-1.5:LRA=11")
    subprocess.run([FF, '-y', '-hide_banner', '-loglevel', 'error', '-i', raw,
                    '-af', af, '-ar', '44100', '-ac', '1', fin], check=True)
    d = wav_dur(fin)
    manifest.append({'key': key, 'line': line, 'audio': f'audio/{key}.wav', 'dur': round(d, 2)})
    print(f'{key}: {d:5.2f}s  "{line[:48]}..."')

with open(os.path.join(OUT, 'scenes.json'), 'w') as f:
    json.dump(manifest, f, indent=2)
total = sum(m['dur'] for m in manifest)
print(f'\nTotal narration: {total:.1f}s  ->  scenes.json written')
