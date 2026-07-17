import React from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY} from '../../config/theme';

/**
 * Capital gains flowing into oil & gas development: a "REALIZED CAPITAL
 * GAINS" node on the left streams along a red path into a drilling derrick
 * that assembles section by section, joined by a producing pumpjack.
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

  // Derrick sections assemble bottom-to-top as capital "arrives".
  const LEVELS = 5;
  const derrickX = bldgX + 170; // derrick center
  const baseHalfW = 92;
  const topHalfW = 20;
  const derrickH = 275;
  const pumpX = bldgX - 10; // pumpjack center
  const pumpIn = interpolate(frame, [delay + 92, delay + 114], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

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
          d={`M ${gainX + 76} ${gainY} C ${gainX + 320} ${gainY}, ${bldgX - 360} ${bldgBaseY - 46}, ${bldgX - 140} ${bldgBaseY - 46}`}
          fill="none"
          stroke={COLORS.white30}
          strokeWidth={2}
        />
        <path
          d={`M ${gainX + 76} ${gainY} C ${gainX + 320} ${gainY}, ${bldgX - 360} ${bldgBaseY - 46}, ${bldgX - 140} ${bldgBaseY - 46}`}
          fill="none"
          stroke={COLORS.redBright}
          strokeWidth={3}
          strokeDasharray="12 20"
          strokeDashoffset={dashOffset}
        />
        <path
          d={`M ${bldgX - 128} ${bldgBaseY - 46} l -16 -9 l 0 18 Z`}
          fill={COLORS.redBright}
        />
      </g>

      {/* Derrick assembling section by section */}
      {Array.from({length: LEVELS}, (_, i) => {
        const levelDelay = delay + 26 + i * 13;
        const rise = spring({
          frame: frame - levelDelay,
          fps,
          config: {damping: 200, stiffness: 130},
        });
        const t0 = i / LEVELS;
        const t1 = (i + 1) / LEVELS;
        const y0 = bldgBaseY - t0 * derrickH;
        const y1 = bldgBaseY - t1 * derrickH;
        const w0 = baseHalfW - t0 * (baseHalfW - topHalfW);
        const w1 = baseHalfW - t1 * (baseHalfW - topHalfW);
        const isTop = i === LEVELS - 1;
        const shift = (1 - rise) * 14;
        return (
          <g
            key={i}
            opacity={rise}
            stroke={isTop ? COLORS.redBright : COLORS.white70}
            strokeWidth={isTop ? 3.5 : 3}
            fill="none"
            strokeLinecap="round"
            transform={`translate(0, ${shift})`}
          >
            <line x1={derrickX - w0} y1={y0} x2={derrickX - w1} y2={y1} />
            <line x1={derrickX + w0} y1={y0} x2={derrickX + w1} y2={y1} />
            <line x1={derrickX - w1} y1={y1} x2={derrickX + w1} y2={y1} />
            <line x1={derrickX - w0} y1={y0} x2={derrickX + w1} y2={y1} />
          </g>
        );
      })}
      {/* Crown block */}
      <rect
        x={derrickX - 14}
        y={bldgBaseY - derrickH - 28}
        width={28}
        height={26}
        fill="none"
        stroke={COLORS.redBright}
        strokeWidth={3}
        opacity={interpolate(frame, [delay + 88, delay + 106], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        })}
      />
      {/* Producing pumpjack beside the derrick */}
      <g
        opacity={pumpIn}
        stroke={COLORS.white70}
        strokeWidth={3.5}
        fill="none"
        strokeLinecap="round"
      >
        <path
          d={`M ${pumpX - 34} ${bldgBaseY} L ${pumpX} ${bldgBaseY - 74} L ${pumpX + 34} ${bldgBaseY}`}
        />
        <line
          x1={pumpX - 58}
          y1={bldgBaseY - 88}
          x2={pumpX + 52}
          y2={bldgBaseY - 76}
        />
        <circle cx={pumpX + 62} cy={bldgBaseY - 74} r={13} />
      </g>
      {/* Ground line under the site */}
      <line
        x1={pumpX - 110}
        y1={bldgBaseY}
        x2={derrickX + baseHalfW + 60}
        y2={bldgBaseY}
        stroke={COLORS.white30}
        strokeWidth={2}
        opacity={nodeIn}
      />
      <text
        x={(pumpX + derrickX) / 2}
        y={bldgBaseY + 40}
        textAnchor="middle"
        fontFamily={FONT_FAMILY}
        fontWeight={600}
        fontSize={21}
        letterSpacing={3}
        fill={COLORS.white70}
        opacity={flowOpacity}
      >
        OIL AND GAS DEVELOPMENT
      </text>
    </svg>
  );
};

