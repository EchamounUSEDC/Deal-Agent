import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {BrollScene} from '../../components/BrollScene';
import {BrandedTitle} from '../../components/BrandedTitle';
import {Logo} from '../../components/Logo';
import {qoz4SceneWindow} from '../timing';

const {durationInFrames} = qoz4SceneWindow('scene1Title');

/**
 * 0:00–0:05 — Aerial energy-operations footage; logo and title fade in.
 */
export const Qoz4Scene1Title: React.FC = () => {
  const frame = useCurrentFrame();
  const logoOpacity = interpolate(frame, [6, 26], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <BrollScene
      src={['assets/qoz-broll/aerial.mp4', 'assets/qoz-broll/operations.mp4', 'assets/rig-broll.mp4']}
      durationInFrames={durationInFrames}
      zoomFrom={1.0}
      zoomTo={1.08}
      overlayOpacity={0.6}
    >
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: 'center',
          flexDirection: 'column',
          gap: 52,
        }}
      >
        <div style={{opacity: logoOpacity}}>
          <Logo height={92} />
        </div>
        <BrandedTitle
          title="QUALIFIED OPPORTUNITY ZONE IV"
          subtitle="Institutional Energy Investment"
          delay={14}
          titleSize={88}
        />
      </AbsoluteFill>
    </BrollScene>
  );
};
