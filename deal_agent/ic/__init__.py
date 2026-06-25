"""Investment-Committee Go/No-Go engine.

Four roles categorise a candidate self-storage deal against two *proven winners* —
Springfield (stabilised DST / income-core) and Hamburg (ground-up development) — and
against the 246-market selection ranking, then return a GO / CONDITIONAL / NO-GO verdict.

    1. Benchmarker     -> classify the deal (income-core vs development) + extract metrics
    2. Screener        -> run the hard methodology gates (pass/fail with reasons)
    3. Market-fit       -> match the deal's market to the weighted market ranking
    4. IC verdict       -> synthesise GO/NO-GO with pros, cons, and the "why it works" story

The scoring in `schema.py` is intentionally simple and gate-based so the exact same
logic is reproduced by live formulas in the Excel dashboard (`workbook.py`).
"""

from .schema import GATES, Deal, evaluate, verdict_of
from .benchmarks import load_benchmarks
from .market import MarketRanking

__all__ = ["GATES", "Deal", "evaluate", "verdict_of", "load_benchmarks", "MarketRanking"]
