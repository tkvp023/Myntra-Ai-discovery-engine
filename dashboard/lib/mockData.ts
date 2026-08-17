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
  generated_at: "2026-08-15T14:00:00Z",
  pipeline_version: "1.0.0",
  kpi_cards: [
    { id: "total_reviews", label: "Reviews Analyzed", value: 87432, unit: "count", sparkline: [52000, 62000, 71000, 80000, 87432], trend: "up", trend_pct: 12.5 },
    { id: "sizing_uncertainty", label: "Sizing Uncertainty", value: 34.0, unit: "percent", sparkline: [28, 30, 32, 33, 34], trend: "up", trend_pct: 2.1 },
    { id: "price_sensitivity", label: "Price Sensitivity", value: 22.0, unit: "percent", sparkline: [20, 21, 22, 22, 22], trend: "stable", trend_pct: 0.3 },
    { id: "unmet_needs", label: "Unmet Needs Identified", value: 12, unit: "count", sparkline: [5, 7, 9, 11, 12], trend: "up", trend_pct: 9.1 },
  ],
  source_distribution: [
    { source: "Play Store", count: 45521, pct: 52.1, color: "#ff3f6c" },
    { source: "Reddit", count: 18234, pct: 20.9, color: "#ff7849" },
    { source: "YouTube", count: 12876, pct: 14.7, color: "#a855f7" },
    { source: "App Store", count: 5432, pct: 6.2, color: "#2dd4bf" },
    { source: "Trustpilot", count: 3210, pct: 3.7, color: "#3b82f6" },
    { source: "PissedConsumer", count: 1567, pct: 1.8, color: "#fbbf24" },
    { source: "Reviews.io", count: 592, pct: 0.7, color: "#6b7280" },
  ],
  top_opportunities: [
    { rank: 1, label: "Sizing Uncertainty", question_id: 3, pct: 34.0, count: 16127, avg_confidence: 0.78, impact_score: 9.2 },
    { rank: 2, label: "Waiting for Price Drop", question_id: 4, pct: 22.0, count: 10435, avg_confidence: 0.82, impact_score: 8.5 },
    { rank: 3, label: "Quality Doubt", question_id: 2, pct: 15.0, count: 7115, avg_confidence: 0.71, impact_score: 7.8 },
    { rank: 4, label: "Cross-Platform Comparison", question_id: 5, pct: 12.0, count: 5692, avg_confidence: 0.74, impact_score: 7.1 },
    { rank: 5, label: "Styling Uncertainty", question_id: 3, pct: 9.0, count: 4269, avg_confidence: 0.69, impact_score: 6.5 },
  ],
  overall_confidence: 0.76,
  primary_signal_docs: 62104,
  secondary_signal_docs: 5369,
  no_signal_docs: 19959,
};

