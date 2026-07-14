import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {SCENE_FADE_FRAMES} from '../config/timing';
import {COLORS} from '../config/theme';

/**
 * Wraps a scene in a restrained fade from/to the navy base so scene cuts
 * read as controlled dissolves rather than hard cuts.
 */
export const SceneFade: React.FC<{
  durationInFrames: number;
  fadeIn?: boolean;
  fadeOut?: boolean;
  children: React.ReactNode;
}> = ({durationInFrames, fadeIn = true, fadeOut = true, children}) => {
  const frame = useCurrentFrame();

  const inOpacity = fadeIn
    ? interpolate(frame, [0, SCENE_FADE_FRAMES], [0, 1], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      })
    : 1;
  const outOpacity = fadeOut
    ? interpolate(
        frame,
        [durationInFrames - SCENE_FADE_FRAMES, durationInFrames],
        [1, 0],
        {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
      )
    : 1;

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.navy}}>
      <AbsoluteFill style={{opacity: Math.min(inOpacity, outOpacity)}}>
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
