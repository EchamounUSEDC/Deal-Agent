import React from 'react';
import {
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS} from '../../config/theme';
import {US_OUTLINE, US_OUTLINE_LENGTH} from '../../components/usMapGeometry';

// Opportunity Zone communities across regions (stylized, same projection
// as the shared outline).
const COMMUNITIES = [
  {x: 250, y: 300}, // Mountain West
  {x: 360, y: 390}, // Southwest
  {x: 470, y: 250}, // Plains
  {x: 520, y: 430}, // Texas
  {x: 600, y: 330}, // Mid-South
  {x: 660, y: 240}, // Midwest
  {x: 700, y: 420}, // Southeast
  {x: 780, y: 300}, // Mid-Atlantic
  {x: 850, y: 190}, // Northeast
  {x: 120, y: 220}, // West Coast
];

/**
 * Minimal U.S. map with Opportunity Zone community markers pulsing in —
 * used as a quiet institutional backdrop element.
 */
export const OpportunityZoneMap: React.FC<{
  width?: number;
  delay?: number;
  traceDuration?: number;
  markerStagger?: number;
  opacity?: number;
}> = ({width = 760, delay = 0, traceDuration = 36, markerStagger = 7, opacity = 1}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const trace = interpolate(
    frame,
    [delay, delay + traceDuration],
    [US_OUTLINE_LENGTH, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.inOut(Easing.cubic),
    },
  );
  const fillOpacity = interpolate(
    frame,
    [delay + traceDuration - 10, delay + traceDuration + 15],
    [0, 0.3],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return (
    <svg
      width={width}
      height={(width * 620) / 1000}
      viewBox="0 0 1000 620"
      style={{display: 'block', opacity}}
    >
      <path
        d={US_OUTLINE}
        fill={COLORS.navySoft}
        fillOpacity={fillOpacity}
        stroke={COLORS.white30}
        strokeWidth={2.5}
        strokeLinejoin="round"
        strokeDasharray={US_OUTLINE_LENGTH}
        strokeDashoffset={trace}
      />
      {COMMUNITIES.map((c, i) => {
        const markerDelay = delay + traceDuration - 8 + i * markerStagger;
        const pop = spring({
          frame: frame - markerDelay,
          fps,
          config: {damping: 14, stiffness: 160, mass: 0.6},
        });
        const ring = interpolate(
          frame,
          [markerDelay, markerDelay + 30],
          [0, 1],
          {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
        );
        return (
          <g key={i}>
            <circle
              cx={c.x}
              cy={c.y}
              r={6 + ring * 16}
              fill="none"
              stroke={COLORS.redBright}
              strokeWidth={1.5}
              opacity={(1 - ring) * 0.7}
            />
            <circle cx={c.x} cy={c.y} r={5.5 * pop} fill={COLORS.redBright} />
          </g>
        );
      })}
    </svg>
  );
};
