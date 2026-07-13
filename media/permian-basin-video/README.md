# The Permian Basin — A Century of American Energy

An 85-second educational motion-graphics video on the history of the Permian
Basin and drilling in West Texas, produced entirely with code (no stock
footage): HTML/SVG animation rendered frame-by-frame in headless Chromium,
narrated with the Kokoro neural TTS model, and assembled with ffmpeg.

## Contents

| File | Purpose |
|---|---|
| `video_template.html` | The whole film: 8 animated scenes driven by a deterministic `renderFrame(t)` function (fonts injected at build time) |
| `build_html.py` | Inlines the Playfair Display / Inter fonts (from npm `@fontsource`) as base64 into `index.html` |
| `gen_vo.py` | Generates the 8 narration takes with Kokoro TTS (`am_michael` voice) and writes `vo_meta.json` |
| `vo_meta.json` | Script lines + measured durations that define the scene timings |
| `render.js` | Playwright frame renderer — 2,543 PNG frames at 1920x1080/30fps |
| `preview.js` | Renders single frames at chosen timestamps for design review |
| `audio_mix.py` | Places the voiceover, synthesizes the ambient underscore (numpy), ducks it under speech, writes `mix.wav` |

## Rebuild

```bash
pip install kokoro-onnx soundfile scipy imageio-ffmpeg
npm install playwright-core        # plus a Chromium binary
# download kokoro-v1.0.onnx + voices-v1.0.bin (kokoro-onnx model files)
python3 gen_vo.py
python3 build_html.py
node render.js
python3 audio_mix.py
ffmpeg -framerate 30 -i frames/f%05d.png -i mix.wav \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest permian_basin.mp4
```

## Story beats (all fact-checked)

1. Hook — the most productive oil field on earth
2. Geology — the Permian period, 299-252 Ma, an ancient inland sea
3. Discovery — Santa Rita No. 1, May 28, 1923, Reagan County
4. Boom — Midland & Odessa; university-land royalties seed the PUF
5. Peak & decline — 2+ MMbbl/d in 1973, then three decades down
6. Shale revolution — horizontal drilling + fracking; Wolfcamp, Spraberry, Bone Spring
7. Today — ~6.5 MMbbl/d, roughly half of U.S. crude output (EIA 2025)
8. Outro — a century on, still the heartbeat of American energy
