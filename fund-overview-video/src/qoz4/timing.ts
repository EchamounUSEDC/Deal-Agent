/**
 * Central timing configuration for the QOZ IV overview.
 *
 * All scene durations are in seconds — edit them here and the scene
 * windows, total length, and sequencing recalculate automatically.
 * Durations are tuned to public/assets/audio/qoz4-narration.mp3.
 */
import {FPS} from '../config/timing';

export const QOZ4_SCENE_SECONDS = {
  scene1Title: 5, //           Drone energy footage + logo + title
  scene2GainFlow: 7.61, //     Capital gains → oil & gas development
  scene3Window180: 8.99, //    180-day window + eligible gains
  scene4TaxBenefits: 10.8, //  Three tax-benefit cards
  scene5Sponsor: 10.41, //     Sponsor strengths callouts
  scene6Horizon: 10.93, //     Year 0 → 10 development timeline
  scene7EndCard: 6.7, //       Sunset footage + end card
} as const;

export type Qoz4SceneKey = keyof typeof QOZ4_SCENE_SECONDS;

const ORDER: Qoz4SceneKey[] = [
  'scene1Title',
  'scene2GainFlow',
  'scene3Window180',
  'scene4TaxBenefits',
  'scene5Sponsor',
  'scene6Horizon',
  'scene7EndCard',
];

export interface Qoz4SceneWindow {
  key: Qoz4SceneKey;
  from: number;
  durationInFrames: number;
}

export const QOZ4_SCENES: Qoz4SceneWindow[] = (() => {
  let cursor = 0;
  return ORDER.map((key) => {
    const durationInFrames = Math.round(QOZ4_SCENE_SECONDS[key] * FPS);
    const window = {key, from: cursor, durationInFrames};
    cursor += durationInFrames;
    return window;
  });
})();

export const qoz4SceneWindow = (key: Qoz4SceneKey): Qoz4SceneWindow => {
  const found = QOZ4_SCENES.find((s) => s.key === key);
  if (!found) {
    throw new Error(`Unknown scene: ${key}`);
  }
  return found;
};

export const QOZ4_TOTAL_DURATION_IN_FRAMES = QOZ4_SCENES.reduce(
  (sum, s) => sum + s.durationInFrames,
  0,
);
