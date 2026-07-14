import React from 'react';
import {AbsoluteFill, interpolate, Sequence, useCurrentFrame} from 'remotion';
import {BrollScene} from '../../components/BrollScene';
import {BrandedTitle} from '../../components/BrandedTitle';
import {Logo} from '../../components/Logo';
import {pcf3SceneWindow} from '../timing';

const {durationInFrames} = pcf3SceneWindow('scene1Title');

// Fast but controlled montage: three quick holds before the title settles.
const CUTS = [
  {src: ['assets/energy-broll-01.mp4', 'assets/rig-broll.mp4'], from: 0},
  {src: ['assets/energy-broll-02.mp4', 'assets/rig-broll.mp4'], from: 1},
  {src: ['assets/broll/aerial.mp4', 'assets/energy-broll-01.mp4', 'assets/rig-broll.mp4'], from: 2},
];
const CUT_FRAMES = Math.floor(durationInFrames / 3);

/**
 * 0:00–0:05 — Controlled montage of producing assets, pipelines, and aerial
 * footage; the logo and title fade in over it.
 */
export const Pcf3Scene1Title: React.FC = () => {
  const frame = useCurrentFrame();
  const logoOpacity = interpolate(frame, [6, 26], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill>
      {CUTS.map((cut, i) => (
        <Sequence
          key={i}
          from={i * CUT_FRAMES}
          durationInFrames={i === CUTS.length - 1 ? durationInFrames - i * CUT_FRAMES : CUT_FRAMES}
          name={`Montage cut ${i + 1}`}
        >
          <BrollScene
            src={cut.src}
            durationInFrames={CUT_FRAMES}
            startFromSeconds={cut.from * 6}
            zoomFrom={1.02 + i * 0.02}
            zoomTo={1.08 + i * 0.02}
            overlayOpacity={0.62}
          />
        </Sequence>
      ))}
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
          title="PRIVATE CAPITAL FUND III"
          subtitle="Diversified Energy Income and Growth"
          delay={14}
          titleSize={96}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