export const MOCK_Q2 = {
  question_id: 2,
  question_text: "What prevents wishlisted products from eventually being purchased?",
  question_short: "Purchase Prevention",
  total_relevant_docs: 28432,
  avg_confidence: 0.78,
  breakdown: [
    { label: "Sizing Uncertainty", tag: "sizing_uncertainty", count: 9667, pct: 34.0, avg_confidence: 0.78, color: "#ff3f6c" },
    { label: "Price Sensitivity", tag: "price_sensitivity", count: 6255, pct: 22.0, avg_confidence: 0.82, color: "#ff7849" },
    { label: "Quality Doubt", tag: "quality_doubt", count: 4265, pct: 15.0, avg_confidence: 0.71, color: "#a855f7" },
    { label: "Waiting for Sale", tag: "waiting_for_sale", count: 3124, pct: 11.0, avg_confidence: 0.85, color: "#2dd4bf" },
    { label: "Style Uncertainty", tag: "style_uncertainty", count: 2560, pct: 9.0, avg_confidence: 0.69, color: "#3b82f6" },
    { label: "Social Validation Needed", tag: "social_validation_needed", count: 1706, pct: 6.0, avg_confidence: 0.66, color: "#fbbf24" },
    { label: "Return Policy Concern", tag: "return_policy_concern", count: 855, pct: 3.0, avg_confidence: 0.74, color: "#ec4899" },
  ],
  segment_splits: {
    gen_z: [
      { label: "Sizing Uncertainty", tag: "sizing_uncertainty", count: 4833, pct: 38.0 },
      { label: "Price Sensitivity", tag: "price_sensitivity", count: 3176, pct: 25.0 },
      { label: "Style Uncertainty", tag: "style_uncertainty", count: 1904, pct: 15.0 },
    ],
    millennial: [
      { label: "Sizing Uncertainty", tag: "sizing_uncertainty", count: 3934, pct: 31.0 },
      { label: "Price Sensitivity", tag: "price_sensitivity", count: 2412, pct: 19.0 },
      { label: "Quality Doubt", tag: "quality_doubt", count: 1906, pct: 15.0 },
    ],
    gen_x: [
      { label: "Sizing Uncertainty", tag: "sizing_uncertainty", count: 1900, pct: 28.0 },
      { label: "Quality Doubt", tag: "quality_doubt", count: 1359, pct: 20.0 },
      { label: "Price Sensitivity", tag: "price_sensitivity", count: 667, pct: 13.0 },
    ],
  },
  source_attribution: [
    { label: "Sizing Uncertainty", tag: "sizing_uncertainty", sources: [
      { source: "Play Store", count: 5300, pct: 55.0 },
      { source: "Reddit", count: 2600, pct: 27.0 },
      { source: "YouTube", count: 1200, pct: 12.0 },
      { source: "App Store", count: 567, pct: 6.0 },
    ]},
  ],
  key_quotes: [
    { text: "Size chart is so confusing, I ordered M and it fits like XL. Never trusting Myntra sizing again.", source: "Play Store", source_id: "gp_001", date: "2026-03-15", confidence: 0.92, tags: ["sizing_uncertainty"], segment: "gen_z" },
    { text: "Been waiting 3 months for this kurta to go on sale. Rs 2,999 is too much for Libas brand.", source: "Reddit", source_id: "reddit_001", date: "2026-05-22", confidence: 0.88, tags: ["waiting_for_sale", "price_sensitivity"], segment: "millennial" },
    { text: "Ye dress bahut acchi hai but size ka pata nahi chalra. Reviews mein koi sizing info nahi hai.", source: "Reddit", source_id: "reddit_002", date: "2026-04-10", confidence: 0.85, tags: ["sizing_uncertainty", "information_gap"], segment: "gen_z" },
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
  generated_at: "2026-08-15T14:00:00Z",
  total_secondary_docs: 5369,
  issue_breakdown: [
    { label: "Delivery Issues", tag: "delivery_problems", count: 1820, pct: 33.9, color: "#ff3f6c" },
    { label: "Refund/Return Friction", tag: "refund_return", count: 1450, pct: 27.0, color: "#ff7849" },
    { label: "Customer Service", tag: "customer_service", count: 980, pct: 18.3, color: "#a855f7" },
    { label: "Product Authenticity", tag: "authenticity_concern", count: 650, pct: 12.1, color: "#2dd4bf" },
    { label: "App/Website Bugs", tag: "technical_issues", count: 469, pct: 8.7, color: "#3b82f6" },
  ],
  correlation_with_hesitation: [
    { systemic_issue: "Delivery Issues", related_hesitation: "sizing_uncertainty", correlation_hint: 0.72, systemic_frequency: 1820, hesitation_frequency: 9667 },
    { systemic_issue: "Refund/Return Friction", related_hesitation: "return_policy_concern", correlation_hint: 0.81, systemic_frequency: 1450, hesitation_frequency: 855 },
    { systemic_issue: "Customer Service", related_hesitation: "quality_doubt", correlation_hint: 0.58, systemic_frequency: 980, hesitation_frequency: 4265 },
    { systemic_issue: "Product Authenticity", related_hesitation: "quality_doubt", correlation_hint: 0.65, systemic_frequency: 650, hesitation_frequency: 4265 },
    { systemic_issue: "App/Website Bugs", related_hesitation: "style_uncertainty", correlation_hint: 0.43, systemic_frequency: 469, hesitation_frequency: 2560 },
  ],
  key_quotes: [
    { text: "Ordered a dress for a wedding, arrived 2 weeks late and was the wrong size. Refund took another 3 weeks.", source: "Trustpilot", date: "2026-02-10", issue: "delivery_problems" },
    { text: "Return process is a nightmare. They rejected my return saying item was 'used' when I just tried it on. Lost ₹1,800.", source: "PissedConsumer", date: "2026-04-03", issue: "refund_return" },
    { text: "Customer care just sends automated replies. Nobody actually reads what I wrote. Gave up after 5 emails.", source: "Trustpilot", date: "2026-05-18", issue: "customer_service" },
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
