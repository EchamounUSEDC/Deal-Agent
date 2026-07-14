import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {AssetCategoryCard} from '../components/AssetCategoryCard';
import {COLORS, TYPE} from '../../config/theme';

/**
 * 0:13–0:25 — Three animated asset-category panels, each with an icon and
 * approved b-roll behind a navy wash.
 */
export const Pcf3Scene3Categories: React.FC = () => {
  const frame = useCurrentFrame();
  const kickerOpacity = interpolate(frame, [4, 22], [0, 1], {
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
        gap: 54,
      }}
    >
      <div style={{...TYPE.label, fontSize: 26, opacity: kickerOpacity}}>
        Investment Strategies
      </div>
      <div style={{display: 'flex', gap: 44}}>
        <AssetCategoryCard
          icon="producing"
          title="PRODUCING ASSETS"
          line1="Proved Developed Producing Assets"
          line2="Current Cash Flow"
          broll={['assets/broll/producing.mp4', 'assets/energy-broll-01.mp4', 'assets/rig-broll.mp4']}
          delay={20}
        />
        <AssetCategoryCard
          icon="development"
          title="DEVELOPMENT OPPORTUNITIES"
          line1="Proved Undeveloped and Development Assets"
          line2="Growth Potential"
          broll={['assets/broll/development.mp4', 'assets/energy-broll-02.mp4', 'assets/rig-broll.mp4']}
          delay={150}
        />
        <AssetCategoryCard
          icon="infrastructure"
          title="INFRASTRUCTURE AND MINERALS"
          line1="Portfolio Diversification"
          line2="Potential Stability"
          broll={['assets/broll/infrastructure.mp4', 'assets/energy-broll-01.mp4', 'assets/rig-broll.mp4']}
          delay={250}
        />
      </div>
    </AbsoluteFill>
  );
};
