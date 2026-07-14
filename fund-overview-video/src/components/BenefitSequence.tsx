import React from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {COLORS, TYPE} from '../config/theme';

/**
 * Introduces a list of benefit statements one at a time, each with a short
 * red tick that draws in beside the text. Earlier items remain on screen at
 * reduced emphasis so the trio reads as a set.
 */
export const BenefitSequence: React.FC<{
  items: string[];
  /** Frame at which the first item appears. */
  delay?: number;
  /** Frames between each item's entrance. */
  stagger?: number;
  fontSize?: number;
}> = ({items, delay = 0, stagger = 55, fontSize = 74}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: 44}}>
      {items.map((item, i) => {
        const itemDelay = delay + i * stagger;
        const enter = spring({
          frame: frame - itemDelay,
          fps,
          config: {damping: 200, stiffness: 90},
        });
        const shift = interpolate(enter, [0, 1], [36, 0]);
        const isLatest = i === items.length - 1 || frame < itemDelay + stagger;
        const emphasis = isLatest ? 1 : 0.55;

        return (
          <div
            key={item}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 34,
              opacity: enter * (0.45 + 0.55 * emphasis),
              transform: `translateX(${shift}px)`,
            }}
          >
            <div
              style={{
                width: 56,
                height: 4,
                backgroundColor: COLORS.red,
                transform: `scaleX(${enter})`,
                transformOrigin: 'left center',
                flexShrink: 0,
              }}
            />
            <div
              style={{
                ...TYPE.hero,
                fontSize,
                letterSpacing: '0.08em',
                lineHeight: 1.1,
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
