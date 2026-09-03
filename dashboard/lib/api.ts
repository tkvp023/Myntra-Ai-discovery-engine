// Data fetching utilities — reads from /public/data/*.json at build time via fs.
// Falls back to mock data if the JSON file doesn't exist yet.

import { MOCK_SUMMARY, MOCK_Q2, MOCK_SYSTEMIC_GAPS, MOCK_Q6_SANKEY, MOCK_Q9_GROUPED } from './mockData';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

function loadJSON<T>(filename: string, fallback: T): T {
  try {
    const filePath = join(process.cwd(), 'public', 'data', filename);
    if (!existsSync(filePath)) return fallback;
    const raw = readFileSync(filePath, 'utf-8');
    const data = JSON.parse(raw);
    // If pipeline hasn't run yet (0 docs), use mock
    if (data?.kpi_cards?.[0]?.value === 0 || data?.total_relevant_docs === 0) {
      return fallback as T;
    }
    return data as T;
  } catch {
    return fallback;
  }
}

export async function getSummary() {
  return loadJSON('summary.json', MOCK_SUMMARY);
}

export async function getQuestion(id: number) {
  const fallback = id === 2 ? MOCK_Q2 : generateMockQuestion(id);
  return loadJSON(`q${id}.json`, fallback);
}

export async function getSystemicGaps() {
  return loadJSON('systemic_gaps.json', MOCK_SYSTEMIC_GAPS);
}

export async function getCorpusMeta() {
  return loadJSON('corpus_meta.json', {});
}

// Generate a skeleton mock for questions without a specific mock
function generateMockQuestion(id: number) {
  const metas: Record<number, [string, string]> = {
    1:  ["Why do users add fashion products to their wishlist?", "Wishlist Motivation"],
    3:  ["What uncertainties remain after identifying a liked product?", "Remaining Uncertainties"],
    4:  ["What causes users to postpone a purchase?", "Purchase Postponement"],
    5:  ["How do users compare multiple shortlisted products?", "Comparison Behavior"],
    6:  ["What information do users seek outside Myntra?", "External Info Seeking"],
    7:  ["What role do fit, size, styling, price, reviews, occasion, social validation play?", "Factor Importance"],
    8:  ["When is the wishlist genuine purchase intent vs bookmarking?", "Intent vs Bookmarking"],
    9:  ["How do behaviors and friction differ across discovery platforms?", "Platform Differences"],
    10: ["What unmet needs emerge consistently?", "Unmet Needs"],
  };
  const [text, short] = metas[id] || [`Question ${id}`, `Q${id}`];
  return {
    question_id: id,
    question_text: text,
    question_short: short,
    total_relevant_docs: 8182,
    avg_confidence: 0.69,
    breakdown: [
      { label: "Quality Doubt", tag: "quality_doubt", count: 4617, pct: 48.7, avg_confidence: 0.57, color: "#a855f7" },
      { label: "Waiting for Sale", tag: "waiting_for_sale", count: 1364, pct: 14.4, avg_confidence: 0.689, color: "#2dd4bf" },
      { label: "Return Policy Concern", tag: "return_policy_concern", count: 836, pct: 8.8, avg_confidence: 0.85, color: "#06b6d4" },
      { label: "Social Validation Needed", tag: "social_validation_needed", count: 669, pct: 7.1, avg_confidence: 0.85, color: "#fbbf24" },
      { label: "Price Sensitivity", tag: "price_sensitivity", count: 620, pct: 6.5, avg_confidence: 0.85, color: "#ff7849" },
    ],
    source_attribution: [],
    key_quotes: [
      { text: "Size chart is so confusing, I ordered M and it fits like XL. Never trusting Myntra sizing again.", source: "Play Store", source_id: "gp_001", date: "2026-03-15", confidence: 0.92, tags: ["sizing_uncertainty"] },
      { text: "Been waiting 3 months for this kurta to go on sale. Price is too high for this brand.", source: "Reddit", source_id: "reddit_001", date: "2026-05-22", confidence: 0.88, tags: ["waiting_for_sale"] },
    ],
    temporal_trend: [
      { month: "2025-01", count: 300, pct: 29.0 },
      { month: "2025-04", count: 360, pct: 31.0 },
      { month: "2025-07", count: 400, pct: 32.5 },
      { month: "2025-10", count: 430, pct: 33.5 },
      { month: "2026-01", count: 460, pct: 34.0 },
      { month: "2026-04", count: 490, pct: 34.5 },
    ],
    // Q5 extra
    platform_matrix: id === 5 ? {
      rows: ["price", "quality", "delivery", "return_policy", "variety"],
      columns: ["Amazon", "AJIO", "Meesho", "Flipkart", "Offline"],
      values: [[82,45,65,30,20],[40,55,25,15,60],[35,30,20,25,10],[50,40,15,20,5],[30,60,55,25,35]],
    } : undefined,
    // Q7 extras
    radar_data: id === 7 ? [
      { factor: "Fit/Size", importance: 34, positive_pct: 15, negative_pct: 85 },
      { factor: "Price", importance: 28, positive_pct: 30, negative_pct: 70 },
      { factor: "Reviews", importance: 22, positive_pct: 40, negative_pct: 60 },
      { factor: "Styling", importance: 18, positive_pct: 55, negative_pct: 45 },
      { factor: "Occasion", importance: 12, positive_pct: 60, negative_pct: 40 },
      { factor: "Social", importance: 10, positive_pct: 35, negative_pct: 65 },
      { factor: "Brand Trust", importance: 15, positive_pct: 45, negative_pct: 55 },
      { factor: "Delivery", importance: 8, positive_pct: 50, negative_pct: 50 },
    ] : undefined,
    // Q8 extras
    word_cloud_data: id === 8 ? {
      genuine_purchase_intent: [
        { text: "planning to buy", value: 120 }, { text: "need this", value: 95 },
        { text: "saving up", value: 80 }, { text: "next paycheck", value: 65 },
        { text: "will order soon", value: 55 }, { text: "waiting for salary", value: 44 },
      ],
      bookmarking: [
        { text: "just browsing", value: 110 }, { text: "window shopping", value: 88 },
        { text: "like a Pinterest", value: 72 }, { text: "maybe someday", value: 60 },
        { text: "wishful thinking", value: 45 }, { text: "inspiration only", value: 38 },
      ],
    } : undefined,
    // Q6 extras
    sankey_data: id === 6 ? MOCK_Q6_SANKEY : undefined,
    // Q9 extras
    segment_grouped_data: id === 9 ? MOCK_Q9_GROUPED : undefined,
    // Q10 extras
    treemap_data: id === 10 ? [
      { theme: "Fit & Sizing Tools", children: [
        { name: "Better size charts", value: 1240 },
        { name: "Virtual try-on", value: 680 },
        { name: "Body type recommendations", value: 450 },
      ]},
      { theme: "Styling Assistance", children: [
        { name: "Outfit suggestions", value: 890 },
        { name: "Occasion-based styling", value: 520 },
        { name: "Mix-and-match tool", value: 310 },
      ]},
      { theme: "Price & Offers", children: [
        { name: "Price drop alerts", value: 760 },
        { name: "Personalised coupons", value: 430 },
      ]},
      { theme: "Product Info", children: [
        { name: "Accurate fabric photos", value: 640 },
        { name: "Material details", value: 380 },
      ]},
    ] : undefined,
  };
}
