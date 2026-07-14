import React from 'react';
import {
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY, TYPE} from '../config/theme';

/**
 * Horizontal 12-month timeline from "Fund Closing" to
 * "Expected Distributions". A red progress line sweeps across the months
 * with a leading marker; endpoint labels anchor each end.
 */
export const DistributionTimeline: React.FC<{
  width?: number;
  delay?: number;
  /** Frames the sweep takes to travel the full 12 months. */
  sweepDuration?: number;
  startLabel?: string;
  endLabel?: string;
}> = ({
  width = 1500,
  delay = 0,
  sweepDuration = 110,
  startLabel = 'FUND CLOSING',
  endLabel = 'EXPECTED DISTRIBUTIONS',
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const height = 220;
  const y = 120;
  const pad = 90;
  const lineWidth = width - pad * 2;

  const progress = interpolate(
    frame,
    [delay + 14, delay + 14 + sweepDuration],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.inOut(Easing.cubic),
    },
  );
  const baseIn = interpolate(frame, [delay, delay + 18], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  const months = Array.from({length: 13}, (_, i) => i);
  const sweepX = pad + lineWidth * progress;

  const endPop = spring({
    frame: frame - (delay + 14 + sweepDuration - 4),
    fps,
    config: {damping: 13, stiffness: 170, mass: 0.7},
  });

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {/* Base line */}
      <line
        x1={pad}
        y1={y}
        x2={pad + lineWidth * baseIn}
        y2={y}
        stroke={COLORS.white30}
        strokeWidth={2}
      />
      {/* Month ticks and labels */}
      {months.map((m) => {
        const x = pad + (lineWidth * m) / 12;
        const tickIn = interpolate(
          frame,
          [delay + 6 + m * 2, delay + 16 + m * 2],
          [0, 1],
          {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
        );
        const major = m === 0 || m === 12;
        const reached = progress >= m / 12;
        return (
          <g key={m} opacity={tickIn}>
            <line
              x1={x}
              y1={y - (major ? 16 : 9)}
              x2={x}
              y2={y + (major ? 16 : 9)}
              stroke={reached ? COLORS.redBright : COLORS.white30}
              strokeWidth={major ? 3 : 2}
            />
            {m % 3 === 0 && !major ? (
              <text
                x={x}
                y={y + 44}
                textAnchor="middle"
                fontFamily={FONT_FAMILY}
                fontSize={20}
                fill={COLORS.white50}
                letterSpacing={2}
              >
                {`MO ${m}`}
              </text>
            ) : null}
          </g>
        );
      })}
      {/* Red progress sweep */}
      <line
        x1={pad}
        y1={y}
        x2={sweepX}
        y2={y}
        stroke={COLORS.redBright}
        strokeWidth={4}
      />
      {/* Leading marker */}
      <circle cx={sweepX} cy={y} r={10} fill={COLORS.redBright} />
      <circle cx={sweepX} cy={y} r={4} fill={COLORS.white} />
      {/* Endpoint markers */}
      <circle cx={pad} cy={y} r={9} fill={COLORS.white} opacity={baseIn} />
      <circle
        cx={pad + lineWidth}
        cy={y}
        r={11 * endPop}
        fill={COLORS.redBright}
      />
      {/* Endpoint labels */}
      <text
        x={pad}
        y={y - 42}
        textAnchor="start"
        fontFamily={FONT_FAMILY}
        fontWeight={600}
        fontSize={26}
        letterSpacing={4}
        fill={COLORS.white}
        opacity={baseIn}
      >
        {startLabel}
      </text>
      <text
        x={pad + lineWidth}
        y={y - 42}
        textAnchor="end"
        fontFamily={FONT_FAMILY}
        fontWeight={600}
        fontSize={26}
        letterSpacing={4}
        fill={COLORS.white}
        opacity={Math.min(endPop, 1)}
      >
        {endLabel}
      </text>
      {/* +12 months annotation under the end marker */}
      <text
        x={pad + lineWidth}
        y={y + 46}
        textAnchor="end"
        fontFamily={TYPE.body.fontFamily}
        fontSize={21}
        fill={COLORS.white50}
        letterSpacing={2}
        opacity={Math.min(endPop, 1)}
      >
        ~12 MONTHS
      </text>
    </svg>
  );
};
