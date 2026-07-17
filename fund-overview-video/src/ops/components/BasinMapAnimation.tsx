import React from 'react';
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY} from '../../config/theme';
import {useAssetExists} from '../../hooks/useAssetExists';
import {US_OUTLINE, US_OUTLINE_LENGTH} from '../../components/usMapGeometry';

export const BASIN_MAP_PATH = 'assets/usedc-basin-map.png';

// Focus basins in the shared projection (viewBox 0 0 1000 620).
const FOCUS_BASINS = [
  {name: 'PERMIAN BASIN', x: 400, y: 405, primary: true, labelDx: 0, labelDy: -52},
  {name: 'DELAWARE BASIN', x: 366, y: 425, primary: false, labelDx: -152, labelDy: 8},
  {name: 'EAGLE FORD SHALE', x: 452, y: 489, primary: false, labelDx: 118, labelDy: 42},
];

/**
 * Basin coverage graphic. Uses the supplied U.S. Energy basin map image
 * (public/assets/usedc-basin-map.png) with a slow zoom when present;
 * otherwise falls back to the branded SVG map. In both modes the three
 * focus basins are called out in brand red.
 */
export const BasinMapAnimation: React.FC<{
  width?: number;
  delay?: number;
}> = ({width = 940, delay = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const mapExists = useAssetExists(BASIN_MAP_PATH);

  const trace = interpolate(
    frame,
    [delay, delay + 40],
    [US_OUTLINE_LENGTH, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.inOut(Easing.cubic),
    },
  );
  const fillOpacity = interpolate(frame, [delay + 30, delay + 55], [0, 0.35], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const imgIn = interpolate(frame, [delay, delay + 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const imgZoom = interpolate(frame, [delay, delay + 320], [1.0, 1.06], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const height = (width * 620) / 1000;

  const markers = (
    <svg
      width={width}
      height={height}
      viewBox="0 0 1000 620"
      style={{position: 'absolute', inset: 0}}
    >
      {mapExists === false ? (
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
      ) : null}
      {FOCUS_BASINS.map((b, i) => {
        const markerDelay = delay + 40 + i * 22;
        const pop = spring({
          frame: frame - markerDelay,
          fps,
          config: {damping: 14, stiffness: 150, mass: 0.7},
        });
        const glow = interpolate(
          frame,
          [markerDelay, markerDelay + 40],
          [0, 1],
          {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
        );
        const r = b.primary ? 34 : 20;
        return (
          <g key={b.name}>
            {/* Illumination */}
            <circle
              cx={b.x}
              cy={b.y}
              r={r + 18 * glow}
              fill="rgba(163, 34, 38, 0.18)"
              opacity={pop}
            />
            <circle
              cx={b.x}
              cy={b.y}
              r={r * pop}
              fill="none"
              stroke={COLORS.redBright}
              strokeWidth={b.primary ? 3.5 : 2.5}
            />
            <circle cx={b.x} cy={b.y} r={5 * pop} fill={COLORS.redBright} />
            <text
              x={b.x + b.labelDx}
              y={b.y + b.labelDy}
              textAnchor="middle"
              fontFamily={FONT_FAMILY}
              fontWeight={700}
              fontSize={b.primary ? 24 : 19}
              letterSpacing={2.5}
              fill={b.primary ? COLORS.redBright : COLORS.white}
              opacity={pop}
            >
              {b.name}
            </text>
          </g>
        );
      })}
    </svg>
  );

  return (
    <div style={{position: 'relative', width, height}}>
      {mapExists ? (
        <AbsoluteFill style={{overflow: 'hidden'}}>
          <Img
            src={staticFile(BASIN_MAP_PATH)}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain',
              opacity: imgIn,
              transform: `scale(${imgZoom})`,
            }}
          />
          {/* Navy wash to keep the supplied map on-brand */}
          <AbsoluteFill style={{backgroundColor: 'rgba(0, 2, 63, 0.35)'}} />
        </AbsoluteFill>
      ) : null}
      {markers}
    </div>
  );
};
