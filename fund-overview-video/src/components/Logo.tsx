import React from 'react';
import {Img, staticFile} from 'remotion';
import {useAssetExists} from '../hooks/useAssetExists';
import {COLORS, FONT_FAMILY} from '../config/theme';

export const LOGO_PATH = 'assets/usedc-logo.png';

/**
 * The supplied transparent U.S. Energy logo. Falls back to a clean SVG
 * wordmark if public/assets/usedc-logo.png has not been added yet.
 */
export const Logo: React.FC<{
  height?: number;
  style?: React.CSSProperties;
}> = ({height = 110, style}) => {
  const exists = useAssetExists(LOGO_PATH);

  if (exists === null) {
    return <div style={{height, ...style}} />;
  }

  if (exists) {
    return (
      <Img
        src={staticFile(LOGO_PATH)}
        style={{height, width: 'auto', display: 'block', ...style}}
      />
    );
  }

  // Wordmark fallback — replace by adding public/assets/usedc-logo.png.
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: height * 0.08,
        fontFamily: FONT_FAMILY,
        color: COLORS.white,
        ...style,
      }}
    >
      <div
        style={{
          fontSize: height * 0.42,
          fontWeight: 700,
          letterSpacing: '0.12em',
          lineHeight: 1,
          whiteSpace: 'nowrap',
        }}
      >
        U.S. <span style={{color: COLORS.redBright}}>ENERGY</span>
      </div>
      <div
        style={{
          fontSize: height * 0.13,
          fontWeight: 500,
          letterSpacing: '0.42em',
          color: COLORS.white70,
          textTransform: 'uppercase',
          whiteSpace: 'nowrap',
        }}
      >
        Development Corporation
      </div>
    </div>
  );
};
