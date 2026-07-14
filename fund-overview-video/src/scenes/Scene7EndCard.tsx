import React from 'react';
import {AbsoluteFill, interpolate, Sequence, useCurrentFrame} from 'remotion';
import {BrollScene} from '../components/BrollScene';
import {EndCard} from '../components/EndCard';
import {sceneWindow} from '../config/timing';

const {durationInFrames} = sceneWindow('scene7EndCard');

// The rig hero shot holds for the first stretch, then dissolves into the
// solid navy end card.
const HERO_FRAMES = Math.round(durationInFrames * 0.38);
const DISSOLVE = 16;

/**
 * 0:53–1:00 — Return to the strongest rig hero shot, then transition into
 * the solid navy end card with logo, red rule, and "Learn More".
 */
export const Scene7EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const cardOpacity = interpolate(
    frame,
    [HERO_FRAMES - DISSOLVE, HERO_FRAMES],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return (
    <AbsoluteFill>
      <Sequence durationInFrames={HERO_FRAMES} name="Rig hero shot">
        <BrollScene
          src={['assets/broll/hero.mp4', 'assets/rig-broll.mp4']}
          durationInFrames={HERO_FRAMES}
          startFromSeconds={2}
          zoomFrom={1.05}
          zoomTo={1.12}
          overlayOpacity={0.45}
        />
      </Sequence>
      <Sequence from={HERO_FRAMES - DISSOLVE} name="End card">
        <AbsoluteFill style={{opacity: cardOpacity}}>
          <EndCard delay={DISSOLVE} />
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};
