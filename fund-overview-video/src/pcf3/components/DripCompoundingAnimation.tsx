import React from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY, TYPE} from '../../config/theme';

/**
 * Distribution Reinvestment Program animation. Quarterly distributions flow
 * from a "DISTRIBUTIONS" node into a growing grid of ownership units; the
 * unit count ticks upward each period while the three sequence statements
 * (reinvest → increase ownership → potential compounding) appear.
 */
export const DripCompoundingAnimation: React.FC<{
  width?: number;
  delay?: number;
  /** Frames between reinvestment periods. */
  periodFrames?: number;
}> = ({width = 1560, delay = 0, periodFrames = 46}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const BASE_UNITS = 8;
  const PERIODS = 5;
  const UNITS_PER_PERIOD = 2;

  const periodsElapsed = Math.min(
    PERIODS,
    Math.max(0, Math.floor((frame - (delay + 26)) / periodFrames) + 1),
  );
  const unitCount = BASE_UNITS + periodsElapsed * UNITS_PER_PERIOD;

  const nodeIn = spring({
    frame: frame - delay,
    fps,
    config: {damping: 200, stiffness: 90},
  });

  // Flowing dashes along the reinvestment path.
  const dashOffset = -((frame - delay) * 1.8);
  const flowOpacity = interpolate(frame, [delay + 16, delay + 34], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const SEQUENCE = [
    'REINVEST ELIGIBLE DISTRIBUTIONS',
    'INCREASE OWNERSHIP',
    'POTENTIAL COMPOUNDING',
  ];

  const svgH = 340;
  const distX = 210;
  const distY = 200;
  const gridX = width - 690;
  const gridY = 84;
  const cell = 52;
  const gap = 12;
  const cols = 6;

  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      <div style={{position: 'relative', width, height: svgH}}>
        <svg width={width} height={svgH}>
          {/* Distributions node */}
          <g opacity={nodeIn}>
            <circle
              cx={distX}
              cy={distY}
              r={62}
              fill={COLORS.navySoft}
              stroke={COLORS.white30}
              strokeWidth={2.5}
            />
            {/* Coin icon */}
            <g stroke={COLORS.white} strokeWidth={3} fill="none">
              <circle cx={distX} cy={distY} r={24} />
              <path
                d={`M ${distX} ${distY - 13} L ${distX} ${distY + 13} M ${distX - 8} ${distY - 6} Q ${distX} ${distY - 14} ${distX + 8} ${distY - 6} M ${distX - 8} ${distY + 6} Q ${distX} ${distY + 14} ${distX + 8} ${distY + 6}`}
              />
            </g>
            <text
              x={distX}
              y={distY + 100}
              textAnchor="middle"
              fontFamily={FONT_FAMILY}
              fontWeight={600}
              fontSize={21}
              letterSpacing={3}
              fill={COLORS.white70}
            >
              QUARTERLY DISTRIBUTIONS
            </text>
          </g>

          {/* Reinvestment flow path */}
          <g opacity={flowOpacity}>
            <path
              d={`M ${distX + 72} ${distY} C ${distX + 260} ${distY}, ${gridX - 240} ${gridY + 140}, ${gridX - 40} ${gridY + 140}`}
              fill="none"
              stroke={COLORS.white30}
              strokeWidth={2}
            />
            <path
              d={`M ${distX + 72} ${distY} C ${distX + 260} ${distY}, ${gridX - 240} ${gridY + 140}, ${gridX - 40} ${gridY + 140}`}
              fill="none"
              stroke={COLORS.redBright}
              strokeWidth={3}
              strokeDasharray="12 20"
              strokeDashoffset={dashOffset}
            />
            <path
              d={`M ${gridX - 28} ${gridY + 140} l -16 -9 l 0 18 Z`}
              fill={COLORS.redBright}
            />
          </g>

          {/* Ownership unit grid */}
          {Array.from({length: BASE_UNITS + PERIODS * UNITS_PER_PERIOD}, (_, i) => {
            const isBase = i < BASE_UNITS;
            const period = isBase ? 0 : Math.floor((i - BASE_UNITS) / UNITS_PER_PERIOD) + 1;
            const unitDelay = isBase
              ? delay + 8 + i * 2
              : delay + 26 + (period - 1) * periodFrames + ((i - BASE_UNITS) % UNITS_PER_PERIOD) * 6;
            const pop = spring({
              frame: frame - unitDelay,
              fps,
              config: {damping: 15, stiffness: 180, mass: 0.6},
            });
            const col = i % cols;
            const row = Math.floor(i / cols);
            const x = gridX + col * (cell + gap);
            const y = gridY + row * (cell + gap);
            return (
              <rect
                key={i}
                x={x + (cell * (1 - pop)) / 2}
                y={y + (cell * (1 - pop)) / 2}
                width={cell * pop}
                height={cell * pop}
                fill={isBase ? COLORS.navySoft : 'rgba(163, 34, 38, 0.35)'}
                stroke={isBase ? COLORS.white30 : COLORS.redBright}
                strokeWidth={2}
              />
            );
          })}

          {/* Unit counter */}
          <text
            x={gridX + (cols * (cell + gap) - gap) / 2}
            y={gridY + 3 * (cell + gap) + 46}
            textAnchor="middle"
            fontFamily={FONT_FAMILY}
            fontWeight={700}
            fontSize={34}
            letterSpacing={2}
            fill={COLORS.white}
            opacity={nodeIn}
            style={{fontVariantNumeric: 'tabular-nums'}}
          >
            {`UNITS OWNED: ${unitCount}`}
          </text>
        </svg>
      </div>

      {/* Sequence statements below the diagram */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          gap: 64,
          marginTop: 34,
        }}
      >
        {SEQUENCE.map((s, i) => {
            const stepDelay = delay + 40 + i * periodFrames;
            const stepIn = spring({
              frame: frame - stepDelay,
              fps,
              config: {damping: 200, stiffness: 100},
            });
            return (
              <div
                key={s}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 16,
                  opacity: stepIn,
                  transform: `translateX(${interpolate(stepIn, [0, 1], [20, 0])}px)`,
                }}
              >
                <div
                  style={{
                    width: 30,
                    height: 3,
                    backgroundColor: COLORS.red,
                    flexShrink: 0,
                  }}
                />
                <div
                  style={{
                    fontFamily: FONT_FAMILY,
                    fontWeight: 600,
                    fontSize: 24,
                    letterSpacing: '0.12em',
                    color: COLORS.white,
                    whiteSpace: 'nowrap',
                  }}
                >
                  {s}
                </div>
              </div>
            );
          })}
      </div>

      <div
        style={{
          ...TYPE.label,
          fontSize: 25,
          marginTop: 40,
          opacity: interpolate(frame, [delay + 60, delay + 80], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }),
        }}
      >
        Additional Units Without Additional Fees
      </div>
    </div>
  );
};
