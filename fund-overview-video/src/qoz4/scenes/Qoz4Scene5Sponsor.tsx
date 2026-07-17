import React from 'react';
import {AbsoluteFill} from 'remotion';
import {BrollScene} from '../../components/BrollScene';
import {SponsorStrengths} from '../components/SponsorStrengths';
import {OpportunityZoneMap} from '../components/OpportunityZoneMap';
import {qoz4SceneWindow} from '../timing';
import {TITLE_SAFE_MARGIN} from '../../config/timing';

const {durationInFrames} = qoz4SceneWindow('scene5Sponsor');

/**
 * 0:36–0:48 — Energy-development footage with institutional callouts,
 * balanced by a quiet Opportunity Zone community map.
 */
export const Qoz4Scene5Sponsor: React.FC = () => {
  return (
    <BrollScene
      src={[
        'assets/qoz-broll/operations.mp4',
        'assets/qoz-broll/production.mp4',
        'assets/rig-broll.mp4',
      ]}
      durationInFrames={durationInFrames}
      startFromSeconds={3}
      zoomFrom={1.0}
      zoomTo={1.06}
      overlayOpacity={0.82}
    >
      <AbsoluteFill
        style={{
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingLeft: TITLE_SAFE_MARGIN + 60,
          paddingRight: TITLE_SAFE_MARGIN + 20,
        }}
      >
        <SponsorStrengths delay={12} stagger={62} fontSize={48} />
        <OpportunityZoneMap width={640} delay={20} opacity={0.55} />
      </AbsoluteFill>
    </BrollScene>
  );
};
