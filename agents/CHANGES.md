# IC Agent Toolkit — Revision Notes

## Revision 3 — "make the agents more useful" (June 2026)

The toolkit shipped **broken** on a clean checkout and had two whole
subsystems that were loaded but never used. This revision makes all agents
run correctly, then adds real capability.

### Correctness — the toolkit now runs end-to-end

- **`screening_agent.py` did not parse.** A `—` escape inside an f-string
  *expression* (`{... 'present — skipped'}`) is a `SyntaxError` on
  Python < 3.12. Moved the text out of the expression. The agent now imports.
- **`extract_deal()` crashed every caller** (drafter, monitor, the whole
  pipeline). The "context managers on all workbook opens" change from the prior
  revision used `with load_workbook(... read_only=True)`, but openpyxl read-only
  workbooks do **not** implement the context-manager protocol on this version
  (`TypeError: 'Workbook' object does not support the context manager
  protocol`). Added an `_open_wb()` helper that closes the workbook in a
  `finally`, working for read-only and read-write alike.
- **Every extracted deal field was `[TBD]` / $0.** `_detect_current_col()`
  selected the *rightmost populated* column — which is an openpyxl
  `ColumnN` placeholder full of zeros — instead of the current underwriting
  column ("Zach Model", index 9). Rewrote it to read the Budget History header
  rows and take the rightmost column carrying a *real* stage label (skipping
  `ColumnN` placeholders). Extraction now matches the known-good `deal.json`
  exactly (levered IRR 18.5%, total cap \$10.03M, equity \$5.77M, etc.).
- **The progress curve zig-zagged** (33% → 39% → 13% → 54%). `_extract_status()`
  took the *last* in-(0,1) cell of each CF Grand Total row, which is a stray
  non-monotonic ratio. Switched to the *first* cell — the costs-incurred
  percentage — giving a monotonic curve (33.4% → 39.1% → 54.0%).

### New — Agent 5: Platform (`platform_agent.py`)

The June-2026 data integration added `load_dev_model()` and
`load_factory_model()` to the framework, but **no agent consumed them**. The
new Platform agent turns that data into an IC deliverable:

- capital-allocation **leaderboard** of the 11 workforce-housing markets,
  ranked by LP IRR, with Phase 1 anchors called out;
- platform roll-up (TPC, LP equity to raise, blended LP IRR);
- **risk flags** (markets at/below the 8% pref hurdle, sub-platform laggards,
  Phase 1 blended-yield trade-off);
- the captive **Factory Fund** engine — P&L ramp (Y1→Y5) and 10-yr waterfall;
- a two-panel chart (LP IRR by market vs. hurdle & avg; Factory EBITDA ramp).

Wired into `pipeline.py` as `STAGE 5`; run alone with `--only platform`.

### New — discovery / leaderboard screening (`screening_agent.py`)

The screening agent was a name-lookup; you could only score markets you already
knew. It is now also a **sourcing tool**:

- `--top N` ranks the whole 246-market model after screening;
- `--state NY` / `--region <substr>` filter the field (state accepts postal
  abbreviations *or* full names; output shows clean 2-letter codes);
- `--advance` / `--consider` keep only those verdicts;
- `--export FILE.csv` writes the screen results (metrics + verdict) to CSV.

Backed by new framework helpers `all_markets()`, `state_abbr()`,
`state_matches()`.

### New — the dormant LLM narrative layer is now wired in

`llm.polish()` existed but **nothing called it**. The screening, monitor, and
platform agents now accept `--polish` (and `pipeline.py --polish`), which adds
a committee-ready narrative when `ANTHROPIC_API_KEY` is set and silently falls
back to the deterministic text otherwise. Numbers and screen logic stay
rule-based — the LLM only rewords.

### Docs

- Added `README.md` for the toolkit (quick start, agent table, data map).

---

## Critical bug fixes

### Version merge (icframework.py)
`pipeline.py` referenced `f.extract_deal.cache_info()`, `f.load_market.cache_info()`,
and `f.MARKET_CSV` — symbols that only existed in the `(1)`-suffix draft of
icframework.  Those features are now in the canonical `icframework.py`.
The duplicate `(1)` files have been removed.

