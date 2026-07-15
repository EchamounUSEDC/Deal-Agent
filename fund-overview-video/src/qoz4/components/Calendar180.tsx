import React from 'react';
import {
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY, TYPE} from '../../config/theme';

const ELIGIBLE = ['Stocks', 'Businesses', 'Real Estate', 'Other Appreciated Assets'];

/**
 * The 180-day investment window: a calendar icon with a day counter running
 * up to 180 over a sweeping timeline, alongside the list of eligible gains.
 */
export const Calendar180: React.FC<{
  width?: number;
  delay?: number;
  countDuration?: number;
}> = ({width = 1560, delay = 0, countDuration = 70}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const calIn = spring({
    frame: frame - delay,
    fps,
    config: {damping: 200, stiffness: 90},
  });
  const count = Math.round(
    interpolate(frame, [delay + 10, delay + 10 + countDuration], [0, 180], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    }),
  );
  const sweep = interpolate(
    frame,
    [delay + 10, delay + 10 + countDuration],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    },
  );

  const lineW = 620;
  const lineX = 90;
  const lineY = 388;

  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 110, width}}>
      {/* Calendar + timeline */}
      <svg width={800} height={430}>
        {/* Calendar body */}
        <g opacity={calIn}>
          <rect
            x={190}
            y={60}
            width={420}
            height={280}
            rx={10}
            fill={COLORS.navySoft}
            stroke={COLORS.white30}
            strokeWidth={2.5}
          />
          <rect x={190} y={60} width={420} height={64} rx={10} fill="rgba(163, 34, 38, 0.35)" />
          <line x1={190} y1={124} x2={610} y2={124} stroke={COLORS.redBright} strokeWidth={2.5} />
          {/* Binder rings */}
          <line x1={280} y1={40} x2={280} y2={84} stroke={COLORS.white} strokeWidth={5} strokeLinecap="round" />
          <line x1={520} y1={40} x2={520} y2={84} stroke={COLORS.white} strokeWidth={5} strokeLinecap="round" />
          {/* Day counter */}
          <text
            x={400}
            y={252}
            textAnchor="middle"
            fontFamily={FONT_FAMILY}
            fontWeight={700}
            fontSize={104}
            letterSpacing={2}
            fill={COLORS.white}
            style={{fontVariantNumeric: 'tabular-nums'}}
          >
            {count}
          </text>
          <text
            x={400}
            y={306}
            textAnchor="middle"
            fontFamily={FONT_FAMILY}
            fontWeight={500}
            fontSize={26}
            letterSpacing={8}
            fill={COLORS.white70}
          >
            DAYS
          </text>
        </g>
        {/* Window sweep under the calendar */}
        <g opacity={calIn}>
          <line
            x1={lineX}
            y1={lineY}
            x2={lineX + lineW}
            y2={lineY}
            stroke={COLORS.white30}
            strokeWidth={2}
          />
          <line
            x1={lineX}
            y1={lineY}
            x2={lineX + lineW * sweep}
            y2={lineY}
            stroke={COLORS.redBright}
            strokeWidth={4}
          />
          <circle cx={lineX + lineW * sweep} cy={lineY} r={9} fill={COLORS.redBright} />
          <circle cx={lineX + lineW * sweep} cy={lineY} r={3.5} fill={COLORS.white} />
          <text
            x={lineX}
            y={lineY + 34}
            fontFamily={FONT_FAMILY}
            fontSize={19}
            letterSpacing={2}
            fill={COLORS.white50}
          >
            GAIN EVENT
          </text>
          <text
            x={lineX + lineW}
            y={lineY + 34}
            textAnchor="end"
            fontFamily={FONT_FAMILY}
            fontSize={19}
            letterSpacing={2}
            fill={sweep >= 1 ? COLORS.white : COLORS.white50}
          >
            DAY 180
          </text>
        </g>
      </svg>

      {/* Eligible gains list */}
      <div style={{display: 'flex', flexDirection: 'column', gap: 30}}>
        <div style={{...TYPE.label, fontSize: 24, marginBottom: 6}}>
          Eligible Gains May Include
        </div>
        {ELIGIBLE.map((item, i) => {
          const itemIn = spring({
            frame: frame - (delay + 26 + i * 16),
            fps,
            config: {damping: 200, stiffness: 100},
          });
          return (
            <div
              key={item}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 22,
                opacity: itemIn,
                transform: `translateX(${interpolate(itemIn, [0, 1], [24, 0])}px)`,
              }}
            >
              <div style={{width: 36, height: 3, backgroundColor: COLORS.red}} />
              <div
                style={{
                  fontFamily: FONT_FAMILY,
                  fontWeight: 600,
                  fontSize: 34,
                  letterSpacing: '0.06em',
                  color: COLORS.white,
                }}
              >
                {item}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
