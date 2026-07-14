import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, TYPE} from '../config/theme';
import {AccentLine} from './AccentLine';
import {Logo} from './Logo';
import {DisclaimerFooter} from './DisclaimerFooter';

/**
 * Solid navy end card: white logo, thin red rule, company name, fund name,
 * and a "Learn More" call to action.
 */
export const EndCard: React.FC<{
  delay?: number;
}> = ({delay = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const logoIn = spring({
    frame: frame - delay,
    fps,
    config: {damping: 200, stiffness: 80},
  });
  const nameOpacity = interpolate(frame, [delay + 14, delay + 34], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const ctaOpacity = interpolate(frame, [delay + 34, delay + 54], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.navy,
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <div
          style={{
            opacity: logoIn,
            transform: `translateY(${interpolate(logoIn, [0, 1], [20, 0])}px)`,
          }}
        >
          <Logo height={130} />
        </div>
        <AccentLine width={260} delay={delay + 10} style={{marginTop: 44}} />
        <div
          style={{
            ...TYPE.hero,
            fontSize: 46,
            letterSpacing: '0.14em',
            marginTop: 44,
            textAlign: 'center',
            opacity: nameOpacity,
          }}
        >
          U.S. ENERGY DEVELOPMENT CORPORATION
        </div>
        <div
          style={{
            ...TYPE.label,
            fontSize: 30,
            letterSpacing: '0.3em',
            color: COLORS.white70,
            marginTop: 22,
            opacity: nameOpacity,
          }}
        >
          2026 Drilling Fund
        </div>
        <div
          style={{
            ...TYPE.body,
            fontSize: 28,
            fontWeight: 500,
            letterSpacing: '0.24em',
            textTransform: 'uppercase',
            color: COLORS.white,
            marginTop: 64,
            padding: '18px 54px',
            border: `1.5px solid ${COLORS.white30}`,
            opacity: ctaOpacity,
          }}
        >
          Learn More
        </div>
      </div>
      <DisclaimerFooter delay={delay + 40} />
    </AbsoluteFill>
  );
};