### Hardcoded Hamburg metadata (icframework.py)
`extract_deal()` hardcoded `name`, `subtitle`, `asset_type`, and `location` as
Hamburg strings.  These are now derived from the workbook path via
`_infer_deal_name()`.  Add a **"Deal Name"** row to Budget History (column B,
value in the current underwriting column) to supply an exact name.

### Hardcoded column index (icframework.py)
`cur = 9` was a magic constant (labeled "Zach Model").  It is now auto-detected
by `_detect_current_col()`, which scans the first 15 Budget History rows for the
rightmost populated column.  `BH_COL_CURRENT = 9` remains as the fallback.

### render() was not concurrent (ic_drafter.py)
`pipeline.py` promised "memo.js + deck.js rendered concurrently" but
`render()` called `subprocess.run()` twice, sequentially.  It now uses
`ThreadPoolExecutor(max_workers=2)` with `as_completed()`.

## Code quality fixes

### Context managers on all workbook opens (icframework.py)
All `load_workbook()` calls now use `with` blocks.  Prevents leaked file handles
on Windows and in long-running processes.

### Named constants for verdict thresholds (icframework.py, screening_agent.py)
`pctile >= 0.80`, `pctile >= 0.50`, `passed >= 3` are now
`f.ADVANCE_PERCENTILE`, `f.CONSIDER_PERCENTILE`, `f.ADVANCE_MIN_PASS`.
Adjust IC policy in one place.

### Named constants for Budget History columns (icframework.py)
`BH_COL_INITIAL = 4`, `BH_COL_FINAL = 5`, `BH_COL_PPM = 6`, `BH_COL_CURRENT = 9`.

### Improved _extract_status heuristics (icframework.py)
`_extract_status()` now takes the **last** float in `(0, 1)` from the Grand Total
row (not the first), reducing the chance of matching a stray percentage column.

### Lazy matplotlib import (monitor_agent.py)
`matplotlib.use("Agg")` and `import matplotlib.pyplot as plt` moved inside
`chart()`.  Importing `monitor_agent` in `pipeline.py` no longer forces the Agg
backend as a module-level side effect.

### Retry logic in llm.py
`polish()` now retries up to 3 times on transient HTTP errors (429, 500–503, 529)
with exponential backoff (1.5 s → 3 s → 6 s).  Each retry and the final fallback
are logged at `WARNING` level.

### _find_header() includes file path in ValueError (icframework.py)
Malformed or updated workbooks now produce a useful error message.

## New features

### --append-log (screening_agent.py, pipeline.py)
`screening_agent.append_to_log(market, result)` writes a row to `deal_log.csv`
with status=Screening, model score, pro-forma IRR, and the one-word verdict.
Skips markets already present.  Exposed as:

    python screening_agent.py "Monroe County" --append-log
    python pipeline.py --screen "Monroe County" --append-log
    python pipeline.py --screen-log --append-log   # screen + log all front-of-funnel

### --rebuild-cache (pipeline.py, build_market_cache.py)
    python pipeline.py --rebuild-cache
Re-extracts `data/market_ranking.csv` from the source workbook and exits.
Equivalent to running `build_market_cache.py` directly.

### --output-dir (pipeline.py, all agents)
    python pipeline.py --output-dir /tmp/ic_out
Sends all generated files (deal.json, .docx, .pptx, .xlsx, .png) to a custom
directory instead of the hardcoded `agents/out/`.  Useful for comparing multiple
projects without overwriting previous outputs.

### os.makedirs(OUT) on import (icframework.py)
The `out/` directory is created automatically if it doesn't exist, so agents
don't fail on a fresh checkout.

## Data files integrated (June 2026)

### Real workbooks now in agents/data/
The following production files replace the placeholder references:
- `data/hamburg_cashflow.xlsx` — actual Hamburg project workbook (Jan 2026 snapshot)
  with Budget History (10 underwriting columns) + CF sheets through CF-Feb 26.
- `data/market_model.xlsx` — actual 246-market weighted ranking model (June 2025,
  v1.1), sheet `WeightedRanking` with full metrics for screening and the CSV cache.
- `data/market_ranking.csv` — pre-extracted CSV cache (246 markets, rebuilt from
  the June 2025 workbook). Screening agent reads this instead of the 16 MB workbook.

### deal.json updated with Feb 2026 actuals
- `pct_complete`: **61%** (committed-minus-remaining basis, Feb 26 CF snapshot)
  Previously 54% from an earlier costs-incurred calculation. The monitor agent
  had flagged this discrepancy; the Feb 2026 actuals resolve it at 61%.
