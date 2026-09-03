// Mock data used during development before real pipeline runs.
// Matches data_contracts.md exactly — swap with real JSONs after scraping.

// ─── Q6 Sankey data ────────────────────────────────────────────────────────
export const MOCK_Q6_SANKEY = {
  nodes: [
    { id: 'Myntra Listing' },
    { id: 'YouTube Reviews' },
    { id: 'Reddit Thread' },
    { id: 'Competitor Site' },
    { id: 'Instagram/TikTok' },
    { id: 'Brand Website' },
    { id: 'Friend / WhatsApp' },
    { id: 'Purchased ✓' },
    { id: 'Abandoned ✗' },
    { id: 'Still Undecided' },
  ],
  links: [
    { source: 'Myntra Listing',  target: 'YouTube Reviews',  value: 3800 },
    { source: 'Myntra Listing',  target: 'Reddit Thread',     value: 2900 },
    { source: 'Myntra Listing',  target: 'Competitor Site',   value: 2100 },
    { source: 'Myntra Listing',  target: 'Instagram/TikTok',  value: 1700 },
    { source: 'Myntra Listing',  target: 'Brand Website',     value: 900  },
    { source: 'Myntra Listing',  target: 'Friend / WhatsApp', value: 600  },
    { source: 'YouTube Reviews', target: 'Purchased ✓',       value: 1900 },
    { source: 'YouTube Reviews', target: 'Abandoned ✗',       value: 1100 },
    { source: 'YouTube Reviews', target: 'Still Undecided',   value: 800  },
    { source: 'Reddit Thread',   target: 'Purchased ✓',       value: 1400 },
    { source: 'Reddit Thread',   target: 'Abandoned ✗',       value: 900  },
    { source: 'Reddit Thread',   target: 'Still Undecided',   value: 600  },
    { source: 'Competitor Site', target: 'Purchased ✓',       value: 700  },
    { source: 'Competitor Site', target: 'Abandoned ✗',       value: 1100 },
    { source: 'Competitor Site', target: 'Still Undecided',   value: 300  },
    { source: 'Instagram/TikTok',target: 'Purchased ✓',       value: 900  },
    { source: 'Instagram/TikTok',target: 'Still Undecided',   value: 800  },
    { source: 'Brand Website',   target: 'Purchased ✓',       value: 600  },
    { source: 'Friend / WhatsApp',target:'Purchased ✓',       value: 500  },
  ],
};

// ─── Q9 Segment cross-tab (GroupedBar) ─────────────────────────────────────
export const MOCK_Q9_GROUPED = [
  { factor: 'Sizing Uncertainty', gen_z: 38, millennial: 31, gen_x: 28 },
  { factor: 'Price Sensitivity',  gen_z: 25, millennial: 19, gen_x: 13 },
  { factor: 'Quality Doubt',      gen_z: 12, millennial: 15, gen_x: 20 },
  { factor: 'Social Validation',  gen_z: 18, millennial: 8,  gen_x: 4  },
  { factor: 'Return Anxiety',     gen_z: 7,  millennial: 11, gen_x: 16 },
  { factor: 'Style Uncertainty',  gen_z: 15, millennial: 9,  gen_x: 6  },
];

