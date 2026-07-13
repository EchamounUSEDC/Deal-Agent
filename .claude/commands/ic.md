---
description: Run the IC Go/No-Go routine on the inbox (or a specific deal file) and brief the verdict.
argument-hint: "[optional path to a deal .xlsx/.xlsm/.csv/.pdf — omit to process everything in deals/inbox/]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
model: opus
---

You are running the **IC Analyst** Go/No-Go routine on demand. Follow the rubric and
workflow in `.claude/agents/ic-analyst.md` — the reproducible math lives in
`scripts/ic_engine.py`. Do not re-implement the scoring; run the engine.

## What to do

1. Locate the engine. From the repo root it is `scripts/ic_engine.py`; if you were
   launched inside the `ic_analyst/` folder it is `scripts/ic_engine.py` there. Use
   whichever exists (`ic_analyst/scripts/ic_engine.py` or `scripts/ic_engine.py`).

2. Decide the target from the argument `$ARGUMENTS`:
   - **If `$ARGUMENTS` is empty** → process the whole inbox:
     ```bash
     python3 scripts/ic_engine.py --inbox
     ```
   - **If `$ARGUMENTS` is a file path** → score that one file:
     ```bash
     python3 scripts/ic_engine.py "$ARGUMENTS"
     ```
   The engine extracts metrics (mapping synonyms — never fabricating), scores the 9-gate
   rubric, runs the downside stress test, writes a formatted report to `deals/reports/`,
   and moves processed inputs to `deals/processed/`.

3. If the inbox is empty and no argument was given, say so plainly and stop — do not
   invent a deal.

4. Open the report(s) the engine just wrote (newest files in `deals/reports/`) if you need
   detail, then **brief the committee in chat**, one short block per deal:
   - **Verdict** (GO / CONDITIONAL GO / NO-GO) and **score / 100**
   - The **1–2 gates** that drove the result (and any critical-fail veto that fired)
   - The **stress-test** outcome (robust vs fragile)
   - The report filename in `deals/reports/`

5. For a multi-deal (master-dashboard) file, also point to the **Ranking** sheet and give
   the ordered list.

Keep the brief tight and committee-ready. Never guess a missing metric — missing is a fail
on critical gates and must be called out. This is analysis to support the decision, not
investment advice.
