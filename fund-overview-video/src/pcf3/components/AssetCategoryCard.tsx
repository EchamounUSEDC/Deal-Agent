import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  Video,
} from 'remotion';
import {COLORS, FONT_FAMILY, TYPE} from '../../config/theme';
import {useFirstExistingAsset} from '../../hooks/useFirstExistingAsset';

export type AssetIcon = 'producing' | 'development' | 'infrastructure';

/**
 * One asset-category panel: icon, title, two supporting lines, and a
 * muted b-roll thumbnail behind a navy wash. Falls back to a flat navy
 * panel when no footage is supplied.
 */
export const AssetCategoryCard: React.FC<{
  icon: AssetIcon;
  title: string;
  line1: string;
  line2: string;
  /** Footage candidates under public/, in order of preference. */
  broll: string[];
  delay?: number;
  width?: number;
  height?: number;
}> = ({icon, title, line1, line2, broll, delay = 0, width = 520, height = 640}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const resolved = useFirstExistingAsset(broll);

  const enter = spring({
    frame: frame - delay,
    fps,
    config: {damping: 200, stiffness: 90},
  });
  const rise = interpolate(enter, [0, 1], [40, 0]);
  const lineIn = interpolate(frame, [delay + 14, delay + 32], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        width,
        height,
        position: 'relative',
        overflow: 'hidden',
        border: `1px solid ${COLORS.white15}`,
        backgroundColor: COLORS.navyDeep,
        opacity: enter,
        transform: `translateY(${rise}px)`,
      }}
    >
      {typeof resolved === 'string' ? (
        <AbsoluteFill>
          <Video
            muted
            loop
            src={staticFile(resolved)}
            style={{width: '100%', height: '100%', objectFit: 'cover'}}
          />
        </AbsoluteFill>
      ) : null}
      {/* Navy wash for legibility (heavier at the bottom text zone) */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg,
            rgba(0, 2, 63, 0.72) 0%,
            rgba(0, 2, 63, 0.6) 45%,
            rgba(0, 1, 40, 0.94) 100%)`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'flex-end',
          padding: '0 40px 52px',
          textAlign: 'center',
        }}
      >
        <CategoryIcon icon={icon} progress={enter} />
        <div
          style={{
            width: 44,
            height: 3,
            backgroundColor: COLORS.red,
            margin: '26px 0',
            transform: `scaleX(${enter})`,
          }}
        />
        <div
          style={{
            ...TYPE.hero,
            fontSize: 34,
            letterSpacing: '0.1em',
            lineHeight: 1.2,
          }}
        >
          {title}
        </div>
        <div
          style={{
            ...TYPE.body,
            fontSize: 22,
            marginTop: 20,
            color: COLORS.white70,
            opacity: lineIn,
          }}
        >
          {line1}
        </div>
        <div
          style={{
            fontFamily: FONT_FAMILY,
            fontSize: 20,
            fontWeight: 600,
            letterSpacing: '0.18em',
            textTransform: 'uppercase',
            color: COLORS.redBright,
            marginTop: 14,
            opacity: lineIn,
          }}
        >
          {line2}
        </div>
      </div>
    </div>
  );
};

const CategoryIcon: React.FC<{icon: AssetIcon; progress: number}> = ({
  icon,
  progress,
}) => {
  const stroke = COLORS.white;
  const common = {
    stroke,
    strokeWidth: 3.5,
    fill: 'none' as const,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
  };
  return (
    <svg
      width={96}
      height={96}
      viewBox="0 0 96 96"
      style={{opacity: progress, transform: `scale(${0.85 + 0.15 * progress})`}}
    >
      <circle
        cx={48}
        cy={48}
        r={44}
        stroke={COLORS.white30}
        strokeWidth={2}
        fill="rgba(10, 13, 82, 0.55)"
      />
      {icon === 'producing' ? (
        // Pumpjack
        <g {...common}>
          <path d="M 30 68 L 42 40 L 54 68" />
          <line x1={24} y1={36} x2={62} y2={42} />
          <circle cx={68} cy={43} r={6} />
          <line x1={26} y1={68} x2={70} y2={68} />
        </g>
      ) : icon === 'development' ? (
        // Derrick with an upward growth arrow
        <g {...common}>
          <path d="M 34 68 L 44 30 L 54 68" />
          <line x1={38} y1={54} x2={50} y2={54} />
          <line x1={40} y1={42} x2={48} y2={42} />
          <path d="M 58 56 L 72 40 M 72 40 L 64 40 M 72 40 L 72 48" />
        </g>
      ) : (
        // Pipeline + mineral layers
        <g {...common}>
          <line x1={24} y1={44} x2={72} y2={44} />
          <line x1={32} y1={38} x2={32} y2={50} />
          <line x1={48} y1={38} x2={48} y2={50} />
          <line x1={64} y1={38} x2={64} y2={50} />
          <path d="M 28 62 Q 48 54 68 62" />
          <path d="M 28 70 Q 48 62 68 70" />
        </g>
      )}
    </svg>
  );
};
