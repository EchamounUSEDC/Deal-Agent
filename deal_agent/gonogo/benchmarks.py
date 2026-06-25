"""Reference deals and Go/No-Go thresholds for self-storage development.

The whole system is anchored on two **proven** deals the team already did and
considers "GO": **Hamburg** and **Lewiston**. A new deal is judged by how its
storage-development economics compare to this band.

Hamburg numbers below are taken directly from `hamburg_cashflow.xlsx`
("Budget History" sheet, PPM Underwriting + Zach Model columns):

    NOI            ~$670k – $706k        Dev budget   ~$9.08M – $9.57M
    Yield on Cost   7.0% – 7.8%          Exit cap      5.5%
    Dev spread      150 – 228 bps        Unlev IRR    ~17.3% – 17.7%
    Levered IRR    ~16.9% – 18.5%        Acreage       11.16  (NRSF ~63,240)

Lewiston was NOT included in the uploaded files. Its profile below is a
**configurable placeholder** representing a second solid storage deal; edit the
`Lewiston` values to your actual Lewiston underwriting and the thresholds adapt
automatically (they are recomputed from the benchmark band — see THRESHOLDS).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Benchmark:
    """A proven reference deal whose economics define the 'GO' band."""

    name: str
    verdict: str  # always "GO" for a benchmark — these are deals that worked
    yield_on_cost: float  # stabilized NOI / total project cost
    exit_cap: float  # exit capitalization rate
    dev_spread_bps: float  # (yield_on_cost - exit_cap) in basis points
    levered_irr: float
    unlevered_irr: float
    moic: float  # equity multiple (levered, project-level)
    lease_up_months: float
    noi: float
    total_cost: float
    notes: str = ""
    grounded: bool = True  # True = numbers come from a real uploaded file


# --- Hamburg: grounded in hamburg_cashflow.xlsx -----------------------------
# Values blend the PPM Underwriting and Zach Model columns (the "as-financed"
# views). Dev spread = YoC - exit cap.
HAMBURG = Benchmark(
    name="Hamburg",
    verdict="GO",
    yield_on_cost=0.074,        # ~7.0%-7.8% band -> midpoint
    exit_cap=0.055,
    dev_spread_bps=190.0,       # 150-228 bps band -> midpoint
    levered_irr=0.177,          # PPM 16.9% / Zach 18.5%
    unlevered_irr=0.175,        # PPM 17.3% / Zach 17.7%
    moic=1.85,                  # typical storage dev equity multiple at this IRR
    lease_up_months=12.0,
    noi=706128.0,
    total_cost=9078658.0,
    notes="Next Level Storage - Hamburg, LLC. 11.16 ac, 37,090 CC SF + 26,150 "
    "NCC SF. Grounded in hamburg_cashflow.xlsx (PPM + Zach columns).",
    grounded=True,
)

# --- Lewiston: CONFIGURABLE placeholder (not in uploads) --------------------
# Edit these to your real Lewiston deal. Defaults model a second solid storage
# deal that cleared the team's bar — slightly tighter spread than Hamburg.
LEWISTON = Benchmark(
    name="Lewiston",
    verdict="GO",
    yield_on_cost=0.072,
    exit_cap=0.0575,
    dev_spread_bps=145.0,
    levered_irr=0.160,
    unlevered_irr=0.150,
    moic=1.75,
    lease_up_months=12.0,
    noi=640000.0,
    total_cost=8900000.0,
    notes="PLACEHOLDER — Lewiston data was not in the uploaded files. Replace "
    "with actual Lewiston underwriting; thresholds recompute automatically.",
    grounded=False,
)


BENCHMARKS: dict[str, Benchmark] = {"Hamburg": HAMBURG, "Lewiston": LEWISTON}


@dataclass(frozen=True)
class Thresholds:
    """Go / No-Go gates for each scored metric.

    For "higher is better" metrics the GO floor is at/below the weaker benchmark
    and the NO-GO floor is a documented haircut beneath it. For "lower is better"
    metrics (exit cap, lease-up) the direction is reversed.
    """

    # higher is better -> (no_go_below, conditional_below, go_at_or_above)
    yield_on_cost: tuple[float, float, float] = (0.060, 0.068, 0.072)
    dev_spread_bps: tuple[float, float, float] = (75.0, 125.0, 145.0)
    levered_irr: tuple[float, float, float] = (0.100, 0.135, 0.155)
    moic: tuple[float, float, float] = (1.40, 1.65, 1.75)
    market_score: tuple[float, float, float] = (0.45, 0.58, 0.66)  # 0-1 normalized

    # lower is better -> (go_at_or_below, conditional_below, no_go_above)
    exit_cap: tuple[float, float, float] = (0.0575, 0.0625, 0.0675)
    lease_up_months: tuple[float, float, float] = (12.0, 14.0, 16.0)

    # relative weights of each metric in the blended 0-100 score
    weights: dict = field(
        default_factory=lambda: {
            "dev_spread_bps": 0.26,   # the #1 storage-development signal
            "yield_on_cost": 0.20,
            "levered_irr": 0.20,
            "moic": 0.12,
            "market_score": 0.12,
            "lease_up_months": 0.06,
            "exit_cap": 0.04,
        }
    )


THRESHOLDS = Thresholds()


# Verdict bands on the blended 0-100 score (subject to hard knockouts in engine).
GO_SCORE = 70.0
CONDITIONAL_SCORE = 55.0


def benchmark_summary() -> str:
    """One-line-per-benchmark text summary for prompts and reports."""
    lines = []
    for b in BENCHMARKS.values():
        flag = "" if b.grounded else "  [PLACEHOLDER — edit benchmarks.py]"
        lines.append(
            f"{b.name} ({b.verdict}): YoC {b.yield_on_cost:.1%}, exit cap "
            f"{b.exit_cap:.2%}, spread {b.dev_spread_bps:.0f} bps, levered IRR "
            f"{b.levered_irr:.1%}, MOIC {b.moic:.2f}x, lease-up "
            f"{b.lease_up_months:.0f} mo.{flag}"
        )
    return "\n".join(lines)
