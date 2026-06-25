"""Go / No-Go ranking system.

Five agents that categorize and rank self-storage development deals against the
team's two proven reference deals — **Hamburg** and **Lewiston** — and return a
single **GO** / **CONDITIONAL** / **NO-GO** verdict per deal, plus a ranked list.

Two layers:
- A deterministic scoring **engine** (`engine.py`) anchored on the benchmark deals,
  so "attach a file -> auto Go/No-Go" works without any API call.
- Five Claude Agent SDK **agents** (`agents.py`) that add the narrative committee
  review on top of the engine's numbers.

Public API:
    from deal_agent.gonogo import (
        BENCHMARKS, score_deal, extract_deals, rank_deals, write_ranking_workbook,
        build_gonogo_committee,
    )
"""

from .benchmarks import BENCHMARKS, Benchmark, THRESHOLDS
from .engine import Verdict, score_deal
from .library import answer, load_library, resolve
from .metrics import DealMetrics, extract_deals
from .ranker import rank_deals, rank_files, write_ranking_workbook


def __getattr__(name: str):
    # Lazy import of agent builders so the engine stays usable without anthropic.
    if name in {
        "build_gonogo_committee", "build_committee_chair", "build_benchmark_curator",
        "build_underwriter", "build_market_scorer", "build_risk_screener",
    }:
        from . import agents

        return getattr(agents, name)
    raise AttributeError(name)


__all__ = [
    "BENCHMARKS",
    "Benchmark",
    "THRESHOLDS",
    "Verdict",
    "score_deal",
    "DealMetrics",
    "extract_deals",
    "rank_deals",
    "rank_files",
    "write_ranking_workbook",
    "answer",
    "resolve",
    "load_library",
    "build_gonogo_committee",
    "build_committee_chair",
    "build_benchmark_curator",
    "build_underwriter",
    "build_market_scorer",
    "build_risk_screener",
]
