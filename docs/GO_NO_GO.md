# Go / No-Go Ranking — Design

A five-agent committee that ranks self-storage development deals **GO /
CONDITIONAL / NO-GO** by benchmarking each against two proven deals the team
already did: **Hamburg** and **Lewiston**.

## Why benchmark-relative

"Will this deal work?" is hard in the abstract but easy in comparison: *does it
look like the deals that worked?* Hamburg and Lewiston are the yardstick. A new
deal is scored on how its storage-development economics stack up to their band.

## The five agents

| # | Agent | Role | Backed by |
|---|-------|------|-----------|
| 1 | **Benchmark Curator** | Owns Hamburg/Lewiston + the thresholds | `benchmark_reference` |
| 2 | **Underwriter** | Extracts + scores the deal's economics | `extract_deal_metrics`, `score_go_no_go` |
| 3 | **Market Scorer** | Judges market quality | `extract_deal_metrics` |
| 4 | **Risk Screener** | Finds hard knockouts + red flags | `score_go_no_go` |
| 5 | **Committee Chair** | Final verdict + ranked list | delegates to 1–4, `rank_and_export` |

The Chair is the entry point and consults the other four as tools — the same
delegation pattern as the existing deal `orchestrator`.

## Two layers

1. **Deterministic engine** (`engine.py`) — encodes the benchmarks as numeric
   thresholds and scores any deal with no API call. This is what makes
   *"attach a file → auto Go/No-Go"* reliable and free.
2. **Agent layer** (`agents.py`) — the five Claude Agent SDK agents reason over
   the engine's output and write the committee narrative.

```
   deal file(s) ─▶ extract_deals() ─▶ DealMetrics ─▶ score_deal() ─▶ Verdict
                                                          │
                  rank_deals() ◀───────────────────────────┘
                       │
                       ▼
        write_ranking_workbook()  →  go_no_go_ranking.xlsx
```

## What gets scored

Each deal is mapped to a normalized metric set (missing fields stay unknown):

| Metric | Direction | Why it matters |
|--------|-----------|----------------|
| **Development spread** (YoC − exit cap) | higher | The #1 ground-up storage signal (weight 26%) |
| **Stabilized yield on cost** (NOI / cost) | higher | Return on the build (20%) |
| **Levered / project IRR** | higher | Equity return (20%) |
| **Equity multiple (MOIC)** | higher | Total return (12%) |
| **Market quality score** | higher | Demand/supply/growth (12%) |
| **Lease-up months** | lower | Execution risk (6%) |
| **Exit cap rate** | lower | Valuation risk (4%) |

Each metric maps to 0–100 via three thresholds (NO-GO floor → 0, CONDITIONAL →
50, GO → 100, interpolated). The blended score is the weighted average over the
metrics actually present.

### Decision bands

- **GO** — score ≥ 70 and no metric below its hard floor.
- **CONDITIONAL** — 55–70; clears every floor but trails the benchmarks.
- **NO-GO** — score < 70 with any **hard knockout**, or score < 55.

A single hard knockout (e.g. levered IRR below 10%) caps the verdict at NO-GO no
matter how strong everything else is.

## Reading any file

`extract_deals()` handles three shapes automatically:

1. **Market-ranking table** (CSV or sheet) with named columns like *Stabilized
   Yield on Cost*, *Dev. Spread*, *Exit Cap %*, *Rank (1 = Best)* → one deal per row.
2. **Side-by-side model** — metrics down column 0, one deal per column (the
   `dev_model_11_markets.xlsx` layout) → one deal per column.
3. **Generic proforma** — any other workbook: scans for metric keywords and
   grabs the nearest numeric value (handles the Springfield DST proforma and most
   one-off attachments).

Same-named deals across sheets are merged, and yield on cost / dev spread are
derived when the file gives NOI, cost, and exit cap but not the ratio itself.

## Plugging in your real Lewiston (and editing the bar)

Hamburg's numbers are grounded in `hamburg_cashflow.xlsx`. **Lewiston was not in
the uploaded files**, so its profile in `benchmarks.py` is a clearly-flagged
placeholder. To use your actual Lewiston deal, edit the `LEWISTON` block in
`deal_agent/gonogo/benchmarks.py`. To move the bar, edit `THRESHOLDS` in the same
file — every score and verdict recomputes from it.

## Ask a question — live answers (in Excel or the terminal)

Instead of reading a frozen table, you can *ask* for a verdict and have it
generated live from the current data.

**In the terminal:**

```bash
python -m deal_agent.gonogo ask "is Hamburg a go or no go?"
python -m deal_agent.gonogo ask "TX" --files dev_model_11_markets.xlsx
```

**In Excel** (live worksheet functions via the `xlwings` add-in):

```
=GONOGO_ASK("is Hamburg a go?")   -> Hamburg: GO (100/100). ...
=GONOGO("TX")                     -> GO
=GONOGO_SCORE("Springfield")      -> 16
=GONOGO_WHY("NE")                 -> NO-GO — fails the IRR floor ...
=GONOGO_BENCHMARK("Hamburg","dev_spread_bps") -> 190
```

Generate a ready-to-use workbook (works as a static snapshot immediately; the
cells go live once xlwings is wired up — see its **Setup** tab):

```bash
python -m deal_agent.gonogo workbook --out GoNoGo_Live.xlsx
```

Setup for live cells: `pip install "xlwings>=0.30"`, `xlwings addin install`, then
in Excel's xlwings ribbon set **UDF Modules** to `deal_agent.gonogo.excel` and
click **Import Functions**.

### Where the live data comes from

`GONOGO_ASK` / `GONOGO` resolve a name (or a whole question) to a deal in the
**deal library**, which is rebuilt on every call from:

- the benchmark deals (Hamburg, Lewiston), plus
- every deal in the files named by the `GONOGO_DEAL_FILES` env var (comma/
  semicolon separated), or dropped into a `./deals` folder.

Because it re-reads on each call, editing the underlying model — or the
benchmarks — changes the answer immediately. That is the "live" behavior: the
spreadsheet computes the verdict on demand rather than storing a stale one.

## Tests

```bash
python -m deal_agent.gonogo.tests.test_engine
```

## Disclaimer

Analytical decision support — **not** legal, financial, or investment advice.
Verify every figure independently before acting.
