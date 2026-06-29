"""Canonical deal metrics, the methodology gates, and the Go/No-Go scoring.

The gate logic here is the single source of truth. `workbook.py` re-creates the exact
same thresholds as live Excel formulas, so the dashboard and the Python engine always
agree on the score and the verdict.

Gate weights sum to 100. Three gates are *critical*: failing any one forces NO-GO
regardless of the weighted score (an investment committee veto).
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional

# --- archetypes -------------------------------------------------------------------
INCOME = "Income/Core (DST/Stabilized)"
DEVELOPMENT = "Development"

# Return targets that the two proven winners cleared (Springfield ~11% IRR all-equity;
# Hamburg ~17% unlevered / ~17% levered on a development).
INCOME_IRR_TARGET = 0.10
DEV_IRR_TARGET = 0.15

# Underwriting floors drawn from the Market Selection "Methodology" sheet.
YIELD_FLOOR = 0.065        # critical: stabilized yield / going-in cap must clear this
YIELD_PREFERRED = 0.075    # full marks at/above (the model's "realistic cap rate > 7.5%")
OPEX_MAX = 0.35            # methodology average op-ex ratio
OPEX_PREFERRED = 0.30      # criteria sheet "preferably under 30%"
MIN_POPULATION = 200_000   # critical: county population floor
GROWTH_PREFERRED = 0.05    # 5-yr population growth "preferably above 5%"
PIPELINE_PREFERRED = 0.05  # development pipeline "preferably under 5%"
PIPELINE_MAX = 0.10        # hard filter removes markets above 10%
NRSF_TARGET = 75_000       # ideal project size
NRSF_LO, NRSF_HI = 40_000, 120_000


@dataclass
class Deal:
    """One self-storage deal — a proven benchmark or a candidate pro forma."""

    name: str
    deal_type: str = INCOME
    is_benchmark: bool = False
    market_label: str = ""

    total_cost: Optional[float] = None
    equity: Optional[float] = None
    debt: Optional[float] = None
    ltv: Optional[float] = None
    going_in_cap: Optional[float] = None
    exit_cap: Optional[float] = None
    noi: Optional[float] = None
    opex_ratio: Optional[float] = None
    yield_on_cost: Optional[float] = None
    dev_spread: Optional[float] = None
    unlevered_irr: Optional[float] = None
    levered_irr: Optional[float] = None
    nrsf: Optional[float] = None
    site_acreage: Optional[float] = None
    units: Optional[float] = None
    avg_rate_per_nrsf: Optional[float] = None

    # market context (filled by the market-fit step)
    market_population: Optional[float] = None
    market_pop_growth_5yr: Optional[float] = None
    market_pipeline_pct: Optional[float] = None
    market_rank: Optional[int] = None
    market_score: Optional[float] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Deal":
        keys = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in d.items() if k in keys})

    @property
    def is_development(self) -> bool:
        return self.deal_type == DEVELOPMENT

    @property
    def best_irr(self) -> Optional[float]:
        # The equity return is the levered IRR; fall back to unlevered only when
        # there is no debt. (Leverage can be dilutive, so MAX would overstate.)
        return self.levered_irr if self.levered_irr is not None else self.unlevered_irr

    @property
    def underwriting_yield(self) -> Optional[float]:
        """Going-in cap for income deals; stabilized yield-on-cost for development."""
        return self.yield_on_cost if self.is_development else self.going_in_cap


@dataclass
class GateResult:
    key: str
    label: str
    weight: float
    critical: bool
    points: float
    passed: bool          # full marks
    cleared: bool         # cleared a critical hurdle (not a hard veto)
    detail: str


# --- gate evaluators --------------------------------------------------------------
# Each returns (points, passed_full, cleared_critical, detail). Total weight = 100.

def _g_irr_beats_cap(d: Deal):
    irr, cap = d.best_irr, d.exit_cap
    if irr is None or cap is None:
        return 0.0, False, False, "IRR or exit cap missing"
    ok = irr > cap
    return (15.0 if ok else 0.0), ok, ok, f"IRR {irr:.1%} vs exit cap {cap:.1%}"


def _g_yield_floor(d: Deal):
    y = d.underwriting_yield
    if y is None:
        return 0.0, False, False, "yield/going-in cap missing"
    if y >= YIELD_PREFERRED:
        return 15.0, True, True, f"yield {y:.2%} ≥ {YIELD_PREFERRED:.1%}"
    if y >= YIELD_FLOOR:
        return 7.5, False, True, f"yield {y:.2%} clears floor but < {YIELD_PREFERRED:.1%}"
    return 0.0, False, False, f"yield {y:.2%} below {YIELD_FLOOR:.1%} floor"


def _g_opex(d: Deal):
    r = d.opex_ratio
    if r is None:
        return 0.0, False, True, "op-ex ratio missing"
    if r <= OPEX_PREFERRED:
        return 10.0, True, True, f"op-ex {r:.1%} ≤ {OPEX_PREFERRED:.0%}"
    if r <= OPEX_MAX:
        return 5.0, False, True, f"op-ex {r:.1%} ≤ {OPEX_MAX:.0%} but > {OPEX_PREFERRED:.0%}"
    return 0.0, False, True, f"op-ex {r:.1%} above {OPEX_MAX:.0%}"


def _g_population(d: Deal):
    p = d.market_population
    if p is None:
        return 0.0, False, False, "market population unknown"
    ok = p >= MIN_POPULATION
    return (12.0 if ok else 0.0), ok, ok, f"population {p:,.0f} vs {MIN_POPULATION:,} floor"


def _g_growth(d: Deal):
    g = d.market_pop_growth_5yr
    if g is None:
        return 5.0, False, True, "5-yr growth unknown (neutral)"
    if g >= GROWTH_PREFERRED:
        return 10.0, True, True, f"5-yr growth {g:.1%} ≥ {GROWTH_PREFERRED:.0%}"
    if g > 0:
        return 5.0, False, True, f"5-yr growth {g:.1%} positive but < {GROWTH_PREFERRED:.0%}"
    return 0.0, False, True, f"5-yr growth {g:.1%} not positive"


def _g_pipeline(d: Deal):
    p = d.market_pipeline_pct
    if p is None:
        return 5.0, False, True, "pipeline unknown (neutral)"
    if p <= PIPELINE_PREFERRED:
        return 10.0, True, True, f"pipeline {p:.1%} ≤ {PIPELINE_PREFERRED:.0%}"
    if p <= PIPELINE_MAX:
        return 5.0, False, True, f"pipeline {p:.1%} ≤ {PIPELINE_MAX:.0%} but > {PIPELINE_PREFERRED:.0%}"
    return 0.0, False, True, f"pipeline {p:.1%} above {PIPELINE_MAX:.0%}"


def _g_return_target(d: Deal):
    irr = d.best_irr
    if irr is None:
        return 0.0, False, True, "IRR missing"
    target = DEV_IRR_TARGET if d.is_development else INCOME_IRR_TARGET
    if irr >= target:
        return 13.0, True, True, f"IRR {irr:.1%} ≥ {target:.0%} archetype target"
    if irr >= target - 0.03:
        return 6.5, False, True, f"IRR {irr:.1%} near {target:.0%} target"
    return 0.0, False, True, f"IRR {irr:.1%} below {target:.0%} target"


def _g_market_rank(d: Deal, total_markets: int = 246):
    r = d.market_rank
    if r is None:
        return 4.0, False, True, "market rank unknown (neutral)"
    if r <= total_markets * 0.5:
        return 8.0, True, True, f"market ranked #{r} (top 50%)"
    if r <= total_markets * 0.75:
        return 4.0, False, True, f"market ranked #{r} (top 75%)"
    return 0.0, False, True, f"market ranked #{r} (bottom quartile)"


def _g_size(d: Deal):
    n = d.nrsf
    if n is None:
        return 3.5, False, True, "project size unknown (neutral)"
    if NRSF_LO <= n <= NRSF_HI:
        return 7.0, True, True, f"{n:,.0f} NRSF in {NRSF_LO//1000}-{NRSF_HI//1000}k band"
    if 25_000 <= n <= 150_000:
        return 3.5, False, True, f"{n:,.0f} NRSF outside ideal band"
    return 0.0, False, True, f"{n:,.0f} NRSF far from {NRSF_TARGET//1000}k target"


GATES = [
    ("irr_beats_cap", "IRR beats exit cap", 15, True, _g_irr_beats_cap),
    ("yield_floor", "Yield clears underwriting floor", 15, True, _g_yield_floor),
    ("opex", "Op-ex ratio in range", 10, False, _g_opex),
    ("population", "Market population ≥ 200k", 12, True, _g_population),
    ("growth", "Positive population growth", 10, False, _g_growth),
    ("pipeline", "Supply pipeline contained", 10, False, _g_pipeline),
    ("return_target", "Return clears archetype target", 13, False, _g_return_target),
    ("market_rank", "Market ranks in upper half", 8, False, _g_market_rank),
    ("size", "Project size near 75k NRSF", 7, False, _g_size),
]

GO_THRESHOLD = 70.0
CONDITIONAL_THRESHOLD = 50.0


def evaluate(deal: Deal) -> dict:
    """Run every gate and return score, verdict, and per-gate detail."""
    results: list[GateResult] = []
    for key, label, weight, critical, fn in GATES:
        points, passed, cleared, detail = fn(deal)
        results.append(GateResult(key, label, weight, critical, points, passed, cleared, detail))

    score = sum(r.points for r in results)
    critical_fail = any(r.critical and not r.cleared for r in results)
    verdict = verdict_of(score, critical_fail)

    pros = [r.detail for r in results if r.passed]
    cons = [r.detail for r in results if not r.passed]
    return {
        "deal": deal.name,
        "deal_type": deal.deal_type,
        "score": round(score, 1),
        "verdict": verdict,
        "critical_fail": critical_fail,
        "gates": results,
        "pros": pros,
        "cons": cons,
    }


def verdict_of(score: float, critical_fail: bool) -> str:
    if critical_fail:
        return "NO-GO"
    if score >= GO_THRESHOLD:
        return "GO"
    if score >= CONDITIONAL_THRESHOLD:
        return "CONDITIONAL GO"
    return "NO-GO"
