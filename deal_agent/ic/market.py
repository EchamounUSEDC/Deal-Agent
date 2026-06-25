"""Load and query the weighted self-storage market ranking.

The ranking (``ic_data/market_ranking.csv``, git-ignored) scores ~246 county markets on
~33 metrics and assigns a Total Weighted Score and Rank (1 = best). The market-fit step
matches a candidate deal's market to a row and copies the market context onto the Deal.
"""

from __future__ import annotations

import csv
import os
from typing import Optional

from .schema import Deal

_HERE = os.path.dirname(__file__)
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
DEFAULT_CSV = os.path.join(_ROOT, "ic_data", "market_ranking.csv")

# CSV header -> the fields we use
COL = {
    "state": "State",
    "cbsa": "CBSA",
    "county": "County / City",
    "population": "2024 Population",
    "growth_5yr": "T60 Population Growth Rate",
    "growth_1yr": "T12 Population Growth Rate",
    "pipeline": "Development Pipeline % Existing NRSF",
    "opex": "Average Op Ex Ratio",
    "exit_cap": "Exit Cap %",
    "yield_on_cost": "Stabilized Yield on Cost",
    "dev_spread": "Dev. Spread",
    "irr": "Pro Forma IRR",
    "score": "Total Weighted Score",
    "rank": "Rank (1 = Best)",
}


def _num(v) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


class MarketRanking:
    def __init__(self, rows: list[dict]):
        self.rows = rows

    @classmethod
    def load(cls, path: str | None = None) -> "MarketRanking":
        p = path or DEFAULT_CSV
        with open(p, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        return cls(rows)

    @property
    def total_markets(self) -> int:
        return len(self.rows)

    def lookup(self, query: str) -> Optional[dict]:
        """Find the best market row for a free-text query (county, city, or CBSA)."""
        q = (query or "").strip().lower()
        if not q:
            return None
        # exact county/city, then substring on county, then CBSA, then state
        for matcher in (
            lambda r: r[COL["county"]].strip().lower() == q,
            lambda r: q in r[COL["county"]].strip().lower(),
            lambda r: r[COL["county"]].strip().lower().split(",")[0] in q,
            lambda r: q in r[COL["cbsa"]].strip().lower(),
            lambda r: q in r[COL["state"]].strip().lower(),
        ):
            hits = [r for r in self.rows if matcher(r)]
            if hits:
                return min(hits, key=lambda r: _num(r[COL["rank"]]) or 1e9)
        # fuzzy fallback: closest county or CBSA name (handles typos / partial names)
        import difflib

        names = {r[COL["county"]].strip().lower(): r for r in self.rows}
        names.update({r[COL["cbsa"]].strip().lower(): r for r in self.rows})
        close = difflib.get_close_matches(q, list(names), n=1, cutoff=0.6)
        return names[close[0]] if close else None

    def enrich(self, deal: Deal, query: str | None = None) -> Optional[dict]:
        """Match the deal's market and copy market context onto the Deal in place."""
        row = self.lookup(query or deal.market_label)
        if not row:
            return None
        deal.market_population = _num(row[COL["population"]])
        deal.market_pop_growth_5yr = _num(row[COL["growth_5yr"]])
        deal.market_pipeline_pct = _num(row[COL["pipeline"]])
        deal.market_score = _num(row[COL["score"]])
        rank = _num(row[COL["rank"]])
        deal.market_rank = int(rank) if rank is not None else None
        return row

    def top(self, n: int = 25) -> list[dict]:
        return sorted(self.rows, key=lambda r: _num(r[COL["rank"]]) or 1e9)[:n]
