import React from 'react';
import {AbsoluteFill} from 'remotion';
import {BrollScene} from '../../components/BrollScene';
import {PartnerBenefitCard} from '../components/PartnerBenefitCard';
import {opsSceneWindow} from '../timing';

const {durationInFrames} = opsSceneWindow('scene5Benefits');

/**
 * Partner benefits — four cards over drilling/construction/partner footage.
 */
export const OpsScene5Benefits: React.FC = () => {
  return (
    <BrollScene
      src={[
        'assets/operations-broll/completion.mp4',
        'assets/operations-broll/rig.mp4',
        'assets/rig-broll.mp4',
      ]}
      durationInFrames={durationInFrames}
      startFromSeconds={6}
      zoomFrom={1.0}
      zoomTo={1.05}
      overlayOpacity={0.85}
    >
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <div style={{display: 'flex', gap: 36}}>
          <PartnerBenefitCard
            icon="accelerate"
            title="ACCELERATE DEVELOPMENT"
            body="Support efficient execution and compressed project timelines."
            delay={12}
          />
          <PartnerBenefitCard
            icon="capital"
            title="REDUCE CAPITAL OUTLAY"
            body="Flexible capital designed to help partners scale development."
            delay={64}
          />
          <PartnerBenefitCard
            icon="economics"
            title="IMPROVE ECONOMICS"
            body="Disciplined technical evaluation and performance-focused operations."
            delay={116}
          />
          <PartnerBenefitCard
            icon="structures"
            title="FLEXIBLE STRUCTURES"
            body="Aligned partnerships designed to distribute risk and create long-term value."
            delay={168}
          />
        </div>
      </AbsoluteFill>
    </BrollScene>
  );
};
