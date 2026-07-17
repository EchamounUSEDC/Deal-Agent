import React from 'react';
import {AbsoluteFill, interpolate, Sequence, useCurrentFrame} from 'remotion';
import {BrollScene} from '../../components/BrollScene';
import {EndCard} from '../../components/EndCard';
import {qoz4SceneWindow} from '../timing';

const {durationInFrames} = qoz4SceneWindow('scene7EndCard');

const HERO_FRAMES = Math.round(durationInFrames * 0.34);
const DISSOLVE = 14;

/**
 * 0:55–1:00 — Production operations at sunset, fading to the navy end card.
 */
export const Qoz4Scene7EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const cardOpacity = interpolate(
    frame,
    [HERO_FRAMES - DISSOLVE, HERO_FRAMES],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return (
    <AbsoluteFill>
      <Sequence durationInFrames={HERO_FRAMES} name="Sunset operations">
        <BrollScene
          src={['assets/qoz-broll/sunset.mp4', 'assets/qoz-broll/aerial.mp4', 'assets/rig-broll.mp4']}
          durationInFrames={HERO_FRAMES}
          startFromSeconds={1}
          zoomFrom={1.04}
          zoomTo={1.1}
          overlayOpacity={0.4}
        />
      </Sequence>
      <Sequence from={HERO_FRAMES - DISSOLVE} name="End card">
        <AbsoluteFill style={{opacity: cardOpacity}}>
          {/* "U.S. ENERGY" is carried by the logo above the title. */}
          <EndCard
            delay={DISSOLVE}
            title="QUALIFIED OPPORTUNITY ZONE IV"
            subtitle={null}
            tagline="Tax-Efficient Energy Investing"
            cta={null}
          />
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};
