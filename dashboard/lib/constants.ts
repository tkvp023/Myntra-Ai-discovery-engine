// constants.ts — question metadata, color palette, source colors
// Used across dashboard pages and components.

export const QUESTION_META: Record<number, { text: string; short: string; color: string }> = {
  1:  { text: 'Why do users add fashion products to their wishlist?',                                   short: 'Wishlist Motivation',      color: '#ff3f6c' },
  2:  { text: 'What prevents wishlisted products from being purchased?',                               short: 'Purchase Prevention',      color: '#ff7849' },
  3:  { text: 'What uncertainties remain after identifying a liked product?',                          short: 'Remaining Uncertainties',  color: '#a855f7' },
  4:  { text: 'What causes users to postpone a purchase?',                                             short: 'Purchase Postponement',    color: '#2dd4bf' },
  5:  { text: 'How do users compare multiple shortlisted products?',                                   short: 'Comparison Behavior',      color: '#3b82f6' },
  6:  { text: 'What information do users seek outside Myntra before purchasing?',                      short: 'External Info Seeking',    color: '#fbbf24' },
  7:  { text: 'What role do fit, size, styling, price, reviews, occasion, and social validation play?', short: 'Factor Importance',        color: '#ec4899' },
  8:  { text: 'When is the wishlist genuine purchase intent vs bookmarking?',                          short: 'Intent vs Bookmarking',    color: '#84cc16' },
  9:  { text: 'How do these behaviors differ across user segments?',                                   short: 'Segment Differences',      color: '#f97316' },
  10: { text: 'What unmet needs emerge consistently across the corpus?',                               short: 'Unmet Needs',              color: '#8b5cf6' },
};

export const SOURCE_COLORS: Record<string, string> = {
  'Play Store':      '#ff3f6c',
  'Reddit':          '#ff7849',
  'YouTube':         '#a855f7',
  'App Store':       '#2dd4bf',
  'Trustpilot':      '#3b82f6',
  'PissedConsumer':  '#fbbf24',
  'Reviews.io':      '#6b7280',
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
