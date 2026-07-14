import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {DistributionTimeline} from '../components/DistributionTimeline';
import {BrandedTitle} from '../components/BrandedTitle';
import {COLORS, TYPE} from '../config/theme';

/**
 * 0:45–0:53 — Horizontal timeline from "Fund Closing" to
 * "Expected Distributions", sweeping across approximately 12 months.
 */
export const Scene6Timeline: React.FC = () => {
  const frame = useCurrentFrame();
  const qualifierOpacity = interpolate(frame, [150, 175], [0, 0.6], {
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
        gap: 40,
      }}
    >
      <BrandedTitle
        title="DISTRIBUTIONS EXPECTED"
        subtitle="Approximately 12 Months After Fund Closing"
        delay={4}
        titleSize={72}
        accentWidth={200}
      />
      <DistributionTimeline width={1520} delay={20} sweepDuration={120} />
      <div
        style={{
          ...TYPE.body,
          fontSize: 24,
          fontStyle: 'italic',
          color: COLORS.white,
          opacity: qualifierOpacity,
        }}
      >
        Subject to production performance and commodity prices.
      </div>
    </AbsoluteFill>
  );
};
