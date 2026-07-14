import React from 'react';
import {
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY, TYPE} from '../../config/theme';

/**
 * Balanced two-panel animation: recurring cash flow on the left (quarterly
 * payment bars pulsing in), increasing asset value on the right (rising
 * step line), joined by a "+" on the brand's red rule.
 */
export const IncomeGrowthSplit: React.FC<{
  width?: number;
  delay?: number;
}> = ({width = 1560, delay = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const panelW = (width - 220) / 2;
  const chartH = 240;

  const panelIn = (i: number) =>
    spring({
      frame: frame - (delay + i * 14),
      fps,
      config: {damping: 200, stiffness: 90},
    });

  const plusIn = spring({
    frame: frame - (delay + 34),
    fps,
    config: {damping: 13, stiffness: 160, mass: 0.7},
  });

  // Left: recurring quarterly bars, equal height (income = recurring).
  const BARS = 6;
  const barW = 42;
  const barGap = (panelW - 120 - BARS * barW) / (BARS - 1);

  // Right: rising value steps.
  const STEPS = 6;
  const stepHeights = [0.3, 0.42, 0.5, 0.62, 0.76, 0.92];

  const labelOpacity = (i: number) =>
    interpolate(frame, [delay + 24 + i * 14, delay + 44 + i * 14], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });

  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 0,
          width,
        }}
      >
        {/* Income panel */}
        <div
          style={{
            width: panelW,
            opacity: panelIn(0),
            transform: `translateY(${interpolate(panelIn(0), [0, 1], [24, 0])}px)`,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 30,
          }}
        >
          <svg width={panelW - 60} height={chartH}>
            {/* Baseline */}
            <line
              x1={30}
              y1={chartH - 30}
              x2={panelW - 90}
              y2={chartH - 30}
              stroke={COLORS.white30}
              strokeWidth={2}
            />
            {Array.from({length: BARS}, (_, i) => {
              const grow = spring({
                frame: frame - (delay + 14 + i * 9),
                fps,
                config: {damping: 200, stiffness: 120},
              });
              const h = 120 * grow;
              const x = 45 + i * (barW + barGap);
              return (
                <g key={i}>
                  <rect
                    x={x}
                    y={chartH - 30 - h}
                    width={barW}
                    height={h}
                    fill={COLORS.navySoft}
                    stroke={COLORS.redBright}
                    strokeWidth={2}
                  />
                  <text
                    x={x + barW / 2}
                    y={chartH - 8}
                    textAnchor="middle"
                    fontFamily={FONT_FAMILY}
                    fontSize={15}
                    letterSpacing={1.5}
                    fill={COLORS.white50}
                    opacity={grow}
                  >
                    {`Q${(i % 4) + 1}`}
                  </text>
                </g>
              );
            })}
          </svg>
          <div style={{...TYPE.hero, fontSize: 42, letterSpacing: '0.1em'}}>
            CURRENT INCOME
          </div>
        </div>

        {/* Plus divider */}
        <div
          style={{
            width: 220,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 0,
          }}
        >
          <div
            style={{
              width: 92,
              height: 92,
              borderRadius: '50%',
              border: `2px solid ${COLORS.redBright}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transform: `scale(${plusIn})`,
              fontFamily: FONT_FAMILY,
              fontSize: 54,
              fontWeight: 300,
              color: COLORS.white,
              lineHeight: 1,
            }}
          >
            +
          </div>
        </div>

        {/* Growth panel */}
        <div
          style={{
            width: panelW,
            opacity: panelIn(1),
            transform: `translateY(${interpolate(panelIn(1), [0, 1], [24, 0])}px)`,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 30,
          }}
        >
          <svg width={panelW - 60} height={chartH}>
            <line
              x1={30}
              y1={chartH - 30}
              x2={panelW - 90}
              y2={chartH - 30}
              stroke={COLORS.white30}
              strokeWidth={2}
            />
            {(() => {
              const usable = panelW - 150;
              const stepW = usable / STEPS;
              const reveal = interpolate(
                frame,
                [delay + 18, delay + 78],
                [0, 1],
                {
                  extrapolateLeft: 'clamp',
                  extrapolateRight: 'clamp',
                  easing: Easing.inOut(Easing.cubic),
                },
              );
              const pts: string[] = [];
              stepHeights.forEach((h, i) => {
                const x1 = 45 + i * stepW;
                const y = chartH - 30 - h * 170;
                pts.push(`${x1},${y}`, `${x1 + stepW},${y}`);
              });
              const totalLen = 2400;
              return (
                <>
                  <polyline
                    points={pts.join(' ')}
                    fill="none"
                    stroke={COLORS.redBright}
                    strokeWidth={3.5}
                    strokeDasharray={totalLen}
                    strokeDashoffset={totalLen * (1 - reveal)}
                  />
                  {/* End marker + upward arrow once revealed */}
                  <g opacity={interpolate(reveal, [0.92, 1], [0, 1])}>
                    <circle
                      cx={45 + STEPS * stepW}
                      cy={chartH - 30 - 0.92 * 170}
                      r={7}
                      fill={COLORS.redBright}
                    />
                  </g>
                </>
              );
            })()}
          </svg>
          <div
            style={{
              ...TYPE.hero,
              fontSize: 42,
              letterSpacing: '0.1em',
              textAlign: 'center',
            }}
          >
            LONG-TERM CAPITAL APPRECIATION
          </div>
        </div>
      </div>

      <div
        style={{
          ...TYPE.label,
          fontSize: 26,
          marginTop: 56,
          opacity: labelOpacity(1),
        }}
      >
        Cash Flow and Asset Divestitures
      </div>
    </div>
  );
};
