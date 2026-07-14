import React from 'react';
import {
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY} from '../config/theme';
import {
  BASINS,
  US_OUTLINE,
  US_OUTLINE_LENGTH as OUTLINE_LENGTH,
} from './usMapGeometry';

/**
 * Minimalist stylized outline of the continental U.S. (hand-drawn SVG path,
 * not a geographic dataset) that traces itself in, then drops markers on
 * established oil & natural gas basins with a soft expanding ring.
 */

export const USMapAnimation: React.FC<{
  width?: number;
  /** Frame at which the outline starts tracing. */
  delay?: number;
  /** Frames the outline takes to trace in. */
  traceDuration?: number;
  /** Frames between marker drops. */
  markerStagger?: number;
}> = ({width = 1000, delay = 0, traceDuration = 40, markerStagger = 10}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const trace = interpolate(
    frame,
    [delay, delay + traceDuration],
    [OUTLINE_LENGTH, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.inOut(Easing.cubic),
    },
  );
  const fillOpacity = interpolate(
    frame,
    [delay + traceDuration - 10, delay + traceDuration + 15],
    [0, 0.35],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  const markersStart = delay + traceDuration - 6;

  return (
    <svg
      width={width}
      height={(width * 620) / 1000}
      viewBox="0 0 1000 620"
      style={{display: 'block'}}
    >
      <path
        d={US_OUTLINE}
        fill={COLORS.navySoft}
        fillOpacity={fillOpacity}
        stroke={COLORS.white50}
        strokeWidth={2.5}
        strokeLinejoin="round"
        strokeDasharray={OUTLINE_LENGTH}
        strokeDashoffset={trace}
      />
      {BASINS.map((basin, i) => {
        const markerDelay = markersStart + i * markerStagger;
        const pop = spring({
          frame: frame - markerDelay,
          fps,
          config: {damping: 14, stiffness: 160, mass: 0.6},
        });
        const ring = interpolate(
          frame,
          [markerDelay, markerDelay + 34],
          [0, 1],
          {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
        );
        const labelOpacity = interpolate(
          frame,
          [markerDelay + 8, markerDelay + 22],
          [0, 0.85],
          {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
        );

        return (
          <g key={basin.name}>
            <circle
              cx={basin.x}
              cy={basin.y}
              r={8 + ring * 22}
              fill="none"
              stroke={COLORS.redBright}
              strokeWidth={2}
              opacity={(1 - ring) * 0.8}
            />
            <circle
              cx={basin.x}
              cy={basin.y}
              r={7 * pop}
              fill={COLORS.redBright}
            />
            <circle
              cx={basin.x}
              cy={basin.y}
              r={2.5 * pop}
              fill={COLORS.white}
            />
            <text
              x={basin.x + (basin.labelDx ?? 0)}
              y={basin.y + (basin.labelDy ?? 30)}
              textAnchor="middle"
              fontFamily={FONT_FAMILY}
              fontSize={17}
              letterSpacing={1.5}
              fill={COLORS.white}
              opacity={labelOpacity}
            >
              {basin.name.toUpperCase()}
            </text>
          </g>
        );
      })}
    </svg>
  );
};
