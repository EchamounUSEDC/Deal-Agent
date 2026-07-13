# IC Analyst

A virtual investment-committee analyst. Drop a deal spreadsheet into `deals/inbox/`, and it
scores the deal against a fixed 9-gate Go/No-Go rubric, runs a downside stress test, and
writes a committee-ready report to `deals/reports/`.

## Setup

```bash
pip install -r requirements.txt
```

## Real-time mode — drop a file in, get an instant verdict

```bash
python3 scripts/ic_watch.py     # watches deals/inbox/ and scores drops the instant they land
```
Leave it running (or double-click **`Watch Inbox.command`** on macOS / **`Watch Inbox.bat`** on
Windows). Drop a deal — `.xlsx`, `.xlsm`, `.csv`, or **`.pdf`** — into `deals/inbox/` and the
verdict prints in the terminal in real time, the report is written to `deals/reports/`, and the
input moves to `deals/processed/`.

## On-demand routine — `/ic` (run it whenever you need it)

Inside a Claude Code session opened in this folder, type:

```
/ic                     # process everything in deals/inbox/ and brief each verdict
/ic path/to/deal.pdf    # score one file (xlsx/xlsm/csv/pdf)
```

The `/ic` slash command (`.claude/commands/ic.md`) is a durable, on-demand routine — no
scheduling, no setup. It runs the engine, writes the report to `deals/reports/`, moves the
input to `deals/processed/`, and briefs the committee (verdict, score, driving gates, stress
result) right in the chat. Use it any time you want an instant Go/No-Go read.

## One-shot / batch

```bash
python3 scripts/ic_engine.py --inbox        # process everything in deals/inbox/ once
python3 scripts/ic_engine.py deal.pdf       # score one file (xlsx/xlsm/csv/pdf)
python3 scripts/ic_engine.py --selftest     # build & score a GO deal and a veto deal
```

Or, inside a Claude Code session opened in this folder, say **"run IC on the new deal"** —
the `ic-analyst` subagent (`.claude/agents/ic-analyst.md`) reads the file, scores it, writes
the report, moves the input to `deals/processed/`, and briefs the verdict.

## What you get

Per deal, a formatted workbook with five sheets: **Verdict · Scorecard · Deal Metrics ·
Stress Test · Sensitivity**. A workbook with one column per deal also gets a **Ranking** sheet.

The full rubric, veto logic, stress test, and IRR handling are documented in
[`CLAUDE.md`](CLAUDE.md) and embedded in the subagent. The engine never fabricates a metric —
missing critical-gate inputs are automatic fails and are flagged in the report.

*Analysis to support the committee — not investment advice.*
