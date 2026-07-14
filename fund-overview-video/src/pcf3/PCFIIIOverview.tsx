import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {PCF3_SCENES, Pcf3SceneKey, PCF3_TOTAL_DURATION_IN_FRAMES} from './timing';
import {PCF3_CAPTIONS} from './captions';
import {COLORS} from '../config/theme';
import {SceneFade} from '../components/SceneFade';
import {CaptionTrack} from '../components/CaptionTrack';
import {AudioTracks} from '../components/AudioTracks';
import {Pcf3Scene1Title} from './scenes/Pcf3Scene1Title';
import {Pcf3Scene2IncomeGrowth} from './scenes/Pcf3Scene2IncomeGrowth';
import {Pcf3Scene3Categories} from './scenes/Pcf3Scene3Categories';
import {Pcf3Scene4Map} from './scenes/Pcf3Scene4Map';
import {Pcf3Scene5Drip} from './scenes/Pcf3Scene5Drip';
import {Pcf3Scene6Accredited} from './scenes/Pcf3Scene6Accredited';
import {Pcf3Scene7EndCard} from './scenes/Pcf3Scene7EndCard';

export const PCF3_NARRATION_PATH = 'assets/audio/pcf3-narration.mp3';

const SCENE_COMPONENTS: Record<Pcf3SceneKey, React.FC> = {
  scene1Title: Pcf3Scene1Title,
  scene2IncomeGrowth: Pcf3Scene2IncomeGrowth,
  scene3Categories: Pcf3Scene3Categories,
  scene4Map: Pcf3Scene4Map,
  scene5Drip: Pcf3Scene5Drip,
  scene6Accredited: Pcf3Scene6Accredited,
  scene7EndCard: Pcf3Scene7EndCard,
};

const SCENE_NAMES: Record<Pcf3SceneKey, string> = {
  scene1Title: '1 — Title Montage',
  scene2IncomeGrowth: '2 — Income + Growth',
  scene3Categories: '3 — Asset Categories',
  scene4Map: '4 — Multi-Region Map',
  scene5Drip: '5 — DRIP',
  scene6Accredited: '6 — Accredited Investors',
  scene7EndCard: '7 — End Card',
};

// Scene 7 handles its own internal dissolve to the end card.
const NO_FADE_OUT: Pcf3SceneKey[] = ['scene7EndCard'];
const NO_FADE_IN: Pcf3SceneKey[] = ['scene1Title'];

export const PCFIIIOverview: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: COLORS.navy}}>
      {PCF3_SCENES.map(({key, from, durationInFrames}) => {
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
      <CaptionTrack cues={PCF3_CAPTIONS} />
      <AudioTracks
        narrationPath={PCF3_NARRATION_PATH}
        durationInFrames={PCF3_TOTAL_DURATION_IN_FRAMES}
      />
    </AbsoluteFill>
  );
};
