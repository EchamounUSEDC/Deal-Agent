import React from 'react';
import {AbsoluteFill} from 'remotion';
import {BrollScene} from '../components/BrollScene';
import {BenefitSequence} from '../components/BenefitSequence';
import {sceneWindow, TITLE_SAFE_MARGIN} from '../config/timing';

const {durationInFrames} = sceneWindow('scene2Benefits');

/**
 * 0:05–0:13 — Continued rig/aerial footage; the three benefit statements
 * enter one at a time.
 */
export const Scene2Benefits: React.FC = () => {
  return (
    <BrollScene
      src={['assets/broll/aerial-basin.mp4', 'assets/rig-broll.mp4']}
      durationInFrames={durationInFrames}
      startFromSeconds={5}
      zoomFrom={1.07}
      zoomTo={1.0}
      overlayOpacity={0.7}
    >
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          paddingLeft: TITLE_SAFE_MARGIN + 120,
        }}
      >
        <BenefitSequence
          items={[
            'TAX ADVANTAGES',
            'CASH FLOW',
            'LONG-TERM CAPITAL APPRECIATION',
          ]}
          delay={54}
          stagger={42}
          fontSize={68}
        />
      </AbsoluteFill>
    </BrollScene>
  );
};
