# Phase 12 — Design System & Component Consistency

**Objective**: Specification of the unified design system tokens, typography, component standards, and scrollbar theme.

---

## 1. Design Tokens & Theme Variables

```css
:root {
    --bg-base: #080D18;
    --bg-sidebar: #0D1424;
    --bg-surface: #111A2C;
    --bg-card: #152036;
    --bg-card-hover: #1A2742;
    --bg-input: #0A101E;
    
    --border-color: #1E293B;
    --border-light: #2A3854;
    --border-focus: #3B82F6;
    
    --primary: #3B82F6;
    --primary-hover: #2563EB;
    --success: #10B981;
    --purple: #8B5CF6;
    --warning: #F59E0B;
    --danger: #EF4444;
    
    --font-sans: 'Inter', 'Noto Sans Thai', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --radius-full: 9999px;
}
```

---

## 2. Component Guidelines

- **Typography**: English uses `Inter`, Thai uses `Noto Sans Thai`. Clear scale from `h1` (2rem/700) down to metadata (0.75rem/500).
- **Buttons & Inputs**: Minimum 44px touch height on mobile; clean focus rings with `--border-focus`.
- **Tables**: Contained in `.table-responsive` with horizontal scroll capability, avoiding any global page overflow.
- **Scrollbars**: Centralized dark theme styling matching `--border-light` and `--bg-base` across body, sidebar, drawers, and modal containers.
- **Drawers & Modals**: Right slide-out drawer on desktop, 100% full-width modal drawer on mobile viewports.
