"""Go / No-Go CLI — rank deals and auto-decide attached files.

Deterministic mode (no API key needed) — attach a file, get a ranking + verdicts
and a color-coded workbook:

    python -m deal_agent.gonogo --files dev_model_11_markets.xlsx proforma.xlsx
    python -m deal_agent.gonogo --files new_deal.xlsx --out my_ranking.xlsx

Agent mode — the five-agent committee writes a narrative review (needs an
ANTHROPIC_API_KEY and the Claude Agent SDK):

    python -m deal_agent.gonogo --files new_deal.xlsx --agents
    python -m deal_agent.gonogo --files deal.xlsx --agent underwriter
"""

from __future__ import annotations

import argparse
import sys

from .ranker import rank_files, write_ranking_workbook


def _print_table(verdicts) -> None:
    print(f"\n{'#':>2}  {'DECISION':11}  {'SCORE':>5}  {'CONF':6}  DEAL")
    print("-" * 64)
    for i, v in enumerate(verdicts, 1):
        print(f"{i:>2}  {v.decision:11}  {v.score:5.1f}  {v.confidence:6}  {v.name}")
    print()
    for v in verdicts:
        print(f"• {v.name}: {v.rationale}")


def _run_agents(which: str, files: list[str]) -> int:
    from . import agents

    builders = agents._BUILDERS
    if which not in builders:
        print(f"Unknown agent {which!r}. Choices: {', '.join(builders)}", file=sys.stderr)
        return 2
    agent = builders[which]()
    prompt = (
        "Evaluate the deal(s) in these files and give a GO / CONDITIONAL / NO-GO "
        "call versus the Hamburg and Lewiston benchmarks, ranked best-first.\n\n"
        f"Files: {', '.join(files)}"
    )
    print(f"\n=== Running agent: {agent.name} ===\n", file=sys.stderr)
    print(agent.run(prompt))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="deal-agent-gonogo", description=__doc__)
    p.add_argument("--files", nargs="+", required=True, help="Deal files (.xlsx/.xls/.csv).")
    p.add_argument("--out", default="go_no_go_ranking.xlsx", help="Output ranking workbook path.")
    p.add_argument("--agents", action="store_true", help="Run the full five-agent committee.")
    p.add_argument(
        "--agent",
        choices=["chair", "benchmark", "underwriter", "market", "risk"],
        help="Run a single Go/No-Go agent instead of the deterministic engine.",
    )
    p.add_argument("--no-workbook", action="store_true", help="Skip writing the .xlsx.")
    args = p.parse_args(argv)

    if args.agents or args.agent:
        return _run_agents(args.agent or "chair", args.files)

    verdicts = rank_files(args.files)
    _print_table(verdicts)
    if not args.no_workbook:
        write_ranking_workbook(verdicts, args.out)
        print(f"Ranking workbook written to: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
