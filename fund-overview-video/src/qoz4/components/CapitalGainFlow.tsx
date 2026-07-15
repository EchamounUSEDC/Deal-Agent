import React from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY} from '../../config/theme';

/**
 * Capital gains flowing into real estate: a "REALIZED CAPITAL GAINS" node
 * on the left streams along a red path into a development that constructs
 * itself floor by floor on the right.
 */
export const CapitalGainFlow: React.FC<{
  width?: number;
  delay?: number;
}> = ({width = 1460, delay = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const height = 430;
  const gainX = 220;
  const gainY = 215;
  const bldgX = width - 420;
  const bldgBaseY = 380;

  const nodeIn = spring({
    frame: frame - delay,
    fps,
    config: {damping: 200, stiffness: 90},
  });
  const flowOpacity = interpolate(frame, [delay + 16, delay + 34], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const dashOffset = -((frame - delay) * 1.8);

  // Building floors rise sequentially as capital "arrives".
  const FLOORS = 6;
  const floorW = 240;
  const floorH = 44;

  return (
    <svg width={width} height={height}>
      {/* Gains node */}
      <g opacity={nodeIn}>
        <circle
          cx={gainX}
          cy={gainY}
          r={64}
          fill={COLORS.navySoft}
          stroke={COLORS.white30}
          strokeWidth={2.5}
        />
        {/* Dollar/gain icon */}
        <g stroke={COLORS.white} strokeWidth={3.5} fill="none" strokeLinecap="round">
          <path d={`M ${gainX} ${gainY - 22} L ${gainX} ${gainY + 22}`} />
          <path
            d={`M ${gainX + 13} ${gainY - 12} Q ${gainX} ${gainY - 24} ${gainX - 11} ${gainY - 12} Q ${gainX - 20} ${gainY - 2} ${gainX} ${gainY} Q ${gainX + 20} ${gainY + 2} ${gainX + 11} ${gainY + 12} Q ${gainX} ${gainY + 24} ${gainX - 13} ${gainY + 12}`}
          />
        </g>
        <text
          x={gainX}
          y={gainY + 106}
          textAnchor="middle"
          fontFamily={FONT_FAMILY}
          fontWeight={600}
          fontSize={21}
          letterSpacing={3}
          fill={COLORS.white70}
        >
          REALIZED CAPITAL GAINS
        </text>
      </g>

      {/* Flow path */}
      <g opacity={flowOpacity}>
        <path
          d={`M ${gainX + 76} ${gainY} C ${gainX + 320} ${gainY}, ${bldgX - 300} ${bldgBaseY - 90}, ${bldgX - 46} ${bldgBaseY - 90}`}
          fill="none"
          stroke={COLORS.white30}
          strokeWidth={2}
        />
        <path
          d={`M ${gainX + 76} ${gainY} C ${gainX + 320} ${gainY}, ${bldgX - 300} ${bldgBaseY - 90}, ${bldgX - 46} ${bldgBaseY - 90}`}
          fill="none"
          stroke={COLORS.redBright}
          strokeWidth={3}
          strokeDasharray="12 20"
          strokeDashoffset={dashOffset}
        />
        <path
          d={`M ${bldgX - 34} ${bldgBaseY - 90} l -16 -9 l 0 18 Z`}
          fill={COLORS.redBright}
        />
      </g>

      {/* Development rising floor by floor */}
      {Array.from({length: FLOORS}, (_, i) => {
        const floorDelay = delay + 26 + i * 12;
        const rise = spring({
          frame: frame - floorDelay,
          fps,
          config: {damping: 200, stiffness: 130},
        });
        const y = bldgBaseY - (i + 1) * floorH;
        const isTop = i === FLOORS - 1;
        return (
          <g key={i} opacity={rise}>
            <rect
              x={bldgX}
              y={y + (1 - rise) * 16}
              width={floorW}
              height={floorH - 6}
              fill={i % 2 === 0 ? COLORS.navySoft : 'rgba(10, 13, 82, 0.35)'}
              stroke={isTop ? COLORS.redBright : COLORS.white30}
              strokeWidth={isTop ? 2.5 : 2}
            />
            {/* Windows */}
            {Array.from({length: 4}, (_, w) => (
              <rect
                key={w}
                x={bldgX + 26 + w * 52}
                y={y + 12 + (1 - rise) * 16}
                width={26}
                height={16}
                fill="rgba(255,255,255,0.16)"
              />
            ))}
          </g>
        );
      })}
      {/* Ground line under the building */}
      <line
        x1={bldgX - 60}
        y1={bldgBaseY}
        x2={bldgX + floorW + 60}
        y2={bldgBaseY}
        stroke={COLORS.white30}
        strokeWidth={2}
        opacity={nodeIn}
      />
      <text
        x={bldgX + floorW / 2}
        y={bldgBaseY + 40}
        textAnchor="middle"
        fontFamily={FONT_FAMILY}
        fontWeight={600}
        fontSize={21}
        letterSpacing={3}
        fill={COLORS.white70}
        opacity={flowOpacity}
      >
        REAL ESTATE DEVELOPMENTS
      </text>
    </svg>
  );
};

