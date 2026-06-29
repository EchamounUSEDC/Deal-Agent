"""Co-Gen CUP Internal Comparison Agent.

A self-contained decision agent that scores the three delivery options for the
Central Utility Plant (CUP) against weighted criteria and recommends a path. It is
intentionally dependency-free (pure stdlib) so the exact same file can be embedded
*inside* the PowerPoint deck and run from anywhere:

    python cogen_comparison_agent.py            # pretty table + recommendation
    python cogen_comparison_agent.py --json     # machine-readable scoring matrix

The figures are sourced from the USGPD "Goals and Timeline" memo (6/5/26) and the
Aaron Equipment Caterpillar CG170-16 quote. Scores are 1 (worst) - 5 (best) from the
perspective of USGPD's stated goals: control, timely delivery, reliability, cost
control, capital efficiency, and long-term thermal payback.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field

# --- Options under consideration -------------------------------------------------
OPTIONS = {
    "self_develop": "USGPD develops, owns & operates the CUP (Mammoth Hill)",
    "mini_district": "Central City third-party Utility Mini-District",
    "grid_only": "Xcel grid-only / independent developer",
}

# --- Weighted criteria (weights sum to 100) -------------------------------------
# weight, then score per option (1-5), with a short rationale tied to the memo.
CRITERIA = [
    {
        "name": "Control & Decision-Making",
        "weight": 20,
        "scores": {"self_develop": 5, "mini_district": 2, "grid_only": 1},
        "rationale": "CUP is essential to Casino delivery; being one user in a larger "
        "district transfers timing and key decisions to a separate entity.",
    },
    {
        "name": "Delivery Timeline / Schedule Certainty",
        "weight": 20,
        "scores": {"self_develop": 5, "mini_district": 2, "grid_only": 1},
        "rationale": "Self-develop keeps the Xcel fast-track CD application on USGPD's "
        "schedule; a district must first hire a developer; Xcel grid build = ~5 years.",
    },
    {
        "name": "Reliability & Risk",
        "weight": 20,
        "scores": {"self_develop": 5, "mini_district": 3, "grid_only": 2},
        "rationale": "Mammoth Hill proximity minimizes pipe-bridge length/traps; a "
        "distant district plant or Idaho Springs power lines add outage risk.",
    },
    {
        "name": "Utility Cost Control",
        "weight": 15,
        "scores": {"self_develop": 5, "mini_district": 2, "grid_only": 2},
        "rationale": "USGPD manages cost internally vs. negotiated utility payments to "
        "a district in perpetuity or market-rate power ($0.07/kWh + transmission).",
    },
    {
        "name": "Capital / Time Value of Money",
        "weight": 15,
        "scores": {"self_develop": 2, "mini_district": 4, "grid_only": 5},
        "rationale": "CUP is a $24M-$30M raise carrying interest before full operation; "
        "an outside owner reduces funds USGPD must syndicate up front.",
    },
    {
        "name": "Long-Term Economic Payback (thermal)",
        "weight": 10,
        "scores": {"self_develop": 5, "mini_district": 3, "grid_only": 1},
        "rationale": "Casino is the primary thermal user; CUP turbine stack discharge "
        "gives 'free heating & cooling' the grid-only path cannot provide.",
    },
]


@dataclass
class OptionResult:
    key: str
    label: str
    weighted_score: float
    max_possible: float = 5.0
    per_criterion: dict = field(default_factory=dict)


def run_internal_comparison() -> dict:
    """Score every option and return a structured comparison matrix."""
    total_weight = sum(c["weight"] for c in CRITERIA)
    results: list[OptionResult] = []
    for key, label in OPTIONS.items():
        weighted = sum(c["scores"][key] * c["weight"] for c in CRITERIA) / total_weight
        results.append(
            OptionResult(
                key=key,
                label=label,
                weighted_score=round(weighted, 2),
                per_criterion={c["name"]: c["scores"][key] for c in CRITERIA},
            )
        )
    results.sort(key=lambda r: r.weighted_score, reverse=True)
    winner = results[0]
    return {
        "title": "CUP Delivery — Internal Comparison",
        "criteria": CRITERIA,
        "results": [asdict(r) for r in results],
        "recommendation": (
            f"Recommend: {winner.label} "
            f"(weighted {winner.weighted_score}/5.0). Include the CUP as part of the "
            f"overall Casino project."
        ),
    }


def format_table(data: dict) -> str:
    keys = [r["key"] for r in data["results"]]
    headers = {r["key"]: r["label"].split("(")[0].strip() for r in data["results"]}
    short = {"self_develop": "Self-Develop", "mini_district": "Mini-District", "grid_only": "Grid-Only"}
    col = [short.get(k, k) for k in keys]
    lines = []
    name_w = max(len(c["name"]) for c in data["criteria"]) + 2
    head = "Criterion".ljust(name_w) + "Wt".rjust(4) + "".join(c.rjust(14) for c in col)
    lines.append(head)
    lines.append("-" * len(head))
    for c in data["criteria"]:
        row = c["name"].ljust(name_w) + f'{c["weight"]:>3}%'
        row += "".join(f'{c["scores"][k]:>14}' for k in keys)
        lines.append(row)
    lines.append("-" * len(head))
    tot = "WEIGHTED SCORE (/5)".ljust(name_w) + "    "
    score_by_key = {r["key"]: r["weighted_score"] for r in data["results"]}
    tot += "".join(f"{score_by_key[k]:>14}" for k in keys)
    lines.append(tot)
    lines.append("")
    lines.append(data["recommendation"])
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    data = run_internal_comparison()
    if "--json" in argv:
        print(json.dumps(data, indent=2))
    else:
        print("=" * 72)
        print(" CO-GEN CUP — INTERNAL COMPARISON AGENT")
        print("=" * 72)
        print(format_table(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
