/** U.S. Energy Development Corporation brand tokens. */

export const COLORS = {
  navy: '#00023F',
  navyDeep: '#000128',
  navySoft: '#0A0D52',
  red: '#82171A',
  redBright: '#A32226',
  white: '#FFFFFF',
  white70: 'rgba(255, 255, 255, 0.7)',
  white50: 'rgba(255, 255, 255, 0.5)',
  white30: 'rgba(255, 255, 255, 0.3)',
  white15: 'rgba(255, 255, 255, 0.15)',
} as const;

export const FONT_FAMILY =
  '"Inter", "Helvetica Neue", Helvetica, Arial, sans-serif';

export const TYPE = {
  hero: {
    fontFamily: FONT_FAMILY,
    fontWeight: 700,
    letterSpacing: '0.06em',
    color: COLORS.white,
  },
  label: {
    fontFamily: FONT_FAMILY,
    fontWeight: 500,
    letterSpacing: '0.22em',
    textTransform: 'uppercase' as const,
    color: COLORS.white70,
  },
  body: {
    fontFamily: FONT_FAMILY,
    fontWeight: 400,
    color: COLORS.white70,
  },
} as const;
