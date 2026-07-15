import React from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY} from '../../config/theme';

const STRENGTHS = [
  'DEEP OPPORTUNITY ZONE EXPERIENCE',
  'DISCIPLINED UNDERWRITING',
  'INSTITUTIONAL EXECUTION',
  'ADVISOR PARTNERSHIP',
  'TRANSPARENCY',
];

/**
 * Institutional callouts introduced one at a time over development footage.
 * Earlier items stay on screen at reduced emphasis so the list builds.
 */
export const SponsorStrengths: React.FC<{
  delay?: number;
  stagger?: number;
  fontSize?: number;
}> = ({delay = 0, stagger = 56, fontSize = 52}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 36}}>
      {STRENGTHS.map((item, i) => {
        const itemDelay = delay + i * stagger;
        const enter = spring({
          frame: frame - itemDelay,
          fps,
          config: {damping: 200, stiffness: 90},
        });
        const isLatest =
          i === STRENGTHS.length - 1 || frame < itemDelay + stagger;
        const emphasis = isLatest ? 1 : 0.55;
        return (
          <div
            key={item}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 30,
              opacity: enter * (0.45 + 0.55 * emphasis),
              transform: `translateX(${interpolate(enter, [0, 1], [36, 0])}px)`,
            }}
          >
            <div
              style={{
                width: 50,
                height: 4,
                backgroundColor: COLORS.red,
                transform: `scaleX(${enter})`,
                transformOrigin: 'left center',
                flexShrink: 0,
              }}
            />
            <div
              style={{
                fontFamily: FONT_FAMILY,
                fontWeight: 700,
                fontSize,
                letterSpacing: '0.08em',
                color: COLORS.white,
                lineHeight: 1.15,
              }}
            >
              {item}
            </div>
          </div>
        );
      })}
    </div>
  );
};