- `remaining`: **$3.47M** (was $4.10M — reflects $5.43M completed to date)
- All other fields confirmed against the actual Budget History col 9 (Zach Model).

### Hamburg market context
Erie County, NY ranks **#200 / 246** in the market model (score 0.477, model
IRR 14.5%). The actual project underwrites at 18.5% levered IRR — outperformance
driven by site-specific CC rates ($18.49/SF), the specific program mix, and
capital structure. The county-level model IRR reflects market averages.

### REIT market data
Top-10 states by REIT acquisitions 2021–2024 documented in CHANGES.md;
NY and MD lead on pro-forma IRR (19.4%) with the lowest SF/capita (6.5).

## New models integrated (June 2026)

### data/dev_model_11_markets.xlsx  (May 29, 2026 · v1.0)
Captive Dev Model for the 11-market workforce-housing platform (The House Factory).
Markets: OK (anchor), NE, TX, NM, GA, AR, KS, AL, TN, AZ, IA.
Sheets: Cover · Market Inputs · Base Assumptions · Per-Market Economics ·
        Per-Market Waterfall · Side-by-Side Comparison · Platform Roll-Up · AMI Validation

New function: **`load_dev_model(path=DEV_MODEL)`** (lru_cache, max 4 per process)
Returns a dict with three top-level keys:
  • `"markets"` — tuple of 11 per-market dicts sorted by project IRR descending.
    Each contains: code, name, tier, premium, distance_mi, rents (2BR/3BR/blended),
    cost build-up (land, site work, soft costs, kit cost), TPC, capital stack
    (LP/GP equity, construction loan), stabilized NOI, perm loan, Y3 refi recap,
    exit cap + value, net exit proceeds, project IRR/MOIC, LP/GP IRR/MOIC,
    NHF 40/40/20 split (nhf_take, usedc_take, newco_take), phase booleans.
  • `"platform"` — aggregate + Phase 1 roll-up: total TPC, LP equity, NOI, exit value,
    avg/min/max LP IRR, Phase 1 avg LP IRR/MOIC, LP equity raised.
  • `"meta"` — title, version, date.

Key outcomes (pre-incentive, base case):
  Platform avg LP IRR: ~12.9%  ·  Phase 1 (TX/OK/AR) avg LP IRR: ~13.8%
  Top market: TX 17.0% LP IRR / 2.19× MOIC  ·  Bottom: NM 8.0% LP IRR

### data/factory_model_standalone.xlsx  (May 28, 2026 · v2.0)
Operating company P&L + Factory Fund waterfall for The House Factory (OKC anchor).
Sheets: Cover · Assumptions · HF P&L · Factory Fund Waterfall · Platform Roll-Up ·
        Exec Comp Detail · Sensitivities · Annual Payout Schedule

New function: **`load_factory_model(path=FACTORY_MODEL)`** (lru_cache, max 4 per process)
Returns a dict with four top-level keys:
  • `"assumptions"` — fund structure (equity, hurdle, promote, hold, exit multiple),
    kit pricing by tier (T1–T4, captive), all-in COGS, production capacity,
    facility capex (land+building $12.5M, equipment $5.5M, reserve $5.5M),
    annual facility cost, AM fee.
  • `"pnl"` — Y1–Y5 dict: revenue, COGS, gross_profit, overhead, ebitda, ebitda_margin.
  • `"waterfall"` — 10-yr fund: LP/GP totals, LP MOIC, GP MOIC, fund IRR, tier-by-tier
    distributions (principal, 8% pref, GP catch-up, 70-30 residual split).
  • `"sensitivities"` — gross margin (price × cost) and EBITDA (capacity × utilization) tables.

Key outcomes:
  Y5 EBITDA: $12.0M / 30.0% margin  ·  Y5 revenue: $39.9M
  10-yr Fund IRR: 40.6%  ·  LP MOIC: 9.74×  ·  GP MOIC: 20.65×
  Exit: 10× Y10 EBITDA = ~$119.8M  ·  Total distributable: $216.5M

### New path constants in icframework.py
  DEV_MODEL     = data/dev_model_11_markets.xlsx
  FACTORY_MODEL = data/factory_model_standalone.xlsx
