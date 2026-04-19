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
`stock-analysis-refresh` scheduled task (weekdays 05:30 + 12:30 PT). Public
URL: https://promptaisolutions.com/stock-analysis/

**Portfolio universe (9 tickers):** MU, META, NVDA, MSFT, AMZN, GOOG, AAPL,
TSLA, BROS. Recipient of the BLUF email is Mike McAteer at
`m-mcateer@hotmail.com`.

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
STEP 7  integrity gate (div 405-440, evi == 18, close delta <=2)
STEP 8  deploy (stash / rebase / push; never force)
STEP 9  email assembly: write email_input.json, run render_email.py,
          Gmail MCP create_draft
STEP 10 audit manifest + circuit breaker maintenance
```

### Python toolkit (stdlib-only except yfinance)
`~/.claude/scheduled-tasks/stock-analysis-refresh/tools/`:
- `quote_feed.py` -- yfinance grounded prices (authoritative)
- `wsb_scan.py` -- Reddit heat + sentiment, case-sensitive ticker match
- `outcome_ledger.py` -- append / settle / stats on the calibration JSONL
- `catalyst_score.py` -- tier x recency scoring, 1.5 min-score gate
- `classify_and_retry.py` -- sub-agent failure classifier + adapted
  retry-prompt generator
- `render_geopolitical.py` -- deterministic renderer for the Vetted
  Geopolitical Scenarios card (marker-delimited in HTML)
- `render_email.py` -- deterministic renderer for the BLUF email
  (Opus writes prose strings; Python renders structure)

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
- `email_input.json` -- feeds render_email.py
- `{run_id}.json` -- audit manifest per run (retain 60)

### Dashboard render markers
Between these markers is machine-written and must NEVER be hand-edited:
```
<!-- GEO_SECTION_START -->
...rendered by tools/render_geopolitical.py...
<!-- GEO_SECTION_END -->
```

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
