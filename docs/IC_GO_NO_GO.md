# Investment-Committee Go/No-Go Engine

A second four-agent layer that scores a **candidate self-storage deal** against two *proven
winners* and the firm's market ranking, then returns a **GO / CONDITIONAL GO / NO-GO** verdict
— delivered both as a Claude-agent narrative and as a **live Excel dashboard** with a dropdown.

## The two proven winners (the benchmark)

| Deal | Archetype | Why it worked |
|------|-----------|---------------|
| **Springfield** | Income/Core DST — all-equity, ~7.0% going-in & exit cap, ~14% op-ex, ~11% IRR | Durable in-place yield, no leverage or lease-up risk, predictable distributions |
| **Hamburg** | Development — ~40% LTV, ~7.4% stabilized yield-on-cost vs ~5.5% exit cap (≈190 bps spread), ~17% IRR, ~63k NRSF / 11 ac | Value created at a yield well above the exit cap in a growing, supply-constrained market |

Every candidate is classified as one of these two archetypes and scored against it.

## The four agents

| # | Agent | Role |
|---|-------|------|
| 1 | **deal-benchmarker** | Extract the candidate's metrics; classify income/core vs development |
| 2 | **deal-screener** | Run the hard methodology gates → pass/fail with reasons |
| 3 | **market-fit-analyst** | Match the deal's market to the ~246-market weighted ranking |
| 4 | **ic-verdict** | Synthesize GO / CONDITIONAL / NO-GO with pros, cons, and the "why it works" story |

They ship as Claude Code subagents in `.claude/agents/` and share one deterministic engine
(`deal_agent/ic/`) so the words and the numbers always agree.

## The gates

Weights sum to 100. Three gates are **critical** — failing any one is a committee veto and
forces NO-GO regardless of score.

| Gate | Threshold | Weight | Critical |
|------|-----------|:------:|:--------:|
| IRR beats exit cap | best IRR > exit cap | 15 | ✅ |
| Yield clears floor | yield ≥ 6.5% (full ≥ 7.5%) | 15 | ✅ |
| Market population | ≥ 200,000 | 12 | ✅ |
| Op-ex ratio | ≤ 35% (pref ≤ 30%) | 10 | |
| Population growth | 5-yr positive (pref ≥ 5%) | 10 | |
| Supply pipeline | ≤ 10% (pref ≤ 5%) | 10 | |
| Return target | IRR ≥ 10% income / 15% dev | 13 | |
| Market rank | upper half of ranking | 8 | |
| Project size | ~40k–120k NRSF (target 75k) | 7 | |

**Verdict:** score ≥ 70 → GO · 50–69 → CONDITIONAL GO · < 50 or any critical fail → NO-GO.

## Use it

```bash
# Score a candidate pro forma (markdown scorecard + side-by-side vs the winners):
python -m deal_agent.ic.cli evaluate --proforma NewDeal.xlsx --market "Nashville, Tennessee"

# Add a candidate to the live Excel dashboard and rebuild it:
python -m deal_agent.ic.cli add --proforma NewDeal.xlsx --market "Nashville, Tennessee"

# (Re)build the dashboard from the benchmarks + saved candidates:
python -m deal_agent.ic.cli build --out IC_GoNoGo_Dashboard.xlsx
```

Inside a Claude Code session you can also say *"use ic-verdict to evaluate NewDeal.xlsx in
Nashville"* and it will drive the benchmarker, screener, and market-fit steps.

## The Excel dashboard

`IC_GoNoGo_Dashboard.xlsx` is self-contained — **no API key, no add-in**:

- **Dashboard** — pick a deal from the **dropdown**; the verdict, the side-by-side vs
  Springfield & Hamburg, and every gate score recalculate instantly (live `INDEX/MATCH` +
  `IF` formulas that reproduce the engine exactly).
- **Add a Deal** — instructions + a one-deal input form (read by the macro button).
- **Deals** — one column per deal. The proven winners are locked; ready-to-fill **"New Deal"
  slots** are pre-wired into the whole engine.
- **Scores** — the live gate engine for every deal at once.
- **Ranking** — all deals with score + verdict; sort by score for the go/no-go ranking list.
- **Market Ranking** / **Market Data** — the weighted ranking (top markets + a full lookup table).

### Adding any deal — drop a spreadsheet in

1. **Double-click launcher (no macros, no command line).** `launchers/Import Deal.command`
   (macOS/Linux) or `launchers/Import Deal.bat` (Windows). Double-click it for a file picker,
   or **drag a pro forma onto it**. It extracts the metrics, **auto-detects the market**
   (fuzzy-matched to the ranking), scores the deal, adds it to `IC_GoNoGo_Dashboard.xlsx`, and
   opens it. Needs Python 3 + this repo + `ic_data/` populated.
2. **In-Excel Import button.** Save the workbook as `.xlsm`, import `excel/AddDeal.bas`, and
   assign the **`ImportProForma`** macro to a button. Click it, pick a pro forma — same
   extraction, all inside Excel, no Python.
3. **Type it in.** On the Deals tab, find the first empty **New Deal** column (yellow cells),
   pick the **Deal type** and the **Market (county)** from the dropdowns, and enter the
   economics. Market stats **auto-fill from the county via `VLOOKUP`**.
4. **Python one-liner (the tested engine of record).**
   `python -m deal_agent.ic.cli add --proforma X.xlsx --market "<county>"`.

> If a pro forma names its market (a "County"/"Market"/"Location" cell), the market is matched
> automatically; otherwise the deal still imports — pick the county from the slot's dropdown to
> complete the market gates. Excel can't embed a macro into an `.xlsx`, so option 2's button is
> a one-time setup; options 1, 3, and 4 need no macros. All decide GO/No-Go off the same
> Springfield & Hamburg statics.

### What files the importer accepts

The Python importer (options 1 & 4 above) reads:

| Input | Handling |
|-------|----------|
| `.xlsx` / `.xlsm` / `.xls` pro forma | line-item scan → NOI, caps, IRR, equity/debt, NRSF |
| `.csv` | same line-item scan |
| **`.zip` package of financials** | unpacks and picks the most relevant statement inside (prefers a Rolling-12 / T-12 / pro forma / underwriting file) |
| **T-12 / rolling-12 operating statement** | reads the **Total** column (or sums the months) → total revenue, NOI, op-ex ratio |

An **operating statement** (actuals) supplies NOI and the op-ex ratio but **not** the
investment metrics — price/cap, IRR, and market. Those rows stay blank and surface as gate
failures, so such a file scores low until you add the deal's cap/return/market assumptions
(type them into the slot, or pair it with a pro forma). The benchmarks are **self-storage**, so
treat verdicts for other property types as a financial read, not an apples-to-apples call.

The dashboard verdicts were validated against the Python engine with a real formula evaluator:
Springfield → GO (85), Hamburg → GO (78.5); a filled development slot → GO (85); thin-yield and
IRR-below-cap deals → NO-GO via the critical veto; an empty slot → NO-GO.

## Data & confidentiality

Real benchmark economics and the market ranking are **client data** and stay out of git
(`ic_data/benchmarks.json`, `ic_data/market_ranking.csv`, `ic_data/candidates.json` are
git-ignored). A committed `ic_data/benchmarks.example.json` documents the schema with
placeholder numbers so the engine runs without the confidential files.

Not legal, financial, or investment advice. Verify all figures independently before acting.
