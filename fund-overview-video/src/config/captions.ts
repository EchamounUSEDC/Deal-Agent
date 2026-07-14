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
    end: 5.04,
    text: 'The U.S. Energy 2026 Drilling Fund is designed to provide accredited investors',
  },
  {
    start: 5.04,
    end: 9.09,
    text: 'with three potential benefits: meaningful tax advantages, cash flow,',
  },
  {start: 9.09, end: 11.17, text: 'and long-term capital appreciation.'},

  // Scene 3 — basins and diversification
  {
    start: 11.97,
    end: 16.1,
    text: 'The Fund develops oil and natural gas wells across established U.S. basins',
  },
  {
    start: 16.1,
    end: 20.05,
    text: 'and is intended for qualified investors seeking to lower taxable income',
  },
  {
    start: 20.05,
    end: 24.23,
    text: 'while diversifying their portfolios through alternative energy investments.',
  },

  // Scene 4 — tax statistics
  {
    start: 24.53,
    end: 30.18,
    text: 'Investors may receive up to a 90% first-year tax deduction through Intangible Drilling Costs,',
  },
  {
    start: 30.18,
    end: 34.06,
    text: 'a potential 15% to 25% depletion allowance on production income,',
  },
  {
    start: 34.06,
    end: 38.56,
    text: 'and potential alternative minimum tax relief on qualifying IDC deductions.',
  },

  // Scene 5 — cash flow target
  {
    start: 39.36,
    end: 42.65,
    text: 'Returns are generated through oil and natural gas production,',
  },
  {
    start: 42.65,
    end: 46.96,
    text: 'with a target of approximately 12% annual cash flow during the first five years,',
  },
  {
    start: 46.96,
    end: 49.66,
    text: 'once sufficient capital is deployed and producing.',
  },

  // Scene 6 — distribution timeline
  {
    start: 50.46,
    end: 55.06,
    text: 'Distributions are expected to begin approximately 12 months after the Fund closes,',
  },
  {
    start: 55.06,
    end: 58.15,
    text: 'subject to production performance and commodity prices.',
  },

  // Scene 7 — close
  {start: 59.05, end: 61.15, text: 'U.S. Energy Development Corporation.'},
  {
    start: 61.15,
    end: 65.35,
    text: 'Direct energy investment backed by more than four decades of experience.',
  },
];
