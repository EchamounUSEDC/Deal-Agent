import React from 'react';
import {
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY} from '../../config/theme';
import {
  US_OUTLINE,
  US_OUTLINE_LENGTH,
} from '../../components/usMapGeometry';

type AssetType = 'producing' | 'development' | 'infrastructure';

interface AssetMarker {
  x: number;
  y: number;
  type: AssetType;
}

// Regional spread across producing basins, development areas, and
// infrastructure corridors (same projection as the outline).
const MARKERS: AssetMarker[] = [
  {x: 395, y: 413, type: 'producing'}, //     Permian
  {x: 452, y: 489, type: 'development'}, //   Eagle Ford
  {x: 526, y: 406, type: 'infrastructure'}, //Haynesville / Gulf corridor
  {x: 452, y: 332, type: 'development'}, //   Anadarko
  {x: 357, y: 220, type: 'producing'}, //     DJ Basin
  {x: 269, y: 227, type: 'infrastructure'}, //Uinta / Rockies
  {x: 381, y: 52, type: 'producing'}, //      Bakken
  {x: 739, y: 220, type: 'development'}, //   Appalachian
  {x: 585, y: 300, type: 'infrastructure'}, //Mid-continent corridor
];

const TYPE_STYLE: Record<AssetType, {label: string}> = {
  producing: {label: 'Producing'},
  development: {label: 'Development'},
  infrastructure: {label: 'Infrastructure & Minerals'},
};

/**
 * Minimalist U.S. map demonstrating investment flexibility: the outline
 * traces in, then markers of three asset types drop across regions, with
 * a small legend distinguishing the types.
 */
export const USAssetMap: React.FC<{
  width?: number;
  delay?: number;
  traceDuration?: number;
  markerStagger?: number;
}> = ({width = 900, delay = 0, traceDuration = 40, markerStagger = 8}) => {
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
    [0, 0.35],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  const markersStart = delay + traceDuration - 6;
  const legendOpacity = interpolate(
    frame,
    [markersStart + MARKERS.length * markerStagger, markersStart + MARKERS.length * markerStagger + 18],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  const renderMarkerShape = (
    m: AssetMarker,
    pop: number,
    key: React.Key,
  ): React.ReactNode => {
    if (m.type === 'producing') {
      return (
        <circle key={key} cx={m.x} cy={m.y} r={8 * pop} fill={COLORS.redBright} />
      );
    }
    if (m.type === 'development') {
      return (
        <circle
          key={key}
          cx={m.x}
          cy={m.y}
          r={8 * pop}
          fill="none"
          stroke={COLORS.white}
          strokeWidth={2.5}
        />
      );
    }
    // infrastructure — diamond
    const s = 9 * pop;
    return (
      <path
        key={key}
        d={`M ${m.x} ${m.y - s} L ${m.x + s} ${m.y} L ${m.x} ${m.y + s} L ${m.x - s} ${m.y} Z`}
        fill={COLORS.navySoft}
        stroke={COLORS.redBright}
        strokeWidth={2.5}
      />
    );
  };

  return (
    <svg
      width={width}
      height={(width * 680) / 1000}
      viewBox="0 0 1000 680"
      style={{display: 'block'}}
    >
      <path
        d={US_OUTLINE}
        fill={COLORS.navySoft}
        fillOpacity={fillOpacity}
        stroke={COLORS.white50}
        strokeWidth={2.5}
        strokeLinejoin="round"
        strokeDasharray={US_OUTLINE_LENGTH}
        strokeDashoffset={trace}
      />
      {MARKERS.map((m, i) => {
        const markerDelay = markersStart + i * markerStagger;
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
              cx={m.x}
              cy={m.y}
              r={8 + ring * 20}
              fill="none"
              stroke={COLORS.redBright}
              strokeWidth={1.5}
              opacity={(1 - ring) * 0.7}
            />
            {renderMarkerShape(m, pop, `m${i}`)}
          </g>
        );
      })}

      {/* Legend */}
      <g opacity={legendOpacity}>
        {(Object.keys(TYPE_STYLE) as AssetType[]).map((t, i) => {
          const lx = 100 + i * 300;
          const ly = 645;
          return (
            <g key={t}>
              {renderMarkerShape({x: lx, y: ly, type: t}, 1, `l${t}`)}
              <text
                x={lx + 20}
                y={ly + 6}
                fontFamily={FONT_FAMILY}
                fontSize={17}
                letterSpacing={1.5}
                fill={COLORS.white70}
              >
                {TYPE_STYLE[t].label.toUpperCase()}
              </text>
            </g>
          );
        })}
      </g>
    </svg>
  );
};
