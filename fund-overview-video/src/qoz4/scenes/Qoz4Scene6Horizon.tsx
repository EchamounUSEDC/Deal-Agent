import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {DevelopmentTimeline} from '../components/DevelopmentTimeline';
import {BrandedTitle} from '../../components/BrandedTitle';
import {COLORS, TYPE} from '../../config/theme';

/**
 * 0:48–0:55 — Year 0 → 10 development timeline; construction becomes
 * stabilized income-producing assets.
 */
export const Qoz4Scene6Horizon: React.FC = () => {
  const frame = useCurrentFrame();
  const supportOpacity = interpolate(frame, [110, 132], [0, 1], {
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
        gap: 20,
      }}
    >
      <BrandedTitle
        title="DESIGNED FOR A 10+ YEAR INVESTMENT HORIZON"
        delay={4}
        titleSize={58}
        accentWidth={200}
      />
      <DevelopmentTimeline delay={16} sweepDuration={110} />
      <div
        style={{
          display: 'flex',
          gap: 70,
          opacity: supportOpacity,
        }}
      >
        {['Limited Liquidity', 'Long-Term Value Creation'].map((t) => (
          <div key={t} style={{display: 'flex', alignItems: 'center', gap: 18}}>
            <div style={{width: 28, height: 3, backgroundColor: COLORS.red}} />
            <div style={{...TYPE.body, fontSize: 27, color: COLORS.white70}}>
              {t}
            </div>
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
