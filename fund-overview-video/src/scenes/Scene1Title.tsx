import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {BrollScene} from '../components/BrollScene';
import {BrandedTitle} from '../components/BrandedTitle';
import {Logo} from '../components/Logo';
import {sceneWindow} from '../config/timing';

const {durationInFrames} = sceneWindow('scene1Title');

/**
 * 0:00–0:05 — Full-screen drilling-rig footage; the logo and a thin red
 * line fade in over the title lockup.
 */
export const Scene1Title: React.FC = () => {
  const frame = useCurrentFrame();
  const logoOpacity = interpolate(frame, [6, 26], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <BrollScene
      src={['assets/rig-broll.mp4']}
      durationInFrames={durationInFrames}
      zoomFrom={1.0}
      zoomTo={1.07}
    >
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: 'center',
          flexDirection: 'column',
          gap: 56,
        }}
      >
        <div style={{opacity: logoOpacity}}>
          <Logo height={96} />
        </div>
        <BrandedTitle
          title="2026 DRILLING FUND"
          subtitle="Fund-Level Overview"
          delay={14}
          titleSize={104}
        />
      </AbsoluteFill>
    </BrollScene>
  );
};
