# USEDC — Opportunity Zones Educational Video

A fully scripted, locally rendered institutional explainer video for
U.S. Energy Development Corporation covering Opportunity Zones: what they
are, the investment timeline, the potential tax benefits, and USEDC's
positioning.

**Deliverable:** `USEDC_Opportunity_Zones_Explainer_1080p.mp4`
(1920×1080, 30 fps, H.264/AAC, ~1:46)

## Structure

| Time | Section | Visuals |
|---|---|---|
| 0:00–0:16 | What are Opportunity Zones | Animated U.S. map (real TopoJSON state geometry), designated-tract dots, info chips |
| 0:16–0:26 | About USEDC — headquarters | **Supplied Fort Worth footage**, lower third, 45+ years counter |
| 0:26–0:34 | About USEDC — operations | **Supplied Pecos, TX rig footage**, animated stat cards (45+ yrs / 4,000+ wells / 13 states + Canada / $4B+) |
| 0:34–1:03 | The OZ investment timeline | 7-node animated timeline (gain → 180 days → QOF → deployment → 2026 recognition → 10-yr hold → potential tax-free appreciation) |
| 1:03–1:26 | Potential tax benefits | Animated valuation/basis-reset chart + keyword cards |
| 1:26–1:46 | Closing + brand endcard | Remaining supplied footage, chips, USEDC wordmark, compliance disclaimer |

## How it was made (no external generation services)

- **Motion graphics** — deterministic HTML/CSS/JS scenes (`pipeline/scenes/`,
  `pipeline/overlays/`) exposing `window.seek(t)`; frames captured at 30 fps
  with headless Chromium via Playwright (`pipeline/render.mjs`).
- **Voiceover** — Piper TTS (`en_US-joe-medium`, run locally) via
  `pipeline/gen_vo.py`.
- **Music** — original ambient corporate bed synthesized in NumPy
  (`pipeline/music.py`).
- **Footage** — the two supplied clips (Fort Worth skyline, Pecos TX rig),
  trimmed, slow-zoomed and color graded in ffmpeg (`pipeline/footage.sh`).
- **Assembly** — xfade chain, VO placement, music ducking and loudness
  normalization in ffmpeg (`pipeline/assemble.sh`).

## Regenerating

```bash
cd pipeline
python3 gen_vo.py          # writes vo/*.wav (requires piper-tts + joe-us-piper-voice)
python3 music.py           # writes audio/music.wav
./footage.sh               # graded footage segments (requires the two source clips)
./render_gfx.sh && ./render_ovl.sh   # frame renders (requires playwright + chromium)
./assemble.sh              # final MP4
```

Fonts: Inter and IBM Plex Mono (via `@fontsource/*` npm packages).
Map data: `us-atlas` (TopoJSON), rendered with `topojson-client`.

## Notes

- The full supplied narration script, read at an institutional pace, does not
  fit in 90 seconds; the cut runs ~1:46. Trimming the script (e.g. the tax
  benefits section) would bring it to 90s if required.
- Brand assets (official USEDC logo/colors) were not supplied; a neutral
  navy/gold institutional system with a text wordmark is used. Swap in brand
  assets in `scenes/endcard.html` and the overlay headers when available.
- The endcard carries an educational/compliance disclaimer.
