import React from 'react';
import {AbsoluteFill, interpolate, Sequence, useCurrentFrame} from 'remotion';
import {BrollScene} from '../../components/BrollScene';
import {EndCard} from '../../components/EndCard';
import {opsSceneWindow} from '../timing';

const {durationInFrames} = opsSceneWindow('scene7EndCard');

const HERO_FRAMES = Math.round(durationInFrames * 0.36);
const DISSOLVE = 14;

/**
 * Closing — hero drilling/production footage into the navy end card.
 */
export const OpsScene7EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const cardOpacity = interpolate(
    frame,
    [HERO_FRAMES - DISSOLVE, HERO_FRAMES],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return (
    <AbsoluteFill>
      <Sequence durationInFrames={HERO_FRAMES} name="Hero shot">
        <BrollScene
          src={['assets/operations-broll/hero.mp4', 'assets/rig-broll.mp4']}
          durationInFrames={HERO_FRAMES}
          startFromSeconds={2}
          zoomFrom={1.05}
          zoomTo={1.12}
          overlayOpacity={0.45}
        />
      </Sequence>
      <Sequence from={HERO_FRAMES - DISSOLVE} name="End card">
        <AbsoluteFill style={{opacity: cardOpacity}}>
          <EndCard
            delay={DISSOLVE}
            title="U.S. ENERGY DEVELOPMENT CORPORATION"
            subtitle={null}
            tagline="Experience. Flexibility. Disciplined Execution."
            cta={null}
          />
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};
