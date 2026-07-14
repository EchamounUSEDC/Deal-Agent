import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  Sequence,
  useCurrentFrame,
} from 'remotion';
import {StatisticCard} from '../components/StatisticCard';
import {DisclaimerFooter} from '../components/DisclaimerFooter';
import {COLORS, TYPE} from '../config/theme';
import {sceneWindow} from '../config/timing';

const {durationInFrames} = sceneWindow('scene4TaxStats');

// Three sequential statistic beats sharing the scene evenly.
const BEAT = Math.floor(durationInFrames / 3);
const BEAT_FADE = 10;

const StatBeat: React.FC<{children: React.ReactNode; last?: boolean}> = ({
  children,
  last,
}) => {
  const frame = useCurrentFrame();
  const opacity = Math.min(
    interpolate(frame, [0, BEAT_FADE], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }),
    last
      ? 1
      : interpolate(frame, [BEAT - BEAT_FADE, BEAT], [1, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        }),
  );
  return (
    <AbsoluteFill
      style={{justifyContent: 'center', alignItems: 'center', opacity}}
    >
      {children}
    </AbsoluteFill>
  );
};

/**
 * 0:21–0:34 — Navy graphic background; the three tax-benefit statistics
 * animate in sequence with large typography and small supporting labels.
 */
export const Scene4TaxStats: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(110% 90% at 50% 25%, ${COLORS.navySoft} 0%, ${COLORS.navy} 60%, ${COLORS.navyDeep} 100%)`,
      }}
    >
      <Sequence durationInFrames={BEAT} name="Stat — 90% IDC">
        <StatBeat>
          <StatisticCard
            label="Tax Advantages"
            stat={{to: 90, prefix: 'UP TO ', suffix: '%'}}
            support="Potential First-Year IDC Tax Deduction"
            delay={4}
            statSize={190}
          />
        </StatBeat>
      </Sequence>
      <Sequence from={BEAT} durationInFrames={BEAT} name="Stat — Depletion">
        <StatBeat>
          <StatisticCard
            label="Production Income"
            stat={{to: 15, toSecondary: 25, suffix: '%', rangeSeparator: '–'}}
            support="Potential Depletion Allowance on Production Income"
            delay={4}
            statSize={190}
          />
        </StatBeat>
      </Sequence>
      <Sequence from={BEAT * 2} name="Stat — AMT Relief">
        <StatBeat last>
          <StatisticCard
            label="Qualifying IDC Deductions"
            headline="POTENTIAL AMT RELIEF"
            support="On Qualifying IDC Deductions"
            delay={4}
            statSize={110}
          />
        </StatBeat>
      </Sequence>

      <DisclaimerFooter delay={16} />

      {/* Static kicker pinned above the rotating stats */}
      <div
        style={{
          position: 'absolute',
          top: 120,
          left: 0,
          right: 0,
          textAlign: 'center',
          ...TYPE.label,
          fontSize: 26,
        }}
      >
        Potential Tax Benefits
      </div>
    </AbsoluteFill>
  );
};
