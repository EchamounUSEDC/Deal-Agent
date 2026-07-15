import React from 'react';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  Video,
} from 'remotion';
import {useFirstExistingAsset} from '../hooks/useFirstExistingAsset';
import {COLORS, FONT_FAMILY} from '../config/theme';

/**
 * Full-screen b-roll with a slow controlled zoom and a dark navy overlay
 * so foreground text stays readable. Accepts a preference-ordered list of
 * footage candidates; if none are present in public/, a branded navy
 * placeholder (derrick silhouette) renders instead of failing.
 */
export type PlaceholderStyle = 'energy' | 'skyline';

export const BrollScene: React.FC<{
  /** Footage candidates under public/, in order of preference. */
  src: string | string[];
  durationInFrames: number;
  /** Seek into the source footage (seconds). */
  startFromSeconds?: number;
  zoomFrom?: number;
  zoomTo?: number;
  overlayOpacity?: number;
  /** Silhouette drawn when no footage is supplied. */
  placeholder?: PlaceholderStyle;
  children?: React.ReactNode;
}> = ({
  src,
  durationInFrames,
  startFromSeconds = 0,
  zoomFrom = 1.0,
  zoomTo = 1.08,
  overlayOpacity = 0.62,
  placeholder = 'energy',
  children,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const candidates = Array.isArray(src) ? src : [src];
  const resolved = useFirstExistingAsset(candidates);

  const zoom = interpolate(frame, [0, durationInFrames], [zoomFrom, zoomTo], {
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.ease),
  });

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.navyDeep, overflow: 'hidden'}}>
      {typeof resolved === 'string' ? (
        <AbsoluteFill style={{transform: `scale(${zoom})`}}>
          <Video
            muted
            loop
            src={staticFile(resolved)}
            startFrom={Math.round(startFromSeconds * fps)}
            style={{width: '100%', height: '100%', objectFit: 'cover'}}
          />
        </AbsoluteFill>
      ) : resolved === false ? (
        <PlaceholderFootage src={candidates[0]} zoom={zoom} style={placeholder} />
      ) : null}

      {/* Navy wash + bottom vignette for text legibility */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg,
            rgba(0, 2, 63, ${overlayOpacity * 0.85}) 0%,
            rgba(0, 2, 63, ${overlayOpacity * 0.55}) 45%,
            rgba(0, 1, 40, ${Math.min(overlayOpacity + 0.18, 0.95)}) 100%)`,
        }}
      />
      {children}
    </AbsoluteFill>
  );
};

/**
 * Branded stand-in shown when footage is missing: slow-zooming navy field
 * with a faint sector-appropriate silhouette and a discreet note naming the
 * file to add.
 */
const PlaceholderFootage: React.FC<{
  src: string;
  zoom: number;
  style: PlaceholderStyle;
}> = ({src, zoom, style}) => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, 600], [0, -40]);

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(120% 90% at 30% 20%, ${COLORS.navySoft} 0%, ${COLORS.navy} 55%, ${COLORS.navyDeep} 100%)`,
      }}
    >
      <AbsoluteFill style={{transform: `scale(${zoom}) translateX(${drift}px)`}}>
        <svg
          width="100%"
          height="100%"
          viewBox="0 0 1920 1080"
          preserveAspectRatio="xMidYMid slice"
        >
          {/* Ground line */}
          <line
            x1="0"
            y1="880"
            x2="1920"
            y2="880"
            stroke="rgba(255,255,255,0.10)"
            strokeWidth="2"
          />
          {style === 'energy' ? (
            <>
              {/* Derrick silhouette */}
              <g
                stroke="rgba(255,255,255,0.14)"
                strokeWidth="6"
                fill="none"
                strokeLinecap="round"
              >
                <path d="M 1210 880 L 1310 300 L 1410 880" />
                <path d="M 1233 740 L 1387 740" />
                <path d="M 1250 640 L 1370 640" />
                <path d="M 1265 540 L 1355 540" />
                <path d="M 1278 440 L 1342 440" />
                <path d="M 1233 740 L 1370 640 M 1250 640 L 1355 540 M 1265 540 L 1342 440" />
                <path d="M 1290 370 L 1330 370 L 1330 300 L 1290 300 Z" />
              </g>
              {/* Pumpjack silhouette */}
              <g
                stroke="rgba(255,255,255,0.10)"
                strokeWidth="6"
                fill="none"
                strokeLinecap="round"
              >
                <path d="M 480 880 L 540 700 L 600 880" />
                <path d="M 420 660 L 660 690" />
                <circle cx="672" cy="694" r="26" />
              </g>
            </>
          ) : (
            <>
              {/* City skyline silhouette */}
              <g stroke="rgba(255,255,255,0.13)" strokeWidth="5" fill="none">
                <path d="M 360 880 L 360 560 L 500 560 L 500 880" />
                <path d="M 395 620 L 465 620 M 395 680 L 465 680 M 395 740 L 465 740 M 395 800 L 465 800" />
                <path d="M 560 880 L 560 400 L 690 400 L 690 880" />
                <path d="M 595 460 L 655 460 M 595 530 L 655 530 M 595 600 L 655 600 M 595 670 L 655 670 M 595 740 L 655 740 M 595 810 L 655 810" />
                <path d="M 750 880 L 750 300 L 780 260 L 810 300 L 810 880" />
                <path d="M 900 880 L 900 480 L 1060 480 L 1060 880" />
                <path d="M 940 540 L 1020 540 M 940 610 L 1020 610 M 940 680 L 1020 680 M 940 750 L 1020 750 M 940 815 L 1020 815" />
                <path d="M 1120 880 L 1120 350 L 1250 350 L 1250 880" />
                <path d="M 1155 410 L 1215 410 M 1155 480 L 1215 480 M 1155 550 L 1215 550 M 1155 620 L 1215 620 M 1155 690 L 1215 690 M 1155 760 L 1215 760" />
                <path d="M 1320 880 L 1320 620 L 1470 620 L 1470 880" />
                <path d="M 1355 680 L 1435 680 M 1355 740 L 1435 740 M 1355 800 L 1435 800" />
              </g>
              {/* Construction crane */}
              <g
                stroke="rgba(255,255,255,0.10)"
                strokeWidth="5"
                fill="none"
                strokeLinecap="round"
              >
                <path d="M 1560 880 L 1560 380" />
                <path d="M 1420 420 L 1720 420" />
                <path d="M 1560 380 L 1620 420" />
                <path d="M 1680 420 L 1680 520" />
                <path d="M 1660 520 L 1700 520 L 1700 555 L 1660 555 Z" />
              </g>
            </>
          )}
        </svg>
      </AbsoluteFill>
      <div
        style={{
          position: 'absolute',
          right: 40,
          bottom: 32,
          fontFamily: FONT_FAMILY,
          fontSize: 20,
          letterSpacing: '0.08em',
          color: 'rgba(255,255,255,0.28)',
        }}
      >
        PLACEHOLDER — add footage at public/{src}
      </div>
    </AbsoluteFill>
  );
};
