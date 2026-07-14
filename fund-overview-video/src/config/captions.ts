/**
 * Caption track, synchronized to the narration script.
 *
 * Times are in seconds from the start of the composition. When you replace
 * public/assets/audio/narration.mp3 with a recorded voiceover, nudge these
 * windows so each caption matches the spoken phrase.
 */

export interface CaptionCue {
  start: number;
  end: number;
  text: string;
}

export const CAPTIONS: CaptionCue[] = [
  // Scenes 1–2 — introduction and three benefits
  {
    start: 0.6,
    end: 5.0,
    text: 'The U.S. Energy 2026 Drilling Fund is designed to provide accredited investors',
  },
  {
    start: 5.0,
    end: 9.0,
    text: 'with three potential benefits: meaningful tax advantages, cash flow,',
  },
  {start: 9.0, end: 12.6, text: 'and long-term capital appreciation.'},

  // Scene 3 — basins and diversification
  {
    start: 13.2,
    end: 17.2,
    text: 'The Fund develops oil and natural gas wells across established U.S. basins',
  },
  {
    start: 17.2,
    end: 20.8,
    text: 'and is intended for qualified investors seeking to lower taxable income',
  },

  // Scene 4 — tax statistics
  {
    start: 21.2,
    end: 24.2,
    text: 'while diversifying their portfolios through alternative energy investments.',
  },
  {
    start: 24.4,
    end: 28.4,
    text: 'Investors may receive up to a 90% first-year tax deduction through Intangible Drilling Costs,',
  },
  {
    start: 28.4,
    end: 31.4,
    text: 'a potential 15% to 25% depletion allowance on production income,',
  },
  {
    start: 31.4,
    end: 33.8,
    text: 'and potential alternative minimum tax relief on qualifying IDC deductions.',
  },

  // Scene 5 — cash flow target
  {
    start: 34.4,
    end: 38.4,
    text: 'Returns are generated through oil and natural gas production,',
  },
  {
    start: 38.4,
    end: 42.4,
    text: 'with a target of approximately 12% annual cash flow during the first five years',
  },
  {
    start: 42.4,
    end: 44.8,
    text: 'once sufficient capital is deployed and producing.',
  },

  // Scene 6 — distribution timeline
  {
    start: 45.4,
    end: 49.4,
    text: 'Distributions are expected to begin approximately 12 months after the Fund closes,',
  },
  {
    start: 49.4,
    end: 52.6,
    text: 'subject to production performance and commodity prices.',
  },

  // Scene 7 — close
  {start: 53.4, end: 56.2, text: 'U.S. Energy Development Corporation.'},
  {
    start: 56.2,
    end: 59.6,
    text: 'Direct energy investment backed by more than four decades of experience.',
  },
];
