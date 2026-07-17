import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {CapitalDeploymentGraphic} from '../components/CapitalDeploymentGraphic';
import {AccentLine} from '../../components/AccentLine';
import {COLORS, TYPE} from '../../config/theme';

/**
 * Capital deployment — ascending project markers, then the annual figure.
 */
export const OpsScene6Capital: React.FC = () => {
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
        <div style={{...TYPE.hero, fontSize: 54, letterSpacing: '0.09em'}}>
          FLEXIBLE CAPITAL ACROSS MULTIPLE PROJECTS
        </div>
        <AccentLine width={200} delay={10} style={{marginTop: 22}} />
      </div>
      <CapitalDeploymentGraphic delay={14} statAt={128} />
    </AbsoluteFill>
  );
};
