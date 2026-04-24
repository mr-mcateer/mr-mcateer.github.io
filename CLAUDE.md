# Project: Prompt AI Solutions
# Owner: Andrew McAteer
# Domain: promptaisolutions.com

## About
AI consulting and scaled communication campaigns. AI as an invisible tool
that amplifies your reach -- not a gimmick.

## Security Rules
- NEVER hardcode API keys in scripts, commands, or chat output.
- ALL secrets live in `.env` and are loaded via env_loader (see education repo).

## Code Style
- No em-dashes in any generated content (use `--` or `|`).
- No emojis unless explicitly requested.
- Pure static HTML/CSS/JS -- no build system, no framework.
- Dark mode support via `data-theme="dark"` attribute.
- Font: Inter (body). Do not introduce Playfair Display in new additions.
- Keep pages under 2000 lines.

## Project Structure
```
CNAME                           # promptaisolutions.com
index.html                      # Solutions landing page
yard-game/                      # Frisbeam GTM pitch
stock-analysis/                 # Portfolio intelligence dashboard (live, auto-refreshed)
img/                            # Site images
.claude/                        # Claude Code config (settings.json, agents/)
.gitignore                      # Prevents .env from being committed
```

## Related Repos
- Education site: github.com/mr-mcateer/prompt-ai-education (promptaieducation.com)

---

## Stock Analysis Dashboard (stock-analysis/index.html)

Live portfolio intelligence artifact. Updated autonomously by the
`stock-analysis-refresh` scheduled task (weekdays 07:33 + 11:33 PT --
morning settle and pre-close-prep slots, both inside RTH and clear of the
3-4pm ET 0DTE reversal window per Options Intelligence Upgrade M1).
Schedule retimed 2026-04-23 from the prior 05:30 + 13:30 PT slots when the
auto-emailer was removed. Public URL:
https://promptaisolutions.com/stock-analysis/

**Portfolio universes:**
- Research / BLUF / conviction scoring (9 tickers): MU, META, NVDA, MSFT,
  AMZN, GOOG, AAPL, TSLA, BROS.
- Options desk (24 tickers, short-duration put-selling per client directive
  2026-04-20): the core 9 + AVGO + OKLO + defense primes (LMT, RTX, NOC,
  GD, PLTR) + addictive-product moats (PM, MO, STZ, SBUX, NFLX) + payment
  rails (V, MA, INTU). Spine: 7-14 DTE, 0.15-0.25 delta, OI >= 500,
  spread <= 5%, puts-primary, covered calls collapsed. As of v3.3
  (2026-04-24), covered calls ARE rendered on the public dashboard as a
  compact 26-45d x 3 strike bucket block on the right of each row, framed
  "if you own the shares" (position-agnostic). The block is visually
  subordinate to the 12-cell put grid per the "collapsed" directive.
  Gamma-wall warning banner required on dashboard. See
  `~/.claude/scheduled-tasks/stock-analysis-refresh/DESIGN_BRIEF.md` and
  `docs/options-compendium.md` for the full rationale.

The auto-emailer was removed 2026-04-23. The dashboard is now the only output
surface; no Gmail drafts are created. See
`stock-analysis/SECRETARY_VISION.md` for the broader "god-like secretary"
reframe currently in design.

### Pipeline architecture (v2.4, post-emailer-removal)

Lives at `~/.claude/scheduled-tasks/stock-analysis-refresh/` (NOT in this
repo). Model: Opus 4.7 1M (via project `.claude/settings.json`). 9-step
pipeline with 2 invariants:

1. **Orchestrator-first retry is the PRIMARY path for `tool_unavailable`.**
   When sub-agent dispatch tier fails to provision WebSearch (observed on
   2026-04-18, affected 10 of 11 agents in one run), the orchestrator
   executes WebSearch directly. Do NOT retry via another sub-agent first --
   the dispatch is the unreliable layer. This is the single most important
   lesson from production validation.

2. **Programmatic renderers, not hand-edits, are the only write path for
   dynamic sections.** Canonical JSON input (`logs/*.json`) is the single
   source of truth. Hand-editing HTML between `<!-- X_SECTION_START -->` and
   `<!-- X_SECTION_END -->` markers will cause drift and is forbidden.

