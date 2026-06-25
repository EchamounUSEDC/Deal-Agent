"""Tools the five Go/No-Go agents call. Each wraps the deterministic engine so
the agents reason over the same numbers a no-API run would produce."""

from __future__ import annotations

import json

from anthropic import beta_tool

from .benchmarks import BENCHMARKS, THRESHOLDS, benchmark_summary
from .engine import score_deal
from .metrics import extract_deals
from .ranker import rank_files, write_ranking_workbook


@beta_tool
def benchmark_reference() -> str:
    """Return the Hamburg and Lewiston reference-deal profiles and the Go/No-Go
    thresholds derived from them. Call this to learn the bar a deal must clear."""
    out = {
        "benchmarks": {
            name: {
                "verdict": b.verdict,
                "yield_on_cost": b.yield_on_cost,
                "exit_cap": b.exit_cap,
                "dev_spread_bps": b.dev_spread_bps,
                "levered_irr": b.levered_irr,
                "moic": b.moic,
                "lease_up_months": b.lease_up_months,
                "grounded_in_uploaded_data": b.grounded,
                "notes": b.notes,
            }
            for name, b in BENCHMARKS.items()
        },
        "thresholds_higher_is_better": {
            "yield_on_cost": THRESHOLDS.yield_on_cost,
            "dev_spread_bps": THRESHOLDS.dev_spread_bps,
            "levered_irr": THRESHOLDS.levered_irr,
            "moic": THRESHOLDS.moic,
            "market_score": THRESHOLDS.market_score,
        },
        "thresholds_lower_is_better": {
            "exit_cap": THRESHOLDS.exit_cap,
            "lease_up_months": THRESHOLDS.lease_up_months,
        },
        "summary": benchmark_summary(),
    }
    return json.dumps(out, indent=2)


@beta_tool
def extract_deal_metrics(path: str) -> str:
    """Extract storage-deal metrics (yield on cost, exit cap, dev spread, IRR,
    MOIC, NOI, cost, lease-up, market score) from any .xlsx/.xls/.csv file.

    Args:
        path: Path to the deal file (proforma, model, or ranking table).
    """
    try:
        deals = extract_deals(path)
    except Exception as exc:  # noqa: BLE001
        return f"Error reading {path!r}: {exc}"
    return json.dumps({"file": path, "deals": [d.as_dict() for d in deals]}, indent=2, default=str)


@beta_tool
def score_go_no_go(path: str) -> str:
    """Score every deal in a file as GO / CONDITIONAL / NO-GO against the
    Hamburg/Lewiston benchmarks, with the per-metric breakdown and rationale.

    Args:
        path: Path to the deal file to evaluate.
    """
    try:
        deals = extract_deals(path)
    except Exception as exc:  # noqa: BLE001
        return f"Error reading {path!r}: {exc}"
    results = []
    for d in deals:
        v = score_deal(d)
        results.append({
            "deal": v.name,
            "decision": v.decision,
            "score": round(v.score, 1),
            "confidence": v.confidence,
            "knockouts": v.knockouts,
            "missing": v.missing,
            "rationale": v.rationale,
            "breakdown": [b.detail for b in v.breakdown],
        })
    return json.dumps({"file": path, "verdicts": results}, indent=2, default=str)


@beta_tool
def rank_and_export(files: str, out_path: str = "go_no_go_ranking.xlsx") -> str:
    """Rank every deal across one or more files and write a color-coded Go/No-Go
    ranking workbook.

    Args:
        files: Comma-separated paths to deal files.
        out_path: Where to write the .xlsx ranking (default go_no_go_ranking.xlsx).
    """
    paths = [p.strip() for p in files.split(",") if p.strip()]
    if not paths:
        return "Error: provide at least one file path."
    try:
        verdicts = rank_files(paths)
        write_ranking_workbook(verdicts, out_path)
    except Exception as exc:  # noqa: BLE001
        return f"Error ranking {paths!r}: {exc}"
    ranked = [{"rank": i + 1, "deal": v.name, "decision": v.decision, "score": round(v.score, 1)}
              for i, v in enumerate(verdicts)]
    return json.dumps({"output_workbook": out_path, "ranking": ranked}, indent=2)
