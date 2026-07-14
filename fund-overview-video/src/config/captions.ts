/**
 * Caption track, synchronized to the narration recording in
 * public/assets/audio/narration.mp3.
 *
 * Times are in seconds from the start of the composition and were measured
 * against the generated voiceover. If you replace the narration, re-time
 * these windows so each caption matches the spoken phrase.
 */

export interface CaptionCue {
  start: number;
  end: number;
  text: string;
}

export const CAPTIONS: CaptionCue[] = [
  // Scenes 1–2 — introduction and three benefits
  {
    start: 0.4,
    end: 4.94,
    text: 'The U.S. Energy 2026 Drilling Fund is designed to provide accredited investors',
  },
  {
    start: 4.94,
    end: 8.89,
    text: 'with three potential benefits: meaningful tax advantages, cash flow,',
  },
  {
    start: 8.89,
    end: 10.92,
    text: 'and long-term capital appreciation.',
  },

  // Scene 3 — basins and diversification
  {
    start: 11.72,
    end: 15.85,
    text: 'The Fund develops oil and natural gas wells across established U.S. basins',
  },
  {
    start: 15.85,
    end: 19.8,
    text: 'and is intended for qualified investors seeking to lower taxable income',
  },
  {
    start: 19.8,
    end: 23.98,
    text: 'while diversifying their portfolios through alternative energy investments.',
  },

  // Scene 4 — tax statistics
  {
    start: 24.28,
    end: 29.93,
    text: 'Investors may receive up to a 90% first-year tax deduction through Intangible Drilling Costs,',
  },
  {
    start: 29.93,
    end: 33.81,
    text: 'a potential 15% to 25% depletion allowance on production income,',
  },
  {
    start: 33.81,
    end: 38.31,
    text: 'and potential alternative minimum tax relief on qualifying IDC deductions.',
  },

  // Scene 5 — cash flow target
  {
    start: 39.11,
    end: 42.4,
    text: 'Returns are generated through oil and natural gas production,',
  },
  {
    start: 42.4,
    end: 46.72,
    text: 'with a target of approximately 12% annual cash flow during the first five years,',
  },
  {
    start: 46.72,
    end: 49.41,
    text: 'once sufficient capital is deployed and producing.',
  },

  // Scene 6 — distribution timeline
  {
    start: 50.21,
    end: 54.81,
    text: 'Distributions are expected to begin approximately 12 months after the Fund closes,',
  },
  {
    start: 54.81,
    end: 57.9,
    text: 'subject to production performance and commodity prices.',
  },

  // Scene 7 — close
  {
    start: 58.8,
    end: 60.81,
    text: 'U.S. Energy Development Corporation.',
  },
  {
    start: 60.81,
    end: 64.82,
    text: 'Direct energy investment backed by more than four decades of experience.',
  },
];
