import React from 'react';
import {AbsoluteFill, interpolate, Sequence, useCurrentFrame} from 'remotion';
import {BrollScene} from '../../components/BrollScene';
import {BenefitSequence} from '../../components/BenefitSequence';
import {Logo} from '../../components/Logo';
import {AccentLine} from '../../components/AccentLine';
import {opsSceneWindow} from '../timing';
import {TYPE} from '../../config/theme';

const {durationInFrames} = opsSceneWindow('scene1Title');

// Controlled montage of operations footage behind the opening titles.
const CUTS = [
  {src: ['assets/operations-broll/rig.mp4', 'assets/rig-broll.mp4'], from: 0},
  {src: ['assets/operations-broll/producing.mp4', 'assets/rig-broll.mp4'], from: 1},
  {src: ['assets/operations-broll/pipeline.mp4', 'assets/rig-broll.mp4'], from: 2},
  {src: ['assets/operations-broll/aerial-permian.mp4', 'assets/rig-broll.mp4'], from: 3},
];
const CUT_FRAMES = Math.floor(durationInFrames / CUTS.length);

/**
 * Opening — montage of rigs, wells, pipelines, and aerial footage with the
 * logo, red rule, and the three descriptors.
 */
export const OpsScene1Title: React.FC = () => {
  const frame = useCurrentFrame();
  const logoOpacity = interpolate(frame, [6, 26], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const secondaryOpacity = interpolate(frame, [180, 205], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill>
      {CUTS.map((cut, i) => (
        <Sequence
          key={i}
          from={i * CUT_FRAMES}
          durationInFrames={
            i === CUTS.length - 1 ? durationInFrames - i * CUT_FRAMES : CUT_FRAMES
          }
          name={`Montage cut ${i + 1}`}
        >
          <BrollScene
            src={cut.src}
            durationInFrames={CUT_FRAMES}
            startFromSeconds={cut.from * 5}
            zoomFrom={1.02 + (i % 2) * 0.03}
            zoomTo={1.09 + (i % 2) * 0.02}
            overlayOpacity={0.68}
          />
        </Sequence>
      ))}
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: 'center',
          flexDirection: 'column',
          gap: 48,
        }}
      >
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 24,
            opacity: logoOpacity,
          }}
        >
          <Logo height={90} />
          <AccentLine width={220} delay={10} />
        </div>
        <BenefitSequence
          items={['EXPERIENCED', 'FLEXIBLE', 'PARTNERSHIP-DRIVEN']}
          delay={40}
          stagger={64}
          fontSize={72}
        />
        <div
          style={{
            ...TYPE.label,
            fontSize: 26,
            opacity: secondaryOpacity,
          }}
        >
          U.S. Energy Development Corporation
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
