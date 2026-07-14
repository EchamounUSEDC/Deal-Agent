import React from 'react';
import {Audio, interpolate, staticFile, useVideoConfig} from 'remotion';
import {useAssetExists} from '../hooks/useAssetExists';
import {TOTAL_DURATION_IN_FRAMES} from '../config/timing';

export const NARRATION_PATH = 'assets/audio/narration.mp3';
export const MUSIC_PATH = 'assets/audio/music.mp3';

/**
 * Narration at full level plus subtle instrumental bed ducked underneath,
 * with a gentle fade-out at the end. Each track renders only if its file
 * has been supplied under public/assets/audio/.
 */
export const AudioTracks: React.FC<{
  narrationPath?: string;
  musicPath?: string;
  /** Composition length used for the end fade (defaults to the 2026 fund). */
  durationInFrames?: number;
}> = ({
  narrationPath = NARRATION_PATH,
  musicPath = MUSIC_PATH,
  durationInFrames = TOTAL_DURATION_IN_FRAMES,
}) => {
  const {fps} = useVideoConfig();
  const narrationExists = useAssetExists(narrationPath);
  const musicExists = useAssetExists(musicPath);

  const fadeOutStart = durationInFrames - Math.round(2.5 * fps);

  return (
    <>
      {narrationExists ? (
        <Audio
          src={staticFile(narrationPath)}
          volume={(f) =>
            interpolate(f, [fadeOutStart, durationInFrames], [1, 0], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            })
          }
        />
      ) : null}
      {musicExists ? (
        <Audio
          loop
          src={staticFile(musicPath)}
          volume={(f) =>
            interpolate(
              f,
              [0, Math.round(1.5 * fps), fadeOutStart, durationInFrames],
              [0, 0.12, 0.12, 0],
              {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
            )
          }
        />
      ) : null}
    </>
  );
};
