/**
 * Central timing configuration for the Operations & Partnership overview.
 *
 * All scene durations are in seconds — edit them here and the scene
 * windows, total length, and sequencing recalculate automatically.
 * Durations are tuned to public/assets/audio/ops-narration.mp3.
 */
import {FPS} from '../config/timing';

export const OPS_SCENE_SECONDS = {
  scene1Title: 10.22, //       Montage + logo + three descriptors
  scene2Capabilities: 12.73, //Full-cycle expertise sequence
  scene3Partnership: 13.7, //  Operated platform + partner data graphic
  scene4Basins: 13.06, //      Basin map with Permian focus
  scene5Benefits: 10.89, //    Four partner-benefit cards
  scene6Capital: 7.71, //      Capital deployment graphic
  scene7EndCard: 6.22, //      Hero footage + end card
} as const;

export type OpsSceneKey = keyof typeof OPS_SCENE_SECONDS;

const ORDER: OpsSceneKey[] = [
  'scene1Title',
  'scene2Capabilities',
  'scene3Partnership',
  'scene4Basins',
  'scene5Benefits',
  'scene6Capital',
  'scene7EndCard',
];

export interface OpsSceneWindow {
  key: OpsSceneKey;
  from: number;
  durationInFrames: number;
}

export const OPS_SCENES: OpsSceneWindow[] = (() => {
  let cursor = 0;
  return ORDER.map((key) => {
    const durationInFrames = Math.round(OPS_SCENE_SECONDS[key] * FPS);
    const window = {key, from: cursor, durationInFrames};
    cursor += durationInFrames;
    return window;
  });
})();

export const opsSceneWindow = (key: OpsSceneKey): OpsSceneWindow => {
  const found = OPS_SCENES.find((s) => s.key === key);
  if (!found) {
    throw new Error(`Unknown scene: ${key}`);
  }
  return found;
};

export const OPS_TOTAL_DURATION_IN_FRAMES = OPS_SCENES.reduce(
  (sum, s) => sum + s.durationInFrames,
  0,
);
