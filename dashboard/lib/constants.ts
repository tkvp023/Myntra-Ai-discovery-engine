// constants.ts — question metadata, color palette, source colors
// Used across dashboard pages and components.

export interface QuestionMeta {
  text: string;
  short: string;
  color: string;
  sourceType: 'primary' | 'secondary' | 'both';
  sourceLabel: string;
  sourceDetail: string;
}

export const QUESTION_META: Record<number, QuestionMeta> = {
  1: {
    text: 'Why do users add fashion products to their wishlist?',
    short: 'Wishlist Motivation',
    color: '#ff3f6c',
    sourceType: 'primary',
    sourceLabel: '4 Primary Discovery Sources',
    sourceDetail: 'Mined from 7,675 reviews across YouTube try-on hauls, Play Store, Reddit, and App Store analyzing user intent and catalog curation.',
  },
  2: {
    text: 'What prevents wishlisted products from being purchased?',
    short: 'Purchase Prevention',
    color: '#ff7849',
    sourceType: 'both',
    sourceLabel: 'Both Primary & Secondary Sources',
    sourceDetail: 'Combines pre-purchase friction (Quality Doubt, Sizing, Sale Waiting) from 4 Primary Sources + courier & return policy friction from Secondary Source (PissedConsumer).',
  },
  3: {
    text: 'What uncertainties remain after identifying a liked product?',
    short: 'Remaining Uncertainties',
    color: '#a855f7',
    sourceType: 'both',
    sourceLabel: 'Both Primary & Secondary Sources',
    sourceDetail: 'Synthesized across fabric opacity doubts, size chart translation issues, and return eligibility concerns.',
  },
  4: {
    text: 'What causes users to postpone a purchase?',
    short: 'Purchase Postponement',
    color: '#2dd4bf',
    sourceType: 'primary',
    sourceLabel: '4 Primary Discovery Sources',
    sourceDetail: 'Mined from YouTube sale anticipation comments, Play Store price feedback, and Reddit festival discount tracking.',
  },
  5: {
    text: 'How do users compare multiple shortlisted products?',
    short: 'Comparison Behavior',
    color: '#3b82f6',
    sourceType: 'primary',
    sourceLabel: '4 Primary Discovery Sources',
    sourceDetail: 'Cross-platform comparisons evaluating price, fabric feel, and delivery speed against Ajio, Meesho, Zara, and Amazon.',
  },
  6: {
    text: 'What information do users seek outside Myntra before purchasing?',
    short: 'External Info Seeking',
    color: '#fbbf24',
    sourceType: 'primary',
    sourceLabel: '4 Primary Discovery Sources',
    sourceDetail: 'External research journeys across YouTube influencer try-ons, Reddit community advice, and Instagram creator reels.',
  },
  7: {
    text: 'What role do fit, size, styling, price, reviews, occasion, and social validation play?',
    short: 'Factor Importance',
    color: '#ec4899',
    sourceType: 'both',
    sourceLabel: 'Both Primary & Secondary Sources',
    sourceDetail: 'Multi-factor importance matrix evaluated across pre-purchase discovery channels and post-order dispute forums.',
  },
  8: {
    text: 'When is the wishlist genuine purchase intent vs bookmarking?',
    short: 'Intent vs Bookmarking',
    color: '#84cc16',
    sourceType: 'primary',
    sourceLabel: '4 Primary Discovery Sources',
    sourceDetail: 'Active conversion funnel vs passive aspirational saving analyzed across 7,675 primary user discussions.',
  },
  9: {
    text: 'How do behaviors and friction differ across discovery platforms?',
    short: 'Platform Differences',
    color: '#f97316',
    sourceType: 'both',
    sourceLabel: 'Both Primary & Secondary Sources',
    sourceDetail: 'Side-by-side attribution across YouTube (65.0%), Play Store (14.4%), Reddit (12.7%), PissedConsumer (6.2%), and App Store (1.7%).',
  },
  10: {
    text: 'What unmet needs emerge consistently across the corpus?',
    short: 'Unmet Needs',
    color: '#8b5cf6',
    sourceType: 'both',
    sourceLabel: 'Both Primary & Secondary Sources',
    sourceDetail: '32 recurring unmet needs spanning fabric verification videos, standardized sizing, and doorstep exchange dispute resolution.',
  },
};

export const SOURCE_COLORS: Record<string, string> = {
  'YouTube':         '#a855f7',
  'Play Store':      '#ff3f6c',
  'Reddit':          '#ff7849',
  'PissedConsumer':  '#fbbf24',
  'App Store':       '#2dd4bf',
};


export const CONFIDENCE_THRESHOLDS = {
  high: 0.8,
  mid:  0.6,
} as const;

export const CHART_COLORS = [
  '#ff3f6c', '#ff7849', '#a855f7', '#2dd4bf',
  '#3b82f6', '#fbbf24', '#ec4899', '#84cc16',
  '#f97316', '#8b5cf6',
];

/** Returns the confidence CSS class key for badge styling */
export function confBadgeClass(conf: number): 'badge-conf-high' | 'badge-conf-mid' | 'badge-conf-low' {
  if (conf >= CONFIDENCE_THRESHOLDS.high) return 'badge-conf-high';
  if (conf >= CONFIDENCE_THRESHOLDS.mid)  return 'badge-conf-mid';
  return 'badge-conf-low';
}
