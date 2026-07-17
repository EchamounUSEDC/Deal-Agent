import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {OPS_SCENES, OpsSceneKey, OPS_TOTAL_DURATION_IN_FRAMES} from './timing';
import {OPS_CAPTIONS} from './captions';
import {COLORS} from '../config/theme';
import {SceneFade} from '../components/SceneFade';
import {CaptionTrack} from '../components/CaptionTrack';
import {AudioTracks} from '../components/AudioTracks';
import {OpsScene1Title} from './scenes/OpsScene1Title';
import {OpsScene2Capabilities} from './scenes/OpsScene2Capabilities';
import {OpsScene3Partnership} from './scenes/OpsScene3Partnership';
import {OpsScene4Basins} from './scenes/OpsScene4Basins';
import {OpsScene5Benefits} from './scenes/OpsScene5Benefits';
import {OpsScene6Capital} from './scenes/OpsScene6Capital';
import {OpsScene7EndCard} from './scenes/OpsScene7EndCard';

export const OPS_NARRATION_PATH = 'assets/audio/ops-narration.mp3';

const SCENE_COMPONENTS: Record<OpsSceneKey, React.FC> = {
  scene1Title: OpsScene1Title,
  scene2Capabilities: OpsScene2Capabilities,
  scene3Partnership: OpsScene3Partnership,
  scene4Basins: OpsScene4Basins,
  scene5Benefits: OpsScene5Benefits,
  scene6Capital: OpsScene6Capital,
  scene7EndCard: OpsScene7EndCard,
};

const SCENE_NAMES: Record<OpsSceneKey, string> = {
  scene1Title: '1 — Title Montage',
  scene2Capabilities: '2 — Full-Cycle Expertise',
  scene3Partnership: '3 — Partnership Platform',
  scene4Basins: '4 — U.S. Basins',
  scene5Benefits: '5 — Partner Benefits',
  scene6Capital: '6 — Capital Deployment',
  scene7EndCard: '7 — End Card',
};

// Scene 7 handles its own internal dissolve to the end card.
const NO_FADE_OUT: OpsSceneKey[] = ['scene7EndCard'];
const NO_FADE_IN: OpsSceneKey[] = ['scene1Title'];

export const USEDCOoperationsOverview: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: COLORS.navy}}>
      {OPS_SCENES.map(({key, from, durationInFrames}) => {
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
      <CaptionTrack cues={OPS_CAPTIONS} />
      <AudioTracks
        narrationPath={OPS_NARRATION_PATH}
        durationInFrames={OPS_TOTAL_DURATION_IN_FRAMES}
      />
    </AbsoluteFill>
  );
};
