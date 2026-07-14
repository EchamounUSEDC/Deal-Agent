import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {COLORS} from '../config/theme';
import {Easing} from 'remotion';

/**
 * Thin red brand rule that draws in from the left.
 */
export const AccentLine: React.FC<{
  width?: number;
  height?: number;
  delay?: number;
  drawDuration?: number;
  color?: string;
  style?: React.CSSProperties;
}> = ({
  width = 220,
  height = 3,
  delay = 0,
  drawDuration = 20,
  color = COLORS.red,
  style,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(
    frame,
    [delay, delay + drawDuration],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    },
  );

  return (
    <div
      style={{
        width,
        height,
        overflow: 'hidden',
        ...style,
      }}
    >
      <div
        style={{
          width: '100%',
          height: '100%',
          backgroundColor: color,
          transform: `scaleX(${progress})`,
          transformOrigin: 'left center',
        }}
      />
    </div>
  );
};
