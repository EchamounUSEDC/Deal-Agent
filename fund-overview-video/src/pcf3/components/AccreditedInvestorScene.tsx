import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {BrollScene} from '../../components/BrollScene';
import {AccentLine} from '../../components/AccentLine';
import {COLORS, TYPE} from '../../config/theme';

/**
 * Qualification screen: heavy navy wash over subtle energy footage, a
 * restrained lock icon, the accredited-investor headline, suitability
 * language, and a small risk qualifier.
 */
export const AccreditedInvestorScene: React.FC<{
  durationInFrames: number;
  broll?: string[];
}> = ({
  durationInFrames,
  broll = ['assets/energy-broll-02.mp4', 'assets/energy-broll-01.mp4', 'assets/rig-broll.mp4'],
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const lockIn = spring({
    frame: frame - 6,
    fps,
    config: {damping: 200, stiffness: 100},
  });
  const supportOpacity = interpolate(frame, [34, 54], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const qualifierOpacity = interpolate(frame, [58, 78], [0, 0.6], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <BrollScene
      src={broll}
      durationInFrames={durationInFrames}
      startFromSeconds={4}
      zoomFrom={1.0}
      zoomTo={1.04}
      overlayOpacity={0.9}
    >
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: 'center',
          flexDirection: 'column',
        }}
      >
        {/* Lock icon */}
        <svg
          width={92}
          height={92}
          viewBox="0 0 92 92"
          style={{opacity: lockIn, transform: `scale(${0.85 + 0.15 * lockIn})`}}
        >
          <circle
            cx={46}
            cy={46}
            r={43}
            stroke={COLORS.white30}
            strokeWidth={2}
            fill="rgba(10, 13, 82, 0.5)"
          />
          <g stroke={COLORS.white} strokeWidth={3.5} fill="none" strokeLinejoin="round">
            <rect x={31} y={42} width={30} height={24} rx={3} />
            <path d="M 36 42 L 36 34 a 10 10 0 0 1 20 0 L 56 42" />
            <circle cx={46} cy={53} r={3.5} fill={COLORS.redBright} stroke="none" />
          </g>
        </svg>

        <div
          style={{
            ...TYPE.hero,
            fontSize: 62,
            letterSpacing: '0.1em',
            marginTop: 42,
            opacity: lockIn,
          }}
        >
          DESIGNED FOR ACCREDITED INVESTORS
        </div>
        <AccentLine width={220} delay={16} style={{marginTop: 32}} />
        <div
          style={{
            ...TYPE.body,
            fontSize: 30,
            maxWidth: 1240,
            textAlign: 'center',
            lineHeight: 1.5,
            marginTop: 36,
            color: COLORS.white70,
            opacity: supportOpacity,
          }}
        >
          Investors Must Be Able to Tolerate Illiquidity and the Risks of
          Private Energy Investments
        </div>
        <div
          style={{
            ...TYPE.body,
            fontSize: 22,
            fontStyle: 'italic',
            marginTop: 40,
            color: COLORS.white,
            opacity: qualifierOpacity,
          }}
        >
          Investing involves risk, including the potential loss of capital.
        </div>
      </AbsoluteFill>
    </BrollScene>
  );
};
