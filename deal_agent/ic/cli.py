"""CLI for the IC Go/No-Go engine.

    # Score a candidate pro forma against Springfield & Hamburg + the market ranking:
    python -m deal_agent.ic.cli evaluate --proforma NewDeal.xlsx --market "Nashville, Tennessee"

    # Add a candidate to the dashboard and rebuild it:
    python -m deal_agent.ic.cli add --proforma NewDeal.xlsx --market "Nashville, Tennessee"

    # (Re)build the Excel dashboard from the benchmarks + saved candidates:
    python -m deal_agent.ic.cli build --out IC_GoNoGo_Dashboard.xlsx
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from .benchmarks import load_benchmarks
from .extract import extract_from_path
from .market import MarketRanking, DEFAULT_CSV
from .report import scorecard
from .schema import Deal
from .workbook import build_workbook

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_CANDIDATES = os.path.join(_ROOT, "ic_data", "candidates.json")


def _load_candidates() -> list[Deal]:
    if not os.path.exists(_CANDIDATES):
        return []
    with open(_CANDIDATES) as f:
        return [Deal.from_dict(d) for d in json.load(f)]


def _save_candidates(cands: list[Deal]) -> None:
    os.makedirs(os.path.dirname(_CANDIDATES), exist_ok=True)
    with open(_CANDIDATES, "w") as f:
        json.dump([c.to_dict() for c in cands], f, indent=2)


def _market() -> MarketRanking | None:
    return MarketRanking.load() if os.path.exists(DEFAULT_CSV) else None


def _prepare(proforma: str, name: str | None, market_query: str | None) -> tuple[Deal, list[str]]:
    deal, notes = extract_from_path(proforma, name=name)
    if market_query:
        deal.market_label = market_query
    mk = _market()
    if mk and (market_query or deal.market_label):
        if mk.enrich(deal, market_query) is None:
            notes.append(f"no market match for {market_query or deal.market_label!r}")
    return deal, notes


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="deal-agent.ic", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    for name in ("evaluate", "add"):
        sp = sub.add_parser(name)
        sp.add_argument("--proforma", required=True, help="Candidate pro forma .xlsx")
        sp.add_argument("--market", default="", help="County/CBSA to match in the ranking")
        sp.add_argument("--name", default="", help="Display name for the deal")

    bp = sub.add_parser("build")
    bp.add_argument("--out", default="IC_GoNoGo_Dashboard.xlsx")

    args = p.parse_args(argv)
    benchmarks = load_benchmarks()

    if args.cmd == "evaluate":
        deal, notes = _prepare(args.proforma, args.name or None, args.market or None)
        print(scorecard(deal, benchmarks))
        if notes:
            print("\n> Notes: " + "; ".join(notes), file=sys.stderr)
        return 0

    if args.cmd == "add":
        deal, notes = _prepare(args.proforma, args.name or None, args.market or None)
        cands = [c for c in _load_candidates() if c.name != deal.name]
        cands.append(deal)
        _save_candidates(cands)
        out = build_workbook("IC_GoNoGo_Dashboard.xlsx", benchmarks, cands, _market())
        print(f"Added {deal.name!r} and rebuilt {out}")
        if notes:
            print("> Notes: " + "; ".join(notes), file=sys.stderr)
        return 0

    if args.cmd == "build":
        out = build_workbook(args.out, benchmarks, _load_candidates(), _market())
        print(f"Wrote {out}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