### Pipeline steps (v3.3, 2026-04-24; pure Python, no sub-agent fanout)
```
STEP 0  safety gates (weekday / network / circuit breaker)
STEP 1  quote_feed.py -- yfinance grounded prices for 24-ticker universe
          (hard gate: need 17/24 = 0.7 coverage)
STEP 2  options_chain.py -- CBOE chain + appends 3 history JSONLs
          (iv_history, premium_history, skew_term_history)
STEP 3  compute_events.py -- earnings + macro window filter
STEP 4  compute_vrp_regime.py -- SPX IV vs realized vol + per-symbol VRP
STEP 5  options_candidates.py v2 -- picks writable CSPs + covered calls
          with premium-vs-median, skew, term-structure stamps
STEP 6  TWO renderers in sequence (both idempotent, marker-managed):
          6a. render_context_strip.py  (VRP chip + 14-day earnings/macro calendar)
          6b. render_premium_grid.py   (24-row table: put grid 4x3 + covered-call
                                        block 1x3 + per-row IV-RV chip +
                                        per-cell rich/cheap-vs-90d-median chip)
STEP 7  integrity gate (div 200-600 post-v3.3, close delta <=2, run_id
          consistency across canonical JSONs)
STEP 8  deploy (stash / rebase / push; never force)
STEP 9  audit manifest + circuit breaker maintenance
```

### Python toolkit (stdlib-only except yfinance)
`~/.claude/scheduled-tasks/stock-analysis-refresh/tools/`:

**Data acquisition + scoring:**
- `quote_feed.py` -- yfinance grounded prices (authoritative, hard gate 7/9)
- `options_chain.py` -- CBOE delayed-quotes option chain fetcher (stdlib only,
  no auth, 15-minute delay). Appends ATM 30-day IV to `iv_history.jsonl` so
  a true 52-week IV rank can be computed after ~20 sessions.
- `options_candidates.py` -- picks the single best cash-secured-put and
  covered-call candidate per ticker using the disciplined-seller spine
  (7-14 day expiry, 0.15-0.25 delta, OI >= 500, spread <= 5%; per the
  2026-04-20 client directive). Output is flagged `public_safe: true`.
- `wsb_scan.py` -- Reddit heat + sentiment, case-sensitive ticker match
- `outcome_ledger.py` -- append / settle / stats on the calibration JSONL
- `catalyst_score.py` -- tier x recency scoring, 1.5 min-score gate
- `classify_and_retry.py` -- sub-agent failure classifier + adapted
  retry-prompt generator

**Deterministic renderers (canonical JSON in, HTML/text out):**

*Active on the daily pipeline (v3.3):*
- `render_context_strip.py` -- `logs/vrp_regime.json` + `logs/known_events.json`
  -> SPX VRP chip (band + size multiplier + verdict) and 14-day earnings +
     high/medium macro calendar pills
     (between `<!-- CONTEXT_STRIP_{START,END} -->`)
- `render_premium_grid.py` -- `logs/options_chain.json` + `logs/known_events.json`
    + `logs/vrp_regime.json` + `tools/compute_premium_stats` (reads
    `logs/premium_history.jsonl`)
  -> 24-row put grid (4 DTE windows x 3 strike buckets = 12 cells/row) + a
     covered-call block on the right (26-45d x 3 strike buckets = 3 cells/row).
     Per-row IV-RV chip from `vrp_regime.per_symbol`. Per-cell rich/cheap/hist
     chip vs that bucket's own 90-day median via
     `compute_premium_stats.classify_premium`. Amber cell border = expiration
     spans an earnings or high-severity macro event.
     (between `<!-- PREMIUM_GRID_{START,END} -->`)

*Retired from the daily pipeline; kept on disk for the planned weekly companion:*
- `render_bluf_grid.py`, `render_portfolio_matrix.py`, `render_deep_dive.py`,
  `render_macro_context.py`, `render_geopolitical.py`, `render_options_ladder.py`,
  `render_regime_tile.py`, `render_options_desk.py`, `render_holdings_strip.py`,
  `sync_heatmap_dividers.py`. These populate per-ticker pages and research
  archives when `stock-analysis-weekly/` ships; they do not run on the daily
  twice-a-day refresh.

**Removed 2026-04-23**: `render_email.py`, `render_email_brief.py`,
`email_decide.py`, `email_state.py`, plus the canonical JSONs
`email_input.json`, `email_brief_input.json`, `communicated_state.json`,
and all `email_decision_{run_id}.json` audit files. The auto-emailer is gone;
the dashboard is the only output surface.