export const MOCK_SUMMARY = {
  generated_at: "2026-08-20T09:46:55Z",
  pipeline_version: "1.0.0",
  kpi_cards: [
    { id: "total_reviews", label: "Reviews Analyzed", value: 8182, unit: "count", sparkline: [4909, 5727, 6545, 7363, 8182] },
    { id: "quality_doubt", label: "Quality Doubt", value: 48.7, unit: "percent", sparkline: [29.2, 34.1, 39.0, 43.8, 48.7] },
    { id: "waiting_for_sale", label: "Waiting for Sale", value: 14.4, unit: "percent", sparkline: [8.6, 10.1, 11.5, 13.0, 14.4] },
    { id: "return_policy_concern", label: "Return Policy Concern", value: 8.8, unit: "percent", sparkline: [5.3, 6.2, 7.0, 7.9, 8.8] },
    { id: "social_validation_needed", label: "Social Validation Needed", value: 7.1, unit: "percent", sparkline: [4.3, 5.0, 5.7, 6.4, 7.1] },
    { id: "unmet_needs", label: "Unmet Needs Identified", value: 32, unit: "count", sparkline: [19, 22, 25, 28, 32] },
  ],
  source_distribution: [
    { source: "YouTube", count: 5319, pct: 65.0, color: "#a855f7" },
    { source: "Play Store", count: 1180, pct: 14.4, color: "#ff3f6c" },
    { source: "Reddit", count: 1039, pct: 12.7, color: "#ff7849" },
    { source: "PissedConsumer", count: 507, pct: 6.2, color: "#fbbf24" },
    { source: "App Store", count: 137, pct: 1.7, color: "#2dd4bf" },
  ],
  top_opportunities: [
    { rank: 1, label: "Quality Doubt", question_id: 2, pct: 48.7, count: 4617, avg_confidence: 0.57, impact_score: 10.0 },
    { rank: 2, label: "Waiting for Sale", question_id: 2, pct: 14.4, count: 1364, avg_confidence: 0.689, impact_score: 9.3 },
    { rank: 3, label: "Return Policy Concern", question_id: 2, pct: 8.8, count: 836, avg_confidence: 0.85, impact_score: 8.6 },
    { rank: 4, label: "Social Validation Needed", question_id: 2, pct: 7.1, count: 669, avg_confidence: 0.85, impact_score: 7.9 },
    { rank: 5, label: "Price Sensitivity", question_id: 2, pct: 6.5, count: 620, avg_confidence: 0.85, impact_score: 7.2 },
  ],
  overall_confidence: 0.69,
  primary_signal_docs: 7675,
  secondary_signal_docs: 507,
  no_signal_docs: 0,
};

export const MOCK_Q2 = {
  question_id: 2,
  question_text: "What prevents wishlisted products from eventually being purchased?",
  question_short: "Purchase Prevention",
  total_relevant_docs: 7557,
  avg_confidence: 0.678,
  breakdown: [
    { label: "Quality Doubt", tag: "quality_doubt", count: 4617, pct: 52.5, avg_confidence: 0.57, color: "#a855f7" },
    { label: "Waiting for Sale", tag: "waiting_for_sale", count: 1364, pct: 15.5, avg_confidence: 0.689, color: "#2dd4bf" },
    { label: "Social Validation Needed", tag: "social_validation_needed", count: 669, pct: 7.6, avg_confidence: 0.85, color: "#fbbf24" },
    { label: "Price Sensitivity", tag: "price_sensitivity", count: 620, pct: 7.0, avg_confidence: 0.85, color: "#ff7849" },
    { label: "Return Policy Concern", tag: "return_policy_concern", count: 836, pct: 8.8, avg_confidence: 0.85, color: "#06b6d4" },
    { label: "Sizing Uncertainty", tag: "sizing_uncertainty", count: 411, pct: 4.7, avg_confidence: 0.85, color: "#ff3f6c" },
    { label: "Style Uncertainty", tag: "style_uncertainty", count: 366, pct: 4.2, avg_confidence: 0.85, color: "#3b82f6" },
  ],
  segment_splits: {
    gen_z: [
      { label: "Social Validation Needed", tag: "social_validation_needed", count: 142, pct: 53.8 },
      { label: "Quality Doubt", tag: "quality_doubt", count: 36, pct: 13.6 },
      { label: "Occasion Mismatch", tag: "occasion_mismatch", count: 24, pct: 9.1 },
    ],
    millennial: [
      { label: "Quality Doubt", tag: "quality_doubt", count: 4578, pct: 53.7 },
      { label: "Waiting for Sale", tag: "waiting_for_sale", count: 1353, pct: 15.9 },
      { label: "Price Sensitivity", tag: "price_sensitivity", count: 608, pct: 7.1 },
    ],
    gen_x: [],
  },
  source_attribution: [
    { label: "Quality Doubt", tag: "quality_doubt", sources: [
      { source: "YouTube", count: 3414, pct: 73.9 },
      { source: "Play Store", count: 519, pct: 11.2 },
      { source: "Reddit", count: 435, pct: 9.4 },
      { source: "PissedConsumer", count: 184, pct: 4.0 },
      { source: "App Store", count: 65, pct: 1.4 },
    ]},
  ],
  key_quotes: [
    { text: "Size chart is so confusing, I ordered M and it fits like XL. Never trusting Myntra sizing again.", source: "Play Store", source_id: "gp_001", date: "2026-03-15", confidence: 0.92, tags: ["sizing_uncertainty"], segment: "gen_z" },
    { text: "Been waiting 3 months for this kurta to go on sale. Price is too high for this brand.", source: "Reddit", source_id: "reddit_001", date: "2026-05-22", confidence: 0.88, tags: ["waiting_for_sale"], segment: "millennial" },
    { text: "Studio pictures look like pure cotton, but fabric in reality is rough and thin.", source: "YouTube", source_id: "yt_001", date: "2026-04-10", confidence: 0.85, tags: ["quality_doubt"], segment: "millennial" },
  ],
  temporal_trend: [
    { month: "2025-01", count: 320, pct: 30.0 },
    { month: "2025-04", count: 380, pct: 32.0 },
    { month: "2025-07", count: 410, pct: 33.0 },
    { month: "2025-10", count: 450, pct: 34.0 },
    { month: "2026-01", count: 480, pct: 34.5 },
    { month: "2026-04", count: 510, pct: 35.0 },
  ],
};

