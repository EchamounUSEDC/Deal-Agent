# Casino Display — 3D Falling Cards & Poker Chips

A full-screen, looping **3D** animation of playing cards and poker chips raining
down onto a felt table, tumbling and piling up with real physics. Built to run
forever on a big screen in front of a casino.

![what it does](https://img.shields.io/badge/3D-three.js%20%2B%20cannon--es-e9c46a)

## Features

- **Real 3D + physics** — cards and chips fall, spin, collide and stack
  (three.js for rendering, cannon-es for rigid-body physics).
- **Self-contained** — card faces, card backs, and chip artwork are all drawn
  procedurally in code. No image files to ship.
- **Runs forever** — objects auto-recycle, so memory stays flat for 24/7 display.
- **Cinematic camera** — slow auto-orbit, warm casino spotlights, and a soft
  bloom glow.
- **Marquee headline** — big glowing casino name + tagline, customizable.
- **Big-screen ready** — one keypress fullscreen, designed for any aspect ratio.

## Run it

Because it loads ES modules, open it through a local web server (not `file://`):

```bash
cd casino-display
python3 -m http.server 8000
# then open http://localhost:8000 in a browser
```

Any static server works (`npx serve`, nginx, etc.).

## Controls

| Key | Action |
|-----|--------|
| `F` | Toggle fullscreen |
| `Space` | Deal a burst of cards/chips |
| `H` | Hide / show the headline text |

## Customize

**Marquee text** via the URL — handy for changing the casino name without
editing code:

```
index.html?title=Lucky%20Star%20Casino&subtitle=Where%20Fortune%20Falls
```

**Look & feel** — edit the `CONFIG` block at the top of `main.js`:

| Setting | Meaning |
|---------|---------|
| `spawnIntervalMs` | How fast new pieces drop |
| `maxObjects` | Max live pieces on screen (caps memory/GPU) |
| `cardChipRatio` | Mix of cards vs chips (0–1) |
| `gravity` | Fall speed feel |
| `felt`, `background` | Table & backdrop colors |

Chip denominations/colors live in `CHIP_STYLES`; the headline styling is in
`index.html`.

## Putting it on the casino big screen

1. Plug the display PC into the screen and set the screen as the primary
   monitor at its native resolution.
2. Open `index.html` (served as above) in **Chrome/Edge**.
3. Press `F` for fullscreen, or launch the browser in kiosk mode so it boots
   straight into the show:

   ```bash
   # Linux / Windows (Chrome) — replace the URL with your served address
   chrome --kiosk --autoplay-policy=no-user-gesture-required http://localhost:8000
   ```

4. Disable the OS screensaver / sleep so it never blanks.

### Network note
The two libraries (three.js, cannon-es) load from a CDN, so the display PC
needs internet on first load (the browser will cache them after). For a
guaranteed-offline kiosk, download those two files locally and point the
`importmap` in `index.html` at the local copies.

## Files

```
casino-display/
├── index.html   # page, styles, marquee, library imports
├── main.js      # 3D scene, physics, procedural card/chip art, render loop
└── README.md
```
