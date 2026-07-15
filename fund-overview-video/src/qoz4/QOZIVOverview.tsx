import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {QOZ4_SCENES, Qoz4SceneKey, QOZ4_TOTAL_DURATION_IN_FRAMES} from './timing';
import {QOZ4_CAPTIONS} from './captions';
import {COLORS} from '../config/theme';
import {SceneFade} from '../components/SceneFade';
import {CaptionTrack} from '../components/CaptionTrack';
import {AudioTracks} from '../components/AudioTracks';
import {Qoz4Scene1Title} from './scenes/Qoz4Scene1Title';
import {Qoz4Scene2GainFlow} from './scenes/Qoz4Scene2GainFlow';
import {Qoz4Scene3Window180} from './scenes/Qoz4Scene3Window180';
import {Qoz4Scene4TaxBenefits} from './scenes/Qoz4Scene4TaxBenefits';
import {Qoz4Scene5Sponsor} from './scenes/Qoz4Scene5Sponsor';
import {Qoz4Scene6Horizon} from './scenes/Qoz4Scene6Horizon';
import {Qoz4Scene7EndCard} from './scenes/Qoz4Scene7EndCard';

export const QOZ4_NARRATION_PATH = 'assets/audio/qoz4-narration.mp3';

const SCENE_COMPONENTS: Record<Qoz4SceneKey, React.FC> = {
  scene1Title: Qoz4Scene1Title,
  scene2GainFlow: Qoz4Scene2GainFlow,
  scene3Window180: Qoz4Scene3Window180,
  scene4TaxBenefits: Qoz4Scene4TaxBenefits,
  scene5Sponsor: Qoz4Scene5Sponsor,
  scene6Horizon: Qoz4Scene6Horizon,
  scene7EndCard: Qoz4Scene7EndCard,
};

const SCENE_NAMES: Record<Qoz4SceneKey, string> = {
  scene1Title: '1 — Skyline Title',
  scene2GainFlow: '2 — Capital Gain Flow',
  scene3Window180: '3 — 180-Day Window',
  scene4TaxBenefits: '4 — Tax Benefit Cards',
  scene5Sponsor: '5 — Sponsor Strengths',
  scene6Horizon: '6 — 10-Year Horizon',
  scene7EndCard: '7 — End Card',
};

// Scene 7 handles its own internal dissolve to the end card.
const NO_FADE_OUT: Qoz4SceneKey[] = ['scene7EndCard'];
const NO_FADE_IN: Qoz4SceneKey[] = ['scene1Title'];

export const QOZIVOverview: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: COLORS.navy}}>
      {QOZ4_SCENES.map(({key, from, durationInFrames}) => {
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
      <CaptionTrack cues={QOZ4_CAPTIONS} />
      <AudioTracks
        narrationPath={QOZ4_NARRATION_PATH}
        durationInFrames={QOZ4_TOTAL_DURATION_IN_FRAMES}
      />
    </AbsoluteFill>
  );
};
