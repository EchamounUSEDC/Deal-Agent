# IC Analyst — project notes for Claude

## IC Analyst (Go/No-Go underwriting agent)

Drop deal spreadsheets into `deals/inbox/` and ask to **"analyze the inbox"** or
**"run IC on the new deal."** The `ic-analyst` subagent (`.claude/agents/ic-analyst.md`)
runs the deterministic engine, writes committee-ready reports, and briefs the verdict.

```bash
python3 scripts/ic_engine.py --inbox        # process every file in deals/inbox/
python3 scripts/ic_engine.py deal.xlsx      # score one file
python3 scripts/ic_engine.py --selftest     # build & score a GO deal and a veto deal
```

- Reports land in `deals/reports/` as `{DealName}_IC-GoNoGo_{YYYY-MM-DD}.xlsx`; processed
  inputs move to `deals/processed/`.
- Layouts vary — the engine maps metric **synonyms** (e.g. "Purchase Price"≈Total cost,
  "Cap Rate at Sale"≈Exit cap, "Levered/Equity IRR/LIRR" are the same). It **never fabricates**
  a metric; missing critical-gate inputs are automatic fails and are flagged in the report.
- A workbook with one column per deal yields one report per deal plus a **Ranking** sheet.

### The rubric (implemented exactly in `scripts/ic_engine.py`)

9 gates / 100 points. `is_dev` = Deal type is Development.

1. **IRR beats exit cap** (15) — Equity IRR > Exit cap → 15; else/missing → 0. *(critical)*
2. **Yield clears floor** (15) — underwriting yield (YoC for dev, else going-in cap): ≥7.5%→15; ≥6.5%→7.5; else/missing→0. *(critical)*
3. **Op-ex in range** (10) — ≤30%→10; ≤35%→5; ≤45%→2.5; else/missing→0.
4. **Population ≥ 200k** (12) — ≥200k→12; else/missing→0. *(critical)*
5. **Positive pop growth** (10) — ≥5%→10; >0%→5; ≤0%→0; missing→5.
6. **Pipeline contained** (10) — ≤5%→10; ≤10%→5; else→0; missing→5.
7. **Return clears target** (13) — dev ≥15%→13/≥12%→6.5; non-dev ≥10%→13/≥7%→6.5; else/missing→0.
8. **Market upper half** (8) — rank ≤123→8; ≤184→4; else→0; missing→4.
9. **Size near 75k NRSF** (7) — 40k–120k→7; otherwise/missing→3.5.

**Veto (any one ⇒ NO-GO):** IRR ≤ exit cap (or missing) · underwriting yield < 6.5% (or missing) ·
population < 200k (or missing). **Verdict:** ≥70 GO · 50–69.9 CONDITIONAL GO · <50 NO-GO.

**Stress test:** exit cap +50 bps, NOI −5%. "YES — robust" only if stressed YoC ≥ 6.5%,
(dev) stressed dev spread ≥ 0, and Equity IRR > stressed exit cap; else "FRAGILE".

**IRR:** computed from annual equity cash flows (Year 0 = −equity) via `numpy_financial` when
present, else the stated levered/equity IRR; the source is recorded on the report.

### Dependencies
`pip install openpyxl pandas numpy-financial` (already in `requirements.txt`).
