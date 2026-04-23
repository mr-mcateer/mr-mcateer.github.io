# Stock Analysis Dashboard -- Secretary Vision (DRAFT v0.1)

> Status: **draft for Andrew's review.** Mark this up. Anything in this file becomes the spec for the rebuild.

---

## 1. Reframe

The current site behaves like a **research analyst with opinions**. It computes a conviction score, declares a stance ("BUY / HOLD / RISK"), refutes bear cases on your behalf, and tells the reader what to do.

The new site behaves like a **god-like secretary**. It does not have opinions. It surfaces the live options market for the holdings universe in the most scannable, decision-supportive form possible, and lets the operator (Mike, you, anyone with the link) decide.

Think Bloomberg terminal compressed into a one-page web view, scoped to one strategy: **always selling premium**.

### What the secretary does NOT do
- Tell anyone whether to act today
- Compute "recommendation tiers" (no act / cherry-pick / pause language)
- Render conviction scores
- Render bull/bear cases
- Render BLUF narratives
- Refute bear theses
- Score catalysts on behalf of the reader
- Predict regime shifts
- Email anyone advice

### What the secretary DOES
- Pull fresh options chains every weekday for the holdings universe
- Render the chains as a dense, scannable, sortable table
- Annotate each row with **passive visual indicators** for: liquidity, IV vs realized vol, event proximity, Thursday weekend-theta opportunity, etc.
- Show the macro context (VIX, SPX, WTI, VRP regime band) as ambient context, not prescription
- Show the calendar of upcoming earnings + macro events that intersect tradable expirations
- Send a thin daily email pointing at the dashboard ("here's today's snapshot; you decide")

---

## 2. The audience

| Audience | What they want | What they do with it |
|---|---|---|
| **Mike** (primary) | Quickly see what's sellable today across his book. Spot Thursday-optimal expiries. Know what's blocked by earnings. | Place put-selling and covered-call orders at his broker. |
| **Andrew** (secondary) | Validate the dashboard as a portfolio of the consulting practice. | Show as case study to Prompt AI Solutions clients. |
| **Public visitors** (tertiary) | See what AI consulting can produce. | Inquire about engagements. |

Privacy invariant unchanged: public dashboard never shows share counts, cash balance, cost basis, or assignment events. Those are email-only, and even there only when Mike has explicitly opted in.

---

## 3. The new primary surface: the Options Sell Table

### Concept

Replace the BLUF grid + Portfolio Matrix + 9 deep-dive sections with **one large table**. Rows = tickers. Columns = put-selling decision inputs at 2-3 strike/expiry combinations per ticker. Plus a calls column for covered-call candidates.

### Layout (rough sketch)

```
TICKER  SPOT   1d%    7-14d PUT @ 0.20delta   7-14d PUT @ 0.15delta   30-45d PUT @ 0.20delta   COVERED CALL @ 0.25delta   STATUS
                      Strike  Prem  Yield      Strike  Prem  Yield     Strike  Prem  Yield      Strike  Prem  Yield        BADGES
NVDA    199.64 -1.4%  $185   $1.20  2.1%       $180   $0.65  1.2%      $175    $3.20  2.4%      $215   $1.80  1.7%        [EARN 14d] [THU-OPT] [IV-RV +6]
META    659.15 -2.3%  $625   $4.20  2.6%       $610   $2.10  1.4%      $600   $11.50  3.1%      $700   $5.60  1.6%        [EARN 7d BLOCK] [CHAOS]
MU      481.72 -1.2%  $455   $3.10  2.7%       ...                                                                         [EARN 60d] [PREM-RICH]
...
LMT     ...    ...    ...                                                                                                  [EARN 21d]
```

Sortable by any column. Default sort: by best yield, with blocked rows pushed to the bottom.

### Visual indicator system (the "secretary's whisper")

Every cell carries passive visual encoding. The reader scans and infers; the system never says "do this."

