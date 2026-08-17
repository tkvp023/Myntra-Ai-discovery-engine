# Dashboard UI Specification
### AI Discovery Engine — Myntra

---

## 1. Design Philosophy

| Principle | Implementation |
|---|---|
| **Dark-mode first** | Deep navy (#0f0f1a) background, light text, reduces eye strain for data-heavy views |
| **Glassmorphism** | Frosted glass cards with backdrop blur, subtle borders, depth through layering |
| **Data density** | Every pixel earns its place — no decorative filler; each element shows actionable data |
| **Progressive disclosure** | Summary → drill-down → raw quotes; users control depth |
| **Responsive but desktop-first** | Primary use on laptop/desktop; tablet-friendly; mobile as read-only |

---

## 2. Global Layout

### Navigation

```
┌────────────────────────────────────────────────────────┐
│  [Logo] AI Discovery Engine    │ Summary │ Q1-Q10 │    │
│                                │ Gaps │ Ask │           │
│                                          [Theme Toggle] │
└────────────────────────────────────────────────────────┘
```

- **Fixed top navbar** — 64px height, glassmorphism background
- **Logo** — Gradient text "AI Discovery Engine" with Myntra-pink accent
- **Nav items** — Summary, Questions (dropdown: Q1–Q10), Systemic Gaps, Ask the Data
- **Active state** — Pink underline with subtle glow
- **Mobile** — Hamburger menu, slide-in sidebar

### Page Transitions
- Pages use **fade-in + slide-up** animation (200ms ease-out)
- Charts animate in with **staggered entrance** (each chart delayed by 100ms)

---

## 3. Responsive Breakpoints

| Breakpoint | Width | Layout |
|---|---|---|
| Desktop (XL) | ≥1440px | 3-column grid for charts |
| Desktop (L) | 1024–1439px | 2-column grid for charts |
| Tablet | 768–1023px | 2-column, smaller charts |
| Mobile | <768px | Single column, stacked cards |

---

## 4. Component Specifications

### 4.1 Stat Card

```
┌──────────────────────┐
│  87,432          ↑12%│
│  Reviews Analyzed    │
│  ~~~~~~~~ (sparkline)│
└──────────────────────┘
```

| Property | Value |
|---|---|
| Width | 25% of container (4 cards per row) |
| Height | 120px |
| Background | `rgba(255,255,255,0.04)` with `backdrop-filter: blur(20px)` |
| Border | 1px solid `rgba(255,255,255,0.08)` |
| Border radius | 16px |
| Value font | Outfit, 36px, bold, white |
| Label font | Inter, 14px, `rgba(255,255,255,0.6)` |
| Trend badge | Green (↑) / Red (↓) / Gray (→), 12px, top-right corner |
| Sparkline | 40px height, stroke = accent color (gradient), no axis labels |
| Hover | Background shifts to `rgba(255,255,255,0.08)`, subtle box-shadow glow |
| Animation | Counter animate from 0 to value (1s ease-out); sparkline draws left-to-right |

### 4.2 Horizontal Bar Chart

| Property | Value |
|---|---|
| Orientation | Horizontal (`layout="vertical"` in Recharts) |
| Bar fill | Linear gradient (left to right), per-bar unique gradient from design tokens |
| Bar height | 28px with 8px gap |
| Label (left) | Category name, Inter 14px, white |
| Label (right) | Percentage + count, Inter 13px, `rgba(255,255,255,0.7)` |
| Confidence badge | Small circle (12px) next to label, color-coded: green (>0.8), yellow (0.6–0.8), red (<0.6) |
| Hover tooltip | Shows: label, exact count, percentage, avg confidence, top source |
| Animation | Bars grow from left (500ms stagger per bar, ease-out) |
| Max bars shown | 8 (with "Show more" expand button for overflow) |

### 4.3 Donut Chart

| Property | Value |
|---|---|
| Size | 280px × 280px |
| Inner radius | 60% (donut hole) |
| Outer radius | 100% |
| Center text | Total count + "total" label |
| Segment colors | From design token palette |
| Segment hover | Segment expands by 5px, tooltip shows label + count + pct |
| Legend | Right-aligned, vertical, with color dots + label + pct |
| Animation | Segments animate clockwise from 0° (800ms ease-in-out) |

### 4.4 Radar Chart

| Property | Value |
|---|---|
| Size | 320px × 320px |
| Axes | 6–8 axes (one per factor) |
| Fill | Semi-transparent gradient (0.3 opacity) |
| Stroke | 2px solid accent color |
| Axis labels | Inter 12px, white, positioned outside |
| Dots | 6px circles at each data point |
| Hover | Dot enlarges to 10px, tooltip shows factor name + value |
| Grid | Concentric polygons at 25%, 50%, 75%, 100% — very subtle (0.1 opacity) |

### 4.5 Heatmap

| Property | Value |
|---|---|
| Cell size | Auto-fit to container, minimum 48px × 36px |
| Color scale | Sequential: `#1a1a2e` (low) → `#a855f7` (medium) → `#ff3f6c` (high) |
| Cell label | Count value, Inter 12px, auto-contrast (white on dark, dark on light) |
| Row/column labels | Inter 13px, `rgba(255,255,255,0.7)` |
| Hover | Cell border highlights (2px white), tooltip shows row + column + value |
| Legend | Horizontal gradient bar below chart with min/max labels |

### 4.6 Sankey Diagram

| Property | Value |
|---|---|
| Node width | 20px |
| Node colors | Per-category from design tokens |
| Link opacity | 0.3 default, 0.7 on hover |
| Link color | Gradient from source node color to target node color |
| Labels | Node labels positioned to the left/right, Inter 13px |
| Hover | Highlight the hovered flow path; dim all other paths |
| Interaction | Click a node to filter — shows only that node's connections |

### 4.7 Word Cloud

| Property | Value |
|---|---|
| Container | Full-width card, 300px height |
| Font | Outfit |
| Size range | 14px (min) to 64px (max) |
| Colors | Rotating through accent palette |
| Rotation | 0° and 90° only (no diagonal — cleaner look) |
| Hover | Word highlights with glow, tooltip shows exact count |
| Click | Filters the page to show quotes containing that word |

### 4.8 Quote Card

```
┌─────────────────────────────────────────┐
│  "Size chart is so confusing, I ordered │
│   M and it fits like XL..."            │
│                                         │
│  [Play Store] [Gen-Z] [Conf: 0.92]     │
│  Mar 15, 2026                           │
└─────────────────────────────────────────┘
```

| Property | Value |
|---|---|
| Background | `rgba(255,255,255,0.03)` |
| Border-left | 3px solid, color matches the tag/category |
| Quote text | Inter 14px, `rgba(255,255,255,0.85)`, italic |
| Max lines | 3 lines collapsed; expandable on click ("Read more") |
| Source badge | Pill shape, 10px font, colored per source |
| Segment badge | Pill shape, 10px font, muted color |
| Confidence | Small circular gauge, 20px diameter |
| Hover | Slight lift (translateY -2px) + shadow increase |

### 4.9 Segment Toggle

```
[Gen-Z ●] [Millennial ○] [Gen-X ○] [All ●]
```

| Property | Value |
|---|---|
| Style | Pill-shaped toggle group (like iOS segmented control) |
| Active state | Filled with gradient background, white text |
| Inactive state | Transparent, muted text |
| Transition | Background slides between options (200ms ease) |
| Position | Top-right of each question section card |
| Behavior | Toggles all charts in that section simultaneously |

### 4.10 Chat Interface (RAG)

```
┌─────────────────────────────────────────┐
│  Suggested: [Sizing issues?]            │
│             [Gen-Z behavior?]           │
│             [Price vs quality?]         │
├─────────────────────────────────────────┤
│                                         │
│      [User bubble — right aligned]      │
│                                         │
│  [AI bubble — left aligned]             │
│  • Bullet point answer                  │
│  • With citations [Reddit, 0.89]        │
│                                         │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────┐        │
│  │ Type a question...    [Send]│        │
│  └─────────────────────────────┘        │
│  Filters: [Segment ▼] [Source ▼]        │
└─────────────────────────────────────────┘
```

| Property | Value |
|---|---|
| User bubble | Right-aligned, gradient background (pink→orange), white text, 14px |
| AI bubble | Left-aligned, glass background, white text, 14px, supports markdown |
| Citation badges | Inline pills with source name + confidence, clickable |
| Input field | Full-width, glass background, 16px, placeholder text |
| Send button | Gradient icon button, pulse animation while generating |
| Suggested queries | Clickable chips above chat area, muted glass background |
| Loading state | Typing indicator (3 bouncing dots) in AI bubble |
| Filter dropdowns | Below input field, glass select elements |

---

## 5. Component States

Every component must handle these states:

| State | Visual |
|---|---|
| **Loading** | Skeleton shimmer animation (gray gradient pulse) matching component shape |
| **Empty** | Muted icon + "No data available" text, centered |
| **Error** | Red-tinted card border + error message + "Retry" button |
| **Loaded** | Full render with entrance animation |
| **Hover** | Defined per component above |
| **Active/Selected** | Defined per component above |

---

## 6. Animation Timing

| Animation | Duration | Easing | Trigger |
|---|---|---|---|
| Page transition | 200ms | ease-out | Route change |
| Card entrance | 300ms | ease-out | Page load (staggered 100ms per card) |
| Chart draw | 500–800ms | ease-in-out | Card enters viewport (Intersection Observer) |
| Counter animate | 1000ms | ease-out | Stat card enters viewport |
| Hover effects | 150ms | ease | Mouse enter/leave |
| Filter change | 300ms | ease-in-out | Segment toggle / filter dropdown |
| Tooltip appear | 100ms | ease | Mouse enter |
| Tooltip disappear | 200ms | ease | Mouse leave |

---

## 7. Accessibility

| Requirement | Implementation |
|---|---|
| Color contrast | All text meets WCAG AA (4.5:1 ratio minimum) |
| Keyboard nav | All interactive elements focusable via Tab; charts navigable via arrow keys |
| Screen reader | Charts include `aria-label` with text summary of data |
| Reduced motion | Respect `prefers-reduced-motion` — disable animations |
| Focus indicators | Visible focus ring (2px solid accent color) on all interactive elements |

---

## 8. Performance Targets

| Metric | Target |
|---|---|
| First Contentful Paint | < 1.2s |
| Largest Contentful Paint | < 2.0s |
| Total Bundle Size | < 500KB (gzipped) |
| Chart render time | < 200ms per chart |
| Image optimization | Next.js `<Image>` with WebP format |
| Code splitting | Per-page chunks; chart libraries lazy-loaded |
