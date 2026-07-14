import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {COLORS, TYPE} from '../config/theme';
import {AccentLine} from './AccentLine';

/**
 * Primary title lockup: large headline, optional kicker/subtitle, and a
 * thin red accent rule. Enters with a restrained rise-and-fade.
 */
export const BrandedTitle: React.FC<{
  title: string;
  subtitle?: string;
  kicker?: string;
  delay?: number;
  align?: 'center' | 'left';
  titleSize?: number;
  accentWidth?: number;
}> = ({
  title,
  subtitle,
  kicker,
  delay = 0,
  align = 'center',
  titleSize = 92,
  accentWidth = 240,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const enter = spring({
    frame: frame - delay,
    fps,
    config: {damping: 200, stiffness: 90},
  });
  const rise = interpolate(enter, [0, 1], [26, 0]);
  const subtitleOpacity = interpolate(
    frame,
    [delay + 12, delay + 30],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    },
  );

  const isCenter = align === 'center';

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: isCenter ? 'center' : 'flex-start',
        textAlign: isCenter ? 'center' : 'left',
      }}
    >
      {kicker ? (
        <div
          style={{
            ...TYPE.label,
            fontSize: 26,
            marginBottom: 26,
            opacity: subtitleOpacity,
          }}
        >
          {kicker}
        </div>
      ) : null}
      <div
        style={{
          ...TYPE.hero,
          fontSize: titleSize,
          lineHeight: 1.08,
          opacity: enter,
          transform: `translateY(${rise}px)`,
        }}
      >
        {title}
      </div>
      <AccentLine
        width={accentWidth}
        delay={delay + 8}
        style={{marginTop: 30, marginBottom: subtitle ? 28 : 0}}
      />
      {subtitle ? (
        <div
          style={{
            ...TYPE.body,
            fontSize: 34,
            fontWeight: 400,
            color: COLORS.white70,
            letterSpacing: '0.04em',
            opacity: subtitleOpacity,
          }}
        >
          {subtitle}
        </div>
      ) : null}
    </div>
  );
};
