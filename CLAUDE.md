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
`stock-analysis-refresh` scheduled task (weekdays 05:30 + 13:30 PT --
afternoon slot moved out of the 3-4pm ET 0DTE reversal window per Options
Intelligence Upgrade M1). Public URL:
https://promptaisolutions.com/stock-analysis/

**Portfolio universes:**
- Research / BLUF / conviction scoring (9 tickers): MU, META, NVDA, MSFT,
  AMZN, GOOG, AAPL, TSLA, BROS.
- Options desk (24 tickers, short-duration put-selling per client directive
  2026-04-20): the core 9 + AVGO + OKLO + defense primes (LMT, RTX, NOC,
  GD, PLTR) + addictive-product moats (PM, MO, STZ, SBUX, NFLX) + payment
  rails (V, MA, INTU). Spine: 7-14 DTE, 0.15-0.25 delta, OI >= 500,
  spread <= 5%, puts-primary, covered calls collapsed. Gamma-wall warning
  banner required on dashboard. See
  `~/.claude/scheduled-tasks/stock-analysis-refresh/DESIGN_BRIEF.md` and
  `docs/options-compendium.md` for the full rationale.

Recipient of the BLUF email is Mike McAteer at `m-mcateer@hotmail.com`.

### Pipeline architecture (v2.3, validated end-to-end 2026-04-18)

Lives at `~/.claude/scheduled-tasks/stock-analysis-refresh/` (NOT in this
repo). Model: Opus 4.7 1M (via project `.claude/settings.json`). 10-step
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

