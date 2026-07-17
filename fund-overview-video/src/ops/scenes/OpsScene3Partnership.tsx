import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {PartnershipDataGraphic} from '../components/PartnershipDataGraphic';
import {COLORS, TYPE} from '../../config/theme';

const CALLOUTS = [
  'Disciplined Underwriting',
  'Informed Development Planning',
  'Ongoing Performance Optimization',
];

/**
 * Operated platform + strategic non-operated partnerships with data
 * flowing back to U.S. Energy.
 */
export const OpsScene3Partnership: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const headOpacity = interpolate(frame, [4, 22], [0, 1], {
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
        gap: 8,
      }}
    >
      <div
        style={{
          textAlign: 'center',
          opacity: headOpacity,
          marginBottom: 6,
        }}
      >
        <div style={{...TYPE.hero, fontSize: 50, letterSpacing: '0.09em'}}>
          OPERATED PLATFORM{' '}
          <span style={{color: COLORS.redBright, fontWeight: 300}}>+</span>{' '}
          STRATEGIC NON-OPERATED PARTNERSHIPS
        </div>
        <div
          style={{
            ...TYPE.label,
            fontSize: 23,
            marginTop: 18,
          }}
        >
          Expanded Access to Subsurface and Operational Data
        </div>
      </div>

      <PartnershipDataGraphic delay={16} />

      <div style={{display: 'flex', gap: 60, marginTop: 4}}>
        {CALLOUTS.map((c, i) => {
          const calloutIn = spring({
            frame: frame - (170 + i * 22),
            fps,
            config: {damping: 200, stiffness: 100},
          });
          return (
            <div
              key={c}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 16,
                opacity: calloutIn,
                transform: `translateX(${interpolate(calloutIn, [0, 1], [18, 0])}px)`,
              }}
            >
              <div style={{width: 28, height: 3, backgroundColor: COLORS.red}} />
              <div style={{...TYPE.body, fontSize: 25, color: COLORS.white}}>
                {c}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
