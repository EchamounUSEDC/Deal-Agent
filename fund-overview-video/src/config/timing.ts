/**
 * Central timing configuration.
 *
 * All scene durations are declared here in seconds. Edit the `seconds`
 * values below and every scene, caption window, and the total composition
 * length recalculate automatically.
 */

export const FPS = 30;

export const SCENE_SECONDS = {
  scene1Title: 5, //    0:00–0:05  Rig footage + logo + title
  scene2Benefits: 8, // 0:05–0:13  Three benefit statements
  scene3Map: 8, //      0:13–0:21  U.S. basin map
  scene4TaxStats: 13, //0:21–0:34  Tax-benefit statistics
  scene5CashFlow: 11, //0:34–0:45  Revenue flow / 12% cash flow
  scene6Timeline: 8, // 0:45–0:53  Distribution timeline
  scene7EndCard: 7, //  0:53–1:00  Hero shot + end card
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