### Pipeline steps
```
STEP 0  safety gates (weekday / network / circuit breaker)
STEP 1a settle prior-run calibration ledger (outcome_ledger.py settle)
STEP 1b GROUNDED quote_feed via yfinance (hard gate: need 7/9)
STEP 1c parallel fanout (5 purpose-built agents, hot-loaded at session start):
          - market-snapshot           (Opus, WebSearch)
          - ticker-research-batch     (Opus, WebSearch; 1 agent, 9 tickers)
          - catalyst-scanner          (Opus, WebSearch)
          - wsb-scanner               (Opus, Bash -> wsb_scan.py)
          - geopolitical-fetcher x N  (HAIKU, WebSearch; 1 per topic,
                                       6 standard topics + orchestrator-
                                       selected emerging)
STEP 1d classify failures + orchestrator-first retry (parent WebSearch
          for tool_unavailable, sub-agent retry for silent_laziness)
STEP 2  data quality gate (7/9 tickers complete required)
STEP 3  conviction calculation (deterministic):
          conv = round(buy_pct*50 + max(upside_high,0)*30 + coverage*20)
STEP 4  catalyst scoring (tier x recency decay; 36h half-life)
STEP 5  append calibration entries (outcome_ledger.py append)
STEP 6  HTML edits (where deltas warrant) + canonical JSON writes +
          programmatic renders (render_geopolitical.py, future BLUF/heatmap)
STEP 7  integrity gate (div 340-380, evi == 18, close delta <=2, run_id consistency across all canonical JSONs)
STEP 8   deploy (stash / rebase / push; never force)
STEP 8.5 email decision gate (email_decide.py): compute materiality
          from deltas vs communicated_state.json; return skip / brief / full
STEP 9   email assembly, routed by 8.5:
          skip  -> no draft, commit ledger with consecutive_skips++
          brief -> write email_brief_input.json, run render_email_brief.py
          full  -> write email_input.json, run render_email.py
          Then Gmail MCP create_draft + email_state.py commit
STEP 10  audit manifest + circuit breaker maintenance
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
  (25-50 day expiry, 0.20-0.35 delta, OI >= 250, tight spreads). Output is
  flagged `public_safe: true`.
- `wsb_scan.py` -- Reddit heat + sentiment, case-sensitive ticker match
- `outcome_ledger.py` -- append / settle / stats on the calibration JSONL
- `catalyst_score.py` -- tier x recency scoring, 1.5 min-score gate
- `classify_and_retry.py` -- sub-agent failure classifier + adapted
  retry-prompt generator

**Deterministic renderers (canonical JSON in, HTML/text out):**
- `render_bluf_grid.py` -- `logs/tickers.json`
  -> 9-card BLUF grid with 4-column evidence strip (analyst count, PT range,
     conviction, bears refuted) (between `<!-- BLUF_GRID_{START,END} -->`)
- `render_portfolio_matrix.py` -- `logs/tickers.json`
  -> Portfolio Matrix comparison table, 9 rows sorted by upside DESC
     (between `<!-- PORTFOLIO_MATRIX_{START,END} -->`)
- `render_deep_dive.py` -- `logs/tickers.json`
  -> Per-ticker deep-dive BLUF cards (9 sections, marker-delimited per ticker:
     `<!-- BLUF_MU_{START,END} -->`, `<!-- BLUF_META_{START,END} -->`, etc.)
- `render_macro_context.py` -- `logs/macro_context.json`
  -> 8-tile risk strip + near-term catalysts + bigger-picture + tariff-exposure table
     (between `<!-- MACRO_CONTEXT_{START,END} -->`)
- `render_geopolitical.py` -- `logs/geopolitical_scenarios.json`
  -> Vetted Geopolitical Scenarios card (between `<!-- GEO_SECTION_{START,END} -->`)
- `render_options_ladder.py` -- `logs/options_candidates.json`
  -> Option Selling Watch card with two tables (best cash-secured put per
     ticker, best covered call per ticker) (between `<!-- OPTIONS_SECTION_{START,END} -->`).
     Refuses to render unless input is flagged `public_safe: true`.
- `render_email.py` -- `logs/email_input.json`
  -> plain-text FULL email subject + body for Mike's Gmail draft

**Email decision + brief path (new 2026-04-20):**
- `email_decide.py` -- reads current canonical JSONs + `logs/communicated_state.json`
  -> returns `{decision: skip|brief|full, materiality_score, deltas[], brief_seed}`.
  Default decision is SKIP. Twice-daily runs that produce no material change
  create no draft. Keep-alive brief fires only after 3+ silent days.
- `render_email_brief.py` -- `logs/email_brief_input.json` (seeded from decide.brief_seed)
  -> compact 150-350 word email, NO fixed sections, leads with top delta.
- `email_state.py` -- the ONLY writer of `logs/communicated_state.json`.
  Commit runs AFTER Gmail draft success (or after a skip is logged).
  Never-re-surface invariant: `catalysts_communicated[]` blocks a source
  URL from leading a second email for 14 days.

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
- `geopolitical_scenarios.json` -- feeds both dashboard card and email
- `options_chain.json` -- CBOE-sourced raw option chain (public market data)
- `options_candidates.json` -- picked best put + best call per ticker,
  public_safe=true, feeds render_options_ladder.py
- `iv_history.jsonl` -- rolling ATM-30d IV history per symbol (public market data)
- `email_input.json` -- feeds render_email.py (FULL tier)
- `email_brief_input.json` -- feeds render_email_brief.py (BRIEF tier; transient, written per-run)
- `communicated_state.json` -- persistent ledger of what Mike was last told.
  Only writer: email_state.py. Consumed by email_decide.py for delta diffs.
  Contains per-ticker {price, conviction, stance, pt_mean, buy_pct, bears_refuted_num},
  macro snapshot, per-scenario likelihood buckets, options actionable list,
  and catalysts_communicated[] URL ring-buffer (14-day retention).
- `watchlist_criteria.json` -- STUB. Mike's screening mandate for new-name
  opportunity surfacing. Scanner disabled until user populates hard_filters.
- `positions.json` -- **PRIVATE**, holdings + cash + open short options. Lives
  in `~/.claude/...` only. Never committed to this repo. Read ONLY by the email
  renderer (v1.1) and by assignment-watch tooling. NEVER by public renderers.
- `{run_id}.json` -- audit manifest per run (retain 60)

### Public / private split (enforced across renderers)
- **Public** site output must never contain: share counts, cash balances, cost
  basis, assignment events, personalized recommendations, or anything that
  names the reader or says "you should". Those go to the private email only.
- **Public renderers** (`render_bluf_grid.py`, `render_portfolio_matrix.py`,
  `render_deep_dive.py`, `render_macro_context.py`, `render_geopolitical.py`,
  `render_options_ladder.py`) read ONLY public-safe canonical JSONs and never
  import from `positions.json`.
- **Private renderer** (`render_email.py`, v1.1+) MAY read positions.json to
  personalize the BLUF email that goes to Mike's inbox directly.

### Dashboard render markers (all machine-written, NEVER hand-edit)
```
<!-- BLUF_GRID_START -->         ...render_bluf_grid.py...        <!-- BLUF_GRID_END -->
<!-- PORTFOLIO_MATRIX_START -->  ...render_portfolio_matrix.py... <!-- PORTFOLIO_MATRIX_END -->
<!-- BLUF_MU_START -->           ...render_deep_dive.py (MU)...   <!-- BLUF_MU_END -->
<!-- BLUF_META_START -->         ...render_deep_dive.py (META)... <!-- BLUF_META_END -->
<!-- BLUF_NVDA_START -->         ...render_deep_dive.py (NVDA)... <!-- BLUF_NVDA_END -->
<!-- BLUF_MSFT_START -->         ...render_deep_dive.py (MSFT)... <!-- BLUF_MSFT_END -->
<!-- BLUF_AMZN_START -->         ...render_deep_dive.py (AMZN)... <!-- BLUF_AMZN_END -->
<!-- BLUF_GOOG_START -->         ...render_deep_dive.py (GOOG)... <!-- BLUF_GOOG_END -->
<!-- BLUF_AAPL_START -->         ...render_deep_dive.py (AAPL)... <!-- BLUF_AAPL_END -->
<!-- BLUF_TSLA_START -->         ...render_deep_dive.py (TSLA)... <!-- BLUF_TSLA_END -->
<!-- BLUF_BROS_START -->         ...render_deep_dive.py (BROS)... <!-- BLUF_BROS_END -->
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
7. **Email writes in plain English, not pipeline jargon.** Tier-grouped
   holdings (Strongest / Solid / Risk Watch) scan better than ranked
   lists. Company names lead, tickers in parens. Every acronym is
   annotated on first use.

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
- Send the Gmail draft automatically. Drafts only; Andrew reviews and sends.
