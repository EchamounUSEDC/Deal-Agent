import React from 'react';
import {
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, TYPE} from '../config/theme';

export interface CountUp {
  /** Final number displayed, e.g. 90. */
  to: number;
  from?: number;
  prefix?: string; // e.g. "UP TO "
  suffix?: string; // e.g. "%"
  /** For ranges like 15–25%: a second number counted alongside the first. */
  toSecondary?: number;
  rangeSeparator?: string;
}

/**
 * Large statistic with subtle count-up, a small uppercase label above and a
 * supporting line below. Used for the tax-benefit and cash-flow figures.
 */
export const StatisticCard: React.FC<{
  stat?: CountUp;
  /** Non-numeric headline (used when there is nothing to count). */
  headline?: string;
  label?: string;
  support?: string;
  delay?: number;
  countDuration?: number;
  statSize?: number;
  align?: 'center' | 'left';
}> = ({
  stat,
  headline,
  label,
  support,
  delay = 0,
  countDuration = 34,
  statSize = 150,
  align = 'center',
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const enter = spring({
    frame: frame - delay,
    fps,
    config: {damping: 200, stiffness: 100},
  });
  const rise = interpolate(enter, [0, 1], [30, 0]);

  const countProgress = interpolate(
    frame,
    [delay + 4, delay + 4 + countDuration],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    },
  );

  let headlineText = headline ?? '';
  if (stat) {
    const value = Math.round(
      (stat.from ?? 0) + ((stat.to - (stat.from ?? 0)) * countProgress),
    );
    headlineText = `${stat.prefix ?? ''}${value}`;
    if (stat.toSecondary !== undefined) {
      const secondary = Math.round(stat.toSecondary * countProgress);
      headlineText += `${stat.rangeSeparator ?? '–'}${secondary}`;
    }
    headlineText += stat.suffix ?? '';
  }

  const supportOpacity = interpolate(
    frame,
    [delay + 14, delay + 32],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  const isCenter = align === 'center';

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: isCenter ? 'center' : 'flex-start',
        textAlign: isCenter ? 'center' : 'left',
        opacity: enter,
        transform: `translateY(${rise}px)`,
      }}
    >
      {label ? (
        <div style={{...TYPE.label, fontSize: 24, marginBottom: 18}}>
          {label}
        </div>
      ) : null}
      <div
        style={{
          ...TYPE.hero,
          fontSize: statSize,
          lineHeight: 1,
          letterSpacing: '0.02em',
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        {headlineText}
      </div>
      {support ? (
        <div
          style={{
            ...TYPE.body,
            fontSize: 30,
            marginTop: 22,
            maxWidth: 900,
            color: COLORS.white70,
            opacity: supportOpacity,
          }}
        >
          {support}
        </div>
      ) : null}
    </div>
  );
};