| Indicator | Visual | Meaning |
|---|---|---|
| **Yield heatmap** | Cell background fades from gray (0%) to green (>3% per 30d) | Higher = more premium per unit cash at risk |
| **Strike distance shading** | Strike text colored by % from spot (0-2% red, 2-5% yellow, 5%+ green) | Wider OTM = more cushion |
| **Earnings within DTE** | Cell crossed-out with strikethrough; tooltip shows date | This contract spans an earnings event |
| **Macro event within DTE** | Cell amber-shaded; tooltip names the event | This contract spans FOMC / CPI / NFP |
| **Liquidity flag** | Tiny red dot on the cell corner | Failed OI/spread gate; shown for transparency |
| **Thursday-optimal badge** | Blue [THU-OPT] pill on the row | Today is Thursday AND a next-Friday expiry exists for this ticker |
| **IV vs realized vol** | Right-edge sparkline showing IV-RV gap | Up-and-green = premium-rich; down-and-red = chaos zone |
| **Earnings calendar countdown** | Right-edge text "EARN 14d" or "EARN 7d BLOCK" | Days until next earnings; BLOCK suffix if it kills the 7-14 DTE window |
| **Macro calendar countdown** | Right-edge text "FOMC 5d" | Days until next high-severity macro event |

Color choices honor dark mode. All indicators are passive; none recommend an action.

### Strike/expiry combinations to display per row

Three put columns + one call column per ticker:
1. **Short-duration aggressive**: 7-14 DTE, 0.20 delta -- the disciplined-seller spine pick (current default)
2. **Short-duration conservative**: 7-14 DTE, 0.15 delta -- deeper OTM, smaller premium, more cushion
3. **Medium-duration**: 30-45 DTE, 0.20 delta -- the standard "monthly" pick for operators who don't want weekly babysitting
4. **Covered call**: 30-45 DTE, 0.25 delta -- if the operator owns shares

Operator decides which column to act on. The secretary just provides them all.

### Additional global widgets (small, top-of-page)

1. **Regime Tile** (already exists) -- VRP band, sizing context. Display only; no recommendation.
2. **Calendar strip** -- next 14 days with earnings + macro events flagged. Hover for details.
3. **Universe IV-RV summary** -- "14 of 24 names show IV below realized vol." Display only.
4. **Freshness badge** -- "Options + regime updated 2026-04-23 13:35 PT | Research updated 2026-04-21".

---

## 4. What gets removed from the current site

| Section | Reason |
|---|---|
| BLUF grid (9 cards) | Research-analyst framing; replaced by Options Sell Table rows |
| Portfolio Matrix table | Conviction scoring is prescriptive |
| 9 per-ticker deep-dive sections | Each ~150 lines of analyst narrative; not used in selling decisions |
| Bull / Bear case cards | Research framing |
| Verdict boxes | Prescriptive |
| Heatmap (9 cards) | Duplicates BLUF; same prescriptive issue |
| Vetted Geopolitical Scenarios card | Narrative framing; we surface event countdowns instead |
| "Bears refuted" column | Prescriptive synthesis |

Estimated reduction: ~1200 lines of HTML. Target final dashboard size: ~600 lines.

---

## 5. What stays from the current site

| Section | Why |
|---|---|
| Site header + nav + dark-mode toggle | Visual identity |
| Macro tile strip (VIX / SPX / NDX / WTI) | Ambient context, not prescription |
| Options Sell Table (NEW, replaces BLUF) | Core deliverable |
| Regime Tile (VRP) | Context, not recommendation |
| Calendar strip (NEW) | Earnings + macro countdowns |
| Footer + disclosures | Compliance / consulting branding |

---

## 6. The new email (much smaller)

The current email is a 800-1500 word BLUF synthesis. Mike skims it; rarely re-reads. The new email is **a thin pointer to the dashboard** plus a one-line "what changed since yesterday."

