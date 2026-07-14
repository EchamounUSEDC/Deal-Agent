import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {SCENES, SceneKey} from './config/timing';
import {COLORS} from './config/theme';
import {SceneFade} from './components/SceneFade';
import {CaptionTrack} from './components/CaptionTrack';
import {AudioTracks} from './components/AudioTracks';
import {Scene1Title} from './scenes/Scene1Title';
import {Scene2Benefits} from './scenes/Scene2Benefits';
import {Scene3Map} from './scenes/Scene3Map';
import {Scene4TaxStats} from './scenes/Scene4TaxStats';
import {Scene5CashFlow} from './scenes/Scene5CashFlow';
import {Scene6Timeline} from './scenes/Scene6Timeline';
import {Scene7EndCard} from './scenes/Scene7EndCard';

const SCENE_COMPONENTS: Record<SceneKey, React.FC> = {
  scene1Title: Scene1Title,
  scene2Benefits: Scene2Benefits,
  scene3Map: Scene3Map,
  scene4TaxStats: Scene4TaxStats,
  scene5CashFlow: Scene5CashFlow,
  scene6Timeline: Scene6Timeline,
  scene7EndCard: Scene7EndCard,
};

const SCENE_NAMES: Record<SceneKey, string> = {
  scene1Title: '1 — Title',
  scene2Benefits: '2 — Benefits',
  scene3Map: '3 — U.S. Basins Map',
  scene4TaxStats: '4 — Tax Statistics',
  scene5CashFlow: '5 — Cash Flow',
  scene6Timeline: '6 — Distribution Timeline',
  scene7EndCard: '7 — End Card',
};

// Scene 1↔2 share continuous rig footage, and scene 7 handles its own
// internal dissolve to the end card — skip the navy fade at those joins.
const NO_FADE_OUT: SceneKey[] = ['scene1Title', 'scene7EndCard'];
const NO_FADE_IN: SceneKey[] = ['scene1Title', 'scene2Benefits'];

export const FundOverview2026: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: COLORS.navy}}>
      {SCENES.map(({key, from, durationInFrames}) => {
        const Scene = SCENE_COMPONENTS[key];
        return (
          <Sequence
            key={key}
            from={from}
            durationInFrames={durationInFrames}
            name={SCENE_NAMES[key]}
          >
            <SceneFade
              durationInFrames={durationInFrames}
              fadeIn={!NO_FADE_IN.includes(key)}
              fadeOut={!NO_FADE_OUT.includes(key)}
            >
              <Scene />
            </SceneFade>
          </Sequence>
        );
      })}
      <CaptionTrack />
      <AudioTracks />
    </AbsoluteFill>
  );
};
