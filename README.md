# Deal-Agent

Four AI agents that **read financial spreadsheets**, **study and interpret maps and
parcel/land areas**, and **formulate a deal** with the company that owns the asset.

| Agent | Does |
|-------|------|
| 🧮 **Financial Analyst** | Interprets financial spreadsheets → income, expenses, NOI, cap rate |
| 🗺️ **Land Surveyor** | Reads parcel geometry + map images/PDFs → acreage, zoning, frontage |
| 🤝 **Deal Strategist** | Adds market research → valuation, offer, structure, contingencies, risks |
| 🧭 **Orchestrator** | Coordinates the three and delivers one integrated recommendation |

Built on the **Claude Agent SDK** (`claude-opus-4-8`, adaptive thinking). See
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full design.

## Investment-Committee Go/No-Go

A second four-agent layer scores a **candidate self-storage deal** against two *proven winners*
— **Springfield** (income/core DST) and **Hamburg** (ground-up development) — and the firm's
~246-market ranking, then returns a **GO / CONDITIONAL GO / NO-GO** verdict. It ships with a
self-contained **live Excel dashboard**: pick a deal from a dropdown and the verdict, the
side-by-side vs the winners, and every gate score recalculate instantly (no API key needed).
**Add any deal** by filling a pre-wired "New Deal" slot — pick a county and the market stats
auto-fill via `VLOOKUP`, and the GO/No-Go decides live off the Springfield/Hamburg statics
(or use the one-click `AddDeal` macro / the `cli add` importer).

| Agent | Does |
|-------|------|
| 📊 **deal-benchmarker** | Extracts a candidate's metrics; classifies income/core vs development |
| ✅ **deal-screener** | Runs the hard methodology gates → pass/fail with reasons |
| 🗺️ **market-fit-analyst** | Matches the deal's market to the weighted market ranking |
| 🧭 **ic-verdict** | Synthesizes GO/NO-GO with pros, cons, and the "why it works" story |

```bash
python -m deal_agent.ic.cli evaluate --proforma NewDeal.xlsx --market "Nashville, Tennessee"
python -m deal_agent.ic.cli add      --proforma NewDeal.xlsx --market "Nashville, Tennessee"  # -> dashboard
```

Full design, gates, and the proven-winner profiles: [`docs/IC_GO_NO_GO.md`](docs/IC_GO_NO_GO.md).

## Install

```bash
pip install -r requirements.txt
cp .env.example .env        # then add your ANTHROPIC_API_KEY
```

## Use it

Full pipeline (the orchestrator coordinates all three specialists):

```bash
python -m deal_agent.cli \
  "Should we acquire this site? Formulate a deal." \
  --files data/operating_statement.xlsx data/parcels.geojson data/plat.pdf
```

Run a single specialist:

```bash
# Financials only
python -m deal_agent.cli "Interpret these financials" \
  --agent financial --files data/t12.xlsx

# Land + maps only
python -m deal_agent.cli "Total acreage and zoning?" \
  --agent land --files data/parcels.geojson data/zoning_map.png

# Valuation + deal terms
python -m deal_agent.cli "Value this and propose an offer" \
  --agent strategist --files data/t12.csv data/parcels.geojson
```

`--agent` accepts `orchestrator` (default), `financial`, `land`, `strategist`.

## Use it from Python

```python
from deal_agent import build_orchestrator

deal_team = build_orchestrator()
brief = deal_team.run(
    "Formulate an acquisition offer for this property.\n"
    "Input files: data/t12.xlsx, data/parcels.geojson, data/plat.pdf"
)
print(brief)
```

## Inputs supported

- **Financials:** `.xlsx`, `.xls`, `.csv`
- **Parcels:** `.geojson`, `.json`, `.shp` (shapefile needs `geopandas`)
- **Maps:** `.png`, `.jpg`, `.gif`, `.webp`, `.pdf` (read via vision)
- **Market data:** live web search

## Sample data

```bash
python examples/make_sample_data.py     # writes examples/sample_data/*
python -m deal_agent.cli "Formulate a deal" \
  --files examples/sample_data/operating_statement.xlsx examples/sample_data/parcels.geojson
```

## Inside Claude Code

The same four roles also ship as Claude Code subagents in `.claude/agents/`. In a Claude
Code session you can say *"use the deal-orchestrator to evaluate these files"* and it will
delegate to `financial-analyst`, `land-surveyor`, and `deal-strategist`.

## Configuration

| Env var | Default | Meaning |
|---------|---------|---------|
| `ANTHROPIC_API_KEY` | — | Required |
| `DEAL_AGENT_MODEL` | `claude-opus-4-8` | Model for all agents |
| `DEAL_AGENT_EFFORT` | `high` | `low` … `max` — thinking depth / cost |
| `DEAL_AGENT_MAX_TOKENS` | `16000` | Max output tokens per turn |

## Disclaimer

Analytical output to support decision-making — **not** legal, financial, or investment
advice. Verify all figures independently before acting.