```
Subject: Options snapshot 2026-04-23 -- 0 clean / 24 blocked (FOMC 7d)

Mike,

Today's snapshot is live: https://promptaisolutions.com/stock-analysis/

What changed since yesterday: nothing material. FOMC continues to block the 7-14 DTE window across all 24 names.

Next clean window opens after FOMC release Thu Apr 30.

Thursday-optimal candidates available: 0 today.

Regime: VRP compressed (-2 vol points), 14 of 24 names show IV below realized vol.

-- Andy
```

That's it. ~80 words. The dashboard is the artifact; the email is the doorbell.

Email decision rule simplifies dramatically:
- Send IF (recommendation_tier_changed OR vrp_band_changed OR new_clean_setups OR is_thursday_with_optimal OR consecutive_skips >= 5)
- Otherwise skip silently

(The word "recommendation" stays in the *internal* state for change-detection but never appears in user-facing prose.)

---

## 7. Refresh schedule

| Surface | Cadence | Trigger |
|---|---|---|
| Options Sell Table | Tue-Fri 13:30 PT | daily-options-pulse cron |
| Regime Tile | Tue-Fri 13:30 PT | daily-options-pulse cron |
| Calendar strip | Tue-Fri 13:30 PT | daily-options-pulse cron |
| Macro tile strip | Mon 05:30 PT | weekly-full-refresh cron |
| Freshness badge | Both | both crons update their portion |

The "weekly full refresh" remains, but its scope shrinks dramatically:
- Refresh macro tiles (VIX, SPX, NDX, WTI)
- Refresh the calendar strip's macro events list (the next 30 days of FOMC / CPI / NFP)
- Refresh the earnings calendar (next 6 weeks of holdings earnings)
- (No analyst research, no geo synthesis, no conviction recalc, no bear rebuttal)

The weekly run becomes a context refresh, not a research synthesis.

---

## 8. Tools that get deleted (cleanup)

| Tool | Reason |
|---|---|
| `tools/wsb_scan.py` | Sentiment scoring is opinion; secretary doesn't have opinions |
| `tools/outcome_ledger.py` | Calibration is academic; not used in selling decisions |
| `tools/classify_and_retry.py` | Sub-agent retry logic; we have far fewer sub-agents now |
| `tools/email_decide.py` | Replaced by simpler change-detection in the new email path |
| `tools/email_state.py` | Replaced by `options_pulse_state.json` (one-line ledger) |
| `tools/render_email_brief.py` | Replaced by inline orchestrator composition (~80 words) |
| `tools/render_email.py` | Full email no longer exists |
| `tools/render_bluf_grid.py` | BLUF grid removed |
| `tools/render_portfolio_matrix.py` | Portfolio matrix removed |
| `tools/render_deep_dive.py` | Deep dive sections removed |
| `tools/render_geopolitical.py` | Geo card removed |
| `tools/catalyst_score.py` | Tier x recency scoring no longer used |
| `tools/render_macro_context.py` | Replaced by simpler macro tile strip refresher |
| Agent: `geopolitical-fetcher` | Geo work removed |
| Agent: `wsb-scanner` | WSB removed |
| Agent: `ticker-research-batch` | Analyst research removed |
| Agent: `catalyst-scanner` | Catalyst scoring removed |
| Agent: `market-snapshot` | Replaced by simple Python pull on the weekly run |

Estimated reduction: 13 Python files + 5 sub-agent definitions removed.

## 9. Tools that get built (new)

| Tool | Purpose |
|---|---|
| `tools/render_options_sell_table.py` | Render the new primary table with full visual indicator system |
| `tools/render_calendar_strip.py` | Render the next-14-day earnings + macro calendar strip |
| `tools/compute_realized_vol.py` | Per-ticker 30d realized vol from yfinance, joined with chain ATM IV; emits chaos / premium-rich / neutral flags |
| `tools/refresh_macro_tiles.py` | Weekly: pull VIX/SPX/NDX/WTI from yfinance, render the macro tile strip |
| `tools/refresh_event_calendar.py` | Weekly: refresh `logs/known_events.json` from earnings + macro APIs (or hand-curated for now) |
| Augmentation: `options_candidates.py` | Add three strike/expiry combinations per ticker (was: 1) |

