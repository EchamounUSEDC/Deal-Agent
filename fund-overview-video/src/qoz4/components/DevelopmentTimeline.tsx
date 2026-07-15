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
 * while milestone icons transition from construction (crane) to a
 * stabilized income-producing asset (completed building).
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
            {/* Construction crane (fades out) */}
            <g
              opacity={1 - doneOpacity}
              stroke={COLORS.white50}
              strokeWidth={3}
              fill="none"
              strokeLinecap="round"
            >
              <path d="M 14 88 L 14 22" />
              <path d="M 0 30 L 44 30" />
              <path d="M 14 22 L 24 30" />
              <path d="M 38 30 L 38 48" />
              <rect x={31} y={48} width={14} height={12} />
              <path d="M 4 88 L 24 88" />
            </g>
            {/* Completed building (fades in) */}
            <g
              opacity={doneOpacity}
              stroke={passed ? COLORS.white : COLORS.white50}
              strokeWidth={3}
              fill="none"
              strokeLinejoin="round"
            >
              <rect x={38} y={34} width={22} height={54} />
              <rect x={20} y={54} width={18} height={34} />
              <line x1={44} y1={46} x2={54} y2={46} />
              <line x1={44} y1={58} x2={54} y2={58} />
              <line x1={44} y1={70} x2={54} y2={70} />
              <line x1={26} y1={64} x2={32} y2={64} />
              <line x1={26} y1={76} x2={32} y2={76} />
              <line x1={14} y1={88} x2={66} y2={88} />
            </g>
          </g>
        );
      })}
    </svg>
  );
};
