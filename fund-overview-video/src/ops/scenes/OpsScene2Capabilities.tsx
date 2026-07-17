import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {BrollScene} from '../../components/BrollScene';
import {CapabilitySequence} from '../components/CapabilitySequence';
import {AccentLine} from '../../components/AccentLine';
import {opsSceneWindow} from '../timing';
import {TITLE_SAFE_MARGIN} from '../../config/timing';
import {TYPE, COLORS} from '../../config/theme';

const {durationInFrames} = opsSceneWindow('scene2Capabilities');

/**
 * Full-cycle expertise — technical-team footage with the five capability
 * labels entering one at a time.
 */
export const OpsScene2Capabilities: React.FC = () => {
  const frame = useCurrentFrame();
  const headOpacity = interpolate(frame, [4, 22], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const supportOpacity = interpolate(frame, [250, 272], [0, 0.75], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <BrollScene
      src={[
        'assets/operations-broll/technical-team.mp4',
        'assets/operations-broll/control-room.mp4',
        'assets/rig-broll.mp4',
      ]}
      durationInFrames={durationInFrames}
      startFromSeconds={2}
      zoomFrom={1.0}
      zoomTo={1.06}
      overlayOpacity={0.82}
    >
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          paddingLeft: TITLE_SAFE_MARGIN + 80,
          gap: 44,
        }}
      >
        <div style={{opacity: headOpacity}}>
          <div style={{...TYPE.hero, fontSize: 58, letterSpacing: '0.09em'}}>
            FULL-CYCLE ENERGY EXPERTISE
          </div>
          <AccentLine width={210} delay={10} style={{marginTop: 22}} />
        </div>
        <CapabilitySequence
          items={[
            'Geological and Subsurface Analysis',
            'Drilling and Completions Engineering',
            'Production Optimization',
            'Economic and Reservoir Evaluation',
            'Project Management',
          ]}
          delay={26}
          stagger={48}
          fontSize={40}
        />
        <div
          style={{
            ...TYPE.body,
            fontSize: 24,
            color: COLORS.white,
            opacity: supportOpacity,
          }}
        >
          From underwriting through development and ongoing operations.
        </div>
      </AbsoluteFill>
    </BrollScene>
  );
};
