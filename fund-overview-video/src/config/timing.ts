/**
 * Central timing configuration.
 *
 * All scene durations are declared here in seconds. Edit the `seconds`
 * values below and every scene, caption window, and the total composition
 * length recalculate automatically.
 */

export const FPS = 30;

// Durations are tuned to the recorded narration in
// public/assets/audio/narration.mp3 so each paragraph lands on its scene.
// If you replace the voiceover, adjust these (and src/config/captions.ts).
export const SCENE_SECONDS = {
  scene1Title: 5, //       0:00–0:05  Rig footage + logo + title
  scene2Benefits: 6.67, // 0:05–0:12  Three benefit statements
  scene3Map: 9.54, //      0:12–0:21  U.S. basin map
  scene4TaxStats: 17.84, //0:21–0:39  Tax-benefit statistics
  scene5CashFlow: 11.1, // 0:39–0:50  Revenue flow / 12% cash flow
  scene6Timeline: 8.59, // 0:50–0:59  Distribution timeline
  scene7EndCard: 7.5, //   0:59–1:06  Hero shot + end card
} as const;

export type SceneKey = keyof typeof SCENE_SECONDS;

/** Frames each scene fades in/out over (restrained cross-dissolve to navy). */
export const SCENE_FADE_FRAMES = 12;

const ORDER: SceneKey[] = [
  'scene1Title',
  'scene2Benefits',
  'scene3Map',
  'scene4TaxStats',
  'scene5CashFlow',
  'scene6Timeline',
  'scene7EndCard',
];

export interface SceneWindow {
  key: SceneKey;
  from: number; // first frame of the scene
  durationInFrames: number;
}

export const SCENES: SceneWindow[] = (() => {
  let cursor = 0;
  return ORDER.map((key) => {
    const durationInFrames = Math.round(SCENE_SECONDS[key] * FPS);
    const window = {key, from: cursor, durationInFrames};
    cursor += durationInFrames;
    return window;
  });
})();

export const sceneWindow = (key: SceneKey): SceneWindow => {
  const found = SCENES.find((s) => s.key === key);
  if (!found) {
    throw new Error(`Unknown scene: ${key}`);
  }
  return found;
};

export const TOTAL_DURATION_IN_FRAMES = SCENES.reduce(
  (sum, s) => sum + s.durationInFrames,
  0,
);

export const VIDEO_WIDTH = 1920;
export const VIDEO_HEIGHT = 1080;

/** Title-safe margin (px from each edge at 1920x1080). */
export const TITLE_SAFE_MARGIN = 96;
