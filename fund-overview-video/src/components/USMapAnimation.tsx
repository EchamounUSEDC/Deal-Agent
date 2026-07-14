import React from 'react';
import {
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY} from '../config/theme';

/**
 * Minimalist stylized outline of the continental U.S. (hand-drawn SVG path,
 * not a geographic dataset) that traces itself in, then drops markers on
 * established oil & natural gas basins with a soft expanding ring.
 */

interface Basin {
  name: string;
  x: number;
  y: number;
  labelDx?: number;
  labelDy?: number;
}

// Marker positions use the same equirectangular projection as the outline:
// x = (lon + 125) * 940 / 59 + 30, y = (49 - lat) * 560 / 25 + 30.
const BASINS: Basin[] = [
  {name: 'Permian', x: 395, y: 413, labelDy: 36},
  {name: 'Eagle Ford', x: 452, y: 489, labelDy: 36},
  {name: 'Haynesville', x: 526, y: 406, labelDy: 36},
  {name: 'Anadarko', x: 452, y: 332, labelDy: -24},
  {name: 'DJ Basin', x: 357, y: 220, labelDy: -24},
  {name: 'Uinta', x: 269, y: 227, labelDy: -24, labelDx: -14},
  {name: 'Bakken', x: 381, y: 52, labelDy: 38},
  {name: 'Appalachian', x: 739, y: 220, labelDy: -24},
];

// Simplified lower-48 outline traced from projected boundary landmarks
// (49th parallel, Great Lakes, Atlantic seaboard, Florida, Gulf coast,
// Mexican border, Pacific coast) in viewBox 0 0 1000 620.
const US_OUTLINE = [
  'M 62 30',
  'L 506 30 L 604 48 L 678 86 L 672 102 L 706 131 L 698 180 L 691 194',
  'L 763 164 L 798 151 L 827 120 L 882 120 L 919 66 L 956 124 L 903 151',
  'L 892 180 L 843 218 L 827 270 L 811 303 L 819 339 L 733 411 L 725 447',
  'L 739 491 L 741 563 L 718 543 L 706 503 L 667 462 L 620 447 L 600 478',
  'L 511 471 L 474 547 L 436 512 L 377 478 L 325 415 L 253 427 L 194 395',
  'L 156 400 L 138 373 L 102 357 L 70 281 L 40 223 L 40 158 L 46 90',
  'L 35 43 Z',
].join(' ');

const OUTLINE_LENGTH = 3400; // generous over-estimate for dash animation

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
