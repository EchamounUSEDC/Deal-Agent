"""Deterministic Go / No-Go scoring, anchored on the benchmark deals.

`score_deal(metrics)` returns a `Verdict`: a blended 0-100 score, a label
(GO / CONDITIONAL / NO-GO), the per-metric breakdown, hard knockouts, and a
plain-English rationale. No API call — this is the engine behind
"attach a file -> auto Go/No-Go".

How a metric scores: each gated metric maps to 0-100 via its three thresholds
in `benchmarks.THRESHOLDS` (NO-GO floor -> 0, CONDITIONAL -> 50, GO -> 100,
linearly interpolated and clamped). The blended score is the weighted average
over the metrics actually present. Any metric at/below its NO-GO floor is a
**hard knockout** that caps the verdict at NO-GO regardless of the blend.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .benchmarks import CONDITIONAL_SCORE, GO_SCORE, THRESHOLDS, benchmark_summary
from .metrics import DealMetrics

# Which metrics are "lower is better" — thresholds read in the reverse direction.
_LOWER_BETTER = {"exit_cap", "lease_up_months"}

# Human labels + value formatters for the report.
_LABELS = {
    "yield_on_cost": "Stabilized Yield on Cost",
    "dev_spread_bps": "Development Spread",
    "levered_irr": "Levered / Project IRR",
    "moic": "Equity Multiple (MOIC)",
    "market_score": "Market Quality Score",
    "lease_up_months": "Lease-Up Period",
    "exit_cap": "Exit Cap Rate",
}


def _fmt(metric: str, v: float) -> str:
    if metric in ("yield_on_cost", "levered_irr", "exit_cap"):
        return f"{v:.2%}"
    if metric == "dev_spread_bps":
        return f"{v:.0f} bps"
    if metric == "moic":
        return f"{v:.2f}x"
    if metric == "lease_up_months":
        return f"{v:.0f} mo"
    if metric == "market_score":
        return f"{v:.2f}"
    return f"{v:g}"


@dataclass
class MetricScore:
    metric: str
    value: float
    points: float          # 0-100 for this metric
    band: str              # "GO" | "CONDITIONAL" | "NO-GO"
    knockout: bool
    detail: str


@dataclass
class Verdict:
    name: str
    score: float                       # blended 0-100
    decision: str                      # "GO" | "CONDITIONAL" | "NO-GO"
    confidence: str                    # "High" | "Medium" | "Low"
    breakdown: list[MetricScore] = field(default_factory=list)
    knockouts: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    rationale: str = ""
    metrics: DealMetrics | None = None

    def as_row(self) -> dict:
        m = self.metrics
        return {
            "Deal": self.name,
            "Decision": self.decision,
            "Score": round(self.score, 1),
            "Confidence": self.confidence,
            "Yield on Cost": _opt(m and m.yield_on_cost, "{:.2%}"),
            "Exit Cap": _opt(m and m.exit_cap, "{:.2%}"),
            "Dev Spread (bps)": _opt(m and m.dev_spread_bps, "{:.0f}"),
            "Levered IRR": _opt(m and m.levered_irr, "{:.2%}"),
            "MOIC": _opt(m and m.moic, "{:.2f}x"),
            "Lease-Up (mo)": _opt(m and m.lease_up_months, "{:.0f}"),
            "Market Score": _opt(m and m.market_score, "{:.2f}"),
            "Knockouts": "; ".join(self.knockouts) or "—",
            "Rationale": self.rationale,
        }


def _opt(v, fmt: str) -> str:
    return fmt.format(v) if isinstance(v, (int, float)) else "—"


def _band_points(value: float, thresholds: tuple[float, float, float], lower_better: bool) -> tuple[float, str]:
    """Map a value to 0-100 points + band using (no_go, conditional, go) gates."""
    lo, mid, hi = thresholds  # for higher-better: no_go < cond < go
    if lower_better:
        # thresholds read (go_at_or_below, conditional_below, no_go_above)
        go, cond, nogo = lo, mid, hi
        if value <= go:
            return 100.0, "GO"
        if value >= nogo:
            return 0.0, "NO-GO"
        if value <= cond:
            return _lerp(value, go, cond, 100.0, 50.0), "CONDITIONAL"
        return _lerp(value, cond, nogo, 50.0, 0.0), "CONDITIONAL"
    # higher better
    if value >= hi:
        return 100.0, "GO"
    if value <= lo:
        return 0.0, "NO-GO"
    if value >= mid:
        return _lerp(value, mid, hi, 50.0, 100.0), "CONDITIONAL"
    return _lerp(value, lo, mid, 0.0, 50.0), "CONDITIONAL"


def _lerp(x, x0, x1, y0, y1) -> float:
    if x1 == x0:
        return y1
    return max(0.0, min(100.0, y0 + (y1 - y0) * (x - x0) / (x1 - x0)))


def score_deal(metrics: DealMetrics) -> Verdict:
    """Score one deal against the benchmark band. Pure function, no I/O."""
    t = THRESHOLDS
    gates = {
        "yield_on_cost": (t.yield_on_cost, False),
        "dev_spread_bps": (t.dev_spread_bps, False),
        "levered_irr": (t.levered_irr, False),
        "moic": (t.moic, False),
        "market_score": (t.market_score, False),
        "lease_up_months": (t.lease_up_months, True),
        "exit_cap": (t.exit_cap, True),
    }

    # Derive yield on cost (NOI/cost) and dev spread (YoC - exit cap) if absent.
    if metrics.yield_on_cost is None and metrics.noi and metrics.total_cost:
        metrics.yield_on_cost = metrics.noi / metrics.total_cost
    if metrics.dev_spread_bps is None and metrics.yield_on_cost is not None and metrics.exit_cap is not None:
        metrics.dev_spread_bps = (metrics.yield_on_cost - metrics.exit_cap) * 10000.0

    breakdown: list[MetricScore] = []
    knockouts: list[str] = []
    missing: list[str] = []
    weighted_sum = 0.0
    weight_total = 0.0

    for metric, (thresholds, lower_better) in gates.items():
        value = getattr(metrics, metric, None)
        if value is None:
            missing.append(_LABELS[metric])
            continue
        points, band = _band_points(value, thresholds, lower_better)
        is_ko = band == "NO-GO"
        detail = f"{_LABELS[metric]} = {_fmt(metric, value)} -> {band} ({points:.0f}/100)"
        breakdown.append(MetricScore(metric, value, points, band, is_ko, detail))
        if is_ko:
            knockouts.append(f"{_LABELS[metric]} {_fmt(metric, value)} below floor")
        w = t.weights.get(metric, 0.0)
        weighted_sum += points * w
        weight_total += w

    score = (weighted_sum / weight_total) if weight_total else 0.0

    # Decision: knockouts cap at NO-GO; otherwise bands on the blended score.
    if knockouts:
        decision = "NO-GO"
    elif score >= GO_SCORE:
        decision = "GO"
    elif score >= CONDITIONAL_SCORE:
        decision = "CONDITIONAL"
    else:
        decision = "NO-GO"

    # Confidence reflects how much of the deal we could actually measure.
    measured = len(breakdown)
    if measured >= 5 and not missing:
        confidence = "High"
    elif measured >= 3:
        confidence = "Medium"
    else:
        confidence = "Low"

    verdict = Verdict(
        name=metrics.name,
        score=score,
        decision=decision,
        confidence=confidence,
        breakdown=breakdown,
        knockouts=knockouts,
        missing=missing,
        metrics=metrics,
    )
    verdict.rationale = _rationale(verdict)
    return verdict


def _rationale(v: Verdict) -> str:
    strong = [b for b in v.breakdown if b.band == "GO"]
    weak = [b for b in v.breakdown if b.band == "NO-GO"]
    soft = [b for b in v.breakdown if b.band == "CONDITIONAL"]
    parts = []
    if v.decision == "GO":
        parts.append(f"GO — scores {v.score:.0f}/100 vs the Hamburg/Lewiston band.")
    elif v.decision == "CONDITIONAL":
        parts.append(f"CONDITIONAL — {v.score:.0f}/100; clears the floor but trails the benchmarks.")
    else:
        if v.knockouts:
            parts.append(f"NO-GO — fails a hard gate ({v.knockouts[0]}).")
        else:
            parts.append(f"NO-GO — {v.score:.0f}/100, below the go bar.")
    if strong:
        parts.append("Strengths: " + ", ".join(b.metric.replace("_", " ") for b in strong) + ".")
    if soft:
        parts.append("Watch: " + ", ".join(b.metric.replace("_", " ") for b in soft) + ".")
    if weak:
        parts.append("Below floor: " + ", ".join(b.metric.replace("_", " ") for b in weak) + ".")
    if v.missing:
        parts.append(f"Not in file: {', '.join(v.missing)}.")
    return " ".join(parts)


def reference_note() -> str:
    return "Benchmarks (proven GO deals):\n" + benchmark_summary()
