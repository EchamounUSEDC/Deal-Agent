import React from 'react';
import {Composition} from 'remotion';
import {FundOverview2026} from './FundOverview2026';
import {PCFIIIOverview} from './pcf3/PCFIIIOverview';
import {QOZIVOverview} from './qoz4/QOZIVOverview';
import {
  FPS,
  TOTAL_DURATION_IN_FRAMES,
  VIDEO_HEIGHT,
  VIDEO_WIDTH,
} from './config/timing';
import {PCF3_TOTAL_DURATION_IN_FRAMES} from './pcf3/timing';
import {QOZ4_TOTAL_DURATION_IN_FRAMES} from './qoz4/timing';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="FundOverview2026"
        component={FundOverview2026}
        durationInFrames={TOTAL_DURATION_IN_FRAMES}
        fps={FPS}
        width={VIDEO_WIDTH}
        height={VIDEO_HEIGHT}
      />
      <Composition
        id="PCFIIIOverview"
        component={PCFIIIOverview}
        durationInFrames={PCF3_TOTAL_DURATION_IN_FRAMES}
        fps={FPS}
        width={VIDEO_WIDTH}
        height={VIDEO_HEIGHT}
      />
      <Composition
        id="QOZIVOverview"
        component={QOZIVOverview}
        durationInFrames={QOZ4_TOTAL_DURATION_IN_FRAMES}
        fps={FPS}
        width={VIDEO_WIDTH}
        height={VIDEO_HEIGHT}
      />
    </>
  );
};