export const MOCK_SYSTEMIC_GAPS = {
  generated_at: "2026-08-20T09:46:59Z",
  total_secondary_docs: 507,
  issue_breakdown: [
    { label: "Refund/Return Friction", tag: "refund_return", count: 263, pct: 34.9, color: "#ff7849" },
    { label: "Product Quality Issues", tag: "quality_issues", count: 184, pct: 24.4, color: "#a855f7" },
    { label: "Social Validation Needed", tag: "social_validation_needed", count: 62, pct: 8.2, color: "#6b7280" },
    { label: "Sizing Uncertainty", tag: "sizing_uncertainty", count: 53, pct: 7.0, color: "#6b7280" },
    { label: "Waiting for Sale", tag: "waiting_for_sale", count: 43, pct: 5.7, color: "#6b7280" },
    { label: "Pricing Complaints", tag: "pricing", count: 39, pct: 5.2, color: "#fbbf24" },
    { label: "Style Uncertainty", tag: "style_uncertainty", count: 36, pct: 4.8, color: "#6b7280" },
    { label: "App/Website Bugs", tag: "technical_issues", count: 29, pct: 3.9, color: "#3b82f6" },
  ],
  correlation_with_hesitation: [
    { systemic_issue: "Refund/Return Friction", related_hesitation: "return_policy_concern", correlation_hint: 0.88, systemic_frequency: 263, hesitation_frequency: 836 },
    { systemic_issue: "Product Quality Issues", related_hesitation: "quality_doubt", correlation_hint: 0.82, systemic_frequency: 184, hesitation_frequency: 4617 },
    { systemic_issue: "Sizing Uncertainty", related_hesitation: "sizing_uncertainty", correlation_hint: 0.74, systemic_frequency: 53, hesitation_frequency: 411 },
  ],
  key_quotes: [
    { text: "Ordered a dress for an event, arrived 2 weeks late and was the wrong size. Return courier refused pickup.", source: "PissedConsumer", date: "2026-02-10", issue: "delivery_problems" },
    { text: "Return process is a nightmare. They rejected my return saying item was 'used' when I just tried it on. Lost ₹1,800.", source: "PissedConsumer", date: "2026-04-03", issue: "refund_return" },
    { text: "Customer care just sends automated replies in app. Nobody actually reads what I wrote. Gave up after 5 attempts.", source: "Play Store", date: "2026-05-18", issue: "customer_service" },
  ],
};

export const QUESTION_META: Record<number, { text: string; short: string }> = {
  1: { text: "Why do users add fashion products to their wishlist?", short: "Wishlist Motivation" },
  2: { text: "What prevents wishlisted products from being purchased?", short: "Purchase Prevention" },
  3: { text: "What uncertainties remain after identifying a liked product?", short: "Remaining Uncertainties" },
  4: { text: "What causes users to postpone a purchase?", short: "Purchase Postponement" },
  5: { text: "How do users compare multiple shortlisted products?", short: "Comparison Behavior" },
  6: { text: "What information do users seek outside Myntra before purchasing?", short: "External Info Seeking" },
  7: { text: "What role do fit, size, styling, price, reviews, occasion, social validation play?", short: "Factor Importance" },
  8: { text: "When is the wishlist genuine purchase intent vs bookmarking?", short: "Intent vs Bookmarking" },
  9: { text: "How do these behaviors differ across user segments?", short: "Segment Differences" },
  10: { text: "What unmet needs emerge consistently across the corpus?", short: "Unmet Needs" },
};