## 10. Tools that stay unchanged

| Tool | Role |
|---|---|
| `tools/quote_feed.py` | Grounded prices for the freshness badge |
| `tools/options_chain.py` | CBOE chain pull |
| `tools/compute_events.py` | Event filter (earnings + macro vs expirations) |
| `tools/compute_vrp_regime.py` | SPX VRP band classification |
| `tools/render_regime_tile.py` | Regime tile render (already display-only, no prescription) |

---

## 11. Migration plan (proposed)

**Phase 1 -- Plan ratification.** You read this doc, mark it up, we converge.

**Phase 2 -- Write the new SKILL.md files** (daily-options-pulse + weekly-full-refresh) reflecting the secretary framing. These become the new contracts.

**Phase 3 -- Build the new tools** (render_options_sell_table, render_calendar_strip, compute_realized_vol, refresh_macro_tiles).

**Phase 4 -- Surgical site rewrite.** Strip the old sections from `stock-analysis/index.html` (keep header, footer, dark-mode CSS). Insert the new sections between marker pairs the renderers can write to.

**Phase 5 -- Validate.** Run today's options pulse against the new flow. Visual QA. Iterate.

**Phase 6 -- Deprecate the old.** Delete the dead tools. Replace `stock-analysis-refresh/SKILL.md` with a pointer to the two new SKILL.md files.

Phases 1 and 2 are work for this session. Phase 3 onward is the second part of the two-part edit you mentioned -- after you've reviewed and improved this doc.

---

## 12. Open questions for Andrew

1. **Is "the holdings" the 24-ticker watchlist universe, or Mike's actual positions?** The watchlist is public-safe; positions are private. The dashboard surface answers this question with how it's titled and scoped.

2. **Three put strike/expiry columns per row -- right number, or too many?** I picked: 7-14d @ 0.20d, 7-14d @ 0.15d, 30-45d @ 0.20d. Could also be 4 columns (add 7-14d @ 0.10d for the very deep OTM crowd) or 2 (drop the medium-duration one).

3. **Cash-secured puts vs naked puts.** Should the table show "cash needed per contract" (assumes CSP) or omit it (since naked puts don't tie up the same cash)? Different audiences.

4. **Universe size 24 -- right?** Adding/removing tickers is now a one-line edit to the SKILL.md. Cheap to revisit.

5. **Email frequency.** The current proposal: send only when something changed (recommendation tier, regime band, new clean setups, Thursday-optimal exists, or 5 days of silence). Acceptable, or do you want a guaranteed Thursday-PM email regardless?

6. **Covered-call column.** Worth showing per row, or only show when the operator has positions? Public dashboard can't know positions; private email could.

7. **What happens to the existing dashboard markup we've invested in?** Specifically: the heatmap card visual style (could be reused for the Options Sell Table), the Regime Tile (keep as-is), the Vetted Geopolitical Scenarios card (delete as proposed?), the Macro Context tiles (slim down per the weekly-refresh proposal?).

8. **Naming.** "Stock Analysis" is now a misnomer; it's an "Options Sell Desk." Keep the URL `/stock-analysis/` (don't break inbound links), but maybe retitle the page to "Options Selling Desk" or similar?

---

## 13. The single sentence test

If a stranger lands on the page, the answer to "what does this site do?" should be:

> **It shows you what options you could sell today on a curated watchlist of stocks, with passive visual cues highlighting the high-yield, the about-to-expire, and the earnings-blocked, so you can decide for yourself.**

If the answer drifts toward "it tells you what to trade" or "it analyzes stocks for you," the design has slipped back into analyst mode and needs to be pulled back.

---

## 14. End of draft

Mark it up. Anything in this file becomes spec.
