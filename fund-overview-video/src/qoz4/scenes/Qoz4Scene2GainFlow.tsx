import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {CapitalGainFlow} from '../components/CapitalGainFlow';
import {BrandedTitle} from '../../components/BrandedTitle';
import {COLORS, TYPE} from '../../config/theme';

/**
 * 0:05–0:13 — Capital gains flow into real estate developments.
 */
export const Qoz4Scene2GainFlow: React.FC = () => {
  const frame = useCurrentFrame();
  const supportOpacity = interpolate(frame, [64, 86], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(110% 90% at 50% 28%, ${COLORS.navySoft} 0%, ${COLORS.navy} 60%, ${COLORS.navyDeep} 100%)`,
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'column',
        gap: 24,
      }}
    >
      <BrandedTitle
        title="TURN CAPITAL GAINS"
        subtitle="INTO LONG-TERM OPPORTUNITY"
        delay={4}
        titleSize={66}
        accentWidth={190}
      />
      <CapitalGainFlow delay={24} />
      <div
        style={{
          ...TYPE.label,
          fontSize: 25,
          opacity: supportOpacity,
        }}
      >
        Designed for Recently Realized Capital Gains
      </div>
    </AbsoluteFill>
  );
};
