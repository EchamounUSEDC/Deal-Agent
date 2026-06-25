"""Render an Investment-Committee scorecard (markdown) for a candidate deal."""

from __future__ import annotations

from .schema import Deal, evaluate

_PCT = {"going_in_cap", "exit_cap", "yield_on_cost", "dev_spread", "ltv", "opex_ratio",
        "unlevered_irr", "levered_irr", "market_pop_growth_5yr", "market_pipeline_pct"}
_MONEY = {"total_cost", "equity", "debt", "noi"}

_VERDICT_ICON = {"GO": "🟢", "CONDITIONAL GO": "🟡", "NO-GO": "🔴"}

_ROWS = [
    ("Deal type", "deal_type"),
    ("Total cost", "total_cost"),
    ("Equity", "equity"),
    ("Debt", "debt"),
    ("LTV", "ltv"),
    ("Going-in cap", "going_in_cap"),
    ("Exit cap", "exit_cap"),
    ("NOI", "noi"),
    ("Op-ex ratio", "opex_ratio"),
    ("Yield on cost", "yield_on_cost"),
    ("Dev. spread", "dev_spread"),
    ("Unlevered IRR", "unlevered_irr"),
    ("Levered IRR", "levered_irr"),
    ("NRSF", "nrsf"),
    ("Market rank", "market_rank"),
]


def _fmt(field, v):
    if v is None:
        return "—"
    if field in _PCT and isinstance(v, (int, float)):
        return f"{v:.1%}"
    if field in _MONEY and isinstance(v, (int, float)):
        return f"${v:,.0f}"
    if field == "nrsf" and isinstance(v, (int, float)):
        return f"{v:,.0f}"
    return str(v)


def scorecard(candidate: Deal, benchmarks: list[Deal]) -> str:
    res = evaluate(candidate)
    icon = _VERDICT_ICON.get(res["verdict"], "")
    out = [
        f"# IC Go/No-Go — {candidate.name}",
        "",
        f"## {icon} **{res['verdict']}**  ·  score {res['score']}/100  ·  {candidate.deal_type}",
        "",
        "### Side-by-side vs proven winners",
        "",
        "| Metric | " + candidate.name + " | " + " | ".join(b.name for b in benchmarks) + " |",
        "|---|" + "---|" * (1 + len(benchmarks)),
    ]
    for label, field in _ROWS:
        cells = [_fmt(field, getattr(candidate, field))]
        cells += [_fmt(field, getattr(b, field)) for b in benchmarks]
        out.append(f"| {label} | " + " | ".join(cells) + " |")

    out += ["", "### Gate scorecard", "", "| Gate | Result | Points |", "|---|---|---|"]
    for g in res["gates"]:
        mark = "✅" if g.passed else ("⚠️" if g.cleared else "❌")
        crit = " (critical)" if g.critical else ""
        out.append(f"| {g.label}{crit} | {mark} {g.detail} | {g.points:g}/{g.weight:g} |")

    out += ["", "### Pros"] + [f"- {p}" for p in res["pros"]]
    out += ["", "### Cons / watch-items"] + [f"- {c}" for c in res["cons"]]
    if res["critical_fail"]:
        out += ["", "> ⛔ **Critical gate failed — committee veto. Verdict is NO-GO regardless of score.**"]
    return "\n".join(out)
