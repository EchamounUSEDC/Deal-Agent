# U.S. Energy Development Corporation — Fund Overview Videos

Institutional fund-overview videos (1920x1080 / 30 fps, ~60s) built with
[Remotion](https://www.remotion.dev), React, TypeScript, and CSS/SVG motion
graphics. Two compositions are registered:

| Composition ID | Fund | Narration file |
| --- | --- | --- |
| `FundOverview2026` | 2026 Drilling Fund | `public/assets/audio/narration.mp3` |
| `PCFIIIOverview` | Private Capital Fund III | `public/assets/audio/pcf3-narration.mp3` |
| `QOZIVOverview` | Qualified Opportunity Zone IV | `public/assets/audio/qoz4-narration.mp3` |
| `USEDCOoperationsOverview` | Operations & Partnership Overview | `public/assets/audio/ops-narration.mp3` |

## Quick start

```bash
cd fund-overview-video
npm install

# Interactive preview
npm run studio

# Render to out/
npm run render                                            # FundOverview2026
npx remotion render PCFIIIOverview out/PCFIIIOverview.mp4  # PCF III
npx remotion render QOZIVOverview out/QOZIVOverview.mp4    # QOZ IV
npx remotion render USEDCOoperationsOverview out/USEDCOoperationsOverview.mp4  # Operations

# In a headless/CI environment with a system Chromium:
REMOTION_BROWSER_EXECUTABLE=/path/to/chromium npm run render
```

## Structure

| Path | Purpose |
| --- | --- |
| `src/config/timing.ts` | **Central timing configuration** for `FundOverview2026` — scene durations (seconds), FPS, dimensions, title-safe margin. Edit durations here; everything recalculates. |
| `src/config/theme.ts` | Brand colors (`#00023F` navy, `#82171A` red), typography tokens. |
| `src/config/captions.ts` | Caption cues for `FundOverview2026`. |
| `src/scenes/` | The seven scenes of the 2026 Drilling Fund timeline. |
| `src/components/` | Shared components: `BrandedTitle`, `StatisticCard`, `BenefitSequence`, `USMapAnimation`, `DistributionTimeline`, `BrollScene`, `DisclaimerFooter`, `EndCard`, plus `RevenueFlow`, `CaptionTrack`, `AudioTracks`, `Logo`, `AccentLine`, `SceneFade`, `usMapGeometry`. |
| `src/pcf3/timing.ts` | **Central timing configuration** for `PCFIIIOverview`. |
| `src/pcf3/captions.ts` | Caption cues for `PCFIIIOverview`. |
| `src/pcf3/components/` | PCF III components: `IncomeGrowthSplit`, `AssetCategoryCard`, `USAssetMap`, `DripCompoundingAnimation`, `AccreditedInvestorScene`. |
| `src/pcf3/scenes/` | The seven scenes of the PCF III timeline. |
| `src/qoz4/timing.ts` | **Central timing configuration** for `QOZIVOverview`. |
| `src/qoz4/captions.ts` | Caption cues for `QOZIVOverview`. |
| `src/qoz4/components/` | QOZ IV components: `CapitalGainFlow`, `Calendar180`, `TaxBenefitCards`, `OpportunityZoneMap`, `DevelopmentTimeline`, `SponsorStrengths`. |
| `src/qoz4/scenes/` | The seven scenes of the QOZ IV timeline. |
| `src/ops/timing.ts` | **Central timing configuration** for `USEDCOoperationsOverview`. |
| `src/ops/captions.ts` | Caption cues for `USEDCOoperationsOverview`. |
| `src/ops/components/` | Operations components: `CapabilitySequence`, `PartnershipDataGraphic`, `BasinMapAnimation`, `PartnerBenefitCard`, `CapitalDeploymentGraphic`. |
| `src/ops/scenes/` | The seven scenes of the Operations timeline. |
| `public/assets/` | All media (logo, basin map, b-roll, audio). |

### Operations overview asset slots

B-roll lives under `public/assets/operations-broll/`: `rig.mp4`,
`producing.mp4`, `pipeline.mp4`, `aerial-permian.mp4`,
`technical-team.mp4`, `control-room.mp4`, `completion.mp4`, `hero.mp4` —
each slot falls back down its candidate list to `assets/rig-broll.mp4`,
then to the branded placeholder. The basin scene uses the supplied
`public/assets/usedc-basin-map.png` when present (shown with a slow zoom
and navy wash under the red basin callouts) and falls back to the shared
SVG map. On-screen statistics (project sizes, the "more than $1 billion
annually" figure) are plain props/text in
`src/ops/components/CapitalDeploymentGraphic.tsx` — edit them there.

### QOZ IV b-roll slots

The QOZ IV composition is an **oil & gas** Opportunity Zone fund and looks
for energy footage under `public/assets/qoz-broll/`: `aerial.mp4`,
`operations.mp4`, `production.mp4`, `sunset.mp4`. Each slot falls back down
its candidate list (ending at `assets/rig-broll.mp4`) and renders the
branded energy placeholder when nothing is supplied. The scene-4 qualifier
("Benefits depend on current law…") is passed to `DisclaimerFooter` in
`src/qoz4/scenes/Qoz4Scene4TaxBenefits.tsx`.

### PCF III b-roll slots

The PCF III composition looks for `assets/energy-broll-01.mp4` and
`assets/energy-broll-02.mp4` (per the asset brief), plus optional dedicated
clips in `assets/broll/`: `producing.mp4`, `development.mp4`,
`infrastructure.mp4`, `aerial.mp4`, `hero.mp4`. Every slot falls back down
its candidate list (ending at `assets/rig-broll.mp4`) and renders a branded
navy placeholder if nothing is supplied. Disclaimer and risk language lives
inline in `src/pcf3/components/AccreditedInvestorScene.tsx` and
`src/components/DisclaimerFooter.tsx` (default text) — edit those strings to
match the offering documents.

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
