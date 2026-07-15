import React from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY, TYPE} from '../../config/theme';

type BenefitIcon = 'defer' | 'appreciation' | 'growth';

interface Benefit {
  icon: BenefitIcon;
  title: string;
  support?: string;
}

const BENEFITS: Benefit[] = [
  {icon: 'defer', title: 'DEFER CAPITAL GAINS TAXES'},
  {
    icon: 'appreciation',
    title: 'POTENTIAL TAX-FREE APPRECIATION',
    support: 'Held 10+ Years',
  },
  {icon: 'growth', title: 'LONG-TERM TAX-EFFICIENT GROWTH'},
];

/**
 * Three tax-benefit cards entering one after another on a navy field.
 */
export const TaxBenefitCards: React.FC<{
  delay?: number;
  stagger?: number;
  cardWidth?: number;
  cardHeight?: number;
}> = ({delay = 0, stagger = 90, cardWidth = 500, cardHeight = 460}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  return (
    <div style={{display: 'flex', gap: 48}}>
      {BENEFITS.map((b, i) => {
        const cardDelay = delay + i * stagger;
        const enter = spring({
          frame: frame - cardDelay,
          fps,
          config: {damping: 200, stiffness: 90},
        });
        const lineIn = interpolate(
          frame,
          [cardDelay + 12, cardDelay + 30],
          [0, 1],
          {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
        );
        return (
          <div
            key={b.title}
            style={{
              width: cardWidth,
              height: cardHeight,
              border: `1px solid ${COLORS.white15}`,
              backgroundColor: 'rgba(10, 13, 82, 0.4)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '0 46px',
              textAlign: 'center',
              opacity: enter,
              transform: `translateY(${interpolate(enter, [0, 1], [44, 0])}px)`,
            }}
          >
            <BenefitGlyph icon={b.icon} progress={enter} />
            <div
              style={{
                width: 44,
                height: 3,
                backgroundColor: COLORS.red,
                margin: '30px 0',
                transform: `scaleX(${lineIn})`,
              }}
            />
            <div
              style={{
                ...TYPE.hero,
                fontSize: 36,
                lineHeight: 1.25,
                letterSpacing: '0.08em',
              }}
            >
              {b.title}
            </div>
            {b.support ? (
              <div
                style={{
                  fontFamily: FONT_FAMILY,
                  fontWeight: 600,
                  fontSize: 22,
                  letterSpacing: '0.2em',
                  textTransform: 'uppercase',
                  color: COLORS.redBright,
                  marginTop: 22,
                  opacity: lineIn,
                }}
              >
                {b.support}
              </div>
            ) : null}
          </div>
        );
      })}
    </div>
  );
};

const BenefitGlyph: React.FC<{icon: BenefitIcon; progress: number}> = ({
  icon,
  progress,
}) => {
  const common = {
    stroke: COLORS.white,
    strokeWidth: 3.5,
    fill: 'none' as const,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
  };
  return (
    <svg
      width={100}
      height={100}
      viewBox="0 0 100 100"
      style={{opacity: progress, transform: `scale(${0.85 + 0.15 * progress})`}}
    >
      <circle
        cx={50}
        cy={50}
        r={46}
        stroke={COLORS.white30}
        strokeWidth={2}
        fill="rgba(10, 13, 82, 0.55)"
      />
      {icon === 'defer' ? (
        // Pause/hold over a document
        <g {...common}>
          <rect x={32} y={26} width={36} height={48} rx={4} />
          <line x1={44} y1={42} x2={44} y2={60} />
          <line x1={56} y1={42} x2={56} y2={60} />
        </g>
      ) : icon === 'appreciation' ? (
        // Rising arrow over a decade marker
        <g {...common}>
          <path d="M 28 66 L 44 50 L 54 58 L 72 36" />
          <path d="M 72 36 L 60 36 M 72 36 L 72 48" />
          <line x1={28} y1={74} x2={72} y2={74} />
        </g>
      ) : (
        // Building with upward accent
        <g {...common}>
          <rect x={34} y={40} width={32} height={34} />
          <line x1={42} y1={50} x2={58} y2={50} />
          <line x1={42} y1={58} x2={58} y2={58} />
          <line x1={42} y1={66} x2={58} y2={66} />
          <path d="M 50 40 L 50 28 M 44 33 L 50 27 L 56 33" />
        </g>
      )}
    </svg>
  );
};
