# Test Coverage Analysis

## Current State

**The project has zero test infrastructure.** There are no test files, no test
runners, no CI/CD pipelines, and no assertion libraries. The codebase is pure
static HTML/CSS/JS with no build system or package manager.

---

## Testable Surface Area

### 1. JavaScript Logic -- `yard-game/js/main.js` (341 lines)

This is the largest concentration of testable behavior. It contains nine
distinct modules inside a single IIFE:

| Module | Lines | Complexity | Priority |
|--------|-------|------------|----------|
| Cart System | 204-301 | High | **Critical** |
| Counter Animation | 50-102 | Medium | High |
| Mobile Navigation | 146-168 | Low | Medium |
| Accordion | 170-191 | Low | Medium |
| Scroll Reveal | 11-46 | Medium | Medium |
| Sticky Nav | 104-123 | Low | Low |
| Hero Parallax | 125-144 | Low | Low |
| Product Gallery | 303-320 | Low | Low |
| Announcement Bar | 322-338 | Low | Low |

### 2. JavaScript Logic -- `index.html` (lines 667-699)

Inline script with three features:

| Module | Lines | Complexity | Priority |
|--------|-------|------------|----------|
| Dark Mode Toggle | 668-681 | Medium | High |
| Scroll Reveal | 683-692 | Low | Low |
| Nav Scroll | 694-698 | Low | Low |

### 3. HTML Pages (14 files)

Structural and content concerns across `index.html`, `yard-game/index.html`,
and 12 sub-pages under `yard-game/pages/` and `yard-game/research/`.

### 4. CSS -- `yard-game/css/styles.css` (~1000+ lines)

Design system with custom properties, responsive breakpoints, glass morphism,
and dark-theme variables.

---

## Recommended Test Improvements (by priority)

### Priority 1 -- Cart System (unit tests)

**Why:** The cart handles money and state. Bugs here directly affect the user
experience and could produce incorrect totals.

**What to test:**
- `getCart()` returns `[]` when localStorage is empty or contains invalid JSON
- `saveCart(cart)` round-trips through `JSON.parse(localStorage.getItem(...))`
- `addToCart(name, price)` creates a new item with `qty: 1`
- `addToCart` increments `qty` when the same product name already exists
- `renderCart()` computes correct `total` (price * qty, summed across items)
- `renderCart()` shows empty-state markup when cart is `[]`
- Remove button splices the correct index and re-renders
- Cart count badges update to the sum of all `qty` values

**Suggested approach:** Extract the pure cart functions (`getCart`, `saveCart`,
`addToCart` logic) into a separate module or make them testable by refactoring
the IIFE. Use a lightweight runner like Vitest or plain Node with
`node:test` + `jsdom` for DOM simulation.

---

### Priority 2 -- Dark Mode Toggle (unit tests)

**Why:** Theme persistence via localStorage is a core UX feature across both
sites. A broken toggle leaves users stuck in the wrong theme.

**What to test:**
- `toggleTheme()` flips `data-theme` from `light` to `dark` and vice versa
- Toggled value is written to `localStorage.setItem('theme', ...)`
- On page load, saved preference is restored from localStorage
- Falls back to `prefers-color-scheme` media query when no saved preference
- Theme icon text content updates correctly (sun vs. moon)

---

### Priority 3 -- Counter Animation Math (unit tests)

**Why:** The easing function (`1 - Math.pow(1 - progress, 3)`) and the
progress calculation (`Math.min(elapsed / duration, 1)`) are pure math that
are trivial to test but easy to break during refactoring.

**What to test:**
- `progress` clamps to 1 when `elapsed >= duration`
- Eased value is 0 at progress=0 and 1 at progress=1
- `Math.round(eased * target)` produces the correct integer at boundaries
- Prefix and suffix attributes are concatenated correctly
- Reduced-motion path skips animation and sets final value immediately

---

### Priority 4 -- Link Integrity and HTML Validation (integration/CI tests)

**Why:** With 14 HTML files cross-linking each other and referencing external
assets, broken links and invalid markup are a real risk on every change.

**What to test:**
- All internal `href` values resolve to existing files
- No broken anchor links (`#section-id` targets exist on the page)
- External URLs return 2xx (or at least not 404)
- All `<img>` tags have non-empty `alt` attributes
- HTML validates (no unclosed tags, duplicate IDs, etc.)

**Suggested approach:** Use `htmlhint` or `html-validate` for static
validation, and a link checker like `lychee` or `broken-link-checker` in CI.

---

### Priority 5 -- Accessibility (automated a11y scans)

**Why:** The sites use custom interactive elements (accordion, mobile drawer,
cart drawer, theme toggle) that need proper ARIA attributes and keyboard
support.

**What to test:**
- Color contrast ratios meet WCAG AA (especially the dark glow theme in
  yard-game, which uses cyan on dark backgrounds)
- All interactive elements are keyboard-reachable (tab order)
- `aria-label` is present on icon-only buttons (cart, close, hamburger)
- Heading hierarchy is sequential (no skipped levels)
- Focus is trapped inside the mobile nav and cart drawers when open
- `prefers-reduced-motion` disables all animations (already implemented in
  JS, but not verified)

**Suggested approach:** Run `axe-core` via `@axe-core/cli` or integrate
`pa11y` into CI. Both can scan static HTML files without a running server.

---

### Priority 6 -- Responsive Layout (visual regression)

**Why:** Both sites have responsive breakpoints (768px in the main site,
multiple breakpoints in yard-game). Layout regressions are invisible without
visual testing.

**What to test:**
- Pages render correctly at 375px (mobile), 768px (tablet), 1280px (desktop)
- Mobile navigation drawer appears/disappears at the correct breakpoint
- Grid layouts collapse to single column on mobile
- No horizontal overflow at any viewport width

**Suggested approach:** Use Playwright's screenshot comparison or Percy for
visual regression. A lightweight alternative is BackstopJS.

---

### Priority 7 -- Mobile Navigation and Drawers (integration tests)

**Why:** The open/close logic manipulates `document.body.style.overflow` and
multiple class toggles. A bug locks the user out of scrolling.

**What to test:**
- Hamburger click opens the mobile nav (`.open` class added)
- Overlay click closes the mobile nav
- Close button click closes the mobile nav
- `body.style.overflow` is set to `'hidden'` when open and `''` when closed
- Same tests for the cart drawer (open/close/overlay)

---

## Recommended Tooling

Given that this is a **zero-dependency static site**, the testing stack should
be minimal and not introduce a heavy build system:

| Tool | Purpose | Why |
|------|---------|-----|
| `vitest` + `jsdom` | Unit tests for JS | Fast, ESM-native, built-in DOM env |
| `@axe-core/cli` | Accessibility scans | No server needed, runs on HTML files |
| `html-validate` | HTML validation | Static analysis, no browser needed |
| `lychee` | Link checking | Fast Rust-based checker, CI-friendly |
| `playwright` | E2E + visual regression | Screenshots, interaction tests |

A minimal `package.json` with these dev dependencies and a GitHub Actions
workflow would cover priorities 1-7 without changing the static-site
architecture.

---

## Suggested First Steps

1. **Add `package.json`** with `vitest` and `jsdom` as dev dependencies
2. **Refactor `main.js`** to export cart functions for testability (or use
   dynamic import in tests)
3. **Write cart unit tests** -- highest value, lowest effort
4. **Add a GitHub Actions workflow** that runs the tests on every push
5. **Add `html-validate`** to the workflow for HTML linting
6. **Add `axe-core`** scans to catch accessibility regressions
