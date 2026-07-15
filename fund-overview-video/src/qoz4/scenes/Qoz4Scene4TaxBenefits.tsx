import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {TaxBenefitCards} from '../components/TaxBenefitCards';
import {DisclaimerFooter} from '../../components/DisclaimerFooter';
import {COLORS, TYPE} from '../../config/theme';

/**
 * 0:22–0:36 — Three tax-benefit cards on a dark navy field.
 */
export const Qoz4Scene4TaxBenefits: React.FC = () => {
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
        gap: 60,
      }}
    >
      <div style={{...TYPE.label, fontSize: 26, opacity: kickerOpacity}}>
        Potential Tax Benefits
      </div>
      <TaxBenefitCards delay={14} stagger={92} />
      <DisclaimerFooter
        text="Benefits depend on current law and individual circumstances."
        delay={40}
      />
    </AbsoluteFill>
  );
};