**Removed 2026-04-19**: `render_scenarios.py` and the Interactive Scenario
Planner section. Macro scenario probabilities change quarterly (when Goldman,
JPM, Morgan Stanley publish new outlooks), not on a twice-daily cadence. The
rendered section looked programmatic but its canonical JSON was a static
snapshot not regenerated by the orchestrator -- creating false confidence of
freshness. The Vetted Geopolitical Scenarios card + BLUF grid Bears column
cover the same territory with actually-live data.

All renderers are idempotent: identical input -> byte-identical output -> `status=unchanged`.
All renderers report a `render_hash` for audit. Content between markers is machine-written
only; hand-edits there are forbidden and will be overwritten on the next run.

### Agent defs (purpose-built, pinned `tools:` allowlist)
`~/.claude/agents/`:
- `market-snapshot.md` -- Opus, WebSearch only
- `ticker-research-batch.md` -- Opus, WebSearch + Bash + Read
- `catalyst-scanner.md` -- Opus, WebSearch only
- `wsb-scanner.md` -- Opus, Bash + Read
- `geopolitical-fetcher.md` -- **HAIKU**, WebSearch only, strict tier-1
  whitelist baked in (Reuters / Bloomberg / WSJ / FT / AP / BBC /
  Economist / Nikkei / .gov / CSIS / CFR / Brookings / Chatham House /
  Atlantic Council / IISS / RAND / PIIE / ECB)

### Canonical JSON inputs (single source of truth)
`~/.claude/scheduled-tasks/stock-analysis-refresh/logs/`:
- `options_chain.json` -- CBOE-sourced raw option chain, feeds
  `render_premium_grid.py` directly (public market data)
- `vrp_regime.json` -- SPX VRP band, size multiplier, verdict, per-symbol
  IV-RV. Feeds `render_context_strip.py` (top chip) and
  `render_premium_grid.py` (per-row IV-RV chip).
- `known_events.json` -- hand-curated earnings + macro calendar (schema uses
  `macro_calendar` with `severity` in {high, medium, low}). Feeds both daily
  renderers. Update manually when new earnings dates or macro events are
  confirmed; the v3.3 grid flags FOMC/CPI/NFP on the cells correctly via
  `macro_calendar` (the pre-v3.3 `macro` key was silently empty).
- `premium_history.jsonl` -- per-bucket premium samples, one row per
  (symbol, type, delta_bucket, dte_bucket) per cycle. Appended by
  `options_chain.py`. Read by `compute_premium_stats` for the rich/cheap
  chip. Need ~15 samples per bucket before the chip stops saying
  "hist N/15"; expect ripening ~15 trading days after first sample.
- `skew_term_history.jsonl` -- per-symbol skew (25d put-call IV diff) and
  term (front/back ATM IV ratio) samples per cycle. Appended by
  `options_chain.py`; classified by `compute_premium_stats`.
- `iv_history.jsonl` -- rolling ATM-30d IV history per symbol (public market data)
- `options_candidates.json` -- picker output v2 (CSP + covered call per
  ticker with `premium_vs_median`, `skew_flag`, `term_flag`). Consumed by
  the audit manifest; its direct render has been retired (the grid reads
  the chain directly).
- `geopolitical_scenarios.json` -- weekly-companion input; not touched by
  the daily pipeline.
- `watchlist_criteria.json` -- STUB. Mike's screening mandate for new-name
  opportunity surfacing. Scanner disabled until user populates hard_filters.
- `positions.json` -- **PRIVATE**, holdings + cash + open short options. Lives
  in `~/.claude/...` only. Never committed to this repo. Currently unread by
  any active tool (the email renderer that previously consumed it was removed
  2026-04-23). Reserved for future assignment-watch tooling.
- `{run_id}.json` -- audit manifest per run (retain 60)

### Public / private split (enforced across renderers)
- **Public** site output must never contain: share counts, cash balances, cost
  basis, assignment events, personalized recommendations, or anything that
  names the reader or says "you should". The auto-emailer that was the only
  consumer of private data has been removed; positions.json is currently
  read by no tool.
- **Public renderers** (`render_context_strip.py`, `render_premium_grid.py`
  on the daily pipeline; the retired-to-weekly set also) read ONLY public-safe
  canonical JSONs and never import from `positions.json`. The covered-call
  block shown in the grid is framed "if you own the shares" precisely so the
  public surface stays position-agnostic; it is a menu, not a call to action.
