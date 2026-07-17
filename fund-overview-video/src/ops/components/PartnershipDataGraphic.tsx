import React from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY} from '../../config/theme';

/**
 * U.S. Energy's operated platform at the center, connected by thin animated
 * lines to strategic operator partners; data-flow dashes stream back into
 * the platform once the links are drawn.
 */
export const PartnershipDataGraphic: React.FC<{
  width?: number;
  delay?: number;
}> = ({width = 1500, delay = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const height = 540;
  const cx = width / 2;
  const cy = 235;

  const PARTNERS = [
    {x: cx - 520, y: 90, label: 'OPERATOR PARTNER'},
    {x: cx - 520, y: 360, label: 'OPERATOR PARTNER'},
    {x: cx + 520, y: 90, label: 'OPERATOR PARTNER'},
    {x: cx + 520, y: 360, label: 'OPERATOR PARTNER'},
  ];

  const centerIn = spring({
    frame: frame - delay,
    fps,
    config: {damping: 200, stiffness: 90},
  });

  // Data flows back toward the platform (dashes move inward).
  const dashOffset = (frame - delay) * 1.7;

  return (
    <svg width={width} height={height}>
      {/* Connections */}
      {PARTNERS.map((p, i) => {
        const linkDelay = delay + 18 + i * 10;
        const draw = interpolate(frame, [linkDelay, linkDelay + 24], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        const flowOpacity = interpolate(
          frame,
          [linkDelay + 26, linkDelay + 44],
          [0, 1],
          {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
        );
        // Line from partner toward center
        const dx = cx - p.x;
        const dy = cy - p.y;
        const len = Math.hypot(dx, dy);
        const trimStart = 96 / len; // outside partner node
        const trimEnd = 1 - 128 / len; // outside platform node
        const x1 = p.x + dx * trimStart;
        const y1 = p.y + dy * trimStart;
        const x2 = p.x + dx * (trimStart + (trimEnd - trimStart) * draw);
        const y2 = p.y + dy * (trimStart + (trimEnd - trimStart) * draw);
        return (
          <g key={i}>
            <line
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke={COLORS.white30}
              strokeWidth={2}
            />
            <line
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke={COLORS.redBright}
              strokeWidth={2.5}
              strokeDasharray="10 18"
              strokeDashoffset={dashOffset}
              opacity={flowOpacity}
            />
          </g>
        );
      })}

      {/* Partner nodes */}
      {PARTNERS.map((p, i) => {
        const nodeIn = spring({
          frame: frame - (delay + 12 + i * 10),
          fps,
          config: {damping: 200, stiffness: 100},
        });
        return (
          <g key={i} opacity={nodeIn}>
            <circle
              cx={p.x}
              cy={p.y}
              r={52}
              fill={COLORS.navyDeep}
              stroke={COLORS.white30}
              strokeWidth={2}
            />
            {/* Derrick glyph */}
            <g
              stroke={COLORS.white70}
              strokeWidth={2.5}
              fill="none"
              strokeLinecap="round"
            >
              <path d={`M ${p.x - 13} ${p.y + 18} L ${p.x} ${p.y - 18} L ${p.x + 13} ${p.y + 18}`} />
              <line x1={p.x - 9} y1={p.y + 5} x2={p.x + 9} y2={p.y + 5} />
              <line x1={p.x - 6} y1={p.y - 6} x2={p.x + 6} y2={p.y - 6} />
            </g>
            <text
              x={p.x}
              y={p.y + 84}
              textAnchor="middle"
              fontFamily={FONT_FAMILY}
              fontWeight={600}
              fontSize={17}
              letterSpacing={2.5}
              fill={COLORS.white50}
            >
              {p.label}
            </text>
          </g>
        );
      })}

      {/* Central platform */}
      <g opacity={centerIn}>
        <circle
          cx={cx}
          cy={cy}
          r={110}
          fill={COLORS.navySoft}
          stroke={COLORS.redBright}
          strokeWidth={3}
        />
        <circle
          cx={cx}
          cy={cy}
          r={122}
          fill="none"
          stroke={COLORS.white15}
          strokeWidth={1.5}
        />
        {/* Platform glyph */}
        <g
          stroke={COLORS.white}
          strokeWidth={3}
          fill="none"
          strokeLinecap="round"
        >
          <path d={`M ${cx - 20} ${cy - 8} L ${cx} ${cy - 52} L ${cx + 20} ${cy - 8}`} />
          <line x1={cx - 13} y1={cy - 24} x2={cx + 13} y2={cy - 24} />
        </g>
        <text
          x={cx}
          y={cy + 26}
          textAnchor="middle"
          fontFamily={FONT_FAMILY}
          fontWeight={700}
          fontSize={25}
          letterSpacing={3}
          fill={COLORS.white}
        >
          U.S. ENERGY
        </text>
        <text
          x={cx}
          y={cy + 56}
          textAnchor="middle"
          fontFamily={FONT_FAMILY}
          fontWeight={500}
          fontSize={18}
          letterSpacing={3.5}
          fill={COLORS.white70}
        >
          OPERATED PLATFORM
        </text>
      </g>

      {/* Data annotation */}
      <text
        x={cx}
        y={height - 22}
        textAnchor="middle"
        fontFamily={FONT_FAMILY}
        fontWeight={500}
        fontSize={22}
        letterSpacing={4}
        fill={COLORS.white70}
        opacity={interpolate(frame, [delay + 60, delay + 80], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        })}
      >
        SUBSURFACE AND OPERATIONAL DATA FLOWS BACK TO THE PLATFORM
      </text>
    </svg>
  );
};
