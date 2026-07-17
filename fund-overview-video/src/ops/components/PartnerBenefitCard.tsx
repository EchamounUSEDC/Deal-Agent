import React from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY, TYPE} from '../../config/theme';

export type BenefitCardIcon =
  | 'accelerate'
  | 'capital'
  | 'economics'
  | 'structures';

/**
 * One partner-benefit card: SVG icon, red rule, title, and supporting line.
 */
export const PartnerBenefitCard: React.FC<{
  icon: BenefitCardIcon;
  title: string;
  body: string;
  delay?: number;
  width?: number;
  height?: number;
}> = ({icon, title, body, delay = 0, width = 400, height = 460}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const enter = spring({
    frame: frame - delay,
    fps,
    config: {damping: 200, stiffness: 90},
  });
  const bodyIn = interpolate(frame, [delay + 12, delay + 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        width,
        height,
        border: `1px solid ${COLORS.white15}`,
        backgroundColor: 'rgba(0, 1, 40, 0.55)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '0 38px',
        textAlign: 'center',
        opacity: enter,
        transform: `translateY(${interpolate(enter, [0, 1], [44, 0])}px)`,
      }}
    >
      <CardGlyph icon={icon} progress={enter} />
      <div
        style={{
          width: 42,
          height: 3,
          backgroundColor: COLORS.red,
          margin: '26px 0',
          transform: `scaleX(${enter})`,
        }}
      />
      <div
        style={{
          ...TYPE.hero,
          fontSize: 31,
          lineHeight: 1.25,
          letterSpacing: '0.08em',
        }}
      >
        {title}
      </div>
      <div
        style={{
          fontFamily: FONT_FAMILY,
          fontWeight: 400,
          fontSize: 21,
          lineHeight: 1.5,
          color: COLORS.white70,
          marginTop: 20,
          opacity: bodyIn,
        }}
      >
        {body}
      </div>
    </div>
  );
};

const CardGlyph: React.FC<{icon: BenefitCardIcon; progress: number}> = ({
  icon,
  progress,
}) => {
  const common = {
    stroke: COLORS.white,
    strokeWidth: 3.2,
    fill: 'none' as const,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
  };
  return (
    <svg
      width={92}
      height={92}
      viewBox="0 0 92 92"
      style={{opacity: progress, transform: `scale(${0.85 + 0.15 * progress})`}}
    >
      <circle
        cx={46}
        cy={46}
        r={42}
        stroke={COLORS.white30}
        strokeWidth={2}
        fill="rgba(10, 13, 82, 0.55)"
      />
      {icon === 'accelerate' ? (
        // Fast-forward chevrons over a timeline
        <g {...common}>
          <path d="M 30 32 L 44 46 L 30 60" />
          <path d="M 46 32 L 60 46 L 46 60" />
          <line x1={26} y1={68} x2={66} y2={68} />
        </g>
      ) : icon === 'capital' ? (
        // Coin with a downward-reduced stack
        <g {...common}>
          <circle cx={46} cy={38} r={14} />
          <path d="M 46 30 L 46 46 M 40 34 Q 46 28 52 34 M 40 42 Q 46 48 52 42" />
          <line x1={30} y1={62} x2={62} y2={62} />
          <line x1={36} y1={70} x2={56} y2={70} />
        </g>
      ) : icon === 'economics' ? (
        // Performance line rising
        <g {...common}>
          <path d="M 26 62 L 40 48 L 50 54 L 66 34" />
          <path d="M 66 34 L 55 34 M 66 34 L 66 45" />
          <line x1={26} y1={68} x2={66} y2={68} />
        </g>
      ) : (
        // Interlocking structure/alignment
        <g {...common}>
          <circle cx={36} cy={46} r={14} />
          <circle cx={56} cy={46} r={14} />
        </g>
      )}
    </svg>
  );
};
