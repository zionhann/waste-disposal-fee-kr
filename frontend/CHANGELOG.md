# Changelog

## 2026-02-03

### style(ui): beautify frontend with seamless minimal design system

- `frontend/src/index.css`: Introduce CSS custom properties design system
  - Color palette (primary, semantic, neutral scale)
  - Typography scale and spacing tokens
  - Shadow, radius, and transition variables
  - Korean-optimized font stack
  - Global keyframe animations (slideIn, fadeIn, pulse, shimmer)
- `frontend/src/App.css`: Rewrite component styles with modern polish
  - Replace borders with soft multi-layer shadows for depth
  - Add gradient search button with hover-lift micro-interaction
  - Redesign result cards with elevated shadows and staggered slideIn animations
  - Refine badges (similarity, category) to pill-shaped with full border-radius
  - Add focus rings (blue glow) for keyboard accessibility on inputs and selects
  - Add empty-state and loading-spinner utility styles
  - Responsive breakpoints for mobile (≤640px)
- `frontend/src/App.tsx`: Minimal markup additions for enhanced UX
  - Add `hasSearched` state to gate empty-state rendering
  - Render empty-state message when a search returns zero results
  - Change error element from `<p>` to `<div>` to match new error-container styling
- `frontend/index.html`: Update page title to "대형폐기물 품목 검색"
