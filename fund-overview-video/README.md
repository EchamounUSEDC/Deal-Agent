# U.S. Energy Development Corporation — 2026 Drilling Fund Overview

A 60-second, 1920x1080 / 30 fps institutional fund-overview video built with
[Remotion](https://www.remotion.dev), React, TypeScript, and CSS/SVG motion
graphics. The final composition ID is **`FundOverview2026`**.

## Quick start

```bash
cd fund-overview-video
npm install

# Interactive preview
npm run studio

# Render the final MP4 to out/FundOverview2026.mp4
npm run render

# In a headless/CI environment with a system Chromium:
REMOTION_BROWSER_EXECUTABLE=/path/to/chromium npm run render
```

## Structure

| Path | Purpose |
| --- | --- |
| `src/config/timing.ts` | **Central timing configuration** — scene durations (seconds), FPS, dimensions, title-safe margin. Edit durations here; everything recalculates. |
| `src/config/theme.ts` | Brand colors (`#00023F` navy, `#82171A` red), typography tokens. |
| `src/config/captions.ts` | Caption cues synchronized with the narration. |
| `src/scenes/` | The seven scenes of the timeline. |
| `src/components/` | Reusable components: `BrandedTitle`, `StatisticCard`, `BenefitSequence`, `USMapAnimation`, `DistributionTimeline`, `BrollScene`, `DisclaimerFooter`, `EndCard`, plus `RevenueFlow`, `CaptionTrack`, `AudioTracks`, `Logo`, `AccentLine`, `SceneFade`. |
| `public/assets/` | All media (logo, b-roll, audio). |

## Media assets

Every media reference degrades gracefully: **if a file is missing, a branded
navy placeholder (or silence) renders instead of failing**, with a discreet
on-screen note naming the file to add. Use only locally supplied, approved
media — do not download third-party footage.

### Replacing the logo

Drop the approved transparent PNG at:

```
public/assets/usedc-logo.png
```

Until it exists, a clean SVG wordmark fallback is shown. No code changes
needed.

### Replacing b-roll

The primary rig footage lives at:

```
public/assets/rig-broll.mp4
```

Scenes also look for optional dedicated clips first and fall back to the
primary rig footage automatically:

| File | Used by |
| --- | --- |
| `public/assets/broll/aerial-basin.mp4` | Scene 2 (benefits) |
| `public/assets/broll/production.mp4` | Scene 5 (cash flow) — first choice |
| `public/assets/broll/pumpjack.mp4` | Scene 5 (cash flow) — second choice |
| `public/assets/broll/hero.mp4` | Scene 7 (closing hero shot) |

Additional approved drilling, pumpjack, aerial-basin, pipeline, and
production clips go in `public/assets/broll/`. To point a scene at a new
clip, edit the `src` candidate list in the corresponding file under
`src/scenes/` (each `BrollScene` takes an ordered list of candidates).
Footage is displayed with `object-fit: cover`, a slow controlled zoom, and a
navy overlay for text legibility — 1080p or higher source is recommended.

### Narration and music

```
public/assets/audio/narration.mp3   # voiceover (full level) — INCLUDED
public/assets/audio/music.mp3       # instrumental bed (ducked to ~12%, looped) — add your own
```

A narration recording is **included**: it was synthesized locally with the
open-source Kokoro neural TTS model (Apache-2.0) via `sherpa-onnx`, using the
"am_michael" voice at a broadcast pace. Scene durations in
`src/config/timing.ts` and caption cues in `src/config/captions.ts` are
timed to this recording (total runtime ≈ 66 s).

To replace it with a studio voiceover, overwrite `narration.mp3` (script
below), then re-time `SCENE_SECONDS` and the caption cues to the new read.
Music is optional and not included — drop an approved instrumental bed at
`music.mp3` and it is automatically looped, ducked under the narration, and
faded out. Missing audio files simply render silent.

### Narration script

> The U.S. Energy 2026 Drilling Fund is designed to provide accredited
> investors with three potential benefits: meaningful tax advantages, cash
> flow, and long-term capital appreciation.
>
> The Fund develops oil and natural gas wells across established U.S. basins
> and is intended for qualified investors seeking to lower taxable income
> while diversifying their portfolios through alternative energy investments.
>
> Investors may receive up to a 90% first-year tax deduction through
> Intangible Drilling Costs, a potential 15% to 25% depletion allowance on
> production income, and potential alternative minimum tax relief on
> qualifying IDC deductions.
>
> Returns are generated through oil and natural gas production, with a target
> of approximately 12% annual cash flow during the first five years once
> sufficient capital is deployed and producing.
>
> Distributions are expected to begin approximately 12 months after the Fund
> closes, subject to production performance and commodity prices.
>
> U.S. Energy Development Corporation. Direct energy investment backed by
> more than four decades of experience.

## Editing scene timing

All durations live in `src/config/timing.ts`:

```ts
export const SCENE_SECONDS = {
  scene1Title: 5,
  scene2Benefits: 8,
  scene3Map: 8,
  scene4TaxStats: 13,
  scene5CashFlow: 11,
  scene6Timeline: 8,
  scene7EndCard: 7,
};
```

Change any value and the scene windows, total composition length, and scene
sequencing update automatically. Caption cues in `src/config/captions.ts`
use absolute seconds, so shift them if you re-time scenes.

## Timeline

Times reflect the current narration-synced durations (≈ 66 s total).

| Scene | Time | Content |
| --- | --- | --- |
| 1 | 0:00–0:05 | Rig footage, logo, red rule, "2026 DRILLING FUND" |
| 2 | 0:05–0:12 | Three benefit statements, one at a time |
| 3 | 0:12–0:21 | Animated U.S. basin map (SVG) |
| 4 | 0:21–0:39 | Sequential tax-benefit statistics with count-up |
| 5 | 0:39–0:50 | 12% cash-flow target + revenue-flow graphic |
| 6 | 0:50–0:59 | 12-month distribution timeline |
| 7 | 0:59–1:06 | Rig hero shot → navy end card, "Learn More" |

## Compliance note

The video includes a persistent accredited-investor disclaimer
(`DisclaimerFooter`) on graphic scenes and a qualifier on the distribution
timeline. Review all on-screen language against the fund's offering
documents before distribution.
