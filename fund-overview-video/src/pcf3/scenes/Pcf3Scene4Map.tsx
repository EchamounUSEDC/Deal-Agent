import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {USAssetMap} from '../components/USAssetMap';
import {COLORS, TYPE} from '../../config/theme';

const HEADLINES = ['MULTI-ASSET', 'MULTI-STRATEGY', 'MULTI-REGION'];

/**
 * 0:25–0:35 — Minimalist U.S. map with regional markers and asset-type
 * icons demonstrating flexibility across locations and strategies.
 */
export const Pcf3Scene4Map: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const supportOpacity = interpolate(frame, [150, 172], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(110% 90% at 50% 30%, ${COLORS.navySoft} 0%, ${COLORS.navy} 65%, ${COLORS.navyDeep} 100%)`,
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'row',
        gap: 90,
        paddingLeft: 40,
      }}
    >
      <div style={{display: 'flex', flexDirection: 'column', gap: 40}}>
        {HEADLINES.map((h, i) => {
          const enter = spring({
            frame: frame - (16 + i * 34),
            fps,
            config: {damping: 200, stiffness: 90},
          });
          return (
            <div
              key={h}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 26,
                opacity: enter,
                transform: `translateX(${interpolate(enter, [0, 1], [30, 0])}px)`,
              }}
            >
              <div style={{width: 46, height: 4, backgroundColor: COLORS.red}} />
              <div style={{...TYPE.hero, fontSize: 58, letterSpacing: '0.08em'}}>
                {h}
              </div>
            </div>
          );
        })}
        <div
          style={{
            ...TYPE.body,
            fontSize: 26,
            maxWidth: 560,
            lineHeight: 1.5,
            marginTop: 18,
            color: COLORS.white70,
            opacity: supportOpacity,
          }}
        >
          Flexibility Across Energy Asset Categories and Geographic Regions
        </div>
      </div>
      <USAssetMap width={880} delay={8} traceDuration={40} markerStagger={9} />
    </AbsoluteFill>
  );
};
