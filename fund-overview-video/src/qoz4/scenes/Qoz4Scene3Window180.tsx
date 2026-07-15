import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {Calendar180} from '../components/Calendar180';
import {AccentLine} from '../../components/AccentLine';
import {COLORS, TYPE} from '../../config/theme';

/**
 * 0:13–0:22 — 180-day investment window with the eligible-gains list.
 */
export const Qoz4Scene3Window180: React.FC = () => {
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
        gap: 26,
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
        <div style={{...TYPE.hero, fontSize: 60, letterSpacing: '0.08em'}}>
          180-DAY INVESTMENT WINDOW
        </div>
        <AccentLine width={210} delay={10} style={{marginTop: 24}} />
      </div>
      <Calendar180 delay={14} />
    </AbsoluteFill>
  );
};
