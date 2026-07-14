/**
 * Central timing configuration for the PCF III overview.
 *
 * All scene durations are in seconds — edit them here and the scene
 * windows, total length, and sequencing recalculate automatically.
 * Durations are tuned to public/assets/audio/pcf3-narration.mp3.
 */
import {FPS} from '../config/timing';

export const PCF3_SCENE_SECONDS = {
  scene1Title: 5, //           Montage + logo + title
  scene2IncomeGrowth: 4.51, // Income / growth split
  scene3Categories: 11.82, //  Three asset-category panels
  scene4Map: 13.75, //         Multi-asset / multi-strategy / multi-region map
  scene5Drip: 14.69, //        Distribution Reinvestment Program
  scene6Accredited: 9.97, //   Accredited-investor qualification screen
  scene7EndCard: 6.42, //      Footage + end card
} as const;

export type Pcf3SceneKey = keyof typeof PCF3_SCENE_SECONDS;

const ORDER: Pcf3SceneKey[] = [
  'scene1Title',
  'scene2IncomeGrowth',
  'scene3Categories',
  'scene4Map',
  'scene5Drip',
  'scene6Accredited',
  'scene7EndCard',
];

export interface Pcf3SceneWindow {
  key: Pcf3SceneKey;
  from: number;
  durationInFrames: number;
}

export const PCF3_SCENES: Pcf3SceneWindow[] = (() => {
  let cursor = 0;
  return ORDER.map((key) => {
    const durationInFrames = Math.round(PCF3_SCENE_SECONDS[key] * FPS);
    const window = {key, from: cursor, durationInFrames};
    cursor += durationInFrames;
    return window;
  });
})();

export const pcf3SceneWindow = (key: Pcf3SceneKey): Pcf3SceneWindow => {
  const found = PCF3_SCENES.find((s) => s.key === key);
  if (!found) {
    throw new Error(`Unknown scene: ${key}`);
  }
  return found;
};

export const PCF3_TOTAL_DURATION_IN_FRAMES = PCF3_SCENES.reduce(
  (sum, s) => sum + s.durationInFrames,
  0,
);
