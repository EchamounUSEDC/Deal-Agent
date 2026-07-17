import React from 'react';
import {
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY} from '../../config/theme';

/**
 * Year 0 → Year 10 horizontal timeline. A red sweep crosses the decade
 * while milestone icons transition from development (drilling derrick) to
 * a stabilized income-producing asset (pumpjack on production).
 */
export const DevelopmentTimeline: React.FC<{
  width?: number;
  delay?: number;
  sweepDuration?: number;
}> = ({width = 1560, delay = 0, sweepDuration = 100}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const height = 300;
  const pad = 100;
  const lineW = width - pad * 2;
  const y = 200;

  const baseIn = interpolate(frame, [delay, delay + 18], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const progress = interpolate(
    frame,
    [delay + 12, delay + 12 + sweepDuration],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.inOut(Easing.cubic),
    },
  );
  const sweepX = pad + lineW * progress;

  // Milestone icons at years 0, 3, 6, 10 — construction fades into a
  // finished building as the sweep passes each milestone.
  const MILESTONES = [0, 3, 6, 10];

  return (
    <svg width={width} height={height}>
      {/* Base line + year ticks */}
      <line
        x1={pad}
        y1={y}
        x2={pad + lineW * baseIn}
        y2={y}
        stroke={COLORS.white30}
        strokeWidth={2}
      />
      {Array.from({length: 11}, (_, yr) => {
        const x = pad + (lineW * yr) / 10;
        const reached = progress >= yr / 10;
        const tickIn = interpolate(
          frame,
          [delay + 4 + yr * 2, delay + 14 + yr * 2],
          [0, 1],
          {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
        );
        return (
          <g key={yr} opacity={tickIn}>
            <line
              x1={x}
              y1={y - (yr % 5 === 0 ? 14 : 8)}
              x2={x}
              y2={y + (yr % 5 === 0 ? 14 : 8)}
              stroke={reached ? COLORS.redBright : COLORS.white30}
              strokeWidth={yr % 5 === 0 ? 3 : 2}
            />
            {yr % 5 === 0 || yr === 10 ? (
              <text
                x={x}
                y={y + 46}
                textAnchor="middle"
                fontFamily={FONT_FAMILY}
                fontSize={21}
                letterSpacing={2}
                fill={COLORS.white50}
              >
                {`YEAR ${yr}`}
              </text>
            ) : null}
          </g>
        );
      })}
      {/* Red sweep */}
      <line
        x1={pad}
        y1={y}
        x2={sweepX}
        y2={y}
        stroke={COLORS.redBright}
        strokeWidth={4}
      />
      <circle cx={sweepX} cy={y} r={9} fill={COLORS.redBright} />
      <circle cx={sweepX} cy={y} r={3.5} fill={COLORS.white} />

      {/* Milestone icons above the line */}
      {MILESTONES.map((yr) => {
        const x = pad + (lineW * yr) / 10;
        const passed = progress >= yr / 10;
        const iconIn = spring({
          frame: frame - (delay + 8 + (yr / 10) * 40),
          fps,
          config: {damping: 200, stiffness: 100},
        });
        // Cross-fade construction → completed as the sweep passes.
        const doneOpacity = interpolate(
          frame,
          [
            delay + 12 + (yr / 10) * sweepDuration,
            delay + 26 + (yr / 10) * sweepDuration,
          ],
          [0, 1],
          {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
        );
        return (
          <g key={yr} opacity={iconIn} transform={`translate(${x - 30}, ${y - 118})`}>
            {/* Drilling derrick (fades out) */}
            <g
              opacity={1 - doneOpacity}
              stroke={COLORS.white50}
              strokeWidth={3}
              fill="none"
              strokeLinecap="round"
            >
              <path d="M 16 88 L 30 24 L 44 88" />
              <line x1={21} y1={66} x2={39} y2={66} />
              <line x1={24} y1={48} x2={36} y2={48} />
              <rect x={25} y={14} width={10} height={10} />
              <path d="M 6 88 L 54 88" />
            </g>
            {/* Producing pumpjack (fades in) */}
            <g
              opacity={doneOpacity}
              stroke={passed ? COLORS.white : COLORS.white50}
              strokeWidth={3}
              fill="none"
              strokeLinecap="round"
            >
              <path d="M 18 88 L 32 56 L 46 88" />
              <line x1={8} y1={50} x2={52} y2={55} />
              <circle cx={58} cy={56} r={7} />
              <line x1={8} y1={50} x2={8} y2={62} />
              <path d="M 6 88 L 58 88" />
            </g>
          </g>
        );
      })}
    </svg>
  );
};
