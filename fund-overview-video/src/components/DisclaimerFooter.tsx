import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {COLORS, FONT_FAMILY} from '../config/theme';
import {TITLE_SAFE_MARGIN} from '../config/timing';

export const DEFAULT_DISCLAIMER =
  'For accredited investors only. This is not an offer to sell securities. ' +
  'Potential benefits are not guaranteed. See offering documents for important risk disclosures.';

/**
 * Small persistent compliance line pinned inside the title-safe area at the
 * bottom of graphic scenes.
 */
export const DisclaimerFooter: React.FC<{
  text?: string;
  delay?: number;
}> = ({text = DEFAULT_DISCLAIMER, delay = 0}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [delay, delay + 20], [0, 0.55], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        left: TITLE_SAFE_MARGIN,
        right: TITLE_SAFE_MARGIN,
        bottom: TITLE_SAFE_MARGIN - 60,
        textAlign: 'center',
        fontFamily: FONT_FAMILY,
        fontSize: 19,
        letterSpacing: '0.05em',
        color: COLORS.white,
        opacity,
      }}
    >
      {text}
    </div>
  );
};
