# Deal-Agent — Architecture

A four-agent system that ingests **financial documents** and **land/parcel data**,
interprets both, and **formulates a deal** with the company that owns the asset.

## The four agents

| # | Agent | Role | Tools |
|---|-------|------|-------|
| 1 | **Financial Analyst** | Reads & interprets financial spreadsheets | `read_spreadsheet`, `financial_summary`, `find_line_items` |
| 2 | **Land Surveyor** | Studies & interprets maps and parcel/land areas | `read_parcel_data`, `analyze_map` |
| 3 | **Deal Strategist** | Researches the market and formulates deal terms | `market_research`, plus read tools for self-verification |
| 4 | **Orchestrator** | Coordinates the three specialists end-to-end | `consult_financial_analyst`, `consult_land_surveyor`, `consult_deal_strategist` |

Each agent is an `Agent` (system prompt + tool set) driven by the Anthropic SDK's
**tool runner**, which runs the call → execute-tool → feed-result loop automatically.
All agents use `claude-opus-4-8` with **adaptive thinking** and configurable **effort**.

## Data flow

```
                    ┌──────────────────────────────────────────────┐
   user objective ─▶│              ORCHESTRATOR (Agent 4)          │
   + file paths     │   plans → delegates → synthesizes brief      │
                    └───────┬───────────────┬──────────────┬───────┘
                            │ (parallel)    │              │
                ┌───────────▼──────┐ ┌──────▼───────────┐  │
                │ FINANCIAL (1)    │ │ LAND SURVEYOR (2)│  │
                │ xlsx/xls/csv     │ │ GeoJSON/SHP +    │  │
                │ → NOI, cap rate  │ │ map img/PDF      │  │
                └───────────┬──────┘ │ → acreage,zoning │  │
                            │        └──────┬───────────┘  │
                            └──────┬────────┘              │
                          findings │                       │
                                   ▼                       ▼
                          ┌────────────────────────────────────┐
                          │ DEAL STRATEGIST (3)                 │
                          │ + web market research               │
                          │ → valuation, offer, structure,      │
                          │   contingencies, risks              │
                          └────────────────────────────────────┘
```

The Financial Analyst and Land Surveyor are **independent** — the orchestrator
dispatches both before synthesizing. Their findings feed the Deal Strategist, whose
proposal the orchestrator folds into a single integrated brief.

## Input types supported

| Input | Handled by | How |
|-------|-----------|-----|
| Excel / CSV (`.xlsx`, `.xls`, `.csv`) | Financial Analyst | `pandas` / `openpyxl` |
| Parcel geometry (`.geojson`, `.json`, `.shp`) | Land Surveyor | `shapely` (+ optional `geopandas` for shapefiles) |
| Map images / PDFs (plats, surveys, zoning) | Land Surveyor | Claude **vision** sub-call |
| External market data | Deal Strategist | Claude server-side **web search** |

## Why these tool choices

- **Spreadsheets → dedicated parse tools, not bash.** Typed tools (`read_spreadsheet`,
  `financial_summary`, `find_line_items`) give the model structured, bounded results
  and keep raw cell dumps out of the context window.
- **Maps → a vision sub-call wrapped as a tool.** `analyze_map` base64-encodes the
  image/PDF and asks Claude to read labels, dimensions, and zoning — things that only
  exist on the drawing, not in the geometry file.
- **Market data → server-side web search wrapped as a tool.** `market_research` returns
  a cited summary so the specialist loop stays simple and reliable.
- **Specialists exposed to the orchestrator as tools.** Delegation is just a tool call,
  so the orchestrator plans and synthesizes without touching raw data itself.

## Area computation note

Parcel coordinates in lon/lat (EPSG:4326) can't be measured in degrees. `read_parcel_data`
detects lon/lat and projects to meters with a latitude-corrected equirectangular
transform about the centroid — accurate to a few percent for parcel-sized polygons. For
survey-grade output, supply already-projected coordinates (a CRS measured in meters).

## Two interfaces, same four roles

1. **Python app** (`deal_agent/`) — a runnable Claude Agent SDK application. Entry point:
   `python -m deal_agent.cli`.
2. **Claude Code subagents** (`.claude/agents/*.md`) — the same four roles as Claude Code
   subagents you can invoke conversationally inside a Claude Code session.

## Extending

- **New document type** → add an `@beta_tool` in `deal_agent/tools/` and attach it to the
  relevant agent's `tools` list.
- **New data source (e.g. county assessor API)** → add a tool calling that API; give it
  to the Deal Strategist (or a new specialist).
- **Tune cost/latency** → set `DEAL_AGENT_EFFORT` (`low`…`max`) and `DEAL_AGENT_MODEL`.

## Disclaimer

Deal-Agent produces **analytical** output to support decision-making. It is not legal,
financial, or investment advice, and its market figures and valuations should be
independently verified before acting.
