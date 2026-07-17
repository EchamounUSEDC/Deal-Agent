import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {BasinMapAnimation} from '../components/BasinMapAnimation';
import {AccentLine} from '../../components/AccentLine';
import {COLORS, FONT_FAMILY, TYPE} from '../../config/theme';

/**
 * Basin coverage — the supplied basin map (or SVG fallback) with Permian,
 * Delaware, and Eagle Ford called out, plus the strategic-focus panel.
 */
export const OpsScene4Basins: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const headOpacity = interpolate(frame, [4, 22], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const primaryIn = spring({
    frame: frame - 120,
    fps,
    config: {damping: 200, stiffness: 90},
  });
  const secondaryIn = spring({
    frame: frame - 170,
    fps,
    config: {damping: 200, stiffness: 90},
  });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(110% 90% at 50% 30%, ${COLORS.navySoft} 0%, ${COLORS.navy} 65%, ${COLORS.navyDeep} 100%)`,
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'row',
        gap: 70,
      }}
    >
      <div style={{display: 'flex', flexDirection: 'column', maxWidth: 640}}>
        <div style={{opacity: headOpacity}}>
          <div style={{...TYPE.hero, fontSize: 56, letterSpacing: '0.08em', lineHeight: 1.15}}>
            ACTIVE ACROSS MAJOR U.S. BASINS
          </div>
          <AccentLine width={200} delay={10} style={{marginTop: 22, marginBottom: 26}} />
          <div style={{...TYPE.body, fontSize: 26, color: COLORS.white70, lineHeight: 1.5}}>
            Conventional and Unconventional Opportunities Across the Lower 48
          </div>
        </div>

        {/* Primary callout */}
        <div
          style={{
            marginTop: 46,
            padding: '26px 34px',
            borderLeft: `4px solid ${COLORS.redBright}`,
            backgroundColor: 'rgba(10, 13, 82, 0.5)',
            opacity: primaryIn,
            transform: `translateX(${interpolate(primaryIn, [0, 1], [26, 0])}px)`,
          }}
        >
          <div style={{...TYPE.label, fontSize: 21, marginBottom: 8}}>
            Strategic Focus
          </div>
          <div
            style={{
              fontFamily: FONT_FAMILY,
              fontWeight: 700,
              fontSize: 42,
              letterSpacing: '0.1em',
              color: COLORS.white,
            }}
          >
            PERMIAN BASIN
          </div>
        </div>

        {/* Secondary callout */}
        <div
          style={{
            marginTop: 22,
            padding: '20px 34px',
            borderLeft: `2px solid ${COLORS.white30}`,
            opacity: secondaryIn,
            transform: `translateX(${interpolate(secondaryIn, [0, 1], [26, 0])}px)`,
          }}
        >
          <div style={{...TYPE.label, fontSize: 19, marginBottom: 6}}>
            Active Operated Projects
          </div>
          <div style={{...TYPE.body, fontSize: 27, color: COLORS.white}}>
            Delaware Basin and Eagle Ford Shale
          </div>
        </div>
      </div>

      <BasinMapAnimation width={880} delay={8} />
    </AbsoluteFill>
  );
};
