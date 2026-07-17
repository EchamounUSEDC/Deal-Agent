import React from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY, TYPE} from '../../config/theme';

const PROJECTS = [
  {label: '$5M', r: 34},
  {label: '$50M', r: 48},
  {label: '$250M', r: 64},
  {label: '$500M+', r: 82},
];

/**
 * Capital deployment: project markers of increasing size ($5M → $500M+),
 * then a transition to the annual deployment statistic.
 */
export const CapitalDeploymentGraphic: React.FC<{
  width?: number;
  delay?: number;
  /** Frame (relative to mount) at which the annual statistic takes over. */
  statAt?: number;
}> = ({width = 1500, delay = 0, statAt = 120}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const markersOpacity = interpolate(
    frame,
    [statAt - 12, statAt + 4],
    [1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );
  const statIn = spring({
    frame: frame - statAt,
    fps,
    config: {damping: 200, stiffness: 90},
  });
  const supportOpacity = interpolate(frame, [delay + 70, delay + 90], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const svgH = 330;
  const cy = 170;
  const totalR = PROJECTS.reduce((s, p) => s + p.r * 2 + 90, -90);
  let cursor = (width - totalR) / 2;

  return (
    <div
      style={{
        position: 'relative',
        width,
        height: svgH + 130,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      {/* Phase 1 — project markers */}
      <div style={{opacity: markersOpacity}}>
        <svg width={width} height={svgH}>
          {PROJECTS.map((p, i) => {
            const cx = cursor + p.r;
            cursor += p.r * 2 + 90;
            const pop = spring({
              frame: frame - (delay + 8 + i * 16),
              fps,
              config: {damping: 15, stiffness: 140, mass: 0.7},
            });
            return (
              <g key={p.label}>
                <circle
                  cx={cx}
                  cy={cy}
                  r={p.r * pop}
                  fill="rgba(10, 13, 82, 0.6)"
                  stroke={i === PROJECTS.length - 1 ? COLORS.redBright : COLORS.white30}
                  strokeWidth={i === PROJECTS.length - 1 ? 3 : 2}
                />
                <text
                  x={cx}
                  y={cy + 8}
                  textAnchor="middle"
                  fontFamily={FONT_FAMILY}
                  fontWeight={700}
                  fontSize={20 + p.r * 0.22}
                  letterSpacing={1}
                  fill={COLORS.white}
                  opacity={pop}
                  style={{fontVariantNumeric: 'tabular-nums'}}
                >
                  {p.label}
                </text>
                <text
                  x={cx}
                  y={cy + p.r + 34}
                  textAnchor="middle"
                  fontFamily={FONT_FAMILY}
                  fontSize={17}
                  letterSpacing={2.5}
                  fill={COLORS.white50}
                  opacity={pop}
                >
                  {`PROJECT ${i + 1}`}
                </text>
              </g>
            );
          })}
        </svg>
        <div
          style={{
            ...TYPE.body,
            fontSize: 26,
            textAlign: 'center',
            color: COLORS.white70,
            opacity: supportOpacity,
          }}
        >
          Typical Project Opportunities — $5 Million to $500 Million or Greater
        </div>
      </div>

      {/* Phase 2 — annual deployment statistic */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          opacity: statIn,
          transform: `translateY(${interpolate(statIn, [0, 1], [26, 0])}px)`,
        }}
      >
        <div style={{...TYPE.label, fontSize: 26, marginBottom: 22}}>
          Recently Deployed
        </div>
        <div
          style={{
            ...TYPE.hero,
            fontSize: 110,
            lineHeight: 1.05,
            letterSpacing: '0.04em',
          }}
        >
          MORE THAN $1 BILLION
        </div>
        <div
          style={{
            ...TYPE.label,
            fontSize: 34,
            letterSpacing: '0.32em',
            color: COLORS.white70,
            marginTop: 20,
          }}
        >
          Annually
        </div>
      </div>
    </div>
  );
};
