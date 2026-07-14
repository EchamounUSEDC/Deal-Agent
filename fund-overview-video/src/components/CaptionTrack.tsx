import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {CAPTIONS} from '../config/captions';
import {COLORS, FONT_FAMILY} from '../config/theme';
import {TITLE_SAFE_MARGIN} from '../config/timing';

/**
 * Bottom-third captions synchronized with the narration. Rendered above all
 * scenes for the whole composition; individual cues fade in/out.
 */
export const CaptionTrack: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;

  const cue = CAPTIONS.find((c) => t >= c.start && t < c.end);
  if (!cue) {
    return null;
  }

  const fade = 0.18; // seconds
  const opacity = Math.min(
    interpolate(t, [cue.start, cue.start + fade], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }),
    interpolate(t, [cue.end - fade, cue.end], [1, 0], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }),
  );

  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center'}}>
      <div
        style={{
          marginBottom: TITLE_SAFE_MARGIN - 40,
          maxWidth: 1400,
          padding: '14px 34px',
          borderRadius: 8,
          backgroundColor: 'rgba(0, 1, 40, 0.72)',
          fontFamily: FONT_FAMILY,
          fontSize: 30,
          fontWeight: 500,
          lineHeight: 1.35,
          color: COLORS.white,
          textAlign: 'center',
          opacity,
        }}
      >
        {cue.text}
      </div>
    </AbsoluteFill>
  );
};
