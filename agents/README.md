# IC Agent Toolkit

Five rule-based agents that take a real-estate deal from **market screen** to
**IC package** to **construction monitoring**, plus a **platform** capital-allocation
view. Every number traces to a workbook cell, so the output is auditable; an
optional LLM layer only rewords the deterministic findings.

```
market name ─▶ ① SCREEN ─▶ ② DRAFT (memo+deck) ─▶ ③ HOPPER ─▶ ④ MONITOR
                                                                  │
                              ⑤ PLATFORM (11-market + Factory Fund)
```

| # | Agent | File | Does |
|---|-------|------|------|
| 1 | **Screening** | `screening_agent.py` | Scores a market against the 246-market model → ADVANCE / CONSIDER / PASS, five-lens write-up. Also a **discovery mode** that ranks the whole model. |
| 2 | **IC Drafter** | `ic_drafter.py` | Extracts a deal record from a project workbook → `deal.json` → house-standard `.docx` memo + `.pptx` deck (Node). |
| 3 | **Hopper** | `hopper_agent.py` | Builds the pipeline dashboard (vertical × stage matrix) from `data/deal_log.csv`. |
| 4 | **Monitor** | `monitor_agent.py` | Construction progress, IRR compression, change-order creep, with flags + chart. |
| 5 | **Platform** | `platform_agent.py` | Capital allocation across the 11-market workforce-housing platform + the captive Factory Fund (P&L ramp, 10-yr waterfall). |

`pipeline.py` runs all five in one process so the workbook is parsed once and
shared across the drafter and the monitor.

## Quick start

```bash
pip install openpyxl matplotlib        # core agents
(cd .. && npm install)                 # only for the .docx / .pptx generators (agent 2)

# Screen one market
python screening_agent.py "Monroe County"

# Discovery: rank the whole model, filter, export
python screening_agent.py --top 25
python screening_agent.py --state NY --advance
python screening_agent.py --advance --top 50 --export advance_markets.csv

# Platform allocation + Factory Fund
python platform_agent.py
python platform_agent.py --markets-only

# Construction monitor
python monitor_agent.py

# Everything (skip Node render if you don't have it)
python pipeline.py --screen "Monroe County" --no-render
python pipeline.py --only platform
```

## Optional LLM narrative

The agents are **fully deterministic by default.** Set an API key and pass
`--polish` to have an LLM reword the findings into committee-ready prose
(numbers and screen logic stay rule-based; on any error it falls back to the
deterministic text):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python screening_agent.py "Monroe County" --polish
python platform_agent.py --polish
python pipeline.py --only monitor platform --polish
```

## Data

> **Note:** the `data/` workbooks and CSVs are **not** in version control — the
> repo gitignores `*.xlsx` / `*.csv` because they may contain confidential client
> data. Drop the files below into `agents/data/` before running the agents.

`data/` holds the production workbooks the agents read:

| File | Used by |
|------|---------|
| `market_model.xlsx` / `market_ranking.csv` | screening + discovery (CSV is the fast-path cache) |
| `hamburg_cashflow.xlsx` | drafter + monitor |
| `deal_log.csv` | hopper |
| `dev_model_11_markets.xlsx` | platform (11-market dev model) |
| `factory_model_standalone.xlsx` | platform (Factory Fund) |

Rebuild the market CSV cache after updating the model workbook:

```bash
python pipeline.py --rebuild-cache      # or: python build_market_cache.py
```

Outputs (`deal.json`, `.docx`, `.pptx`, `.xlsx`, `.png`, `platform_report.txt`)
land in `out/` — override with `--output-dir DIR`.

## Disclaimer

Analytical output to support decision-making — **not** legal, financial, or
investment advice. Verify all figures independently before acting.
