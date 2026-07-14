import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONT_FAMILY} from '../config/theme';

/**
 * Clean animated revenue-flow diagram: producing wells → fund → investor
 * distributions, with dashes flowing along the connectors.
 */
export const RevenueFlow: React.FC<{
  width?: number;
  delay?: number;
}> = ({width = 1500, delay = 0}) => {
  const frame = useCurrentFrame();
  const height = 260;
  const y = 130;

  const nodes = [
    {x: 190, label: 'PRODUCING WELLS'},
    {x: width / 2, label: 'FUND REVENUE'},
    {x: width - 190, label: 'INVESTOR DISTRIBUTIONS'},
  ];

  const nodeIn = (i: number) =>
    interpolate(frame, [delay + i * 12, delay + i * 12 + 16], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });

  // Flowing dashes: animate dashoffset continuously
  const dashOffset = -((frame - delay) * 1.6);
  const connectorIn = (i: number) =>
    interpolate(frame, [delay + 10 + i * 14, delay + 34 + i * 14], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {/* Connectors with flowing dashes */}
      {[0, 1].map((i) => {
        const x1 = nodes[i].x + 66;
        const x2 = nodes[i + 1].x - 66;
        const grow = connectorIn(i);
        return (
          <g key={i} opacity={grow}>
            <line
              x1={x1}
              y1={y}
              x2={x1 + (x2 - x1) * grow}
              y2={y}
              stroke={COLORS.white30}
              strokeWidth={2}
            />
            <line
              x1={x1}
              y1={y}
              x2={x1 + (x2 - x1) * grow}
              y2={y}
              stroke={COLORS.redBright}
              strokeWidth={3}
              strokeDasharray="14 22"
              strokeDashoffset={dashOffset}
            />
            {/* Arrowhead */}
            <path
              d={`M ${x2} ${y} l -16 -9 l 0 18 Z`}
              fill={COLORS.redBright}
              opacity={grow >= 1 ? 1 : 0}
            />
          </g>
        );
      })}

      {/* Nodes */}
      {nodes.map((node, i) => {
        const o = nodeIn(i);
        return (
          <g key={node.label} opacity={o}>
            <circle
              cx={node.x}
              cy={y}
              r={52}
              fill={COLORS.navySoft}
              stroke={i === 2 ? COLORS.redBright : COLORS.white30}
              strokeWidth={2.5}
            />
            {i === 0 ? (
              // Derrick icon
              <g
                stroke={COLORS.white}
                strokeWidth={3}
                fill="none"
                strokeLinecap="round"
              >
                <path
                  d={`M ${node.x - 16} ${y + 22} L ${node.x} ${y - 24} L ${node.x + 16} ${y + 22}`}
                />
                <line
                  x1={node.x - 11}
                  y1={y + 6}
                  x2={node.x + 11}
                  y2={y + 6}
                />
                <line
                  x1={node.x - 7}
                  y1={y - 8}
                  x2={node.x + 7}
                  y2={y - 8}
                />
              </g>
            ) : i === 1 ? (
              // Barrel/production icon
              <g stroke={COLORS.white} strokeWidth={3} fill="none">
                <rect
                  x={node.x - 15}
                  y={y - 20}
                  width={30}
                  height={40}
                  rx={5}
                />
                <line
                  x1={node.x - 15}
                  y1={y - 6}
                  x2={node.x + 15}
                  y2={y - 6}
                />
                <line
                  x1={node.x - 15}
                  y1={y + 6}
                  x2={node.x + 15}
                  y2={y + 6}
                />
              </g>
            ) : (
              // Distribution icon (outward arrows)
              <g
                stroke={COLORS.white}
                strokeWidth={3}
                fill="none"
                strokeLinecap="round"
              >
                <circle cx={node.x} cy={y} r={9} />
                {[45, 135, 225, 315].map((deg) => {
                  const rad = (deg * Math.PI) / 180;
                  const sx = node.x + Math.cos(rad) * 15;
                  const sy = y + Math.sin(rad) * 15;
                  const ex = node.x + Math.cos(rad) * 27;
                  const ey = y + Math.sin(rad) * 27;
                  return (
                    <line key={deg} x1={sx} y1={sy} x2={ex} y2={ey} />
                  );
                })}
              </g>
            )}
            <text
              x={node.x}
              y={y + 96}
              textAnchor="middle"
              fontFamily={FONT_FAMILY}
              fontWeight={600}
              fontSize={22}
              letterSpacing={3.5}
              fill={COLORS.white70}
            >
              {node.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};
