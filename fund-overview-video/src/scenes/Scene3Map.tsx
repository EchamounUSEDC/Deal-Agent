import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {USMapAnimation} from '../components/USMapAnimation';
import {COLORS, TYPE} from '../config/theme';
import {AccentLine} from '../components/AccentLine';

/**
 * 0:13–0:21 — Minimalist animated U.S. map with markers across established
 * oil and natural gas basins.
 */
export const Scene3Map: React.FC = () => {
  const frame = useCurrentFrame();

  const headlineOpacity = interpolate(frame, [8, 28], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const secondLineOpacity = interpolate(frame, [110, 132], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.navy,
        background: `radial-gradient(110% 90% at 50% 30%, ${COLORS.navySoft} 0%, ${COLORS.navy} 65%, ${COLORS.navyDeep} 100%)`,
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'column',
      }}
    >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          opacity: headlineOpacity,
          marginBottom: 8,
        }}
      >
        <div style={{...TYPE.hero, fontSize: 44, letterSpacing: '0.08em'}}>
          Designed Exclusively for Accredited Investors
        </div>
        <AccentLine width={200} delay={14} style={{marginTop: 22}} />
      </div>

      <USMapAnimation width={880} delay={10} traceDuration={42} markerStagger={12} />

      <div
        style={{
          ...TYPE.body,
          fontSize: 32,
          letterSpacing: '0.1em',
          color: COLORS.white70,
          textTransform: 'uppercase',
          opacity: secondLineOpacity,
          marginTop: 8,
        }}
      >
        Alternative Energy Portfolio Diversification
      </div>
    </AbsoluteFill>
  );
};
