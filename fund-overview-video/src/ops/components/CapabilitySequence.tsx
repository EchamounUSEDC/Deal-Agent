import React from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, FONT_FAMILY} from '../../config/theme';

/**
 * Numbered capability labels introduced one at a time; earlier items stay
 * at reduced emphasis so the full-cycle list builds down the screen.
 */
export const CapabilitySequence: React.FC<{
  items: string[];
  delay?: number;
  stagger?: number;
  fontSize?: number;
}> = ({items, delay = 0, stagger = 50, fontSize = 44}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 34}}>
      {items.map((item, i) => {
        const itemDelay = delay + i * stagger;
        const enter = spring({
          frame: frame - itemDelay,
          fps,
          config: {damping: 200, stiffness: 90},
        });
        const isLatest = i === items.length - 1 || frame < itemDelay + stagger;
        const emphasis = isLatest ? 1 : 0.55;
        return (
          <div
            key={item}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 28,
              opacity: enter * (0.45 + 0.55 * emphasis),
              transform: `translateX(${interpolate(enter, [0, 1], [34, 0])}px)`,
            }}
          >
            <div
              style={{
                fontFamily: FONT_FAMILY,
                fontWeight: 600,
                fontSize: 22,
                letterSpacing: '0.14em',
                color: COLORS.redBright,
                width: 44,
                flexShrink: 0,
                fontVariantNumeric: 'tabular-nums',
              }}
            >
              {String(i + 1).padStart(2, '0')}
            </div>
            <div
              style={{
                width: 40,
                height: 3,
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
                letterSpacing: '0.07em',
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
