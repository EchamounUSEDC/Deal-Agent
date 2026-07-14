import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {DripCompoundingAnimation} from '../components/DripCompoundingAnimation';
import {AccentLine} from '../../components/AccentLine';
import {COLORS, TYPE} from '../../config/theme';

/**
 * 0:35–0:46 — Distribution Reinvestment Program: quarterly distributions
 * flow into additional partnership units and the unit count compounds.
 */
export const Pcf3Scene5Drip: React.FC = () => {
  const frame = useCurrentFrame();
  const titleOpacity = interpolate(frame, [4, 22], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(110% 90% at 50% 25%, ${COLORS.navySoft} 0%, ${COLORS.navy} 60%, ${COLORS.navyDeep} 100%)`,
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'column',
        gap: 30,
      }}
    >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          opacity: titleOpacity,
        }}
      >
        <div style={{...TYPE.hero, fontSize: 52, letterSpacing: '0.1em'}}>
          DISTRIBUTION REINVESTMENT PROGRAM
        </div>
        <AccentLine width={200} delay={10} style={{marginTop: 24}} />
      </div>
      <DripCompoundingAnimation delay={18} periodFrames={88} />
    </AbsoluteFill>
  );
};
