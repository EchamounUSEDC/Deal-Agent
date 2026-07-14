import React from 'react';
import {Composition} from 'remotion';
import {FundOverview2026} from './FundOverview2026';
import {
  FPS,
  TOTAL_DURATION_IN_FRAMES,
  VIDEO_HEIGHT,
  VIDEO_WIDTH,
} from './config/timing';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="FundOverview2026"
      component={FundOverview2026}
      durationInFrames={TOTAL_DURATION_IN_FRAMES}
      fps={FPS}
      width={VIDEO_WIDTH}
      height={VIDEO_HEIGHT}
    />
  );
};
