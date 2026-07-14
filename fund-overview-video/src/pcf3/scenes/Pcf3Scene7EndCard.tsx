import React from 'react';
import {AbsoluteFill, interpolate, Sequence, useCurrentFrame} from 'remotion';
import {BrollScene} from '../../components/BrollScene';
import {EndCard} from '../../components/EndCard';
import {pcf3SceneWindow} from '../timing';

const {durationInFrames} = pcf3SceneWindow('scene7EndCard');

const HERO_FRAMES = Math.round(durationInFrames * 0.36);
const DISSOLVE = 16;

/**
 * 0:53–1:00 — Strong production/infrastructure footage dissolving into the
 * navy end card.
 */
export const Pcf3Scene7EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const cardOpacity = interpolate(
    frame,
    [HERO_FRAMES - DISSOLVE, HERO_FRAMES],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return (
    <AbsoluteFill>
      <Sequence durationInFrames={HERO_FRAMES} name="Production hero shot">
        <BrollScene
          src={['assets/broll/hero.mp4', 'assets/energy-broll-01.mp4', 'assets/rig-broll.mp4']}
          durationInFrames={HERO_FRAMES}
          startFromSeconds={2}
          zoomFrom={1.05}
          zoomTo={1.12}
          overlayOpacity={0.45}
        />
      </Sequence>
      <Sequence from={HERO_FRAMES - DISSOLVE} name="End card">
        <AbsoluteFill style={{opacity: cardOpacity}}>
          {/* "U.S. ENERGY" is carried by the logo above the title. */}
          <EndCard
            delay={DISSOLVE}
            title="PRIVATE CAPITAL FUND III"
            subtitle={null}
            tagline="A Diversified Approach to Energy Income and Growth"
            cta={null}
          />
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};
