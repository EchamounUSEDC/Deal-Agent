import React from 'react';
import {AbsoluteFill} from 'remotion';
import {IncomeGrowthSplit} from '../components/IncomeGrowthSplit';
import {COLORS} from '../../config/theme';

/**
 * 0:05–0:13 — Balanced split: recurring cash flow on one side, increasing
 * asset value on the other.
 */
export const Pcf3Scene2IncomeGrowth: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(110% 90% at 50% 30%, ${COLORS.navySoft} 0%, ${COLORS.navy} 60%, ${COLORS.navyDeep} 100%)`,
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <IncomeGrowthSplit delay={8} />
    </AbsoluteFill>
  );
};
