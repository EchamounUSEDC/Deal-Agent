# Import launchers — drop a spreadsheet in, get a Go/No-Go

No command line, no Excel macros. Two ways to use either launcher:

- **Double-click** it → a file picker opens → choose one or more pro forma files.
- **Drag a spreadsheet onto it** → that file is imported directly.

It reads each pro forma, auto-detects the market (fuzzy-matched to the 246-market
ranking), scores it GO / CONDITIONAL / NO-GO against Springfield & Hamburg, adds it to
`IC_GoNoGo_Dashboard.xlsx`, and opens the dashboard.

| Your computer | Use |
|---------------|-----|
| macOS / Linux | `Import Deal.command` |
| Windows | `Import Deal.bat` |

**Requirements:** Python 3 with this repo installed (`pip install -r requirements.txt`) and
your `ic_data/benchmarks.json` + `ic_data/market_ranking.csv` in place.

If a pro forma doesn't name its market, the deal still imports — just pick the county from
the dropdown on its slot (Deals tab) to complete the market gates.

macOS note: the first time, right-click `Import Deal.command` → Open (to clear the
"unidentified developer" prompt). You may also need: `chmod +x "Import Deal.command"`.
