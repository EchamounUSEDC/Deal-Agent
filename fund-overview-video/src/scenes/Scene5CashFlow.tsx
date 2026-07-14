import React from 'react';
import {AbsoluteFill} from 'remotion';
import {BrollScene} from '../components/BrollScene';
import {StatisticCard} from '../components/StatisticCard';
import {RevenueFlow} from '../components/RevenueFlow';
import {sceneWindow} from '../config/timing';

const {durationInFrames} = sceneWindow('scene5CashFlow');

/**
 * 0:34–0:45 — Oil-production b-roll beneath the 12% cash-flow target and a
 * clean revenue-flow graphic from producing wells to investor distributions.
 */
export const Scene5CashFlow: React.FC = () => {
  return (
    <BrollScene
      src={[
        'assets/broll/production.mp4',
        'assets/broll/pumpjack.mp4',
        'assets/rig-broll.mp4',
      ]}
      durationInFrames={durationInFrames}
      startFromSeconds={10}
      zoomFrom={1.0}
      zoomTo={1.06}
      overlayOpacity={0.78}
    >
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: 'center',
          flexDirection: 'column',
          gap: 70,
          paddingTop: 20,
        }}
      >
        <StatisticCard
          label="Targeting Approximately"
          stat={{to: 12, suffix: '%'}}
          support="Annual Cash Flow — During the First Five Years Once Sufficient Capital Is Deployed and Producing"
          delay={8}
          statSize={170}
          countDuration={40}
        />
        <RevenueFlow width={1460} delay={46} />
      </AbsoluteFill>
    </BrollScene>
  );
};
