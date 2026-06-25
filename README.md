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

## Go / No-Go ranking (5-agent committee)

A second system, `deal_agent.gonogo`, ranks self-storage deals **GO / CONDITIONAL /
NO-GO** by comparing each one to the team's two proven deals — **Hamburg** and
**Lewiston**. Five agents act as an investment committee:

| Agent | Does |
|-------|------|
| 🎯 **Benchmark Curator** | Owns the Hamburg/Lewiston bar and the GO/NO-GO thresholds |
| 📊 **Underwriter** | Extracts a deal's economics and scores them vs the bar |
| 🌍 **Market Scorer** | Judges market quality (demand, supply, growth) |
| ⚠️ **Risk Screener** | Hunts hard knockouts and red flags |
| 🧭 **Committee Chair** | Synthesizes one GO/CONDITIONAL/NO-GO call + ranked list |

A deterministic engine (anchored on the benchmarks) backs the agents, so **attach a
file → auto Go/No-Go works with no API key**:

```bash
# Rank deals and write the color-coded ranking workbook
python -m deal_agent.gonogo --files dev_model_11_markets.xlsx new_proforma.xlsx \
  --out go_no_go_ranking.xlsx

# Run the five-agent committee for a narrative review (needs ANTHROPIC_API_KEY)
python -m deal_agent.gonogo --files new_proforma.xlsx --agents

# One specialist only
python -m deal_agent.gonogo --files new_proforma.xlsx --agent risk
```

The output workbook has three tabs: **Go-No-Go Ranking** (color-coded, with the
benchmark deals shown as anchor rows), **Score Detail** (per-metric breakdown), and
**Method & Benchmarks**. How a deal is scored — and how to plug in your real Lewiston
numbers — is in [`docs/GO_NO_GO.md`](docs/GO_NO_GO.md).

### Ask a question — live answers

Ask for a verdict in plain English and have it generated live from the current data —
in the terminal or inside Excel:

```bash
python -m deal_agent.gonogo ask "is Hamburg a go or no go?"   # -> Hamburg: GO (100/100). ...
python -m deal_agent.gonogo workbook --out GoNoGo_Live.xlsx   # ready-to-use 'Ask' workbook
```

In Excel (live functions via the `xlwings` add-in — see the workbook's Setup tab):

```
=GONOGO_ASK("is the TX deal a go?")   =GONOGO("Hamburg")   =GONOGO_WHY("NE")
```

Point it at your deals with the `GONOGO_DEAL_FILES` env var or a `./deals` folder;
it re-reads them on every call, so edits to your model change the answer immediately.

```python
from deal_agent.gonogo import rank_files, write_ranking_workbook
verdicts = rank_files(["dev_model_11_markets.xlsx", "new_proforma.xlsx"])
write_ranking_workbook(verdicts, "go_no_go_ranking.xlsx")
for v in verdicts:
    print(v.decision, round(v.score, 1), v.name)
```

The same five roles also ship as Claude Code subagents (`.claude/agents/gonogo-*.md`).

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
