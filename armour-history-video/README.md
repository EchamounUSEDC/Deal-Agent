# From Cowtown to a New Era of Energy

A browser-based, hand-drawn animated history film (~2:20) telling the story of
the Fort Worth Stockyards, the Armour Building, and its new life as the
headquarters of **U.S. Energy Development Corporation**.

Everything is rendered live in the browser: warm ivory paper, ink lines that
draw themselves, watercolor washes, erase/dust/wipe transitions, narration,
a subtle procedural music bed, and one-click WebM export.

## Running the project locally

The app is plain HTML/CSS/JS — no build step. Because it fetches audio files,
serve it over HTTP rather than opening `index.html` directly:

```bash
cd armour-history-video

# any static server works; for example:
python3 -m http.server 8000
# then open:
#   http://localhost:8000/
```

Click **Begin** on the loading screen (a click is required so the browser
allows audio). The film plays through all eight scenes automatically.

### Controls

| Control | Action |
| --- | --- |
| ▶ / ❚❚ | Play / pause (also `Space`) |
| ⟲ | Restart from the beginning |
| Progress bar | Click to seek (scene boundaries are ticked) |
| 🔊 / 🔇 | Mute / unmute (also `M`) |
| Export | Record the full film and download a `.webm` |
| ⛶ | Full screen (also `F`) |

## Exporting the finished animation as a video

1. Click **Export**. The film restarts and plays through in real time while
   `canvas.captureStream(30)` + `MediaRecorder` capture it at 1920×1080/30fps.
2. Let it play to the end (a red **RECORDING** badge shows while capturing).
3. When it finishes, `armour-building-history.webm` downloads automatically.

Notes:

- **Audio in the export**: background music, sound effects, and *file-based*
  narration (see below) are mixed through Web Audio and included in the WebM.
  Browser speech-synthesis narration **cannot** be captured by MediaRecorder —
  add real narration files before a final export.
- Chrome/Edge produce the best results (VP9 + Opus). Convert to MP4 with
  `ffmpeg -i armour-building-history.webm -c:v libx264 -c:a aac out.mp4`.

## Replacing placeholder assets

All slots live in `assets/`:

| Asset | Where | Notes |
| --- | --- | --- |
| **Official U.S. Energy logo** | `assets/logo/` | The film currently uses a text placeholder (Scene 7 signage, Scene 8 end card). Once the official mark is supplied, draw it into the final card or overlay it in post — the layout leaves clear space. Do **not** recreate the logo approximately. |
| **Professional narration** | `assets/narration/scene-01.mp3` … `scene-08.mp3` | Files are auto-detected at load (`AUDIO_MANIFEST` in `scenes.js`). When present they **override** speech synthesis, are included in exports, and scene durations stretch to fit longer takes. |
| **Background music** | `assets/music/background.mp3` | Auto-detected; loops and is ducked under narration. Until supplied, a quiet procedural acoustic bed plays. Cinematic-Western, no vocals, royalty-free/owned only. |
| **Sound effects** | `assets/sfx/` | Wind, train whistle, cattle, and hammer cues are currently synthesized in code (`playSfx` in `script.js`); drop replacements here and wire them in the same function. |
| **Reference imagery** | `assets/reference/historical/`, `assets/reference/armour-building/` | For the illustrator/reviewers only — nothing in these folders is loaded by the app. |

## Editing the story

- **Narration text** — each scene's `narration` string in `scenes.js`.
- **Scene timing** — each scene's `duration` (seconds) in `scenes.js`;
  element-level `at`/`dur` values choreograph individual strokes.
- **Historical claims** — every fact lives in `HISTORICAL_FACTS` at the top of
  `scenes.js`, including a **“FACTS TO VERIFY BEFORE FINAL EXPORT”** checklist
  (construction year is deliberately never stated; the 2025 move-in year comes
  from the project brief).
- **Artwork** — scenes are lists of SVG path elements built by small helpers
  (`longhorn()`, `railTracks()`, `armourBuilding()`, …). Add or edit paths and
  they inherit the hand-drawn line treatment automatically.

## File map

```
armour-history-video/
├── index.html      stage, loading screen, control bar
├── styles.css      chrome styling (film itself is canvas-rendered)
├── scenes.js       facts, narration, audio manifest, all 8 scenes' artwork
├── script.js       engine: drawing, transitions, audio, export, controls
├── README.md
└── assets/         logo / narration / music / sfx / reference placeholders
```

## Known limitations

- Speech-synthesis narration is a *placeholder* voice: quality varies by
  browser/OS and it is absent from exported video (see above).
- Export runs in real time (~2:20) by design so audio stays in sync.
- Seeking during export is disabled to keep the recording continuous.
