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
export const AudioTracks: React.FC = () => {
  const {fps} = useVideoConfig();
  const narrationExists = useAssetExists(NARRATION_PATH);
  const musicExists = useAssetExists(MUSIC_PATH);

  const fadeOutStart = TOTAL_DURATION_IN_FRAMES - Math.round(2.5 * fps);

  return (
    <>
      {narrationExists ? (
        <Audio
          src={staticFile(NARRATION_PATH)}
          volume={(f) =>
            interpolate(
              f,
              [fadeOutStart, TOTAL_DURATION_IN_FRAMES],
              [1, 0],
              {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
            )
          }
        />
      ) : null}
      {musicExists ? (
        <Audio
          loop
          src={staticFile(MUSIC_PATH)}
          volume={(f) =>
            interpolate(
              f,
              [0, Math.round(1.5 * fps), fadeOutStart, TOTAL_DURATION_IN_FRAMES],
              [0, 0.12, 0.12, 0],
              {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
            )
          }
        />
      ) : null}
    </>
  );
};
