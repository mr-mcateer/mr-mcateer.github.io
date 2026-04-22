# Options-Selling Compendium for the Stock-Analysis Refresh

> Internal reference. Not part of the published site. Generated 2026-04-20.
>
> Audience: Andrew + Claude, as the two developers of the stock-analysis-refresh
> pipeline. The public dashboard and the Mike-McAteer email must remain in
> plain English; this document is the technical substrate that lets us pick
> the right trades to surface in plain English.
>
> **Companion build plan:** the engineering brief that turns this knowledge
> base into shippable code lives at
> `~/.claude/scheduled-tasks/stock-analysis-refresh/DESIGN_BRIEF.md`. That
> document is the canonical roadmap, milestone sequence, interface spec, and
> acceptance-test harness for v2 of the pipeline. This compendium answers
> "why and what"; the design brief answers "how and when."

---

## Table of contents

1. [Preface and purpose](#preface-and-purpose)
2. [Part I -- Why premium selling has a structural edge](#part-i--why-premium-selling-has-a-structural-edge)
   - **Section 1a -- The 2024-2026 regime, honestly (compression reality check)**
3. [Part II -- The greeks, translated](#part-ii--the-greeks-translated)
4. [Part III -- Strategy catalog](#part-iii--strategy-catalog)
5. [Part IV -- Entry selection framework](#part-iv--entry-selection-framework)
6. [Part V -- Risk management](#part-v--risk-management)
7. [Part VI -- Advanced analysis (the dealer view)](#part-vi--advanced-analysis-the-dealer-view)
8. [Part VII -- Visualization compendium](#part-vii--visualization-compendium)
9. [Part VIII -- Practitioner knowledge, by community](#part-viii--practitioner-knowledge-by-community)
10. [Part IX -- Flash-trader techniques that retail can harvest](#part-ix--flash-trader-techniques-that-retail-can-harvest)
11. [Part X -- The money-making playbook](#part-x--the-money-making-playbook)
12. [Part XI -- Integration roadmap with the current pipeline](#part-xi--integration-roadmap-with-the-current-pipeline)
13. [Part XII -- The calibration loop](#part-xii--the-calibration-loop)
14. [Part XIII -- The "do not" catalog](#part-xiii--the-do-not-catalog)
15. [Part XIV -- Tax treatment of short premium](#part-xiv--tax-treatment-of-short-premium)
16. [Part XV -- Margin mechanics and buying power](#part-xv--margin-mechanics-and-buying-power)
17. [Part XVI -- Commissions, fees, and slippage](#part-xvi--commissions-fees-and-slippage)
18. [Part XVII -- Behavioral protocol](#part-xvii--behavioral-protocol)
19. [Part XVIII -- Assignment mechanics in detail](#part-xviii--assignment-mechanics-in-detail)
20. [Part XIX -- Single-name playbook (the 9-ticker universe)](#part-xix--single-name-playbook-the-9-ticker-universe)
21. [Part XX -- End-to-end worked portfolio example](#part-xx--end-to-end-worked-portfolio-example)
22. [Appendix A -- Plain-English glossary](#appendix-a--plain-english-glossary)
23. [Appendix B -- Formula reference](#appendix-b--formula-reference)
24. [Appendix C -- Reading list](#appendix-c--reading-list)

---

## Preface and purpose

The stock-analysis-refresh pipeline already picks, twice a day, the single
best short put and short call per ticker from the CBOE delayed feed and
renders them to the public dashboard as the Option Selling Watch card. That
is version 1. This document is the reference that drives versions 2 through
N: what to add, in what order, and how to present it so the user (Mike, and
any future reader of the site) keeps trusting the output.

The central claim of this compendium is simple. Selling options at the
right strike, at the right time, on liquid large-cap names, and with
disciplined sizing, is one of the most dependable sources of positive
expected return available to a patient individual account. The edge is
small per trade, structural rather than speculative, and completely ruined
by two kinds of mistakes: sizing too big and selling at the wrong time.
Almost every idea in this document exists to help us avoid those two
mistakes at scale.

Every section below has three parts: **why this matters**, **what the
practitioner consensus is**, and **what to build in the pipeline**. The
third part is what turns this reference into production code.

---

## Part I -- Why premium selling has a structural edge

### 1. The volatility risk premium (VRP)

Implied volatility -- the vol number the market bakes into option prices --
is on average higher than subsequent realized volatility. The difference is
called the volatility risk premium (VRP). On SPX, the long-run VRP is
roughly 3 to 4 vol points: ATM 30-day implied vol has averaged around 19%
while subsequent realized vol has averaged around 15-16%. On single-name
equities the VRP tends to be wider and noisier. On indices it is tighter
and more reliable.

### 1a. The 2024-2026 regime, honestly (reality check)

**This is the single most important context in this document and the
one most retail vol-selling content gets wrong.** The long-run SPX VRP
is ~4 vol points. The current VRP, measured over rolling windows, is
materially below that. Where we sit as of April 2026:

| Window                          | Approx VRP (IV - RV) |
|---------------------------------|----------------------|
| Point-in-time (mid-March 2026)  | +7.5 vol points      |
| Trailing 3 months               | +4 to +6 pts         |
| Trailing 6 months               | +2.9 pts median      |
| Trailing 12 months              | +1 to +2 pts         |
| Trailing 24 months              | +0.5 to +1.5 pts     |
| 35-year historical average      | +4.09 pts (CFA Institute) |

**The reconciliation of apparently-contradictory claims:**
- The point-in-time 7.5-point VRP (SharpeTwo, Penn Mutual, March 2026)
  is real, but it reflects an *acute shock* regime (Iran strike,
  tariff shock, geopolitical tail premium getting embedded).
- The "near-zero or negative 12-month rolling VRP" claim (Robot
  Wealth, 2024-2025) is also real, because the 2023-2025 baseline was
  structurally compressed.
- Both are simultaneously true at different zoom levels.

**Why the baseline has been compressed:**
1. **0DTE dealer long-gamma suppresses intraday realized vol.** 0DTE
   now drives 59%+ of SPX volume; retail is net short these options;
   dealers are net long-gamma and hedge by selling strength / buying
   weakness. This mechanically compresses 30-day RV.
2. **Short-vol crowding.** More capital chasing the VRP competes IV
   lower, even as RV stays compressed.
3. **Post-2022 low-macro-vol regime** with rate-cut expectations
   dampened institutional hedging demand.
4. The 2025 dispersion-trading explosion (records in late 2025) moved
   single-name VRP higher but index VRP lower.

**Tenor matters.** For the 25-50 DTE seller specifically:
- 7-15 DTE (0DTE-adjacent): VRP MOST compressed, frequently negative.
- **25-50 DTE**: moderately compressed but positive. Our band.
- 56-63 DTE: somewhat healthier VRP (independent SharpeTwo studies
  show 56-63 was a better edge-per-risk band than 42-49 in
  2023-2024).
- 60-90 DTE: healthiest current VRP (geopolitical tail premium
  embedded here, 0DTE doesn't compete).

**Single-name vs index.** Single-name megacap VRPs (NVDA, META,
MSFT, etc.) are structurally RICHER right now than index VRPs, for
two reasons: (a) dispersion is elevated, (b) 0DTE suppression is an
SPX phenomenon. But single-name sellers absorb gap risk (earnings,
product launches, capex pre-announcements) that index sellers do
not. The richer premium is compensation for non-diversifiable
idiosyncratic risk, not free money.

**Brutal, honest conclusion for a 25-50 DTE premium seller:**

- Disciplined, well-sized 25-50 DTE put-selling in the current
  regime should **realistically expect 6-10% annualized** before
  taxes and drawdowns.
- **10-18% annualized is achievable only with** sophisticated
  filters (VRP-regime gating, IV rank + VRP joint-filter), tenor
  bias toward 45-60 DTE, single-name diversification that captures
  the dispersion premium, AND disciplined sizing through tail
  events.
- **The "15-20%+" numbers in retail options-selling content are
  folklore from the 2017-2019 golden era**, when VRP was reliably
  4+ points and 0DTE volume hadn't yet re-wired the short end.
- The CBOE PUT and BXM benchmarks -- professional, no-slippage,
  disciplined-execution versions of premium selling -- show ~9-10%
  annualized since inception, and that is before retail friction.

**The single-sentence take-away:** retail premium sellers in
2024-2026 have been harvesting a 1-2-point VRP while telling
themselves it is 4 points. The backtests they anchor to ran on a
friendlier regime. The edge is still positive. It is not what the
options-education industry sells.

**Pipeline implication.** Add a "current regime" tile to the
dashboard that displays:
- Rolling 30-day SPY VRP (computed from our IV history + realized
  price data).
- A plain-English "VRP status: compressed / normal / elevated"
  label using the tables above.
- A sizing multiplier suggestion (0.5x if compressed, 1.0x if
  normal, 1.25x if elevated).

This is the single most honesty-preserving tile we can add.

Why does the VRP exist? Because most natural option demand is **insurance
demand**. Long-only equity investors want downside protection and are
willing to pay a premium for it, the same way homeowners pay more in
insurance premiums than the expected value of future claims. Someone has
to write that insurance. The writers are paid to bear tail risk. On
average, the payment exceeds the realized tail losses, because fear of
the tail is persistently greater than the tail's actual frequency. That
spread is the VRP, and it is what we are farming.

The VRP is not a free lunch. It is the structural compensation paid to
capital willing to accept a negatively skewed, leptokurtic return stream.
**Most of the time you make small amounts; rarely, you lose large amounts.**
The long-run expected value is positive if -- and only if -- your sizing
keeps you alive through the rare losses.

### 2. Structural flows that fund the VRP

Three persistent flows pay the premium seller:

1. **Pension funds and endowments** systematically buy downside protection
   on equity exposure. The CBOE's own PUT index documents decades of this
   one-sided flow.
2. **Retail call-buying** on meme and growth names provides a mirror-image
   flow on the upside: retail buys OTM calls because the convex payoff is
   psychologically attractive, and they pay elevated skew to get it.
3. **Corporate hedging** (forex, commodity, equity collar strategies like
   the JPM Collar fund) periodically rebalances massive option positions
   and injects flow at known points in the calendar.

A premium seller sitting in between these three counterparties is
collecting a fee for being the flexible balance-sheet. The trade does not
require a market view. It requires **liquidity, patience, and correct
sizing**.

### 3. Positive expectancy, negative skew

Every short-option trade looks like this: high probability of a small
positive return, low probability of a large negative return. That shape
is called **negative skew**. The long-run EV is positive if the
expected-loss-per-tail-event is smaller than the cumulative small wins
between tails. This is quantifiable:

- Selling a 30-delta put collects premium roughly equal to `0.30 * expected
  move`. The "probability of touching" that strike before expiry is roughly
  `2 * delta = 60%` (the classic tastytrade rule of thumb). Caveat: the 2x
  heuristic derives from the reflection principle under Brownian motion with
  zero drift. Real equities have positive drift (expected return > 0) and
  jumps (earnings gaps, news gaps, macro shocks), which means the 2x rule
  *underestimates* probability of touch for short puts in trending-up
  markets and *overestimates* it for short calls in the same regime. For
  our 9-ticker megacap-tech universe with a persistent upward drift, the
  touch rate on our short puts is likely a few points higher than 2*delta
  naively suggests.
- On average the trade wins ~70% of the time. When it loses, the loss is
  typically 2-3x the premium.
- Net expected value: modest positive, **only if** the 70% / 30% odds hold
  on average. They do hold on diversified books over many trades. They do
  not hold on any single trade.

This is why **sizing and diversification are the core of the edge**, not
individual trade selection. The spine gates in [`options_candidates.py`]
are important, but a perfectly-gated single trade still loses. A hundred
well-gated trades, sized correctly, will tend to profit.

### 4. Why the edge persists

People ask: "if this works, why isn't it arbitraged away?" Three reasons:

1. **Capacity**. The VRP is deep enough to absorb trillions, but narrow
   enough that you cannot lever it 10x without catastrophic tail exposure.
   Pod shops and systematic vol funds harvest a chunk; the rest is left
   on the table because levering up to take it requires accepting fat
   left-tail events that blow up the fund.
2. **Psychology**. Premium selling requires eating 5 small losses in a row
   without changing the process. Most humans cannot. Funds with monthly
   reporting cycles cannot. The edge persists because the strategy is
   emotionally corrosive even when it is mathematically sound.
3. **Rare regime changes**. In the 2008 and March-2020 regimes, the VRP
   inverted for weeks. Anyone short premium without tail hedges blew up.
   That memory keeps capital on the sidelines, which keeps the long-run
   VRP attractive for the survivors.

Our pipeline should therefore assume the edge is real but sizes are the
risk, and bake tail-protection awareness into every signal.

---

## Part II -- The greeks, translated

Greeks are the sensitivities of an option's value to changes in spot,
time, and vol. Every signal we build eventually cashes out in terms of
greeks. This section covers them in plain English first, then formally.

### 5. Delta

**Plain English.** Delta is the number of shares the option acts like,
right now. A 0.30 delta call behaves, over tiny price moves, like 30
shares of stock.

**Delta as probability -- handle with care.** Delta is *approximately*
the market-implied probability of expiring ITM, but precisely it is
`N(d1)`, while the true risk-neutral ITM probability is `N(d2) =
N(d1 - sigma*sqrt(T))`. These differ by a `sigma*sqrt(T)` term -- about
1-2 percentage points for short-dated options, about 5-8 points for 45
DTE options at 30-50% vol. Delta systematically *overstates* ITM
probability for higher vol and longer DTE. And both quantities are
*risk-neutral*, not *physical*; the physical (actual) probability of
ITM is typically a few points lower still, because the risk-neutral
measure over-prices downside (and that over-pricing IS the VRP we are
harvesting). The practical summary: a 0.30 delta short put has a
real-world ITM expiration probability closer to 22-25%, not 30%.
Favorable for the seller, but not as favorable as the naive
"delta = 30%" reading would suggest.

**Formal.** Delta = partial derivative of option value with respect to
spot. For calls, delta is in [0, 1]; for puts, delta is in [-1, 0]. A
deep ITM call has delta near 1 (moves dollar-for-dollar with stock), an
ATM call has delta near 0.5, and a deep OTM call has delta near 0.

**What a seller cares about:**
- Short put delta is positive (you want the stock to go up).
- Short call delta is negative (you want the stock to go down or stay put).
- Your **net book delta** is the sum of all your position deltas. For a
  premium-seller portfolio that is long 100 shares each of 9 names and
  running a wheel on some of them, net book delta is typically very long
  (hundreds of delta units). That is equity-market exposure in disguise.
- The **pipeline should track and display** net book delta over time, not
  just individual trade delta.

### 6. Gamma

**Plain English.** Gamma is how fast delta changes as the stock moves.
If delta is your speed, gamma is your acceleration. Gamma is highest for
ATM options near expiry -- this is why selling short-dated ATM options
is terrifying: a tiny stock move can flip the option from safe to
catastrophic before you can react.

**Formal.** Gamma = second derivative of option value with respect to
spot = first derivative of delta. Gamma is always non-negative for long
options and non-positive for short options.

**What a seller cares about:**
- Short gamma is the source of most premium-seller blowups. When you are
  short gamma and the underlying moves against you, your losses accelerate.
- Gamma peaks at the strike, around the money, and is high in the last
  ~21 days before expiration. This is the origin of the "21-DTE rule"
  (see Part V).
- At the portfolio level, **net book gamma** is the concentration risk
  nobody sees. A portfolio with 9 short puts all sitting near 0.30 delta
  on 9 correlated names has enormous short gamma that activates together
  on a market-wide drawdown.

### 7. Theta

**Plain English.** Theta is the money time gives you. If nothing moves,
an option you are short loses extrinsic value every day, and that value
accrues to you. Theta is positive for premium sellers and is the
"coupon" we are trying to clip.

**Formal.** Theta = partial derivative of option value with respect to
time. Usually quoted per calendar day. Theta accelerates non-linearly
as expiration approaches -- this is where the 21-DTE rule comes from.

**What a seller cares about:**
- Theta / vega ratio is the measure of "how much do I earn per unit of
  vol risk I am bearing?" High theta/vega is attractive.
- Theta acceleration near expiration is seductive but traded against
  gamma acceleration. The sweet spot is 25-50 DTE -- reasonable theta
  without catastrophic gamma.
- At the portfolio level, **net book theta** is the headline number
  everyone wants on a dashboard: "you are earning ~$X per day from
  short premium as long as nothing moves too much."

### 8. Vega

**Plain English.** Vega is how much the option moves when implied vol
moves by one percentage point. Short options have negative vega: if
IV goes up, you lose; if IV goes down, you win.

**Formal.** Vega = partial derivative of option value with respect to
implied volatility. Typically quoted per one-vol-point move.

**What a seller cares about:**
- Selling into high IV (high IV rank) gives you room to earn on BOTH
  time decay AND vol compression. That is the canonical edge of the
  disciplined seller.
- Selling into low IV gives you only time decay, and any vol expansion
  wipes out months of theta income in days.
- **Net book vega** is the tail-risk proxy. A portfolio that is short
  $500 of vega will lose $500 for every one-point VIX spike. A 10-point
  VIX spike (common in a panic) costs $5,000 on a book that thought it
  was earning $X / day from theta.

### 9. Second-order greeks

Not strictly required to trade, but essential to build sophisticated
analytics around OPEX and dealer-flow dynamics.

- **Vanna**: change in delta per change in implied vol. Drives the
  "charm flow" we will discuss in Part VI. When IV falls, dealer call
  hedges unwind -- this is measurable and predictable around monthly
  OPEX.
- **Charm**: change in delta per passage of time. Drives the same OPEX
  flow from a different angle. As time passes on OTM options, their
  delta drifts toward zero; dealers who were hedged must unwind.
- **Vomma** (a.k.a. volga): change in vega per change in implied vol.
  This is the "vega-convexity" that makes vol-of-vol (VVIX) dangerous.
- **Color**: change in gamma per passage of time. Explains why gamma
  concentration near OPEX matters.

We do not need to compute these ourselves -- CBOE's feed gives us
first-order greeks already. We *do* need to understand them because
they explain why the market is not smooth around known-flow events,
and therefore why our entries should cluster in some windows and avoid
others.

### 10. A unified mental model

Every short option position can be summarized as:

> I am getting paid **theta** per day to hold **negative vega**,
> **negative gamma**, and a **directional delta** I believe I can manage.

Those four numbers are what we display. Everything else is decoration.

---

## Part III -- Strategy catalog

Our current spine only supports cash-secured puts and covered calls.
This section catalogs the strategies we *could* add and what each one
is good for. The roadmap in Part XI sequences them.

### 11. Cash-secured put (CSP)

**Mechanic.** Sell one put, reserve (strike * 100) in cash to buy the
stock if assigned.

**Why.** Highest risk-adjusted return per dollar of buying power of any
simple short-option strategy for a patient long-equity investor. You
get paid to name the price you would be willing to buy a stock you
already want to own.

**Good when.** You would buy the underlying at the strike anyway. IV
rank is elevated. The stock is not in a news window (earnings, Fed
week for rate-sensitive names).

**Bad when.** Stock is in an obvious downtrend and headed through your
strike. You would not actually want to own shares at the strike.
Account cannot absorb assignment.

**In our system.** This is already the core of `options_candidates.py`.
The spine (25-50 DTE, 0.20-0.35 delta, OI 250, spread 15%) encodes a
solid consensus.

### 12. Covered call (CC)

**Mechanic.** Own 100 shares, sell one call against them.

**Why.** Converts some upside into current income. Works best on names
you would tolerate selling at the call strike -- i.e., where the strike
represents a price you would happily exit at.

**Good when.** You own the shares and have a target sell price. IV rank
is elevated. You are not in an earnings window.

**Bad when.** You are ideologically attached to the shares and would
feel pain being called away (see Part XIII). The name is in the early
innings of a multi-bagger move.

**In our system.** Already implemented. The covered-call candidate is
the second table in the Option Selling Watch card.

### 13. The Wheel

**Mechanic.** Sell CSP -> if assigned, sell CCs on the assigned shares
-> if called away, sell another CSP -> repeat.

**Why.** Turns premium selling into a cyclic income engine on names
you believe in. The assignment is a feature, not a failure, because
you wanted to own the stock at that strike.

**Good when.** You have a universe of 5-15 stocks you are willing to
own long-term. Your capital per cycle is large enough to actually take
assignment.

**Bad when.** The wheel becomes an excuse to short puts on names you
would not actually buy. This is the #1 way retail wheel-traders lose
money.

**In our system.** The two-table layout already hints at the wheel:
the left column is the "enter" leg, the right column is the "exit"
leg. The pipeline should eventually track which ticker is in which
phase (flat, short CSP, long shares from assignment, short CC) and
display the whole cycle in the private email.

### 14. Credit spreads (bull put, bear call)

**Mechanic.** Sell a near-the-money put and buy a further-OTM put
(bull put spread). Or sell a near-the-money call and buy a further-OTM
call (bear call spread).

**Why.** Defined max loss. Drastically reduced buying-power
requirement. Lets you run more positions in the same account. Caps
your tail exposure.

**Good when.** Your account is small or you want to scale to more
tickers. You expect mean reversion in the opposite direction.

**Bad when.** The spread is narrow enough that slippage eats too much
of the premium. Very tight spreads (like $1-wide on a $500 stock) are
usually not worth the friction.

**In our system.** High-value addition for version 2. A `bull_put_spread`
candidate per ticker that uses the existing chain and suggests the
optimal long wing at ~15-delta beyond the short strike. Enables a
"defined-risk wheel" variant for readers who cannot tie up $20k in CSP
buying-power per contract.

### 15. Iron condor

**Mechanic.** Bull put spread + bear call spread in the same expiry on
the same underlying. Profits when the stock stays in a range.

**Why.** Pure volatility-selling strategy. Maximum theta for a given
buying-power footprint. Defined max loss on either side.

**Good when.** IV rank is high and you expect mean reversion (you are
selling the expected move). The underlying is rangebound (sideways
tape).

**Bad when.** Trending markets. Earnings. Low-liquidity names where
the four-leg spread eats too much bid-ask. Over-sized condors stacked
across correlated names.

**In our system.** Works only for tickers with tight bid-ask spreads
across four legs (our current 15% spread gate applies per leg). Build
as v3 addition. The analytics are more complex because the max loss,
probability-of-touching-each-wing, and breakeven analysis requires
multi-leg math.

### 16. Short strangle

**Mechanic.** Sell a put at ~0.20 delta below, sell a call at ~0.20
delta above. Undefined risk (naked on both sides).

**Why.** The pure short-vol trade. Classic tastytrade preferred
vehicle. Symmetric premium collection around the current price.

**Good when.** IV rank high. You trust the underlying not to gap.
Account is large enough to survive assignment on either leg.

**Bad when.** Anywhere you cannot afford naked exposure. Small
accounts. Any name that could realistically gap 20%+ in either
direction (meme stocks, biotech, earnings).

**In our system.** Should NOT surface on a public dashboard as a
recommendation because naked strangle risk is asymmetric to the reader
(different accounts have different risk capacity). Could appear in the
private email as a note: "IV rank 78 on NVDA -- a 30-day 0.20-delta
strangle would pay ~$18/contract." Informational only.

### 17. Jade lizard

**Mechanic.** Sell an OTM put + sell a call credit spread, sized so
total credit received >= width of the call spread. Result: zero
upside risk. Downside is a naked put.

**Why.** The "no upside risk" construction is psychologically
appealing in strongly bullish regimes -- you cannot be wrong on the
upside breakout.

**Good when.** You are short-term neutral-to-bullish, IV rank is
elevated, and you can tolerate the put side.

**In our system.** A signature tastytrade construction worth
surfacing when the chain supports it. Low priority for v1 but a
natural way to present "combined CSP + CC with a capped call side."

### 18. Ratio spreads

**Mechanic.** Sell N of one strike, buy M of another (N > M). Often
1-by-2 or 1-by-3 put ratios for "broken wing" looks.

**Why.** Extract more premium with less upside hedge cost. Useful
when the skew is steep.

**Good when.** Put skew is steep (i.e., downside puts are expensively
priced relative to at-the-money puts). You can read the skew curve.

**Bad when.** You do not understand the unbalanced exposure. The
leverage can blow up if the name gaps to the short strike.

**In our system.** Advanced. Only worth surfacing if we build a
skew-analysis feature first (Part VI) and can tell the reader
"NVDA put skew is rich -- a ratio spread captures this."

### 19. Calendar / diagonal spreads

**Mechanic.** Sell short-dated option, buy longer-dated option at the
same (calendar) or different (diagonal) strike.

**Why.** Profits from term-structure contango and accelerating theta
decay on the near leg. Defined risk.

**Good when.** Term structure is in steep contango (near-dated vol
cheaper than longer-dated). You want exposure to theta without naked
vega risk on the long side.

**Bad when.** Backwardation (near-dated vol higher than longer-dated)
-- this is usually around events and is a signal NOT to trade calendar
spreads.

**In our system.** Requires term-structure analysis (Part VI) which
we do not yet have. A v4 addition.

### 20. Poor man's covered call (PMCC)

**Mechanic.** Buy a deep-ITM long-dated call (a LEAP), sell a short-dated
OTM call against it.

**Why.** Simulates a covered call without needing 100 shares of capital.
Appropriate for smaller accounts wanting to run the "own shares + sell
calls" motion cheaply.

**Good when.** You want covered-call income on a name whose shares
would eat too much buying power.

**Bad when.** You underestimate the gamma risk on the short call leg
when price approaches the short strike. You do not account for
dividends (the long LEAP does not collect them).

**In our system.** Worth mentioning in the compendium; probably NOT a
public-dashboard suggestion because it requires account-level context
(capital available, whether to use shares or LEAPs, etc.) that we do
not know publicly.

### 21. Earnings-specific plays (do NOT sell through earnings)

The community consensus is brutal and nearly unanimous: **do not be
short premium through an earnings announcement on single-name
equities**. The IV crush after earnings works for you, but the
directional gap risk is uncontrolled and regularly destroys quarters
of accumulated theta.

Flow: our pipeline should flag any ticker whose chosen expiration
spans an earnings date and either (a) swap to a pre-earnings expiration
or (b) flag the trade as "earnings-contaminated" and skip it.

### 22. Choosing the right strategy per ticker

Decision tree we should encode in the pipeline:

```
IS IV RANK > 50?
  YES -> rank the underlying
    - If $BP_available / contract > (strike * 100): use CSP (the simplest wheel entry)
    - If $BP_available / contract < (strike * 100): use bull-put spread
    - If you also own 100+ shares: use CC
    - If your view is rangebound AND liquidity is great: use iron condor
  NO (IV rank low) -> do not sell naked premium; either
    - stand aside
    - use a calendar if term-structure is in contango
    - use a debit-side strategy entirely
```

---

## Part IV -- Entry selection framework

### 23. IV rank vs IV percentile

**IV rank** = (current_iv - 52w_low) / (52w_high - 52w_low) * 100.
A linear interpolation between the 52-week range.

**IV percentile** = fraction of the last 252 trading days with IV
lower than current. A density-based measure.

Both are attempts to normalize "is current vol elevated, historically?"
for a given name. They disagree in skewed distributions: a name that
spent 240 days at low IV and 12 days at very-high IV will have a high
IV rank even at modest IV levels, but a low IV percentile.

**Consensus use.** Sell premium above IV rank 30 (Option Alpha), above
50 (tastytrade research), above 70 (more disciplined). The gate is
softer as the ticker's history gets shorter.

**In our system.** `options_chain.py` computes IV rank from
`iv_history.jsonl`. The 20-session minimum before IV rank becomes valid
is a real constraint -- until spring 2026 we have insufficient history,
which is why the pipeline soft-passes when IV rank is missing. Once we
cross the 60-session threshold, we should harden the gate: IV rank
below 30 disqualifies new entries unless manually overridden.

### 24. DTE selection: the 25-50 day sweet spot

Tastytrade research (repeated in dozens of their podcasts, with trade-
database support) claims that ~45-DTE entries managed to ~21-DTE exits
are the optimal theta/gamma trade-off. The logic:

- Before 45 DTE, theta decay is too slow relative to the buying-power
  commitment.
- Closer than 21 DTE, gamma starts dominating theta -- a single adverse
  move wipes out more than you have left to earn.
- Closer than 7 DTE, gamma is catastrophic. Pin risk, assignment risk,
  slippage on exits -- everything gets worse.

Our 25-50 DTE window is consistent with this. The management rule we
should encode: **close or roll at 21 DTE remaining** (or at 50% of max
profit, whichever comes first). Neither of these is currently encoded
-- they require either a separate "position manager" script or a live
broker integration.

### 25. Delta selection: 0.16, 0.20, 0.30 regimes

- **0.40 delta**: aggressive. Empirically ~84% win rate on a 5-year
  SPY short-put-strangle backtest (navigationtrading.com, 2024),
  +179% cumulative return. Premium large. Most exposure to assignment.
- **0.30 delta**: "tastytrade standard." Empirical ~61% win rate on
  single-leg short puts in the same study -- marginally unprofitable
  at the individual-ticker level because tail losses outweighed the
  thinner premium capture. Delta 30 works ONLY inside a strangle or
  a diversified book, NOT as a single-name single-leg play.
- **0.20 delta**: balanced. ~80% expire worthless. Our current default
  high-end of the band.
- **0.16 delta**: one standard deviation. ~84% expire worthless. The
  "I want to be mostly sure" choice. Premium lower.
- **0.10 delta**: tails. ~90% expire worthless. Premium often not worth
  the tail exposure.

**Important caveat on delta-as-probability.** Delta is a *risk-neutral*
probability of ITM expiration, which is close to but NOT equal to the
physical (real-world) probability. In practice the physical probability
of a short put being ITM at expiry is typically a few percentage points
LOWER than (1 - |delta|) would suggest, because the risk-neutral measure
over-prices downside. So a 0.20 delta put has risk-neutral ~80% hit
rate, physical ~82-84% hit rate. Favorable skew for sellers, but it is
not a free lunch: the risk-neutral overpricing is precisely the VRP we
are harvesting.

**Consensus.** 0.16-0.30 is the operational band; going below 0.16
leaves too much premium on the table, going above 0.30 exposes too
much assignment risk for most sellers.

**In our system.** Our 0.20-0.35 band is slightly more aggressive
than the conservative standard. Fine for large-cap names. Should
narrow to 0.16-0.25 for speculative names (our ticker_profile allows
per-ticker adjustment, but we do not yet vary delta by profile --
add that in v2).

### 26. Liquidity gates

Our current gates (OI >= 250, volume >= 10, bid-ask <= 15%, bid >=
$0.10) are reasonable but below the institutional bar. Serious sellers
use:

- OI >= 1000 on at least the short leg.
- Daily volume >= 100 on the selected contract.
- Bid-ask spread <= 5% of mid, not 15%.
- Minimum credit of $0.25 per contract.

For our 9-ticker universe (all very liquid large caps), even the
tighter gates would still fit. Tightening would reduce the number of
candidate expirations but improve fill quality and reduce slippage
meaningfully. Worth tightening in v2 once we have confirmed the
pipeline routinely picks a valid candidate.

### 27. Event filters

Mandatory pre-entry check list:

- **Earnings**. Is the chosen expiration after the ticker's next
  earnings date? If yes, skip or shorten the expiration.
- **Fed meeting**. For rate-sensitive names (e.g., the megacap cloud
  tickers whose multiples depend on rates), avoid selling into an
  FOMC week.
- **Triple-witching / quad-witching**. Monthly OPEX (3rd Friday) has
  elevated gamma; quarterly OPEX (March, June, September, December)
  has elevated *and* unpredictable flow.
- **CPI / NFP / PPI / PCE**. Macro prints that reliably move the S&P.
  Sell AFTER the print if possible; avoid selling the morning-of.
- **Known company-specific events**. Product launches, investor days,
  SEC deadlines. These are irregular; best captured via the
  catalyst-scanner agent's output.

**In our system.** The `catalyst-scanner` agent already surfaces
earnings and rating changes. The options pipeline should cross-reference
the catalyst output and suppress trade suggestions where a material
catalyst falls inside the option's holding period. Pipeline hook: run
after the catalyst scanner, before `render_options_ladder.py`.

### 28. The "do not sell" checklist

Before surfacing a CSP / CC / spread candidate, the pipeline should
verify:

1. IV rank >= 30 (if known); soft-flag if unknown.
2. No earnings in the holding period.
3. Ticker is not in a material catalyst window (analyst day, product
   launch, regulatory deadline flagged by catalyst-scanner).
4. Ticker's current realized 20-day vol is NOT materially above implied
   (which would mean vol is UNDER-priced, not over-priced; you would
   be selling too cheap).
5. Liquidity gates passed (OI, volume, spread, bid).
6. Spot has not moved >= 3% intraday (do not sell into a freshly-expanded
   intraday range; wait for stabilization).
7. VIX is below some threshold if the pipeline is in "cautious" mode
   (VIX > 35 = crisis; selling single-name premium in a crisis is
   structurally wrong unless you are specifically harvesting elevated
   VRP with deliberate tail hedges).

Only candidates that pass ALL of the above should appear in the public
dashboard. This is a natural extension of `options_candidates.py`.

---

## Part V -- Risk management

This is the section that matters most. Strategy selection is fun;
sizing is the only thing that matters for long-run survival.

### 29. Position sizing (why Kelly fails and what to use instead)

The Kelly criterion gives the growth-optimal bet size when you know
your edge and your odds. For a premium seller:

```
kelly_fraction = (p * b - q) / b
  where
    p = probability of winning (e.g., 0.70 for a 0.30-delta short put)
    q = 1 - p
    b = payoff ratio (premium received / max loss)
```

For a typical 0.30-delta 30-DTE short put on a $100 stock collecting
$2 in premium: p ~ 0.70, q ~ 0.30, b = premium / max_loss = 2 / 98 ~
0.020 (you collect $2, you can lose up to $98 if the stock goes to zero
in the tail). Kelly suggests:

```
kelly = (0.70 * 0.020 - 0.30) / 0.020 ~ -14.3
```

That is -1430%. The scalar is negative and large. What it is saying:
on a *per-single-trade* basis, without diversification or management,
naive Kelly says DO NOT bet. The payoff ratio (gain / loss) is so
skewed in the wrong direction that the 70% win rate cannot rescue it.

The reason the wheel actually works is a combination of three effects
that naive Kelly ignores:

1. **Management**. Closing at 50% max profit or at 21 DTE means the
   realized max loss is not strike-minus-premium; it is bounded by
   rolling mechanics and typically much smaller.
2. **Diversification**. Ten independent trades on different tickers
   dramatically reduce the variance of the book, effectively raising
   edge per unit variance.
3. **Directional bias**. On names you would buy at the strike anyway,
   "max loss" is not really loss -- it is buying a stock you wanted at
   a discount. The Kelly formulation over-states the downside.

These three effects combine to make premium selling positive-EV on a
portfolio basis, even though naive per-trade Kelly is strongly
negative. The math is not "quarter-Kelly with diversification
assumptions baked in" (an earlier handwave) -- it is "Kelly plus
variance reduction via management, plus non-linear utility of
assignment, makes the strategy profitable at modest size."

The sober conclusion: **do not size using Kelly** for short-option
strategies. Size using the practitioner consensus numbers below,
which are empirically-calibrated rather than theoretically derived.

A corrected Kelly for a diversified wheel is much more complex.
**Practitioner consensus, with specific numbers:**

- **Daily theta target**: 0.06 - 0.10% of account equity (tastytrade /
  Option Alpha canon). $100k account targets $60-$100 per day.
- **Max short-premium gross notional**: 50% of account equity
  (aggressive); 30% (conservative). The VegaGang-hedged camp runs at
  25-30% with a small perpetual tail hedge.
- **Max single-ticker concentration**: 5-7% of account in notional at
  risk. 9-ticker equal-weight deployment would target 3-4% per name.
- **Max sector concentration**: 25% of total short premium in any one
  sector (most-cited threshold on r/thetagang).
- **Cash reserves**: 30% minimum idle cash at all times for assignment
  capacity and margin shocks.
- **DTE entry**: 30-45 days (tastytrade standard), 25-50 day outer
  bounds (our current range).
- **Delta**: 0.15-0.30 for undefined-risk premium, 0.30-0.40 for
  covered calls on long holdings.
- **Profit target**: close at 50% of max profit.
- **Loss management**: close at 200% of credit received (a 2x stop on
  premium received) OR roll at 21 DTE, whichever comes first.
- **IV rank filter**: IVR > 30 for entry (soft filter); VRP > 3 vol
  points (harder, more useful filter).
- **Liquidity minimum**: OI > 250 on the short strike, bid-ask spread
  under 5% of mid.

**Defined vs undefined risk camps:**

- **Small accounts (< $50k)**: defined-risk only (vertical spreads,
  iron condors). Undefined short puts on megacaps consume too much BP.
- **Mid accounts ($50k-$250k)**: mix. Undefined puts on index/megacap,
  defined spreads on single names.
- **Larger accounts ($250k+)**: undefined is fine on quality names IF
  cash can cover 2x assignment.

**In our system.** The public dashboard should not size for the reader.
The private email CAN, once we read positions.json:

- Compute total short-premium BP used across all open positions.
- Express as percent of portfolio equity.
- Flag if crossing 35%.

### 30. Portfolio-level greek exposure limits

A single short put looks safe. Nine short puts on correlated megacaps
are a single Nasdaq short-volatility bet in disguise. At the portfolio
level we care about:

- **Net book delta** relative to account equity.
- **Net book gamma** (the hidden concentration).
- **Net book vega** (the hidden vol exposure).
- **Net book theta** (the headline income number).

Soft rules that serious practitioners adopt:

- Net beta-weighted delta as a multiple of account equity: keep under
  0.6 in normal regimes (i.e., you are no more than 60% long SPX-
  equivalent).
- Net vega as percent of monthly expected premium: keep vega absolute
  value under 2x the monthly theta income. This caps the "a 2-point IV
  spike cancels a month of income" exposure at 2 months.
- Net gamma as a function of expected daily P&L variance: opaque, but
  in practice capped by DTE and delta discipline. If DTE >= 21 and
  delta <= 0.30 across the book, gamma is bounded.

**In our system.** The private email should report these four numbers
on every refresh. The public dashboard should show them in aggregate
(no personalization) if we can agree that is safe.

### 31. Correlation-adjusted sizing

Nine megacaps are not nine independent bets. NVDA and MU move together
on semi-cycle news (and would do so with AVGO if it were in the
universe; it is not today but is a likely future add). META / GOOG / AMZN / MSFT / AAPL all move
together on megacap-tech-flow days. TSLA moves somewhat separately.
BROS is roughly idiosyncratic.

Naive sizing of 1 contract per name ignores this. The sector-tilt
adjustment:

- Group tickers by correlation cluster (e.g., semis, megacap cloud,
  consumer, single-name).
- Apply a per-cluster cap on total short vega.
- When a new candidate would push a cluster over cap, suppress it.

**In our system.** For v2 this is a cluster-cap rule on top of the
current per-ticker selection. For v3 this is a portfolio-optimizer
that picks the *best subset* rather than the best candidate per
ticker, subject to cluster constraints.

### 32. The 21-DTE rule and when to break it

Tastytrade's empirical finding: closing or rolling at 21 DTE improves
win rate and reduces tail loss compared to holding to expiration. The
reason is gamma acceleration -- the last three weeks are where short
options go bad fastest.

**The rule**: close the position when either (a) 21 days remain OR
(b) you have captured 50% of max profit, whichever comes first.

**When to break it**: if the trade is deeply winning (e.g., 80%+ of
max) and the remaining premium is de minimis, rolling out to a new
45-DTE cycle is better than holding residual pennies.

**In our system.** This is a *management* rule, not an *entry* rule.
Our current pipeline only picks entries. Implementing management
requires either (a) a broker API integration to actually close
positions or (b) a "positions ledger" that logs when a trade is
opened and flags at 21 DTE in the email with "your short NVDA put at
$180 has 21 days left -- close or roll."

Option (b) is achievable with positions.json + a small renderer. Call
it `render_position_manager.py` for the private email only.

### 33. Rolling mechanics

Rolling = close the current short option, open a new one with more
favorable terms. Legitimate reasons to roll:

1. **21-DTE reached**, want to continue the theta stream -> roll out
   to the next ~45-DTE expiration at a similar delta.
2. **Losing trade** (underlying moved through strike) -> roll out and
   down (for short puts) or out and up (for short calls) to give the
   trade more time and reduce the short strike's ITM-ness.
3. **Winning trade** at 50%+ of max -> roll to a newer-dated, closer-
   strike position with similar delta, capturing the profit and
   keeping exposure.

**Rule of thumb**: only roll for a credit. If you cannot roll for a
credit (i.e., the new position does not pay enough to cover the cost
of closing the old one), you are just papering over a losing trade.
Take the loss.

**In our system.** Rolling is a management decision, not an entry
decision. The pipeline should surface rolling opportunities in the
private email once we log open positions in positions.json with
open_date and current_value.

### 34. Assignment management

If a short put is assigned, you now own 100 shares at the strike.
Standard responses:

1. **Keep them and sell CCs**. The wheel proceeds. Only acceptable if
   the strike is a price you were already willing to own at.
2. **Sell them immediately at the market**. Take the loss, redeploy.
   Acceptable if your view has changed on the name.
3. **Hedge with puts below** to cap further loss. Defensive.

The worst response: panic-sell at a lower price, then re-buy when it
rallies. This is the "sell the dip, buy the rip" trap that destroys
wheel accounts.

**In our system.** The private email should track assignment events in
positions.json and surface the choice clearly on the next refresh.

### 35. Tail hedging

The rare catastrophic loss is what kills undiversified premium sellers.
Three approaches:

1. **Size small enough that tail losses are survivable**. The cheapest
   hedge. If the worst-case drawdown is 30% and you can live with that,
   no explicit hedge is needed.
2. **Perma-long VIX calls or SPX puts** as a small (1-3% of equity)
   ongoing cost. Pays off in crises. Structural drag 80% of the time;
   life-saver in the remaining 20%.
3. **Dynamic hedge**: increase long-VIX exposure when VIX term
   structure goes into backwardation (a reliable pre-crisis signal).

Most retail sellers skip hedging entirely. This works until it doesn't.

**In our system.** For v2, just display a VIX term-structure tile so
the reader can see contango vs backwardation at a glance. No explicit
hedge recommendations (public dashboard constraint).

---

## Part VI -- Advanced analysis (the dealer view)

Moving from "pick good strikes" to "pick good times." The ideas in this
section are how sophisticated vol sellers time their entries.

### 36. Skew: the shape of the smile

At-the-money IV is one number. The full **skew curve** plots IV across
strikes or deltas at a given expiration. Three universal empirical
observations on equities:

1. **Downside skew** (puts more expensive than calls in vol terms). The
   market persistently prices downside protection at a premium. This is
   the direct evidence of the insurance-demand flow.
2. **Skew steepens in risk-off**. When fear rises, put skew widens.
3. **Skew varies by name**. Megacap cloud stocks show moderate skew;
   meme/high-beta show steep skew in both directions; utility-like
   names show flat skew.

**Practitioner use.** The 25-delta risk reversal (RR25) is the classic
skew metric: `RR25 = IV(25d_call) - IV(25d_put)`. Large negative values
= steep put skew = fear. Large positive values = call skew = bull
speculation. Time series of RR25 is a regime indicator.

**A premium seller's use of skew:**
- Steep put skew = puts are richly priced, calls relatively cheap.
  Prefers short put strategies over short call strategies on that name.
- Steep call skew = calls are richly priced, puts relatively cheap.
  Prefers short call strategies on that name (though usually requires
  a long-share position or a bull-call-spread structure).
- Flat skew = neither side is meaningfully richer; pick based on
  directional view or IV rank.

**In our system.** Compute RR25 from the chain data we already fetch.
Add a `skew_rr25` field per ticker in `options_chain.json`. Display as
a per-ticker indicator (steep put / balanced / steep call). Use as a
tiebreaker when CSP and CC both look attractive.

### 37. Term structure: what a premium seller wants

ATM IV at different expirations forms a **term structure curve**.

- **Contango** (normal): longer-dated > shorter-dated. Implies vol is
  expected to rise slowly over time. Favorable for premium sellers --
  short-dated is relatively cheap vs. longer-dated, so calendars or
  the simple "sell the front month" works.
- **Backwardation** (stress): shorter-dated > longer-dated. Implies
  market is pricing near-term stress that is expected to resolve.
  Seen before earnings, before FOMC, during crises. *UNFAVORABLE* for
  naked short-front-month premium selling -- you are catching the
  expensive vol right before the event that priced it.

**Practitioner use.** Front-month / back-month IV ratio is a
single-number summary. Ratio > 1 means backwardation on that name =
event risk priced in = step aside.

**A premium seller's use of term structure:**
- Normal contango = sell the ~30-DTE expiration.
- Backwardation on a ticker = wait for the event to resolve, then
  sell AFTER the event when IV collapses back to contango. This is
  literally the "sell the IV crush" trade.
- VIX term structure (front VIX future vs 2nd VIX future) is the
  market-wide version. VIX backwardation = step aside on SPX/QQQ
  short premium.

**In our system.** The chain data already has multiple expirations.
Compute ATM IV at the current (~30d) and next (~60d) expiration per
ticker, ratio them, and surface as a "term structure" field. Same for
VIX (VIX term structure is a macro signal already covered in the
macro section but should be cross-referenced from the options section).

### 38. Dealer gamma exposure (GEX)

Market makers are net short gamma to public demand. When they hedge
their books, their hedging activity moves the tape. Gamma exposure
analytics quantify this.

**The SqueezeMetrics GEX formula** (index level):
```
GEX = sum over strikes of:
  (call_OI * call_gamma) - (put_OI * put_gamma)
  all multiplied by spot^2 * 0.01
```

Or, informally: how much underlying the dealers must buy (if positive
GEX) or sell (if negative GEX) for every 1% move.

**The two regimes:**
- **Positive GEX (long gamma, dealers are "long vol"):** dealer hedging
  REDUCES realized vol. Rallies are sold into, dips are bought.
  Intraday range contracts. A disciplined premium seller should
  prefer selling in this regime -- realized vol will undershoot
  implied vol, maximizing VRP capture.
- **Negative GEX (short gamma, dealers are "short vol"):** dealer
  hedging AMPLIFIES realized vol. Rallies are chased, dips are sold.
  Intraday range expands. Premium sellers face *higher realized vol
  than implied*, which is the VRP inverted -- exactly the wrong regime
  to sell premium.

**The "zero-gamma" flip level** is the spot price at which dealer GEX
flips sign. Daily awareness of whether SPX is above or below zero-gamma
is one of the highest-signal regime indicators for short-vol traders.

**In our system.** Single-name GEX is harder to compute reliably from
our data (we would need the full chain, not just trimmed). Index-level
GEX on SPX/QQQ is computable if we fetch SPX/QQQ option chains. For v2
consider adding this as a macro-context tile: "SPX is above / below
zero-gamma today -- this regime favors / disfavors short vol." Free
third-party tools (SpotGamma partial data, Menthor-Q summaries, Reuters
occasional reports) can be sourced by the macro-snapshot agent if we
cannot compute it ourselves.

### 39. Charm and vanna flows around OPEX

Two mechanical effects drive predictable money at known moments:

**Charm flow.** As time passes, OTM options drift toward zero delta.
Dealers short puts (long delta hedge) must sell underlying as charm
flows. Dealers short calls (short delta hedge) must buy underlying.
Net equity-index charm flow is typically *positive* (equity buying)
approaching monthly OPEX, because there is more OTM call open interest
than OTM put open interest in index options. This is the source of
the "pre-OPEX drift higher" effect.

**Vanna flow.** When IV falls, put delta shrinks and call delta
shrinks. Dealer hedges unwind: buying equity back. Falling VIX into
OPEX therefore forces equity buying. This is why VIX-down weeks into
OPEX tend to rally.

**The classic OPEX trade:** equities tend to drift up into monthly
OPEX on charm + vanna flows, then sometimes dump the week after as
the flows unwind. The pattern is real but inconsistent. Selling
premium should account for it: avoid selling calls into a known
charm/vanna rally; avoid selling puts into the post-OPEX unwind.

**In our system.** The calendar awareness is simple: a boolean
`in_opex_week` flag on the macro context. The pipeline can use it to
soft-flag suggested entries ("charm/vanna flow may affect tape this
week") without changing picks.

### 40. 0DTE spillover

See [Section 66a](#0dte-spillover-considerations) in Part IX for the
full treatment of 0DTE second-order effects on the 25-50 DTE seller,
including the pipeline refresh-timing fix. 0DTE is discussed there
rather than duplicated here.

### 41. Realized vs implied volatility (the VRP captured)

The acid test of whether our premium selling is actually earning the
VRP: at month-end, compute realized 20-day vol per ticker, compare to
the average implied 30-day vol we sold into. The difference is the
VRP we captured (before fees, slippage, and assignment P&L).

Per-ticker tracking over months reveals:

- **Tickers with consistently large VRP** are our best hunting grounds.
- **Tickers with negative VRP** (realized > implied) signal either a
  regime change or that this name is not a good short-premium target.
- **The aggregate VRP** across the book tells us whether we are in a
  good regime for the strategy at all.

**In our system.** This is the single most valuable calibration output
we could build. Log the IV we sold at in a `trades_opened.jsonl`.
Monthly cron computes realized vol per ticker per month, joins to the
IV sold, produces a ledger row. The private email reports "this month
we captured X vol points of VRP on average across the book."

### 42. Volatility surface fitting

Advanced: fit an SVI (Stochastic Volatility Inspired) or SABR model
to the full chain. Gives you:

- A smooth surface so you can interpolate to strikes/expirations not
  listed.
- A decomposition into level, skew, curvature, and term structure
  parameters that are more stable than raw IV.
- Arbitrage-free pricing (important for spread strategies).

This is overkill for our current needs. Flagging as a v5+ addition
if the pipeline evolves into something closer to a quantitative
signal engine.

---

## Part VII -- Visualization compendium

How to *show* the data. The constraint: the public dashboard renders
as static HTML at twice-daily cadence, no client-side interactivity
beyond what's already there. The private email is Gmail-compatible
inline HTML (tables only).

### 43. P&L (payoff) diagram

The classic "hockey stick" plot of P&L at expiration versus underlying
price. Every option strategy should be reducible to one of these.

**Single short put.** Looks like an inverted cliff: flat at max
premium above the strike, sloping down linearly below the strike,
breakeven at strike minus premium.

**Short strangle.** Tent shape: flat max at the center, sloping down
on both sides.

**Iron condor.** Trapezoid: flat max at the center (between the two
short strikes), sloping down outside each short strike, bounded by
the long wings.

**Implementation.** Inline SVG is perfect for this. Each trade card
gets a ~200x80 px SVG showing the payoff with current spot marked.
Python can generate the SVG as a string in the renderer. No JS
needed. This would be a major visual upgrade to the current
text-table trade cards.

### 44. IV rank dashboard tile

A single number with visual context. Three good designs:

1. **Gauge** (semicircle): 0 to 100, a needle showing current IV rank.
   Colors: green below 30 (do not sell), yellow 30-50 (marginal), amber
   50-70 (good), red 70+ (very rich). Familiar and readable at a glance.
2. **Bar**: horizontal bar filled by IV rank percentage, with
   color-coded thresholds.
3. **Historical line**: a sparkline of IV-rank-over-time for the last
   90 days. Tells you whether IV rank is rising (entries getting
   cheaper) or falling (entries getting more expensive).

Recommend: a single **sparkline + current value + threshold bar** hybrid
per ticker. Fits in a card, communicates trend + level + regime.

### 45. Skew smile plot

IV on the y-axis, strike (or delta) on the x-axis, for a given
expiration. The classic "smile" shape.

**Implementation.** Per-ticker inline SVG with ~10 data points. Show
the ATM IV as a horizontal reference. Mark the short-put strike and
short-call strike as vertical markers. A glance tells you whether the
selected strikes are on the "rich" side of the smile (good) or the
"cheap" side (bad).

### 46. Term structure curve

ATM IV plotted against DTE for 3-5 listed expirations on the ticker.
A flat curve = balanced. Upward slope = contango (normal). Downward
slope = backwardation (event risk).

**Implementation.** Per-ticker inline SVG line chart, 5 data points.
A single-color line with tick marks. Overlay a horizontal "today's
sold IV" reference line so the reader can see where the pipeline is
picking from on the curve.

### 47. Strike ladder with OI and volume

The "options wall" view. Strikes on the y-axis, OI (and volume) as
horizontal bars extending from each strike. Coloring: calls in one
color, puts in another.

**Why it matters.** Concentration of OI at a strike can exert a
pinning effect near expiration. Major strike clusters ("max pain"
levels) telegraph likely pin zones.

**Implementation.** Inline SVG per ticker, ~30 strikes deep. A major
visual upgrade; shows at a glance where the action is.

### 48. GEX profile

Bar chart of dealer gamma exposure per strike, showing zero-gamma
flip level. Useful for SPX/QQQ macro context, less for individual
megacaps.

**Implementation.** SVG bar chart if we have the data. Or embed a
SpotGamma-style image manually (they offer free snapshots) for the
macro card.

### 49. Probability cone

A fan-chart showing the expected price range over time, derived from
ATM vol. At 1 standard deviation, ~68% of price outcomes fall within
the cone; at 2 SD, ~95%.

**Implementation.** Per-ticker inline SVG, computed from current IV
and DTE:
```
expected_move_at_t = spot * iv * sqrt(t_days / 365)
```
Plot the 1SD and 2SD bounds out to the trade's expiration. Mark the
short strike. Visually answers: "how much room do I have before the
strike is in the cone?"

### 50. Theta decay heatmap

A 2D matrix: columns = DTE buckets, rows = delta buckets, cell color =
per-day theta yield. Shows at a glance where the best theta/dollar
lives.

**Implementation.** SVG heatmap at the portfolio level. Less useful
per-ticker, very useful as a portfolio-level diagnostic in the
private email.

### 51. Portfolio greek roll-up

A 4-row table in the private email:

```
           current    vs yesterday    as % of equity
delta      +1,240           +80         58%
gamma        -120            -5          -
theta       +$185          +$10          -
vega        -$340          -$20        (2 months theta)
```

The "as % of equity" column is the grounding -- are we taking too
much risk relative to the account?

### 52. Calibration chart (actual vs implied hit rate)

The pipeline's own track record. For every closed trade, log:
- Short delta at entry.
- Expired worthless? (yes/no)

After ~50 closed trades, plot: bucket by short-delta (0.10, 0.15, 0.20,
0.25, 0.30), and for each bucket show "actual worthless rate" vs "1 -
avg_delta = implied rate". A calibrated system sits on the 45-degree
line. Persistent overshoot = our picks are better than random; persistent
undershoot = we are selling at the wrong times.

This is the most powerful honesty mirror the system can build.

### 53. Per-trade cards (enhanced)

Current cards are text-table rows. Upgraded cards could include:

- Inline SVG payoff diagram (~200x80 px).
- Inline SVG probability cone showing strike relative to 1SD expected
  move.
- Explicit breakeven price (strike - premium for short put).
- Explicit "what could go wrong" paragraph in plain English.
- Catalyst flags ("earnings in 14 days -- spans expiration") if any.
- Historical win-rate for similar trades on this ticker from our own
  ledger.

The delta from today's Option Selling Watch table to upgraded cards
is the highest-visibility visual improvement we can make.

### 53.1. Rendering approach (brief)

Pure inline SVG generated by Python renderers for every chart in
the roadmap. Matplotlib `savefig(format='svg')` for anything too
complex for hand-written SVG strings. No client-side JS dependency,
works in Gmail, canonical JSON stays the source of truth. If a
future feature ever requires client-side interactivity, that is a
separate decision not required by anything in this compendium.

---

## Part VIII -- Practitioner knowledge, by community

This section distills what people who actually sell premium for a
living have converged on, organized by where the knowledge comes from.
Each subsection ends with "what it changes in our pipeline."

### 54. Tastytrade research -- the empirical canon

Tom Sosnoff's firm publishes an ongoing stream of studies based on
its proprietary trade dataset. The headline "200,000+ trades" figure
that circulates in retail options blogs is *self-reported and not
independently audited*; individual published studies cite smaller
samples (e.g., 4,872 iron condor trades on SPY in one widely-cited
study). Treat the aggregate marketing number with appropriate
skepticism; treat the per-study sample sizes as real.

Their findings, with independent-replication status noted where
applicable:

- **The 45-DTE entry window** produces the best theta/gamma trade-off.
  Sellers entering at 45 DTE and managing at 21 DTE show ~15-20%
  better risk-adjusted returns than holding to expiration. *Held up
  in third-party tests.*
- **The 50% max-profit take-off rule.** Closing winners at 50% of max
  profit rather than holding to expiration improves Sharpe on the
  strategy by reducing the tail where a winner turns into a loser in
  the last week.
- **The 21-DTE "gamma wall."** ATM option gamma is 3-5x higher in the
  last 21 days than in the 30-45 DTE band. The rule: close or roll at
  21 DTE.
- **Strangles over single legs for diversified books.** 11-year
  project-finance.com study of short strangles at 30 DTE, managed at
  21 DTE or 50% profit: 60% weekly win rate, smoother drawdowns
  (-11% max vs -13.7% for straddles).
- **Trade small, trade often.** Their size-and-occurrence discipline:
  daily theta target ~0.06-0.10% of account equity. A $100k account
  targets $60-$100 of daily theta, not $500.

The tastytrade findings are the empirical spine that the current
`options_candidates.py` already encodes in its 25-50 DTE / 0.20-0.35
delta window. Confirmed, not decorative.

**Pipeline implication.** Add a "manage at 21 DTE or 50% profit"
signal line in the private email once positions are tracked in
`positions.json`. This is where the theoretical meets the actionable
(see Part XI).

### 55. The r/thetagang consensus

r/thetagang is the retail premium-selling community. Its public
blowup threads are the best free teacher we have on what NOT to do.
The filtered consensus as of 2025-2026:

**Strategies currently in favor:**
- Wheel on SPY / QQQ and cash-rich megacaps (MSFT, GOOG, AAPL) remains
  the default. This is our universe almost verbatim.
- Migration from naked CSPs to put credit spreads when buying power
  binds. The "defined-risk wheel."
- Jade lizards and iron condors on indices when markets are rangebound.

**Canonical blowup causes (2023-2025):**
- **Naked-call wipeouts.** The "$100k loss became $600k in minutes"
  thread is cited across the sub. Naked calls on meme names
  (Opendoor +43% in a day, Krispy Kreme +39%, GoPro +73% in 2025)
  destroyed accounts.
- **Concentration blowups.** August 2024 yen carry-trade unwind: VIX
  printed 65.73 intraday on August 5, 2024 (close 38.57 that day), and
  SPX dropped about 6.1% over the August 1 - August 5 window. The
  intraday spike was brief but real, and sellers with stop-loss rules
  that triggered on intraday marks got executed at the worst prices.
  Rule: use close-of-day marks for risk triggers when the intraday
  print is a spike; otherwise momentum traders harvest your stops.
- **Small-cap liquidity traps** (BROS-style): "juicy premium" becomes
  instant bag-holding when the chain is thin. Directly relevant to
  our BROS ticker.
- **Earnings assignment.** Anyone who sold puts on a name without
  checking the earnings calendar, then took a 15% down gap.

**The "unwritten rules," ranked:**
1. Never sell naked calls. Asymmetric unlimited risk with zero
   asymmetric reward.
2. Never sell puts through earnings unless IV rank > 50 AND you would
   happily buy the stock 20% lower.
3. Take profits at 50% of max.
4. Manage losers by 21 DTE, not at expiry.
5. If you cannot articulate in one sentence why a stock's IV is
   elevated, do not sell its premium.
6. Never size any single position > 5% of account.

**Survival data.** Precise numbers are contested across studies, but
the direction is unanimous:
- FINRA's day-trading data cites ~72% of day traders losing annually.
- SEBI's 2023 India derivatives study (published September 2023,
  covering FY2022; often miscited as US) shows 91% of retail
  derivatives traders losing; the 2024 update increased the figure.
- Hedge Fund Alpha's analysis of 8M retail trader samples shows
  74-89% lose during volatility events.
- Tim de Silva et al. (London Business School, 2019-2021) show net
  retail options-premium losses totaling ~$2B over that study window.

Wheel traders with under $25k accounts who leverage aggressively
typically blow up within 18 months. Consistent winners overwhelmingly
trade indices or megacaps, not single-name long-tail stocks. The
consensus claim we can state defensibly: **the majority of retail
options traders lose money over any 12-month horizon; the fraction is
higher during volatility events than during calm regimes.**

**Pipeline implication.** The BROS profile needs special handling.
Its "high_beta" tag in `options_candidates.py` raises the IV floor
but does not account for the thin-chain liquidity trap. We should
tighten liquidity gates on BROS specifically (OI >= 1000, not 250)
or consider surfacing it only as an informational card, not a
suggested trade.

### 56. Option Alpha's systematic edge

Kirk Du Plessis's Option Alpha has converged on systematic,
rules-based execution:

- **50% profit target. 200% credit-received stop-loss.** Simple pair
  of rules that capture tastytrade's findings in executable form.
- **IV rank filter > 30 for entries.** Lower than tastytrade's
  traditional 50; their backtests showed the incremental occurrences
  between 30-50 were still profitable on aggregate.
- **"Give it a chance" management.** Small losers should be held
  patiently unless the underlying's thesis has broken. Most losers
  recover in the 30-45 DTE window. *Tastytrade's own research
  supports this.*
- **Automation over discretion.** Their 2025 pivot to rules-based
  "bots" runs backtests that dominate discretionary versions of the
  same rules.

**The Option Alpha SPY put-credit-spread canonical study** (2023,
updated 2025): 30 DTE, short strike at 0.30 delta, long strike at
0.10 delta, managed at 50%/200%. Sample size ~1000 trades. Win rate
73%, Sharpe ~1.2 on a lightly-diversified book. *This is the
reference "baseline return" for a disciplined defined-risk seller.*

**Pipeline implication.** Our spine is conservative enough on single
names. Adding a bull-put-spread variant that replicates the Option
Alpha spec (0.30 short, 0.10 long, 30 DTE) gives readers a
capital-efficient alternative for names where the CSP buying power
is prohibitive.

### 57. SpotGamma / SqueezeMetrics / Menthor-Q

The three dominant dealer-flow analytics shops. Each has a daily
product and a research archive.

**SqueezeMetrics (2015-present).** Published the original open
white paper on GEX and DIX. Their "Volatility Trigger" (now
repackaged at SpotGamma) is the zero-gamma flip level. Their DIX
(Dark Index) replication on GitHub by jensolson is free.

**SpotGamma (2019-present).** The most accessible product. Free
daily notes give the current SPX zero-gamma, call wall, put wall.
Their Founder's Notes layout -- top-of-page tile grid with key
levels (gamma flip, call/put walls, vanna), then narrative, then
charts -- is worth copying for our dashboard layout (per the
visualization research).

**Menthor-Q (2023-present).** Newer entrant. Best known for their
JPM Collar analytics and institutional flow decomposition. Their
free articles on charm and vanna around OPEX are the cleanest
explanations public on the internet.

**The signal menu across all three:**
- Zero-gamma flip level (SPX, QQQ). Above = stabilizing; below =
  amplifying.
- Call wall / put wall (largest OI concentrations). Pinning targets.
- 25-delta risk reversal time series. Skew regime.
- Vanna/charm exposure around OPEX.
- HIRO (Hedging Impact of Retail Options) -- proprietary to
  SpotGamma, measures intraday retail-driven dealer-hedge flows.

**Pipeline implication.** We should compute our own zero-gamma proxy
for SPX and QQQ using the public CBOE feed, and surface it as a
single daily tile ("SPX is above / below zero-gamma -- this regime
favors / disfavors short vol"). The jensolson/SPX-Gamma-Exposure
repo on GitHub is the canonical Python replication we can port.

### 58. Euan Sinclair and the quant blog scene

Sinclair (Bluefin Trading) is the serious academic voice on
vol-selling. His 2024 book with Andrew Mack, *Retail Options Trading*,
is the most recent authoritative text.

**Core Sinclair claims, distilled:**
- The variance risk premium (VRP) is real and persistent. Any
  strategy that sells implied vol has "a significant head start on
  being profitable if the premium is there."
- **Mechanics matter less than the environment.** You can be sloppy on
  strike selection if you are disciplined on regime detection.
  Conversely, perfect strike selection in a compressed-VRP regime
  still loses.
- Size for the worst historical regime you can imagine, not the
  average. "Survival > optimization."
- Implied vol by itself is uninformative -- only IV vs RV tells you
  whether the trade has edge.

**Rising voices worth tracking (2024-2026):**
- **Sharpe Two** (substack.com). Rigorous backtests combining IV rank
  with VRP filtering. Their "Blending IV Rank and VRP: A Path to
  Sharpe 2+" piece is the tightest empirical case for the two-filter
  approach.
- **Predicting Alpha**. Volatility-surface analytics tailored to
  retail. Paywalled but their free posts on the wheel are excellent.
- **Days to Expiry** (daystoexpiry.com). Practical research on the
  21-DTE rule and theta-decay curves.
- **Robot Wealth** (Kris Longmore). Occasional SPX vol studies with
  public code.
- **Moontower** (Kris Abdelmessih). Dealer-flow, skew, and
  market-making intuition. Best writing in the space for building
  mental models.

**Pipeline implication.** Sinclair's "IV vs RV" vs "IV alone"
distinction maps directly onto our need for a `vrp_tracker.jsonl`.
Until we compute realized vol per ticker, we have no ground truth on
whether we are selling into a VRP or into a realized-vol regime
shift.

### 59. r/VegaGang and the tail-risk critique

The counter-community. Their frame: premium sellers are "picking
pennies in front of a steamroller." Their specific critiques:

- **Theta-sellers are long delta in disguise.** Selling puts is an
  implicit bullish bet with capped upside and catastrophic downside.
  If equities grind higher, the wheel looks smart; if they crash,
  decades of premium evaporates in weeks.
- **Long-vol regimes cluster.** 2008, March 2020, August 2024. Three
  major vol-expansion events in 16 years. Any premium-selling
  strategy without explicit tail hedges has ~5-10% probability per
  year of catastrophic loss.
- **"Decades of selling evaporate in 3 sessions."** The Volmageddon
  2018 episode killed the XIV ETN overnight; the March 2020 episode
  liquidated multiple vol-selling funds.

**How a disciplined seller responds:**
- **Hold a small perpetual tail hedge** (2-3% of equity in VIX calls
  or far-OTM SPX puts rolled monthly). Taleb's framing: pay a small
  fixed premium to be long the tail you are otherwise short.
- **Keep 30%+ of capital in cash** at all times. Not deployed, not
  margin'd. Dry powder for the regime change.
- **Cap short-premium gross notional at 50%** of account equity.
  Most serious practitioners are at 30%.
- **Never write premium on names you cannot afford to be assigned
  twice on.** If a single assignment would eat 40%+ of account, size
  is too large.

**Pipeline implication.** The public dashboard cannot personalize
sizing, but it can show a daily "regime tile" that flashes amber
when VIX term structure goes into backwardation (the most reliable
leading indicator of a regime kill-zone). That is the one signal
that matters most for VegaGang's concerns.

### 60. GitHub: the actually-useful repos

Our pipeline is stdlib + yfinance. We should stay that way for the
core but port signal ideas from these repos:

**Data and analytics:**
- **jensolson/SPX-Gamma-Exposure** (https://github.com/jensolson/SPX-Gamma-Exposure)
  -- canonical GEX replication from CBOE public OI. Port for our
  zero-gamma proxy tile.
- **jensolson/Dark-Pool-Buying** (https://github.com/jensolson/Dark-Pool-Buying)
  -- DIX replication. Dark-pool buying intensity is a weak but real
  signal. Optional.
- **Matteo-Ferrara/gex-tracker** -- lighter GEX scraping of CBOE.
- **FlashAlpha-lab/awesome-options-analytics** -- the curated list of
  everything in this category. Good starting reference.
- **py_vollib_vectorized** -- stale (last release 2020) but still the
  fastest Python BSM greeks implementation. Pin the version if we
  decide to compute greeks ourselves rather than rely on CBOE's feed.
- **QuantLib-Python** -- actively maintained (v1.40, Dec 2025). The
  only serious open-source path for stochastic vol models, SABR, and
  arbitrage-free surfaces. Overkill unless we expand beyond simple
  CSPs.
- **XanderRobbins/Arbitrage-Free-Volatility-Surface** -- production-
  grade SVI fitting with Heston calibration. The newest serious
  entrant for full surface modeling.

**Execution and workflow (IBKR-based):**
- **brndnmtthws/thetagang** -- the reference wheel/CSP bot on IBKR.
  Its `thetagang.toml` config is worth reading as a spec for what a
  disciplined-seller spine looks like in code. Its post-2023 evolution
  added VIX hedging, exchange-hours gating, and regime-aware
  rebalancing -- all directly relevant to our roadmap.
- **ib-api-reloaded/ib_async** -- the community fork of ib_insync.
  The original author (Ewald de Wit) passed away in early 2024; all
  active development is on this fork. Use this, not ib_insync, if we
  ever add live broker integration.
- **tastyware/tastytrade** -- typed async Python SDK. Cleaner than
  ib_async for multi-leg constructs; broker-specific.

**Backtesting:**
- **QuantConnect LEAN** -- the only serious open-source options
  backtester with assignment mechanics, early exercise, and margin
  modeling out of the box. If we ever validate our wheel rules
  against historical data, this is the tool.
- **michaelchu/optopsy** -- lightweight Python-only options
  backtester with 28 built-in strategies and greeks filtering. Good
  for fast strategy screening.
- **rgaveiga/optionlab** -- v1.3.2 (Jan 2025). Strategy P&L
  evaluation with greeks and probability-of-profit. Even lighter
  than optopsy.

**Data sources (paid-vs-free tier):**
- **CBOE public delayed quotes** -- what we use. Free, no auth, 15-min
  delay. Fine for overnight planning.
- **Tradier sandbox** -- free paper-trading token with ORATS-sourced
  greeks and IV. Best free "complete" endpoint.
- **Polygon.io** -- $199/mo for full options EOD. Most-cited paid API
  among retail quants.
- **ORATS** -- $200+/mo. 25 years of EOD options data with 98
  proprietary indicators + a hosted backtest engine.
- **CBOE DataShop LiveVol** -- $105/mo plus exchange fees. What funds
  buy. Gold standard.

**Pipeline implication.** Immediate wins: port jensolson's GEX
replication for an SPX/QQQ regime tile. Read thetagang.toml to
calibrate our gate thresholds. Longer-term: if we add live execution,
use ib_async; if we add rigorous backtesting, use LEAN.

---

## Part IX -- Flash-trader techniques that retail can harvest

Flash traders (market makers, systematic vol funds, high-frequency
dealers) have capital, latency, and information advantages a retail
premium seller cannot match. But many of their edges have
slow-moving, calendar-predictable "footprints" in the tape that a
patient retail seller can harvest. This section catalogs those
footprints.

### 61. Monthly OPEX flow patterns

**The mechanic.** Monthly SPX equity options expire on the third
Friday. In the week before, dealer hedging of OTM options produces
**charm-driven equity buying** (as delta drifts toward zero on OTM
puts, dealers who were short puts and long stock as a hedge unwind).
This creates a statistically significant **upward drift into monthly
OPEX** on SPX since 1990. The Monday AFTER OPEX is, conversely, the
statistically weakest day of the month, as the pin flow unwinds.

**How to harvest:**
- **Open new 30-45 DTE CSPs** on the Monday of monthly-OPEX week.
  Front-month IV is typically elevated (about to crush), and the
  charm-flow tailwind supports the downside you just sold.
- **Close short CCs** ahead of OPEX Friday rather than holding for
  the pin. The "pin" often pins JUST above your short strike on
  names with heavy call-side OI.
- **Avoid opening new CCs** in the OPEX-week pinning window because
  call-side max-pain pinning moves price toward your short strike.
- **Avoid opening anything fresh** the Monday AFTER OPEX. The
  statistical weakness is real; wait 24 hours.

**Pipeline implication.** Add a calendar-aware `is_opex_week` flag to
the macro context. The options_candidates picker can soft-flag
candidates with the OPEX-week context ("flow tailwind" or
"post-OPEX-weakness window").

### 62. The JPM Collar roll

The single most reliable quarterly flow event in equities.

**The structure.** JPMorgan's Hedged Equity Fund complex (share
classes JHEQX / JHQAX / JHQDX / JHQRX) totals roughly **$20.1B in AUM
as of April 2026** (down from ~$22B peak in 2023). JHEQX is the
original share class and the one everyone means when they say "the
JPM Collar." On the last business day of each calendar quarter, it
rolls its collar:

- Sells a call at roughly 3.5% - 5.5% OTM (not "3-5% OTM" as is often
  claimed; the exact levels depend on the rebalance date's spot and
  the fund's mandate).
- Buys a put spread (typically a 5% - 20% OTM put spread, again
  approximate).
- Net position: long equity with a capped upside and a downside
  buffer.

The roll trades tens of thousands of SPX contracts in a concentrated
window. In the 2-3 weeks before the roll, the existing collar is
still active, and its gamma profile pins SPX near the short-call
strike (the "call wall").

**The specific execution window:** JPM rolls between **12pm and 2pm
Eastern Time** on the last business day of the quarter. If VIX blips
during that window, that is the roll.

**How to harvest:**
- **Expect SPX pinning near the prior quarter's short-call strike**
  in the last 2 weeks of a quarter. Sell CCs ABOVE that strike; sell
  CSPs below it.
- **Expect a vol blip between 12pm-2pm ET** on the last business day
  of a quarter. Do not open new positions during that window.
- **After the roll completes**, the new collar's short-call strike
  becomes the next quarter's pinning target.

**Pipeline implication.** Add `is_jpm_roll_window` as a calendar flag
for the last 3 business days of March, June, September, December.
Widen CC strikes during this window. Mention the current JPM collar
strikes (visible in SPX OI data) in the macro context so the reader
knows where the quarterly pin is likely to live.

### 63. VIX term-structure arbitrage (and the pre-event skip)

Retail cannot easily trade the VIX futures curve, but its shape is
the cleanest regime signal we have.

**Contango** (normal): VX1 < VX2 < VX3 < ... A smooth upslope.
Realized vol expected to be stable or drift higher. Favorable for
SHORT equity premium.

**Backwardation** (stress): VX1 > VX2 > VX3. The front month is
richer than deferred months. Market pricing near-term stress that
is expected to resolve. **UNFAVORABLE** for short equity premium.
Every major equity drawdown has been preceded by at least 2 days of
VIX backwardation. This is the single most reliable regime signal
in options.

**The VIX options expiration cycle** is not the same as equity OPEX.
VIX options expire on the **Wednesday 30 days before the following
month's SPX monthly expiration**. The Tuesday before VIX OPEX has
cheap short-dated vega; the Wednesday after often has a rich 30-day
VIX -- favorable for selling new 30-45 DTE equity premium.

**Pipeline implication.** Our macro context already surfaces VIX.
Upgrade it to display:
- `vix_spot` and `vx1`, `vx2`, `vx3` futures levels.
- `vix_term_structure_ratio = vx1 / vx2` (> 1 = backwardation = step
  aside).
- `vix_opex_date` and `days_to_vix_opex`.
- A boolean `favorable_for_new_premium_selling` derived from
  VIX-term-structure state.

### 64. Dealer gamma-hedge exploitation

**The regime map:**

| Regime          | Dealer behavior       | Realized vol | Seller action          |
|-----------------|-----------------------|--------------|------------------------|
| Above zero-gamma | Sell rips, buy dips  | Dampened     | Sell more premium      |
| Below zero-gamma | Chase moves both ways | Amplified    | Reduce size, skip      |

The zero-gamma level (SpotGamma's "Volatility Trigger") is
computable from public CBOE open-interest data using the
jensolson/SPX-Gamma-Exposure methodology.

**Per-ticker GEX** (single-name gamma exposure) is noisier but
meaningful for the biggest-OI names in our basket: AAPL, NVDA, TSLA,
META, AMZN. MU and BROS have thin chains; use QQQ GEX as the proxy
for them.

**How to harvest:**
- Above zero-gamma = dampening = sell more premium. Tighter strikes
  OK.
- Below zero-gamma = amplifying = reduce size by 50%, widen strikes
  (go to 0.16 delta rather than 0.30).

**Pipeline implication.** The zero-gamma proxy can be computed from
the options_chain we already fetch. Add `gex_regime` per ticker
("long_gamma" | "short_gamma" | "at_flip") and aggregate to an SPX
"market regime" tile. Use as a size multiplier in `options_candidates.py`:
size = base_size * (1.0 if long_gamma else 0.5).

### 65. Dispersion trading at the portfolio level

Dispersion traders are short index vol and long single-name vol,
betting that realized single-name vol > realized index vol (because
correlations are less than 1). They harvest the correlation decay
in their favor.

**Retail cannot run dispersion directly** -- it requires shorting
SPX/QQQ vol and simultaneously buying vol on basket constituents.
But the INSIGHT is valuable:

- **Correlations between megacap-tech tickers compress during
  long-gamma regimes** (when dealers dampen moves, cross-correlations
  rise).
- **Correlations expand during risk-off events** (everything moves
  together; dispersion traders get crushed).
- **For a premium seller, rising correlation = concentration risk
  rising.** Nine "diversified" short puts become a single Nasdaq
  short-vol bet.

**How to harvest:**
- Track 20-day rolling pairwise correlations among our 9 tickers.
- When correlations spike (indicator: average pairwise > 0.85),
  reduce portfolio gross premium by 25-50%.
- When correlations are low (< 0.65), the "diversified wheel"
  actually works as advertised.

**Pipeline implication.** Add `correlation_regime` as a portfolio-
level metric. Daily compute of 9x9 correlation matrix; track
average pairwise and max pairwise; flag when the portfolio is
effectively concentrated even if contract counts look diversified.

### 66. Pin risk and pin harvesting

On OPEX Friday, large-OI strikes exert a magnetic pull on the
underlying. The "max pain" strike is the strike at which total
option holder value is minimized -- i.e., the strike at which the
most option premium expires worthless. Because dealers dominate the
hedging, the tape tends to drift toward max-pain strikes into the
close.

**For a short premium seller:**
- **Pin risk is binary.** If your short strike is EXACTLY at max pain
  on OPEX Friday, you face asymmetric risk: stock may pin just
  above (you are assigned) or just below (you keep the premium).
- **Pin HARVEST** is the opposite: if you are short strikes AWAY from
  max pain, the pin WORKS FOR YOU (the tape drifts to the pin
  strike, away from yours, and your position decays cleanly).

**Practical rule:** never hold a short option through expiration
within $0.50 of a major-OI strike cluster. Close the day before.

**Pipeline implication.** If we ever track open positions, add a
"pin risk flag" at 48 hours before expiry that compares the short
strike to the nearest max-pain / high-OI cluster.

### 66a. 0DTE spillover considerations

0DTE (zero-days-to-expiration) SPX options are 59% of SPX options
volume as of full-year 2025 (Cboe data). They are NOT directly a
concern for 25-50 DTE sellers, but they create second-order effects:

- **Aggregate 0DTE gamma is dealer-LONG** (retail is net seller). This
  dampens intraday vol, which is PART of why the VRP on 30-45 DTE
  equity premium has remained positive in 2025-2026 (compressed
  realized vol, stable implied vol).
- **The 3pm-4pm ET reversal window** is where 0DTE hedging flows peak.
  Avoid entering new 25-50 DTE positions in the last 30 minutes of
  any session, especially on macro days (FOMC, CPI, NFP).
- **Monday morning SPX 0DTE concentration** telegraphs the week's
  dealer positioning. Niche signal but real.

**Pipeline implication.** Our afternoon refresh at 12:30 PT = 15:30
ET = 3:30 PM Eastern sits squarely inside the dangerous 0DTE
reversal window. Move it to 13:30 PT (4:30 PM ET, after the close)
so the data reflects settled EOD prices rather than mid-window
chaos. The email is planning tomorrow's actions, not intraday
trading, so a 30-minute delay costs nothing and improves data
quality materially. One-line change in the scheduled-tasks config.

---

## Part X -- The money-making playbook

This section answers "how do we actually make large amounts of money."
The honest answer: slowly, systematically, by not blowing up. What
follows is a distillation.

### 67. The disciplined-seller spine (current state)

Our current spine -- encoded in `options_candidates.py` -- is sound
for v1:
- 25-50 DTE.
- 0.20-0.35 absolute delta.
- OI >= 250, volume >= 10, bid-ask <= 15%, bid >= $0.10.
- Per-ticker IV floor by profile (22% on AAPL through 70% on OKLO).

This reliably surfaces reasonable trades without requiring the
sophistication of the rest of this document. It is good enough to
actually make money if sized correctly.

### 68. The expansion playbook: add these signals, in this order

Prioritized roadmap of signal additions, each with an expected
improvement in pick quality:

1. **Event filter against catalyst-scanner output**. Block trades
   spanning known earnings. Medium effort, high expected value.
   Prevents the single worst trade type.
2. **IV-rank hard gate once 60 sessions of iv_history accumulate**.
   Auto-enable in mid-summer 2026. No new data; just flip the gate.
3. **Skew (RR25) per ticker** and a "prefers puts / prefers calls"
   tag. Drives strategy selection between CSP and CC intelligently.
4. **Term structure ratio per ticker**. Skip tickers in single-name
   backwardation.
5. **Cluster-level vega cap**. Prevent 5 semiconductor CSPs in a
   single day.
6. **Realized-vs-implied tracker** (monthly VRP report by ticker).
7. **Bull-put-spread alternative candidate** for BP-constrained
   readers.
8. **Position-manager output** (21-DTE flags) in the private email.

Each of these is a small, testable, independently valuable addition.
None require rewriting the spine.

### 69. Specific high-conviction setups

**Setup A: IV-rank spike without earnings.** A single-name IV rank
jumps from 30 to 70 with no scheduled earnings within the next 60
days. This is usually a macro-induced repricing (sector rotation,
analyst spook, peer-company miss). The VRP is temporarily fat; fade it
by selling a 30-45 DTE put at 0.25 delta. Historical hit rate: very
high. This is the single best setup a disciplined seller has.

**Setup B: Post-earnings IV crush.** An earnings print is over, the
stock moved modestly (less than the expected move), and IV has
collapsed from 80 to 40. Selling premium *immediately after* earnings
captures the crushed IV without the gap risk. Works best on names that
tend to drift rather than whipsaw after earnings (megacaps more than
biotech).

**Setup C: VIX spike followed by term-structure normalization.** VIX
goes from 15 to 25 in a day, then starts to flatten/contango. This is
the canonical "blood in the streets, but not more blood coming" setup.
Sell SPX / QQQ / mega-cap puts at 0.20 delta, 30-45 DTE. Size small
(1/2 normal) because tails can extend.

**Setup D: Pre-OPEX week charm flow.** Sell OTM calls into monthly
OPEX week on tickers that have already run up into it. The charm flow
tends to pin, and the IV crush into OPEX Friday is reliable.

### 70. When to step aside

Equally important: the "do not trade" setups.

- VIX term structure in backwardation (front > back).
- Ticker-specific backwardation (usually pre-event).
- IV rank below 20 on the ticker.
- Any unresolved macro catalyst within the next 3 days (FOMC, CPI,
  NFP, OPEX, quarter-end).
- Aggregate book delta already at cap.
- You personally feel the urge to "get back" a previous loss. (The
  pipeline can't know this, but the user can.)

### 71. Expected returns: what to actually expect

Premium selling is not get-rich-quick. Realistic expectations for a
well-managed, disciplined wheel on large-cap names:

- Gross monthly premium on 30% BP-committed book: 1-2% of account
  equity per month.
- Drag from assignment-era losses: ~30-50% of gross.
- Net annualized: 5-12% above what the underlying produced on a
  long-only basis.

That extra 5-12% compounded over a decade is real money. It is not
10x in a year.

The "unlimited tokens" premise of this project does not change those
base rates. It does let us:
1. Time entries better (skew, term structure, catalyst filters).
2. Size correctly (cluster constraints, portfolio greeks).
3. Avoid the small number of bad decisions that destroy compounding.
4. Survive the regimes that kill less-disciplined sellers.

Those four improvements, stacked, could plausibly lift the net
annualized from the 5-12% band to the 10-18% band. That is what
"make large amounts of money" looks like in reality.

### 72. Why most retail sellers lose money

The r/thetagang graveyard is full of accounts that did the opposite of
what this document recommends:

- Over-sized into small-cap names with wide bid-ask spreads.
- Sold premium into earnings.
- Sold at low IV rank because the premium was small and they needed
  more contracts to "make it worth it" -- a sizing error disguised as
  entry discipline.
- Rolled losing positions indefinitely rather than taking the loss.
- Concentrated into one sector (commonly semiconductors or one meme
  stock).
- Added leverage via spreads at the worst possible time (right before
  a vol expansion).

Our pipeline's job is not just to pick trades. It is to structurally
prevent these six failure modes from happening.

---

## Part XI -- Integration roadmap with the current pipeline

This section connects everything above to concrete file-level changes
in `~/.claude/scheduled-tasks/stock-analysis-refresh/`.

### 73. Current state (as of 2026-04-20)

Already in place:
- `options_chain.py` -- fetches chain, trims, appends ATM IV to
  `iv_history.jsonl`.
- `options_candidates.py` -- picks best short put + short call per
  ticker with the disciplined-seller spine.
- `render_options_ladder.py` -- public card with two tables.
- Pipeline hook: runs after quote_feed, before the email assembly.

### 74. New canonical JSONs to emit

All new canonical JSONs live in
`~/.claude/scheduled-tasks/stock-analysis-refresh/logs/`:

- `options_skew.json` -- per-ticker RR25 + full 10-point skew samples
  + interpretation tag ("steep put skew", "balanced", "steep call skew").
- `options_term_structure.json` -- per-ticker front/back IV ratio,
  contango/backwardation tag.
- `options_cluster_limits.json` -- cluster assignments, per-cluster
  vega caps, current cluster utilization.
- `options_events.json` -- per-ticker next-earnings, next-material-
  catalyst (cross-referenced from catalyst-scanner output).
- `vrp_tracker.jsonl` -- monthly append: per-ticker realized 20d vol,
  avg implied sold, captured VRP in vol points.
- `positions_manager.json` -- per-open-position (from positions.json)
  DTE remaining, pct_of_max_profit, suggested action
  (hold / close / roll). **PRIVATE**. Read only by private email.

### 75. New renderers to build

All public renderers read only public-safe JSONs (nothing from
positions.json):

- `render_skew_card.py` -- a portfolio-level skew overview card.
  Simple table, one row per ticker, RR25 value + interpretation tag.
- `render_term_structure_card.py` -- a portfolio-level term structure
  overview card. Similar table format.
- `render_events_filter.py` -- writes an "upcoming catalysts" sidebar
  that feeds the main card. Not directly rendered; used by
  `options_candidates.py` as an upstream filter.
- Enhanced `render_options_ladder.py` with per-trade SVG cards (Part
  VII.43 and VII.53).

Private renderers (read positions.json, for private email only):

- `render_position_manager.py` -- per-open-position status lines for
  the email, with 21-DTE flags and rolling suggestions.
- `render_book_greeks.py` -- the 4-row portfolio greek table.
- `render_vrp_report.py` -- monthly captured-VRP report appended to
  end-of-month email.

### 76. Pipeline hooks

Order of operations in the refresh (new steps marked with *):

```
STEP 1c  fanout (existing agents) + fetch options_chain.json
*STEP 1c.1  compute options_skew.json from chain
*STEP 1c.2  compute options_term_structure.json from chain
*STEP 1c.3  compute options_events.json (joins catalyst-scanner output
            with chain expirations)
STEP 3   conviction calculation
STEP 4   catalyst scoring
*STEP 4.5  options_candidates.py (now with filters: event, skew, term
            structure, cluster) produces candidates
*STEP 4.6  vrp_tracker.jsonl append (if end of trading month)
STEP 6   HTML edits + renders (now including new cards)
STEP 7   integrity gate
STEP 8   deploy
*STEP 8.5  if positions.json exists: render_position_manager.py,
            render_book_greeks.py, (end-of-month) render_vrp_report.py
STEP 9   email assembly
STEP 10  audit
```

### 77. Ordered addition priority

Do them in this order to maximize value per unit work:

1. Event filter (catalyst-scanner integration). 1-2 hour task. High
   protective value.
2. SVG payoff diagrams in existing cards. 3-4 hour task. Major visual
   upgrade.
3. Skew (RR25) computation and card. Half-day task. Drives strategy
   intelligence.
4. Term structure card. Half-day task.
5. Cluster-level vega cap. Full-day task (requires portfolio-
   optimizer-lite logic).
6. Position manager for private email. Full-day task (requires
   positions.json structure finalized).
7. Bull-put-spread candidate alternative. Full-day task.
8. VRP tracker + monthly report. Full-day task (mostly end-of-month
   report logic).
9. Book-level greeks for private email. Half-day task once positions
   are tracked.
10. Calibration chart over closed trades. Full-day task once we have
    50+ closed trades.

---

## Part XII -- The calibration loop

The pipeline should learn from its own picks. This is what turns it
from "reasonable signal" to "systematically improving signal."

### 78. What to log per trade

For every trade the pipeline surfaces, record:

- Opened at (ISO timestamp).
- Ticker, strategy (csp, cc, bps, etc.), strike, expiration, DTE.
- Short delta at entry.
- IV at entry, IV rank at entry.
- Premium collected.
- Rationale tags (e.g., ["iv_rank_high", "post_earnings_crush"]).

Once closed:
- Closed at (ISO timestamp).
- Exit reason (expired_worthless, rolled, closed_at_50pct,
  closed_at_21dte, assigned).
- Realized P&L per contract.
- Realized vol over the holding period.

Structure: `trades_ledger.jsonl` in the logs directory. Private (do
not publish).

### 79. Actual vs implied hit rate

Group closed trades by entry delta bucket. Compute: fraction that
expired worthless / were closed profitably. Compare to 1 - avg_delta.
A calibrated system matches. An edge-showing system overperforms.

### 80. Captured VRP by ticker

For every ticker: average sold IV - average realized vol over the
same period. Monthly summary. Informs per-ticker IV floor adjustments
and the "good / not good" hunting grounds map.

### 81. How to update spine defaults from data

If data shows 0.20-delta picks outperform 0.30-delta picks on a
risk-adjusted basis for a given ticker profile, narrow the default
delta band for that profile. Same for DTE, same for IV floor. Small
adjustments every quarter based on accumulated data.

### 82. Bayesian posterior on win rate

After ~30 trades per ticker, maintain a Beta(alpha, beta) posterior
on "probability of winning a trade" per ticker. Beta(1,1) prior.
Update after each closed trade. Display in the ticker card as
"pipeline win rate on this ticker: 73% (based on 42 closed trades)."

---

## Part XIII -- The "do not" catalog

Extracted from every hard-won mistake in the community.

### 83. Do not sell naked premium on:

- Stocks you would not own at the strike.
- Stocks you cannot afford to own at the strike.
- Stocks whose chain is illiquid enough that you cannot exit without
  taking a large bid-ask haircut.
- Stocks entering earnings within the holding period.
- Stocks at IV rank below 20 unless you have a very specific reason.

### 84. Do not roll:

- Losing trades for a net debit. Ever. Just take the loss.
- Just to "avoid assignment." If you would own the shares anyway,
  assignment is fine.
- Into a weaker underlying chain (worse liquidity, wider spread).
- More than twice on the same position. If you have rolled twice and
  it is still losing, you were wrong about the underlying.

### 85. Do not oversize:

- More than 30-35% of account BP committed to short premium.
- More than 3-4 contracts of any single ticker.
- More than 1 cluster (sector) at any given vega cap.

### 86. Do not sell premium in these regimes:

- VIX term structure backwardation.
- VIX > 35 (without specifically harvesting crisis VRP with hedges).
- 3 days before FOMC on rate-sensitive names.
- During a known credit-market stress episode (widening HY spreads).
- When you are tilted from a recent loss.

### 87. Regime changes that kill premium sellers

The catastrophic scenarios to memorize:

- **2020-03** (COVID flash crash): VIX closed around 14 at the end of
  January 2020, crossed 20 in the last week of February, and reached
  its closing peak of 82.69 on March 16, 2020 (intraday high 85.47 on
  March 18). Roughly 4 weeks from regime-calm to panic, not "7 days".
  Anyone short vol without hedges was liquidated.
- **2018-02** (Volmageddon): XIV unwind. Short-vol ETN products
  dissolved overnight.
- **2010-05** (Flash crash): 9 minutes of chaos. Market makers
  widened spreads to uncrossable, causing stop-loss cascades.
- **2008-10** (GFC): VIX > 80 for weeks. Realized > implied daily.
  Short-premium strategies lost 12-18 months of gains.

In every case: VIX term structure went into backwardation *before*
the blowup. Contango -> backwardation transition is the single most
reliable leading indicator of a regime kill-zone.

### 88. Black swan signatures

In the public dashboard, these signals should put the pipeline into
"defensive mode" (reduced trade suggestions, larger cushions):

- VIX term structure: 3rd-month future < 1st-month future for 3+ days.
- HY credit spreads widening >= 100bp in a week.
- SPX 20-day realized vol > 30-day implied for a week.
- VVIX > 130 (the vol-of-vol signal that tail hedges are being
  bought aggressively).
- Single-day SPX move > 3%.

Any two of these firing = step aside for 72 hours.

---

## Part XIV -- Tax treatment of short premium

The single largest return driver most retail premium sellers ignore.
For a US taxpayer in 2026 at a 32% federal bracket with 5% state, the
difference between single-name equity premium (taxed as STCG) and SPX /
XSP / NDX / RUT / VIX premium (taxed under Section 1256's 60/40 rule)
is ~10 percentage points of effective tax rate per dollar of gross
premium. Over a five-year compounded book, that materially widens or
narrows the CAGR. A sophisticated seller rotates some of the short-
premium notional into broad-based index options specifically for the
tax arbitrage.

### 89. Section 1256 contracts -- what qualifies and why it matters

**Authority.** IRC section 1256 (26 USC 1256). Reported on IRS Form
6781. Applicable to "non-equity options" on broad-based indices that
trade on a qualified board or exchange.

**Options that qualify for Section 1256 treatment:**

| Symbol | Underlying | Notes |
|--------|------------|-------|
| SPX / SPXW | S&P 500 | European, cash-settled. The gold standard. |
| XSP | Mini-SPX (1/10 SPX) | European, cash-settled. Small-contract variant. |
| NDX / NQX | Nasdaq-100 | European, cash-settled. |
| RUT / MRUT | Russell 2000 | European, cash-settled. |
| DJX | Dow Jones Industrial | European, cash-settled. |
| XEO / OEX | S&P 100 | European / American, cash-settled. |
| VIX | CBOE Volatility | European, cash-settled. |

**Single-name options (AAPL, MSFT, NVDA, etc.) do NOT qualify.** Nor
do SPY, QQQ, IWM options (those are ETF options treated as equity
options). Narrow-sector index options with fewer than 10 components or
concentrated weighting also do not qualify.

**Three Section 1256 mechanics that matter:**

1. **60/40 treatment regardless of holding period.** Every
   Section-1256 gain or loss is deemed 60% long-term capital gain /
   40% short-term capital gain, even on a one-day trade. For a 32%
   federal + 5% state taxpayer, the blended effective rate is 26.8%
   versus 37% on equivalent STCG.
2. **Mark-to-market at year-end.** Open Section-1256 positions on
   December 31 are deemed sold at fair market value. No deferral by
   straddling year-end.
3. **Three-year loss carryback.** Individuals (not entities) can
   elect to carry net Section-1256 losses back 3 years against prior
   Section-1256 gains. Significant if you have a big vol-spike year.

**Wash sales do NOT apply to Section 1256 contracts.** This is one of
the most underappreciated features of SPX/XSP trading. A loss on an
SPX short put can be immediately re-entered without the 30-day
waiting period that would apply to AAPL.

### 90. Equity options -- the STCG trap

Short premium collected on single-name options is **almost always
short-term capital gain** because:

- Short-option closed-or-expired gains are STCG regardless of how long
  the position was open (IRC section 1234(b)).
- A 25-50 DTE wheel measures in weeks; the 1-year LTCG threshold never
  applies to the option itself.
- Assignment resets the clock: when a short put is assigned, the
  premium reduces the basis in the acquired stock; the stock's holding
  period starts the day after assignment.
- When a covered call is assigned, the call premium is added to the
  sale proceeds of the stock; the stock's own holding period
  determines LT vs ST on the share sale.

**2026 effective federal+state tax drag on STCG** (single filer):

| Federal bracket | Fed STCG | +5% state | +CA top | +NY/NYC |
|-----------------|----------|-----------|---------|---------|
| 24% ($206k+)    | 24%      | 29.0%     | 37.3%   | 34.9%   |
| 32% ($256k+)    | 32%      | 37.0%     | 45.3%   | 42.9%   |
| 35% ($626k+)    | 35%      | 40.0%     | 48.3%   | 45.9%   |
| 37% ($752k+)    | 37%      | 42.0%     | 50.3%   | 47.9%   |

Texas and Florida have no state income tax. California and New York
tax all capital gains as ordinary income (no LTCG preference), so
Section-1256's 60/40 benefit is federal-only in those states.

### 91. Wash sale rules on rolled positions

IRC section 1091. The IRS has never defined "substantially identical"
for options and refused to issue guidance for 30+ years. Industry
practical framework (used by TradeLog, GainsKeeper, most broker 1099-B
calculations):

**Clearly wash sale:**
- Close a short put at a loss, reopen the same strike / same
  expiration within 30 days.
- Close a long put at a loss, buy the same strike / same expiration
  within 30 days.
- Close stock at a loss, sell a deep-ITM put within 30 days (put is
  economically equivalent to the stock).

**Generally safe (industry consensus, not IRS-blessed):**
- Different strike AND different expiration are NOT substantially
  identical.
- Rolling a short put down-and-out (lower strike, later expiry) at a
  loss is typically treated as non-wash.
- Rolling a short call up-and-out on a covered call is similarly
  treated as non-wash.
- Stock assigned from a short put: the loss on the put is baked into
  the share basis, so there is no separate wash trigger.

**Danger zones in the wheel cycle:**
- CSP loss -> new CSP at same strike, next week's expiry: high
  wash-sale risk.
- Stock called away at a loss -> new CSP at or above the call strike
  within 30 days: facts-and-circumstances; Fairmark treats as possible
  wash.
- Closing a long-stock leg at a loss then writing a deep-ITM short
  put: treat as wash sale.

**The clean path through the wheel:** if you take a loss on a
single-name option, wait 31 days before re-entering that specific
name, or rotate to SPX/XSP for the dead zone (wash-sale doesn't apply
to Section 1256).

### 92. IRA / Roth rules (2026, by broker)

All IRAs: no margin, no short stock, no naked short anything, no
positions that could create a debit beyond account equity.

| Broker      | CSP | CC  | Debit spreads | Credit spreads in IRA       | Max level in IRA  |
|-------------|-----|-----|---------------|-----------------------------|-------------------|
| Schwab      | Yes | Yes | Yes           | Yes, needs application      | Spreads (L2/L3)   |
| Fidelity    | Yes | Yes | Yes           | Yes with limited margin     | Spreads           |
| Vanguard    | Yes | Yes | Limited       | Very limited                | L1 or L2 mostly   |
| IBKR        | Yes | Yes | Yes           | Yes                         | Up to L4 taxable  |
| tastytrade  | Yes | Yes | Yes           | Yes (no account minimum)    | Spreads           |
| Robinhood   | Yes | Yes | Yes           | Yes (L3)                    | L3; no naked      |

**No broker allows naked calls or naked puts in an IRA.** "Cash-
secured put" in an IRA means 100% of the assignment value sits in
cash or T-bills.

### 93. Worked example: $100k account, 1.5% gross monthly premium

Assumptions: 32% federal + 5% state marginal, MAGI over $200k so NIIT
applies, 1.5% monthly gross premium, **25% realized-loss drag** on
gross (to model assignment outcomes and closed-at-loss trades), net
compounded monthly after tax. The LTCG rate at the 32% bracket is
**15%** (20% band starts at ~$545k taxable income in 2026). All
ending-balance numbers carry +/- 1-2% uncertainty depending on the
assumed loss-drag schedule; the *delta* between scenarios is more
reliable than the absolute endpoints.

- STCG effective = 32% + 5% state + 3.8% NIIT = **40.8%**
- Section-1256 blended = 0.60 * (15% + 5% + 3.8%) + 0.40 * 40.8% =
  0.60 * 23.8% + 0.40 * 40.8% = **30.6%**

Effective federal-only, NIIT-inclusive comparison:

| Scenario                         | Effective tax | 5-yr ending | 5-yr gain | CAGR   |
|----------------------------------|---------------|-------------|-----------|--------|
| 100% single-name wheel (STCG)    | 40.8%         | $168,841    | $68,841   | 11.05% |
| 50% SPX / 50% single-name        | 35.7%         | $178,013    | $78,013   | 12.22% |
| 100% SPX equivalent              | 30.6%         | $188,127    | $88,127   | 13.47% |

**Dollar lift from SPX substitution at $100k starting capital:**
- Half-and-half: **+$9,172** over 5 years.
- 100% SPX: **+$19,286** over 5 years.

**Per-state override (same book, same rates, different residency):**

| State      | STCG effective | S1256 effective | 5-yr lift (100% SPX vs STCG) |
|------------|----------------|-----------------|------------------------------|
| TX / FL    | 32% + 3.8%     | 60% * 18.8% + 40% * 35.8% | ~$19,500 |
| OR (Andrew)| 32% + 9.9% + 3.8% | 60% * 28.7% + 40% * 45.7% | ~$20,900 |
| CA (top)   | 32% + 13.3% + 3.8% (no pref) | 60% * 32.1% + 40% * 49.1% | ~$22,100 |
| NY/NYC     | 32% + 10.9% + 3.8% (no pref) | 60% * 29.7% + 40% * 46.7% | ~$21,000 |

Caveat: California, New York, and several other states tax all
capital gains as ordinary income, so the Section-1256 60/40 benefit
is federal-only in those states. The lift is still positive (federal
rate differential alone is significant) but smaller than in TX / FL.

At $1M deployed capital, the 100%-SPX vs 100%-single-name delta is
~$190-$221k over 5 years depending on state. This is why serious
premium-selling desks rotate into XSP / SPX wherever delta and
liquidity permit.

**Pipeline implication -- this is the NEXT pipeline addition, not a
v5 aspiration.** Add an SPX / XSP "tax-efficient equivalent" candidate
alongside each single-name CSP. Compute the beta-adjusted equivalent
short put on SPX that produces similar short-vol exposure. Present as
"same risk profile, lower tax drag" with both the single-name and the
SPX alternative displayed side-by-side. The reader chooses based on
their own tax situation. Estimated effort: 1-2 days. Estimated
after-tax-return improvement: 1-2 percentage points annualized,
compounding for as long as the book is held.

### 94. Tax traps specific to short premium selling

- **Constructive sales (IRC 1259).** Holding appreciated stock and
  entering a position that "substantially eliminates risk of loss and
  opportunity for gain" triggers recognition at FMV. A standard
  not-deep collar does NOT trigger; a deep collar CAN.
- **Straddle rules (IRC 1092).** Offsetting positions that
  substantially reduce risk defer losses until the offsetting gain
  position is closed. A short put + long put at a lower strike on the
  same ticker is a straddle. The **Qualified Covered Call exception
  (IRC 1092(c))**: owning stock + writing a not-deep-ITM CC with >30
  days to expiry is excluded from straddle treatment. Writing a CC
  that is materially ITM drops the QCC protection.
- **Conversion transactions (IRC 1258)** and **constructive ownership
  (IRC 1260)** attack loss-harvesting via swaps and deep-ITM LEAPs.
  Not typically relevant to a wheel, but worth knowing.

**Critical caveat.** This section is a summary for orientation.
Andrew should run any material tax-structuring decision past a CPA
familiar with derivatives, not act on this compendium alone.

---

## Part XV -- Margin mechanics and buying power

How the broker actually computes "BP consumed" per trade is the single
most important variable determining how many CSPs can fit in an
account. Reg-T and Portfolio Margin differ by 3-5x for the same risk.

### 95. Reg-T margin formulas (FINRA Rule 4210)

All formulas are per contract; multiply by 100 for per-contract BP.
`P` = premium received, `S` = underlying spot, `K` = strike.

**Cash-secured put (CSP):**
```
BP = (K * 100) - (P * 100)
```

**Naked short put (Reg-T):**
```
BP_per_contract = max(
    (0.20 * S) - OTM_amount + P,   # 20% test
    (0.10 * K) + P,                # 10%-of-strike floor
    $2.50 + P                      # $250 per-contract floor
) * 100
```
Where `OTM_amount = max(S - K, 0)`.

**Naked short call (Reg-T):** same ladder with `OTM_amount =
max(K - S, 0)` and the 10% floor on `S` (underlying) rather than `K`.

**Covered call:** zero additional BP; the long 100 shares collateralize.

**Vertical spread (credit):** `BP = (width - net_credit) * 100`.

**Iron condor:** `BP = max(call_width, put_width) * 100 - net_credit *
100`. Only one side can be breached at expiration, so FINRA allows the
offset.

### 96. Portfolio Margin (PM)

**Eligibility thresholds (verified 2026):**
- IBKR: $110k to upgrade, $100k maintenance floor.
- Schwab: $125k initial, Level 3 options approval, 20-question
  knowledge assessment, $100k maintenance floor.
- tastytrade: $175k (highest retail bar).
- Fidelity / E*TRADE: ~$150k typical.
- FINRA 4210 floor: $100k; each broker adds a cushion.

**How PM computes BP (OCC TIMS framework):**
- Individual equities stressed -15% to +15% in ~10 price points.
- Broad indices stressed +/- 8%.
- Implied vol shocked up and down simultaneously at each price point.
- The single scenario with the largest portfolio loss becomes the
  margin requirement.
- Offsetting positions across the book reduce worst-case stress --
  this is where PM gets its efficiency.

**Typical BP reduction vs Reg-T** for a diversified short-premium
book at 0.15-0.30 delta, 30-45 DTE: 50-80% BP reduction. A Reg-T
naked put consuming $2,500 typically consumes $500-1,000 under PM.

**The BP cascade risk** (the single most important thing in this
section). PM recomputes worst-case scenarios in real time. When VIX
jumps 10 points, the vol shock applied at each price scenario widens
(typically from +/-30% of current IV to +/-50%), re-pricing every
short option at a worse loss. A book at 40% of PM BP pre-shock can
hit 90% mid-shock. The broker issues a same-day forced-liquidation;
you sell into the bottom. **Never deploy more than 50% of PM BP** to
short premium in steady-state. Seasoned sellers run 30-40%.

### 97. Worked example: 9 CSPs at 0.25 delta, 30 DTE

Using approximate current strikes and premiums for our 9 tickers
(AAPL at $270, NVDA at $202, etc. from an April 2026 snapshot):

| Ticker | Spot  | 0.25d put K | Premium | CSP BP   | Reg-T Naked | PM BP (65% cut) |
|--------|-------|-------------|---------|----------|-------------|-----------------|
| MU     | 455   | 415         | 5.50    | $40,950  | $8,552      | $2,993          |
| META   | 689   | 630         | 8.00    | $62,200  | $12,971     | $4,540          |
| NVDA   | 202   | 185         | 3.20    | $18,180  | $3,714      | $1,300          |
| MSFT   | 423   | 390         | 4.50    | $38,550  | $7,906      | $2,767          |
| AMZN   | 251   | 230         | 3.00    | $22,700  | $4,711      | $1,649          |
| GOOG   | 339   | 312         | 3.80    | $30,820  | $6,308      | $2,208          |
| AAPL   | 270   | 250         | 2.60    | $24,740  | $5,024      | $1,758          |
| TSLA   | 401   | 360         | 8.50    | $34,150  | $7,762      | $2,717          |
| BROS   | 53.44 | 48          | 0.95    | $4,705   | $1,174      | $411            |
| **Total** |    |             |         | **$276,995** | **$58,122** | **$20,343** |

**As a percentage of a $250k account:**
- Cash-secured on all 9: **111%** -- the book does not fit. A $250k
  cash account cannot run the full 9-ticker wheel; you would drop
  2-3 expensive names (META, MU, TSLA) or move to weekly cycles at
  closer strikes.
- Reg-T naked on all 9: **23%** -- comfortably fits, 77% cushion.
- Portfolio margin on all 9: **8%** -- trivially fits; the 92%
  headroom IS the trap (see BP cascade).

### 98. The April 2026 PDT rule elimination

SEC approved FINRA's elimination of the Pattern Day Trader rule on
**April 14, 2026** (SR-FINRA-2025-017). The $25,000 minimum-equity
requirement and "4 day-trades in 5 business days" designation are
gone. Effective approximately 45 days after FINRA's Regulatory
Notice (late May / early June 2026). Brokers have an 18-month phase-
in for real-time monitoring systems.

**What didn't change:**
- Reg-T initial margin (50% long stock, CBOE option-margin
  methodology) -- unchanged.
- Maintenance margin (25% Reg-T floor, stricter at most brokers) --
  unchanged.
- IRA cash-settled requirement -- unchanged.
- Good-faith and freeride rules in cash accounts -- unchanged.
- Options Buying Power and SPAN / portfolio-margin thresholds --
  unchanged.

**What did change:** real-time intraday margin. If portfolio real-
time exposure exceeds equity, BP is cut intra-day. Five intraday
calls in five business days triggers a 90-day restriction. Net
effect for wheel sellers: if you stay cash-secured, nothing changes.
For sub-$25k accounts running defined-risk spread rolls, the rule
change is genuinely liberating. And the intraday margin standard
makes VIX-spike BP cascades *faster* -- minutes, not hours -- which
reinforces the 50% cushion rule above.

**Pipeline implication.** The private email should surface Reg-T vs
PM BP utilization as a tile once positions.json is populated, with a
red flag if utilization > 50% of PM or > 80% of Reg-T. That is the
stress-survival canary.

---

## Part XVI -- Commissions, fees, and slippage

The 15% bid-ask spread gate in our current spine is very generous.
Real-world friction eats a significant fraction of gross premium,
especially on thinner-chain names.

### 99. Per-contract commission structure (2026)

| Broker        | Per-contract commission | Exchange + ORF fees  | All-in round trip per contract |
|---------------|-------------------------|----------------------|-------------------------------|
| IBKR (Lite)   | $0.65                   | ~$0.05               | ~$1.40                        |
| IBKR (Pro)    | $0.15-$0.65 tiered      | pass-through         | varies                        |
| Schwab        | $0.65                   | included             | $1.30                         |
| Fidelity      | $0.65                   | included             | $1.30                         |
| tastytrade    | $1.00 open / $0 close   | $0.03 ORF            | $1.06                         |
| Robinhood     | $0.00                   | regulatory only      | ~$0.10                        |

For our 9-ticker universe at typical 25-50 DTE 0.20-0.30 delta
premiums of $1.00-$5.00 per share ($100-$500 per contract), the
round-trip commission friction is **0.25-1.3%** of gross premium.

### 100. Bid-ask spread reality

The current spine allows up to 15% bid-ask spread. At a $1.00 mid,
15% spread is $0.15. A round-trip into-out-of a $1.00 premium
position therefore loses up to $0.30 to spread, or **30% of gross
premium**.

**Realistic assumptions:**
- Mid-price fills happen ~1/3 of the time on liquid names (MSFT,
  AAPL, GOOG, AMZN).
- Typical fill: about 1/3 of the way from mid to NBBO. For a $1.00
  mid and a 5% spread ($0.05 total), expected slippage per fill is
  ~$0.017, or 1.7% of premium per leg, 3.3% round trip.
- On wider-spread names (BROS, occasionally MU on low-volume days):
  spreads can be 8-12%, making round-trip slippage 6-10%.

**The right gate.** Tighten our spread limit from 15% to 8% for
candidate qualification. Names with spreads > 8% on the target
expiration should either drop to an informational-only card (shown
but not recommended) or force a spread-based alternative (bull put
spread with a closer-strike long wing to reduce leg-count and
slippage dependency).

### 101. Putting it together: expected-net-yield calculation

For a sample CSP with $2.00 premium:
```
gross = $2.00 x 100 = $200
spread slippage (8% spread, 1/3-of-mid fill) = -$2.67 per leg x 2 = -$5.33
round-trip commissions = -$1.30
pre-tax net = $200 - $5.33 - $1.30 = $193.37
STCG tax (37% effective) = -$71.55
after-tax net = $121.82
```

That $2.00-premium CSP is actually $1.22 of after-tax income per
contract. Or, expressed as a haircut: **39% of gross premium is lost
to friction + tax**. The "yield" numbers on our dashboard are pre-
friction, pre-tax, and should remain pre-friction pre-tax for
comparability, but we owe the reader an explicit "here is what a
realistic net looks like" note so no one is under-informed.

**Pipeline implication.** Add a single plain-English footnote under
the Option Selling Watch card: "Premium yield shown is pre-commission,
pre-spread-slippage, pre-tax. Realistic net to a US single-filer
seller is typically 55-65% of the shown yield on single-name equity
options; 70-75% on broad-based index options (SPX/XSP) due to
Section-1256 tax treatment."

---

## Part XVII -- Behavioral protocol

The second-biggest determinant of long-term survival after sizing.
The literature on trader decision-making is unambiguous: process
beats prediction. Pre-committed rules that survive emotion beat
post-hoc judgment under stress.

### 102. The pre-trade checklist (codify, commit, execute)

Before opening any short-premium position, the reader should verify
in writing (the private email could prompt this):

1. **Ticker.** Is it on the authorized list (9 tickers plus indices)?
2. **IV rank.** Is IVR > 30 (or, preferably, VRP > 3 vol-points)?
3. **DTE.** In the 30-45 day window?
4. **Delta.** In 0.16 - 0.30 band for single-name naked puts?
5. **Catalyst check.** Any earnings / product event / macro print
   inside the expiration window? If yes, skip or shorten.
6. **Cluster cap.** Does adding this position exceed the sector
   cluster's vega cap?
7. **Size.** Is the notional < 5% of account equity? Is total short
   premium BP < 30-35% of account?
8. **Liquidity.** OI > 250, bid-ask < 8%, volume > 10 on the chosen
   contract?
9. **Regime.** Is VIX term structure in contango? Is SPX above
   zero-gamma?
10. **Post-loss cooling.** Have I taken a loss in this sector in the
    last 72 hours?

If ANY answer is unfavorable, skip. No "just this one" exceptions.

### 103. The "never act during a drawdown day" rule

On a day where the account is down > 1%, do not open new positions.
The psychological research (Kahneman-Tversky, Thaler, and the modern
behavioral-finance canon) is unambiguous: loss-averse decision-making
after a fresh loss is systematically worse than decision-making from
a baseline state. The brain is looking to "win back" the loss, which
produces over-sized and poorly-selected trades.

Pre-commit: no new positions until the next trading day's open. The
pipeline could gate new suggestions when the account is in a
drawdown day; we do not have that hook yet.

### 104. Decision journaling

Every trade opened should be logged with:
- Entry rationale (one sentence).
- Expected probability of max profit realization.
- Specific conditions under which the trade would be closed early
  (roll trigger, stop-loss level).
- Pre-committed close date (21 DTE) or profit target (50% max).

At close, compare actual to expected. Do this for 100 trades and you
will discover your actual edge (vs your imagined edge) with
statistical precision. This is the calibration loop in Part XII,
applied behaviorally.

### 105. Post-loss sector cooldown

After any loss (realized or roll-for-debit) on a ticker, impose a
72-hour cooldown before opening new positions in the same sector
(not just the same ticker). Rationale: sector-level drawdowns are
correlated, and the natural "get back in" urge after a loss tends to
concentrate risk in exactly the sector that just hurt you.

### 106. The weekly review

One standing meeting per week with the data:
- Closed trade outcomes vs. expectation.
- Any rule violations? (There should be none; if there are, diagnose.)
- Open book greek summary (from the pipeline).
- Any regime changes warrant sizing adjustments?

The weekly review is the behavioral equivalent of the pipeline's
calibration ledger. It is what keeps emotion out of the process.

**Pipeline implication.** Private email should include, once per
week (Sunday?), a "weekly review checklist" prompt with last 7 days
of data pre-populated. Make the habit frictionless.

---

## Part XVIII -- Assignment mechanics in detail

Most of what the compendium says about assignment has been high-level
("if assigned, sell CCs"). The mechanical detail below is what you
need to not get surprised.

### 107. Early exercise of short calls (dividend risk)

Short calls are exercised early almost exclusively for the dividend.
The rule: if the stock has an ex-dividend date before the call's
expiration, and the call's remaining extrinsic value is LESS than the
dividend, the rational call holder will exercise early to capture the
dividend.

**Applicable dividend-paying names in our universe:**
- AAPL (quarterly dividend, ~0.5% yield).
- MSFT (quarterly dividend, ~0.8% yield).
- GOOG (recently initiated small dividend).
- META (initiated small dividend 2024).
- AMZN, NVDA, MU, TSLA, BROS: no dividend or irrelevantly small.

**Practical implication.** When selling covered calls on dividend
names, check the ex-div calendar. If ex-div falls before expiration
and the call is ITM, monitor extrinsic value in the 1-2 days before
ex-div. If extrinsic < dividend, close the call or roll it out to
avoid early exercise.

### 108. Pin risk

On OPEX Friday, if the underlying closes within ~$0.05 of the short
strike, the option may or may not be exercised unpredictably. The
asymmetric outcome: you either keep the position open over the
weekend (and have Monday gap risk) or you get assigned unexpectedly
and own 100 shares at Monday's open, possibly down several percent
from Friday's close.

**Rule:** never hold short options through expiration within $0.50
of a major-OI strike. Close the day before.

### 109. Broker-specific auto-exercise

- **Robinhood:** closes ITM short options at market on expiration
  Friday if the customer does not have the funds/shares to cover.
  This can produce bad fills. Keep accounts adequately capitalized.
- **IBKR:** does NOT auto-exercise or auto-close; it is the
  customer's responsibility. If you forget to close an ITM short
  put before expiration, you will be assigned.
- **Schwab / Fidelity / tastytrade:** auto-exercise ITM long options
  at standard $0.01-ITM threshold; do not auto-close ITM shorts.

**Rule:** know your broker's rules. Never leave ITM short options
open through expiration unless you intend to be assigned.

### 110. Settlement timing and next-day BP

Option settlement has been T+1 since 1994 (unchanged). The underlying
stock that you acquire from assignment now also settles T+1 (changed
from T+2 in May 2024, SEC Rule 15c6-1 amendment). When a short put
is assigned on Friday's close:
- Monday morning: 100 shares appear in the account at the strike.
- BP adjusts instantly: cash is debited by strike * 100.
- If Reg-T, no additional BP hit beyond the cash outflow.
- If PM, the stress-test includes new shares; net BP impact depends
  on portfolio offsets.

For same-day roll-down-and-out: trade both legs on Friday morning, do
NOT wait for close, because Friday-close assignment can sneak up.

### 111. Hard-to-borrow stock post-assignment

If a covered call is exercised against you and your shares are sold,
you are flat. But if you don't own the shares and a naked call is
exercised, you are now SHORT the shares and exposed to short-stock
borrow rates. On hard-to-borrow names (rare in our universe; some
biotech and meme names can go to 20%+ annualized borrow) this can
accrue quickly.

**Applicable in our universe:** very rare, but worth knowing for
BROS during stress regimes (its float is smaller than the megacaps).

**Pipeline implication.** Small: the private email's position
manager should flag any assignment-imminent position in the
ex-dividend window or within $0.50 of a major OI strike, and any
short-call position on a dividend-paying name with extrinsic
approaching the dividend amount.

---

## Part XIX -- Single-name playbook (the 9-ticker universe)

The rest of this compendium is generic. This part is specific: what
actually matters for selling premium on each of our 9 tickers in
2026. Catalysts, IV behavior, typical earnings moves, the dominant
thesis-breakers, and per-ticker strike/DTE discipline. All dates are
approximate windows; always verify with the company IR page before
trading.

> **READ FIRST: the three dangerous names in this book.**
>
> Skip to Section 121 before reading anything else. Three of the
> nine tickers (**TSLA**, **BROS**, **META**) are materially more
> dangerous for naked short-premium than the others, for specific
> and different reasons:
>
> - **TSLA**: three structural tails (Q4 deliveries, robotaxi
>   events, Musk political). Historical earnings moves 10-18% vs
>   implied 9-12%, meaning the market systematically under-prices
>   TSLA vol. Defined-risk spreads only; do not sell naked puts.
> - **BROS**: 80x P/E on a 3-5% comp growth story is a liquidity
>   trap. Any disappointment = -20% gap. Realized option-premium
>   capture is ~50% of screen after slippage. Defined-risk only;
>   seriously consider dropping from the universe.
> - **META**: $115-135B 2026 capex is an asymmetric bomb. Any
>   quarter with revenue decel + capex re-up triggers a -12-15%
>   gap. Sell between earnings only; avoid structures spanning
>   earnings dates.
>
> The remaining six (MU, NVDA, MSFT, AMZN, GOOG, AAPL) are "business
> as usual" premium selling. MSFT is the safest.

### 112. MU (Micron Technology)

**Profile.** Semi-cyclical. Memory (DRAM / NAND). HBM exposure to
NVDA / AMD. Our ticker_profile: "semi_cyclical", IV floor 40%.

**2026 catalyst calendar (approximate):**
- Fiscal Q3 FY26 earnings: late June 2026 (June 24-27 typical).
- Fiscal Q4 FY26 earnings: late September 2026.
- HBM4 volume ramp ongoing Q2 calendar 2026. Calendar-2026 HBM supply
  100% booked.

**Thesis breakers:**
- Memory-cycle rollover. DRAMeXchange contract prints turning
  sequentially negative is the leading indicator. Historically, when
  DRAM spot prices top, MU compresses 30-50% in 6 months.
- Samsung HBM3E qualification at NVDA that splinters Micron's share.
- Capex step-up above $25B flagging over-build risk if AI-inference
  demand cools.

**IV behavior around earnings.**
- IV rank typically 50-70 running into prints.
- Implied earnings move: ~7% historical average.
- Actual moves blow past: Q2 FY26 printed +16% on a recent quarter.
- Post-print crush: -30 to -40 vol points.

**Do-not-sell window:** 10 trading days before each quarterly print.
Avoid late September (FY guide).

**Per-ticker discipline.** 0.20 delta, 35-45 DTE, strikes >= 10%
OTM. Avoid naked CCs against core positions (upside tail is fat).
Defined-risk put spreads preferred over naked puts when IV rank > 70.

### 113. META (Meta Platforms)

**Profile.** Mega-cap growth. AI / social / Reality Labs. Our
ticker_profile: "mega_cap_growth", IV floor 28%.

**2026 catalyst calendar:**
- Q1 2026 earnings: April 29, 2026 (AMC).
- Q2 2026 earnings: late July 2026.
- Q3 2026 earnings: late October 2026.
- Connect developer conference: mid-September 2026.

**Thesis breakers:**
- Capex guide shock. 2026 capex band is $115-135B (up from $70-72B
  in 2025) for Meta Superintelligence Labs. Any quarter where revenue
  growth decelerates below ~18% while capex keeps growing triggers a
  "no ROIC" sell-off (late-2022 replay was -26% on one print).
- FTC cross-appeal of the November 2025 Boasberg antitrust ruling.
  Any remedy-phase ruling could shift the regulatory overhang.

**IV behavior:**
- IV rank typically 70-85 earnings week.
- Implied earnings move: ~7-8%.
- Actuals have run hot (+/-12-15%) on capex-guide prints.
- Post-event crush: -25 to -35 vol points.

**Do-not-sell window:** April 22 - May 2, 2026 (present week). Late
July. Late October. Any AG action on the FTC appeal.

**Per-ticker discipline.** 25-35 DTE. Sell 0.15-0.20 delta puts ONLY
between earnings. Strangles post-print when IV collapses.
Covered-call strikes >= 12% OTM.

### 114. NVDA (NVIDIA)

**Profile.** Semi-cyclical / AI megacap. Ticker_profile:
"semi_cyclical", IV floor 40%.

**2026 catalyst calendar:**
- Q1 FY27 earnings: May 20, 2026 (AMC). Guide $78.0B +/-2%,
  non-GAAP GM ~75%.
- Computex Taipei: mid-May 2026.
- GTC DC: already occurred spring 2026.
- GTC Fall: October 2026 (smaller catalyst).
- Rubin R100 production ramp: H2 2026.

**Thesis breakers:**
- TSMC CoWoS-L yield stall. NVDA has booked 800-850k wafers for 2026
  and >50% of CoWoS capacity. A packaging bottleneck plus
  OpenAI-Broadcom ASIC ramp in late 2026 could pull 2-3 points off
  gross margin.
- China export-control tightening: -15% tail.
- Rubin Ultra yield issues (dual-die config already a retreat from
  the original four-die spec).

**IV behavior:**
- Pre-earnings IV rank routinely 80-95.
- Implied earnings move: ~8-9%.
- Actuals: 9-14% -- the largest reliable-outperformance of any
  megacap.
- Post-print crush is the largest in our universe.

**Do-not-sell window:** May 12-22, 2026. Computex week (May 19-23).
Any US-China chip export update.

**Important caveat for April 2026.** A research snapshot suggested
NVDA's IV rank was ~12 in early April 2026, which would make
premium too thin to sell against the tail risk. This number is a
research claim, not verified in our own `iv_history.jsonl`;
**always check the current IV rank from our pipeline before
acting**. If the pipeline reports IV rank < 30 on NVDA on any given
refresh, skip; if it reports > 40, our standard spine applies.
NVDA's earnings-adjacent days typically push IV rank to 80-95.

**Per-ticker discipline.** 35-45 DTE CSPs at 0.15 delta or tighter
while IV rank is low. Scale up to 0.20-0.25 delta only when IV rank
> 50. CCs only against committed shares, strike >= 15% OTM.

### 115. MSFT (Microsoft)

**Profile.** Megacap cloud / AI. Ticker_profile: "mega_cap_growth",
IV floor 28%.

**2026 catalyst calendar:**
- Q3 FY26 earnings: April 29, 2026 (AMC). Azure guide 37-38% cc.
- Build developer conference: late May 2026.
- Q4 FY26 earnings: late July 2026.

**Thesis breakers:**
- Azure print below +37% constant currency. Commercial RPO is $625B
  with ~45% OpenAI-linked. OpenAI's Broadcom-chip deployments begin
  late 2026 -- a public announcement of first production inference
  off-Azure would compress MSFT's AI multiple.
- Capex normalized at ~$150B/year. Copilot seat-growth deceleration
  below +100% y/y would re-price the entire name.

**IV behavior:**
- Lowest-vol name of the 9. IV rank 30-50 pre-earnings.
- Implied earnings move: ~4-5%.
- Actuals: 3-7%.
- Crush is modest: -10 to -15 vol points.

**Do-not-sell window:** April 22 - May 2, 2026. Build week. Late
July.

**Per-ticker discipline.** Best "core" CSP/CC ticker in the book.
30-45 DTE, 0.20-0.25 delta puts fine. CCs at 8-10% OTM are
reasonable (the upside tail is benign relative to TSLA or NVDA).

### 116. AMZN (Amazon)

**Profile.** Megacap growth / cloud + retail. Ticker_profile:
"mega_cap_growth", IV floor 28%.

**2026 catalyst calendar:**
- Q1 2026 earnings: April 29, 2026 (AMC).
- Q2 2026 earnings: late July 2026.
- Q3 2026 earnings: late October 2026 (most important; holiday
  guide).
- AWS re:Invent: December 1-5, 2026.
- Prime Day: typically mid-July.

**Thesis breakers:**
- AWS growth below 20% y/y breaks the margin-expansion thesis.
- Tariff pass-through on 3P marketplace. Chinese sellers are ~49%
  of 3P GMV; de-minimis ended January 2026. Retail operating margin
  is mid-single-digit, so a 10% import-cost increment flows straight
  to North America segment margin. A Q1/Q2 print showing NA margin
  compression of 150bp would trigger -15%.

**IV behavior:**
- IV rank 60-75 pre-earnings.
- Implied earnings move: ~6-7%.
- Actuals: 5-10%.
- Crush: meaningful -20 vol points typical.

**Do-not-sell window:** April 22 - May 2, 2026. Late July. Late
October. re:Invent week.

**Per-ticker discipline.** 30-45 DTE, 0.15-0.20 delta puts. AMZN is
trading ~21% below 52-week high entering April 2026 -- coiled
spring. Size normal; do not overweight.

### 117. GOOG (Alphabet)

**Profile.** Megacap / search + cloud + autonomy. Ticker_profile:
"mega_cap_growth", IV floor 28%.

**2026 catalyst calendar:**
- Q1 2026 earnings: April 29, 2026 (AMC). Consensus ~$2.62 EPS /
  ~$100.76B revenue.
- Google I/O: mid-May 2026.
- DOJ appeal oral arguments: expected Q3 2026.

**Thesis breakers (TWO parallel tails):**
1. DOJ cross-appeal filed February 3, 2026 seeks stronger remedies.
   Any ruling expanding behavioral remedies to include partial
   divestiture of ad-tech could trigger -20%.
2. AI Overviews now on ~30% of queries. Morgan Stanley estimates
   choice-screen + AI-cannibalization could cost 5-8% of search
   traffic over 3 years, $15-25B revenue-at-risk. Any quarter with
   Search revenue growing < 6% y/y cracks the thesis.

**IV behavior:**
- IV rank 55-70 pre-earnings.
- Implied earnings move: ~5-6%.
- Actuals: 4-9%.
- Waymo announcements are now a separate vol catalyst.

**Do-not-sell window:** April 22 - May 2, 2026. I/O week. Any DOJ
appeal docket update.

**Per-ticker discipline.** 30-40 DTE CSPs at 0.15 delta. Keep size
modest -- legal-remedy tail is bimodal; a -12% overnight from a
court filing that pins your short put is a realistic risk.

### 118. AAPL (Apple)

**Profile.** Megacap steady. Ticker_profile: "mega_cap_steady", IV
floor 22%.

**2026 catalyst calendar:**
- Q2 FY26 earnings: May 7, 2026 (AMC).
- WWDC: June 8-12, 2026 (Gemini-powered Siri overhaul expected).
- iPhone 18 Pro + iPhone Fold launch: September 2026.
- Q3 FY26 earnings: late July 2026.

**Thesis breakers:**
- iPhone Fold reception. First foldable at ~$2,000. If unit/ASP math
  disappoints, or if China's 23% Q1 2026 iPhone growth reverses as
  government subsidy tapers, the multiple compresses.
- Watch Counterpoint / IDC weekly China iPhone data in June-August.

**IV behavior:**
- IV rank 40-60 pre-earnings.
- Implied earnings move: 3-4%.
- Actuals: often 4-7%.
- **Event stacking**: WWDC + September launch + Q4 guide cluster in
  a 4-month window.

**Do-not-sell window:** April 30 - May 9. June 5-14 (WWDC).
September 8-26 (launch + pre-orders). Late October.

**Per-ticker discipline.** 25-35 DTE through summer (short-dated to
dodge catalysts). CCs 5-8% OTM fine outside event windows. AVOID
45-DTE structures that straddle WWDC plus a launch-rumor cycle.

### 119. TSLA (Tesla)

**Profile.** High-beta. Ticker_profile: "high_beta", IV floor 45%.

**2026 catalyst calendar:**
- Q1 2026 earnings: April 22, 2026 (AMC) -- **two days after this
  document's generation date**.
- Q2 delivery print: early July 2026.
- Q2 earnings: late July 2026.
- Cybercab mass production: late April 2026 (now).
- Robotaxi expansion to 8 cities: by June 2026.
- Q4 delivery print: early January 2027 (historically the single
  worst vol day of the year for TSLA).

**Thesis breakers (THREE stacked risks):**
1. Q1 deliveries already missed (358k vs 366k consensus) with 50k
   inventory overhang. NA tariff drag on margin is live.
2. Robotaxi incident / NHTSA investigation on the Dallas/Houston
   unsupervised rollout = -20% single-day event.
3. Musk political overhang is unpriced; any renewed cap-table
   distraction can move -10%.

**IV behavior:**
- Highest-vol name of the 9. IV rank 70-95 pre-earnings routinely.
- Implied earnings move: 9-12%.
- Actuals: 10-18% (the market systematically UNDER-prices TSLA vol).
- Crush: -35 to -50 vol points.
- Weekly vol stays elevated between earnings because of Musk tweets
  and delivery-data leaks.

**Do-not-sell window:** April 18-24, 2026 (earnings in 2 days from
doc generation). Early January 2027 (Q4 deliveries). Any robotaxi
safety headline.

**Per-ticker discipline (IMPORTANT).** Do NOT sell naked puts on
TSLA. Defined-risk spreads only. 25-35 DTE, short strike >= 15%
OTM, long leg 20-25% OTM. CCs are the sanest structure if you hold
shares. Size at half your normal unit.

### 120. BROS (Dutch Bros)

**Profile.** High-beta small cap. Ticker_profile: "high_beta", IV
floor 45%. Special: thin liquidity.

**2026 catalyst calendar:**
- Q1 2026 earnings: May 13, 2026.
- Q2 2026 earnings: early August 2026.
- Q3 2026 earnings: early November 2026.
- Full-year guide: revenue $2.00-2.03B, EBITDA $355-365M, same-shop
  3-5% full year, Q1 4-6%.

**Thesis breakers:**
- P/E 80.6x vs restaurant peer 52x vs industry 20.6x means ANY comp
  miss is -20%+.
- Q1 guide flagged 200bp COGS pressure from coffee costs. A May
  print at 3% comps instead of 5% cracks it.
- **Structural risk: small-cap liquidity.** Average daily volume ~3M
  shares; bid-ask on options is wide; realized slippage on
  option-premium capture is typically half of screen.

**IV behavior:**
- IV rank 70-85 routine.
- Implied earnings move: 8-12%.
- Actuals: 10-20% (has been -20% on a single comp miss twice in
  last 6 quarters).
- Crush: -30 vol points, but option spreads are wide enough that
  realized capture is ~50% of screen.

**Do-not-sell window:** May 6-15. August and November earnings weeks.
Any consumer-discretionary weekly data softness (Redbook, BofA
spending pulse) in the weeks leading up.

**Per-ticker discipline (IMPORTANT).** Defined-risk ONLY. Short put
spreads 30-40 DTE, 0.20 delta, width <= $5. Do NOT ladder this name
-- one bad print and you take assignment on an illiquid name
trading at 80x with multiple-compression tail still ahead.

**Consider dropping BROS from the universe entirely.** The liquidity
trap plus the multiple-compression tail plus the small-cap behavior
make it the worst risk-reward of the 9 for a premium seller. The
argument for keeping it: it provides high-IV-rank optionality when
the megacaps are quiet. The argument against: the realized net (after
slippage) is materially worse than screen suggests, and one bad
print can wipe out the prior 12 months of BROS income.

### 121. Top three most dangerous names for naked premium selling

**TSLA > BROS > META**, in that order.

**TSLA**: single worst name for naked CSPs. Three structural tails
(Q4 deliveries, robotaxi events, Musk political). Historical earnings
moves 10-18% vs implied 9-12%: the market UNDER-prices TSLA vol. Size
at half normal. Defined-risk put spreads only. If holding shares, CCs
are fine but >= 15% OTM.

**BROS**: hidden danger because it looks sleepy. 80x P/E + 3-5% comp
growth means any disappointment is a -20% gap. Small-cap liquidity
makes assignment genuinely painful. Defined-risk put spreads only,
strike >= 10% OTM, width <= $5, notional <= $10k per spread, never
ladder through earnings. Strongly consider dropping from universe.

**META**: third-riskiest because the capex guide is an asymmetric
bomb. $115-135B 2026 capex means any quarter with revenue decel +
capex re-up triggers -12-15% gap (replayed twice in 2022 and Oct
2024). Sell between earnings only; 25-35 DTE; 0.15 delta; avoid
structures spanning earnings dates.

**Safest names for contrast:** MSFT (lowest vol, cleanest),
GOOG/AMZN (stable between catalysts), AAPL fine between event stack,
NVDA fine when IV rank > 40 (currently too low to sell profitably),
MU when DRAM contract prints are still sequentially positive.

### 122. Pipeline implication for single-name discipline

All of the per-ticker rules above should be encoded in the pipeline
as:

- **Per-ticker delta overrides.** Current code has a single
  `target_delta_abs_low = 0.20` / `target_delta_abs_high = 0.35`
  band for all tickers. Replace with per-ticker bands pulled from
  `TICKER_SPECIFIC_DISCIPLINE` map that encodes what this section
  says (e.g., TSLA max delta 0.15; BROS max delta 0.20; MSFT up to
  0.25).
- **Per-ticker DTE overrides.** Same idea. AAPL should default to
  25-35 DTE through summer; MSFT/GOOG can run 30-45.
- **Per-ticker structure overrides.** TSLA and BROS should surface
  bull-put-spread candidates, not naked puts. Others default to
  naked (the current behavior).
- **Per-ticker event-exclusion lists.** Each ticker's calendar of
  known 2026 catalysts is maintained in a small JSON
  (`ticker_events.json`) and used to zero-out candidate expirations
  that span known events.

This is v2 work, maybe 2-3 days of effort once the skeleton is
agreed. High-value relative to the current one-size-fits-all spine.

---

## Part XX -- End-to-end worked portfolio example

This section threads every principle in this compendium through a
single concrete trading session, start to finish. The assumption:
a $250,000 portfolio-margin account, Oregon resident, 32% federal
bracket, looking to open the week's new CSPs and evaluate existing
covered calls.

### 123. Step 1 -- Regime check (Parts I, VI)

Consult the macro-context tile set on the dashboard:
- VIX spot: 19.4. VX1/VX2 ratio: 0.94 (contango). No backwardation.
- SPX above zero-gamma: yes.
- Rolling 30-day SPX VRP: +3.1 points (low-end normal). **Size
  multiplier: 1.0x.**
- No FOMC / CPI / NFP / OPEX in next 72 hours.
- No major 9-ticker earnings in next 48 hours (TSLA's April 22
  earnings is past, META/MSFT/AMZN/GOOG April 29 cluster is in 9
  days).

**Verdict: green light for new entries on non-earnings-contaminated
names.**

### 124. Step 2 -- Per-ticker screen (Parts III, IV, XIX)

Filter the 9 tickers through event windows and per-ticker discipline:

| Ticker | Earnings in holding window? | Discipline gate                   | Eligible? |
|--------|-----------------------------|-----------------------------------|-----------|
| MU     | No (late June)              | 0.20 delta, 35-45 DTE, >= 10% OTM | Yes       |
| META   | Yes (Apr 29)                | Skip -- earnings contamination    | **No**    |
| NVDA   | Yes (May 20)                | Verify IV rank > 40; if not, skip | Conditional|
| MSFT   | Yes (Apr 29)                | Skip                              | **No**    |
| AMZN   | Yes (Apr 29)                | Skip                              | **No**    |
| GOOG   | Yes (Apr 29)                | Skip                              | **No**    |
| AAPL   | Yes (May 7)                 | Skip (in 17 days, 30-DTE spans)   | **No**    |
| TSLA   | No (earnings past)          | Defined-risk spread only, <=0.15d | Yes (DR)  |
| BROS   | Yes (May 13)                | Skip                              | **No**    |

**Eligible names today: MU, NVDA (conditional), TSLA (defined-risk).**
6 of 9 are blocked by the earnings cluster. This is the reality of
operating through earnings season and the reason the pipeline's
event filter is load-bearing.

### 125. Step 3 -- IV and VRP check on eligible names

From `options_chain.json` refresh (**numbers illustrative; the
pipeline checks actual values on each run**):
- MU ATM 30-day IV: 48%. IV rank (from iv_history): 62. Passes gate.
- NVDA ATM 30-day IV: 15%. IV rank: 12. **Fails NVDA-specific gate
  (need > 40). Skip.**
- TSLA ATM 30-day IV: 58% (post-earnings crushed from 85 pre-event).
  IV rank: 48. Passes but elevated baseline.

**Remaining eligible: MU, TSLA (defined-risk only).**

### 126. Step 4 -- Cluster check (Part V)

Current open-position book (from `positions.json`):
- 2 short MU puts (semis cluster, vega $180)
- 1 short NVDA put opened previously (semis cluster, vega $130)

Total semis cluster short vega: $310. Cap per sector cluster: say
$500 (roughly 25% of total premium cap in a $250k account).

Adding 2 more MU puts would push semis cluster to ~$490, right at
cap. **Size constraint: max 1 new MU contract, not 2.** (If AVGO or
another semis name were in the universe, the cap would bind harder.)

### 127. Step 5 -- Select strike and size

For MU at $455 spot, aim 0.20 delta, 35 DTE (aligning with the Section
97 worked table but with delta reduced from 0.25 to 0.20 per MU's
per-ticker discipline in Section 112; BP estimates scale down
proportionally):
- Target strike: ~$415 (8.8% OTM).
- Premium at $415 strike 35 DTE: $5.50 (from chain).
- Reg-T naked put BP: ~$8,552 / contract.
- Cash-secured BP: $40,950 / contract.
- PM BP estimate: ~$3,000 / contract (lower delta reduces worst-case
  stress-test loss, so actual PM BP would be slightly under $3,000).

Size: 1 contract (cluster-cap limit). Total BP consumed on this
trade under PM: $3,000. Current total PM BP utilization pre-trade:
say 35%. Post-trade: 36.2%. Still below the 50% soft cap.

### 128. Step 6 -- Expected net yield calculation (Part XVI)

Gross premium: $5.50 x 100 = **$550**.
- Spread slippage (8% spread on $5.50 mid = $0.44 spread, 1/3-of-mid
  fill per leg) = -$7.33 per leg x 2 = -$14.67.
- Round-trip commissions (IBKR Pro or similar): ~$1.30.
- Pre-tax net = $550 - $14.67 - $1.30 = **$534.03**.

Tax drag (Oregon, 32% federal + 9.9% state + 3.8% NIIT = **45.7%**
effective on STCG for MU single-name):
- After-tax net = $534.03 x (1 - 0.457) = **$290.00**.

Compare to an SPX equivalent at similar beta-adjusted exposure (if
the pipeline computed one):
- Hypothetical SPX short put with $500 gross premium.
- Friction: ~$12 slippage + $1.30 commissions = ~$486.70 pre-tax.
- Section-1256 blended rate for Oregon: 60% * (15% + 9.9% + 3.8%) +
  40% * 45.7% = 60% * 28.7% + 40% * 45.7% = **35.5%**.
- After-tax net = $486.70 x (1 - 0.355) = **$313.93**.

The SPX equivalent generates ~$24 more after-tax on a comparable
beta-adjusted trade, or about 8% more net yield per unit of vol-
sold. This is the quantified case for rotating part of the book to
SPX / XSP over time.

### 129. Step 7 -- Pre-commit exit rules

Before the trade opens, the decision journal records:
- **Entry**: MU short put, strike $415, expiry in 35 days, delta
  0.20 at entry, IV 48%, IV rank 62. Rationale: "semis-cycle VRP,
  high IV rank, MU earnings past expiration. Size capped at 1 due
  to semis cluster."
- **Profit target**: close at 50% of max profit (i.e., buy back at
  $2.75 mid).
- **Management trigger**: close or roll at 21 DTE remaining if trade
  is not yet at 50% profit.
- **Stop loss**: close at 200% of credit received (~$11.00 mid) if
  MU drops through strike and the trade runs against.
- **Earnings contingency**: if MU pre-announces or issues a
  negative pre-release, close immediately regardless of P&L.

### 130. Step 8 -- Monitoring the open position

Over the next 35 days, the private email surfaces:
- Day 1-7: P&L tracking; position should move with delta.
- Day 14: first management checkpoint ("is it at 50% yet?").
- Day 21: mandatory management checkpoint. If not at 50% profit,
  decide: close, roll, or hold with tighter stop.
- Any DRAM-cycle news, NVDA / AMD / TSMC quarterly updates, or
  HBM-supply news should trigger a "reassess" prompt.

### 131. Step 9 -- Close or roll

At Day 21:
- Scenario A: MU rallied, position at 62% of max profit. **Close
  for $2.09 mid. Net: $550 - $209 - slippage - commissions =
  ~$330 pre-tax, ~$179 after-tax.** Record outcome in
  `trades_ledger.jsonl`.
- Scenario B: MU flat, position at 38% of max profit. **Hold 7 more
  days; if still < 50% at 14 DTE, close regardless.**
- Scenario C: MU dropped to $410, position at -60% (losing trade).
  **Roll the put down-and-out for a net credit to a 30 DTE, $395
  strike. If no net credit available, close and take the loss.**

### 132. Step 10 -- Calibration update

Every closed trade feeds the calibration ledger:
- Entry delta / actual outcome (expired worthless?).
- IV at entry vs realized vol over holding period (captured VRP).
- Rationale tags from entry vs actual exit driver.
- Per-ticker rolling win rate (Bayesian posterior update).

After 50 closed trades, the calibration chart answers: "are our
picks actually better than random?" That is the honesty mirror the
pipeline exists to hold up.

### 133. The "what if we did nothing today" scenario

A disciplined seller should be comfortable with zero new positions
on 1-2 days per month. Today had 6 of 9 tickers blocked by the
earnings cluster, NVDA's IV too low, and the semis cluster near cap
on the remaining eligible name. A reasonable alternative to forcing
the MU trade: wait 10 days, let the earnings cluster resolve,
re-screen the entire 9-ticker universe with fresh IV ranks, and
deploy fresh premium into the post-earnings IV-crush window -- which
is historically one of the best setups available (Setup B in Section
69).

**There is no requirement to trade today.** The pipeline's twice-
daily cadence surfaces the best trades when they exist; it does not
demand you take a trade every refresh.

---

## Appendix A -- Plain-English glossary

- **Delta**: the option's price sensitivity to $1 stock moves. Also a
  rough probability.
- **Gamma**: the option's delta sensitivity to $1 stock moves.
  Acceleration.
- **Theta**: the daily dollar change from time passing.
- **Vega**: the dollar change per 1-point change in implied vol.
- **IV rank**: where current implied vol sits in its 52-week range, as
  a percent.
- **VRP (volatility risk premium)**: the persistent gap where implied
  vol > realized vol. The structural edge of premium selling.
- **CSP (cash-secured put)**: short put backed by cash equal to strike.
- **CC (covered call)**: short call against owned shares.
- **The Wheel**: CSP -> assigned -> CC -> called away -> CSP -> ...
- **OPEX**: monthly option expiration (3rd Friday). Quarterly OPEX
  (March, June, September, December) is bigger.
- **0DTE**: options expiring same day.
- **GEX (gamma exposure)**: aggregate dealer gamma position. Positive
  = dampening, negative = amplifying.
- **Skew**: the shape of the IV-across-strikes curve. Put skew =
  downside protection is more expensive than upside.
- **Term structure**: IV across different expirations. Contango =
  longer > shorter (normal). Backwardation = shorter > longer (stress).
- **Assignment**: being required to fulfill the short option contract.
  Short put assigned = you buy 100 shares at strike. Short call
  assigned = you sell 100 shares at strike.
- **The 21-DTE rule**: a management rule to close or roll short
  options at 21 days remaining, because gamma acceleration ruins
  returns past that point.
- **RR25 (25-delta risk reversal)**: IV(25d_call) - IV(25d_put). A
  single-number skew summary.

---

## Appendix B -- Formula reference

**Black-Scholes call price** (for reference; CBOE feed gives us
prices and greeks directly):
```
C = S * N(d1) - K * exp(-rT) * N(d2)
d1 = [ln(S/K) + (r + sigma^2/2) * T] / (sigma * sqrt(T))
d2 = d1 - sigma * sqrt(T)
```

**Delta**:
- Call delta: N(d1)
- Put delta: N(d1) - 1

**Gamma** (same for call and put):
```
gamma = phi(d1) / (S * sigma * sqrt(T))
```

**Theta** (per day, divide by 365):
```
call_theta = - [S * phi(d1) * sigma / (2 * sqrt(T))] - r * K * exp(-rT) * N(d2)
put_theta  = - [S * phi(d1) * sigma / (2 * sqrt(T))] + r * K * exp(-rT) * N(-d2)
```

**Vega** (per 1% IV move):
```
vega = S * phi(d1) * sqrt(T) / 100
```

**IV rank**:
```
iv_rank = (iv_current - iv_52w_low) / (iv_52w_high - iv_52w_low) * 100
```

**Expected move** (1 standard deviation):
```
expected_move = spot * iv * sqrt(dte / 365)
```

Alternative: expected_move ~ ATM straddle price (the straddle's mid
price is approximately the one-SD move).

**RR25**:
```
rr25 = iv_25_delta_call - iv_25_delta_put
```

**Premium yield annualized on cash-at-risk for short put**:
```
yield_annualized = (premium / strike) * (365 / dte) * 100
```

(Our current pipeline uses a 30-day-equivalent normalization -- same
idea, different denominator.)

**Kelly fraction for a binary bet**:
```
kelly = (p * b - q) / b
  p = probability of winning
  q = 1 - p
  b = payoff ratio (gain / loss)
```

**Do NOT use Kelly for short-option sizing.** For a typical 0.30-delta
short put, `b = premium / max_loss ~ 0.02`, which makes naive per-trade
Kelly strongly negative (order of -1400%). The wheel is
positive-EV only because (a) management caps realized max loss well
below theoretical max, (b) diversification reduces book variance, and
(c) assignment on names you would own anyway is not really a "loss."
See Section 29 for the full derivation. Size using the practitioner
consensus numbers (30-50% of equity gross short-premium notional; 5%
max per ticker; 25% sector cap), not Kelly.

---

## Appendix C -- Reading list

**Books**:
- Sheldon Natenberg, *Option Volatility and Pricing*. The canonical
  reference. Dense but necessary.
- Euan Sinclair, *Volatility Trading* (2013). The quant-flavored
  treatment of VRP and vol-selling.
- Euan Sinclair, *Positional Option Trading* (2020). The practical
  follow-up,
  focused on how to actually execute.
- Euan Sinclair and Andrew Mack, *Retail Options Trading* (2024).
  The most recent Sinclair text specifically aimed at retail
  premium sellers. Distills the VRP-plus-regime-detection logic this
  compendium uses as its spine.
- Lawrence McMillan, *Options as a Strategic Investment*. The classic
  retail reference.
- Benn Eifert, *Volatility: Practical Options Theory* (his Twitter
  threads + QVR Advisors research).

**Research archives**:
- Tastytrade Research Team's "Market Measures" and "The Skinny on
  Options" studies. tastytrade.com/research
- Option Alpha research. optionalpha.com
- CBOE research (PUT index, PPUT index, BXM index methodology docs).
  cboe.com/us/indices

**Quant blogs**:
- Robot Wealth (Kris Longmore) -- periodic vol-selling studies.
- FOSS Trading -- R packages for options analytics.
- Moontower (Kris Abdelmessih) -- excellent on skew and dealer flows.

**Community**:
- r/thetagang -- read the pinned "starter guide" and "biggest losses"
  threads.
- r/options -- Redtexture's FAQ and pinned DD.
- tastytrade's YouTube archive.
- SpotGamma's free daily notes (GEX context for SPX).

---

*End of compendium v1.0 foundation. Part VIII (practitioner knowledge)
and Part IX (flash-trader techniques) to be expanded from research
agent output.*