- **Future personalization tooling** (assignment watch, per-lot CC sizing) must
  live in a separate private tool with its own canonical JSON, never consumed
  by the public dashboard renderers.

### Dashboard render markers (all machine-written, NEVER hand-edit)

*Active on the daily v3.3 pipeline:*
```
<!-- CONTEXT_STRIP_START -->   ...render_context_strip.py...  <!-- CONTEXT_STRIP_END -->
<!-- PREMIUM_GRID_START -->    ...render_premium_grid.py...   <!-- PREMIUM_GRID_END -->
```

*Reserved for the planned weekly companion pipeline; NOT rendered daily:*
```
<!-- BLUF_GRID_START -->         ...render_bluf_grid.py...        <!-- BLUF_GRID_END -->
<!-- PORTFOLIO_MATRIX_START -->  ...render_portfolio_matrix.py... <!-- PORTFOLIO_MATRIX_END -->
<!-- BLUF_{MU,META,NVDA,MSFT,AMZN,GOOG,AAPL,TSLA,BROS}_START/END -->
<!-- MACRO_CONTEXT_START -->     ...render_macro_context.py...    <!-- MACRO_CONTEXT_END -->
<!-- GEO_SECTION_START -->       ...render_geopolitical.py...     <!-- GEO_SECTION_END -->
<!-- OPTIONS_SECTION_START -->   ...render_options_ladder.py...   <!-- OPTIONS_SECTION_END -->
```
Any manual edit between these markers will be overwritten on the next autonomous run.
Add fresh data to the canonical JSON in `~/.claude/scheduled-tasks/stock-analysis-refresh/logs/` instead.

### Lessons from production validation (2026-04-18)
1. **Sub-agent tool provisioning is non-deterministic.** Same agent type
   can receive WebSearch in one dispatch and not in the next. The
   orchestrator-first retry pattern is load-bearing, not a nice-to-have.
2. **Purpose-built agent defs with explicit `tools:` frontmatter solve
   the provisioning lottery** on session start. Session must restart for
   new agent defs to hot-load.
3. **Grounded price feed (yfinance) caught stale WebSearch-derived
   prices on BROS (+5.6%) that would otherwise have published.** The
   hard gate (9/9 prices required) is essential.
4. **Strict tier-1 source whitelist drops topics that look researched
   but aren't.** Russia-Ukraine was dropped from one run for having only
   1 tier-1 source. The 2-tier-1 gate is strict by design.
5. **Contradiction detection is a first-class output**, not a footnote.
   The aggregator surfaces source-level disagreement (e.g. Iran Hormuz:
   WaPo said open, Bloomberg said blockade holds, reality turned out
   closed). Users need to see the disagreement itself.
6. **Programmatic renderers eliminate the "did I update all 27 surfaces"
   drift problem.** Canonical JSON + deterministic render is cheaper
   than 27 Edit-tool calls and always consistent.
7. **The auto-emailer was retired 2026-04-23.** The dashboard alone is the
   public artifact. Lessons learned about plain-English summarization,
   tier-grouped holdings (Strongest / Solid / Risk Watch), company-name-first
   formatting, and acronym annotation carry forward into how dashboard cards
   are written.

### Commit message convention
Autonomous refresh runs use:
`Auto-refresh run_id=YYYYMMDDTHHMMSS -- <short headline>`
followed by a body enumerating material conviction deltas, source
counts, any retries engaged, and dropped scenarios.

### Do NOT
- Hand-edit between `<!-- X_SECTION_START --> / <!-- X_SECTION_END -->` markers.
- Push without stash / rebase first (repo has unrelated WIP in other dirs).
- Force-push ever.
- Skip hooks (--no-verify).
- Fabricate analyst counts, PT ranges, or source citations.
- Publish a scenario with fewer than 2 tier-1 sources.
- Resurrect the auto-emailer without explicit user direction (removed 2026-04-23).
- Add "buy" / "sell" / "act on this" / tier / rank prose to the premium grid
  or context strip. The rich/cheap-vs-median chip and cell tints are the only
  passive whispers; everything else must stay data, not prescription.
- Re-enable the "Per-ticker", "Geopolitics", or "Tariffs" nav tabs until the
  `stock-analysis-weekly/` companion pipeline ships. Stale research links are
  worse than missing links.
