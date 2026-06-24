"""
AGENT 1 \u2014 Screening Agent (the RFQ gate)
-----------------------------------------
Feed it a market (county / state / CBSA name).  It locates the site in the
246-market weighted-ranking model, scores it against the screening criteria,
and drafts a five-lens ADVANCE / CONSIDER / PASS verdict.

Usage:
    python screening_agent.py "Niagara County"
    python screening_agent.py "Erie County, New York"
    python screening_agent.py "Montgomery County, Maryland"
    python screening_agent.py "Monroe County" --append-log

Every verdict line traces to a metric vs. a threshold.  Thresholds
(ADVANCE_PERCENTILE, CONSIDER_PERCENTILE, ADVANCE_MIN_PASS) are defined in
icframework.py so they\u2019re auditable and adjustable in one place.
"""
import sys, csv, os
import icframework as f

try:
    import llm
except Exception:  # llm is optional; screening is fully deterministic without it
    llm = None


def _criterion(value, threshold, direction):
    if value is None:
        return None
    return (value >= threshold) if direction == "ge" else (value <= threshold)


def screen(market: dict) -> dict:
    """Apply the screening criteria + five-lens logic to one market record."""
    c = f.CRITERIA
    checks = {
        "Population \u2265 200k":        _criterion(market["population"],     *c["min_population"][:2]),
        "Pop growth (T12) \u2265 5%":    _criterion(market["pop_growth_t12"], *c["pop_growth_t12"][:2]),
        "Dev pipeline < 5%":         _criterion(market["dev_pipeline"],   *c["dev_pipeline"][:2]),
        "Op-ex ratio < 30%":         _criterion(market["op_ex_ratio"],    *c["op_ex_ratio"][:2]),
        "Pro forma IRR > 4% floor":  _criterion(market["pro_forma_irr"],  *c["return_floor"][:2]),
    }
    passed   = sum(1 for v in checks.values() if v)
    testable = sum(1 for v in checks.values() if v is not None)
    pctile   = 1 - (market["rank"] - 1) / market["total_markets"]

    # Five-lens verdict (rule-based)
    lenses = {
        "Strategic Fit": (
            f"Self-storage program fit; {market['region']} region.  "
            f"Ranks #{market['rank']} of {market['total_markets']} "
            f"({pctile:.0%} percentile)."
        ),
        "Market Opportunity": _market_lens(market),
        "Management Team":    "Operator track record assessed separately (not in market model).",
        "Financial Profile":  (
            f"Pro forma IRR {f.pct(market['pro_forma_irr'])}, "
            f"yield on cost {f.pct(market['yield_on_cost'])}, "
            f"dev spread {market['dev_spread']:.0f} bps; CC rent {f.usd(market['cc_rate'])}/NRSF."
            if market["dev_spread"] is not None else
            f"Pro forma IRR {f.pct(market['pro_forma_irr'])}."
        ),
        "Risk Profile": _risk_lens(market),
    }

    # Verdict uses named thresholds from icframework \u2014 no magic numbers here
    if pctile >= f.ADVANCE_PERCENTILE and passed >= f.ADVANCE_MIN_PASS:
        verdict = "ADVANCE \u2014 strong fit; qualify for due diligence"
    elif pctile >= f.CONSIDER_PERCENTILE or passed >= f.ADVANCE_MIN_PASS:
        verdict = "CONSIDER \u2014 mixed; advance only with a clear thesis"
    else:
        verdict = "PASS \u2014 below the model\u2019s threshold on multiple criteria"

    return {
        "market":     market,
        "checks":     checks,
        "passed":     passed,
        "testable":   testable,
        "percentile": pctile,
        "lenses":     lenses,
        "verdict":    verdict,
    }


def _market_lens(m):
    bits = [f"supply {m['sf_per_capita']:.1f} SF/capita"]
    if m["sf_per_capita"] is not None:
        bits[0] += " (low = undersupplied)" if m["sf_per_capita"] < 7 else " (elevated)"
    bits.append(f"pipeline {f.pct(m['dev_pipeline'])}")
    bits.append("T12 growth " + f.pct(m["pop_growth_t12"]))
    return "; ".join(bits) + "."


def _risk_lens(m):
    flags = []
    if m["op_ex_ratio"] and m["op_ex_ratio"] > 0.30:
        flags.append(f"op-ex {f.pct(m['op_ex_ratio'])} above 30% target")
    if m["dev_pipeline"] and m["dev_pipeline"] > 0.05:
        flags.append(f"pipeline {f.pct(m['dev_pipeline'])} signals new-supply pressure")
    if m["pop_growth_t12"] is not None and m["pop_growth_t12"] < 0.05:
        flags.append("sub-5% population growth")
    return ("; ".join(flags) + ".") if flags else "No criteria breached."


def _polish_screen(m, s, fallback):
    """Optional LLM narrative for a single screen \u2014 rewords findings, no new figures."""
    if llm is None or not llm.available():
        return fallback
    facts = (
        f"Market: {m['county']}, {m['state']} ({m['region']} region). "
        f"Model rank #{m['rank']}/{m['total_markets']} ({s['percentile']:.0%} pctile). "
        f"Verdict: {s['verdict']}. Criteria passed {s['passed']}/{s['testable']}. "
        f"Pro forma IRR {f.pct(m['pro_forma_irr'])}, yield on cost {f.pct(m['yield_on_cost'])}, "
        f"SF/capita {m['sf_per_capita']}, dev pipeline {f.pct(m['dev_pipeline'])}, "
        f"op-ex {f.pct(m['op_ex_ratio'])}, T12 pop growth {f.pct(m['pop_growth_t12'])}."
    )
    prose = llm.polish(
        system=llm.IC_SYSTEM,
        user=("Write a 1-paragraph RFQ screening note for this market using ONLY "
              "these figures. State the verdict and the two or three metrics that "
              "drive it.\n\n" + facts),
        max_tokens=300, fallback="",
    )
    if not prose:
        return fallback
    return fallback + "\n\n  SCREEN NOTE (LLM narrative)\n    " + prose.replace("\n", "\n    ")


def report(query: str, polish: bool = False) -> str:
    hits = f.lookup_market(query)
    if not hits:
        return f"No market in the model matches \u2018{query}\u2019.  Try a county or state name."
    m = hits[0]
    s = screen(m)
    L = []
    L.append("=" * 64)
    L.append(f"  RFQ SCREEN \u2014 {m['county']}")
    L.append(f"  {m['cbsa']}  \u00b7  {m['state']}  \u00b7  {m['region']} region")
    L.append("=" * 64)
    L.append(f"\n  VERDICT:  {s['verdict']}")
    L.append(
        f"  Model rank: #{m['rank']} of {m['total_markets']}  "
        f"({s['percentile']:.0%} percentile)  \u00b7  score {m['score']:.3f}"
    )
    L.append(f"  Criteria passed: {s['passed']}/{s['testable']}\n")
    L.append("  SCREENING CRITERIA")
    for k, v in s["checks"].items():
        mark = "PASS" if v else ("FAIL" if v is not None else "n/a ")
        L.append(f"    [{mark}]  {k}")
    L.append("\n  KEY METRICS")
    L.append(f"    Population            {m['population']:,.0f}")
    L.append(f"    Pop growth (T12)      {f.pct(m['pop_growth_t12'])}")
    L.append(f"    SF per capita         {m['sf_per_capita']:.1f}")
    L.append(f"    Development pipeline  {f.pct(m['dev_pipeline'])}")
    L.append(f"    Op-ex ratio           {f.pct(m['op_ex_ratio'])}")
    L.append(f"    CC rent $/NRSF        {f.usd(m['cc_rate'])}")
    L.append(f"    Pro forma IRR         {f.pct(m['pro_forma_irr'])}")
    L.append(f"    Yield on cost         {f.pct(m['yield_on_cost'])}")
    L.append("\n  FIVE-LENS SCREEN")
    for lens, txt in s["lenses"].items():
        L.append(f"    {lens}:")
        L.append(f"      {txt}")
    L.append("\n" + "=" * 64)
    text = "\n".join(L)
    if polish:
        text = _polish_screen(m, s, text)
    return text


def append_to_log(market: dict, result: dict, path=f.DEAL_LOG) -> bool:
    """Append a completed screen result to the deal log CSV.

    Writes one row: status='Screening', model score, pro-forma IRR, and
    the one-word verdict.  If a row for this market already exists it is
    left unchanged \u2014 re-screen with the pipeline\u2019s stage_screen for updates.

    Returns True if a row was written, False if the market was already present.
    """
    existing = set()
    if os.path.exists(path):
        with open(path, newline="") as fh:
            for row in csv.DictReader(fh):
                existing.add(row.get("market", "").lower())

    name = market["county"]
    if name.lower() in existing:
        return False

    verdict_word = result["verdict"].split(" \u2014 ")[0]   # ADVANCE / CONSIDER / PASS
    row = {
        "deal":     name,
        "vertical": "Self-Storage",
        "market":   name,
        "status":   "Screening",
        "score":    f"{market['score']:.3f}" if market["score"] else "",
        "irr":      f"{market['pro_forma_irr']:.3f}" if market["pro_forma_irr"] else "",
        "notes": (
            f"{market['county']} #{market['rank']}/{market['total_markets']}; "
            f"verdict {verdict_word}; {result['passed']}/{result['testable']} pass"
        ),
    }
    file_exists = os.path.exists(path)
    with open(path, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["deal", "vertical", "market", "status", "score", "irr", "notes"])
        if not file_exists:
            w.writeheader()
        w.writerow(row)
    return True


# ---------------------------------------------------------------- discovery mode

def rank_markets(top=25, state=None, region=None, verdicts=None):
    """Screen the WHOLE model and return the best opportunities as (market, screen).

    This turns the screening agent from a name-lookup into a sourcing tool:
    rank all 246 markets, optionally filter to a state / region or to specific
    verdicts (e.g. only ADVANCE), and take the top N by model rank.

    Parameters
    ----------
    top      : int   \u2014 keep at most this many markets (by model rank; 0 = all)
    state    : str   \u2014 case-insensitive exact match on the State column
    region   : str   \u2014 case-insensitive substring match on the Economic Region
    verdicts : set   \u2014 keep only these verdict words, e.g. {"ADVANCE", "CONSIDER"}
    """
    rows = []
    for m in f.all_markets():
        if state and not f.state_matches(m.get("state"), state):
            continue
        if region and region.lower() not in str(m.get("region", "")).lower():
            continue
        s = screen(m)
        if verdicts and s["verdict"].split(" \u2014 ")[0] not in verdicts:
            continue
        rows.append((m, s))
    rows.sort(key=lambda ms: ms[0]["rank"])
    return rows[:top] if top else rows


def leaderboard(top=25, state=None, region=None, verdicts=None) -> str:
    """Formatted leaderboard of the best-ranked markets after screening."""
    rows  = rank_markets(top=top, state=state, region=region, verdicts=verdicts)
    scope = []
    if state:    scope.append(f"state={state}")
    if region:   scope.append(f"region~{region}")
    if verdicts: scope.append("/".join(sorted(verdicts)))
    scope_s = ("  \u00b7  " + ", ".join(scope)) if scope else ""

    L = []
    L.append("=" * 72)
    L.append(f"  MARKET LEADERBOARD \u2014 top {len(rows)} by model rank{scope_s}")
    L.append("=" * 72)
    L.append(f"  {'#':>3}  {'County / City':26} {'ST':3} {'Pass':>5} "
             f"{'IRR':>6} {'Score':>6}  Verdict")
    for m, s in rows:
        head = s["verdict"].split(" \u2014 ")[0]
        L.append(
            f"  {m['rank']:>3}  {str(m['county'])[:26]:26} {f.state_abbr(m['state']):3} "
            f"{s['passed']}/{s['testable']:<3} {f.pct(m['pro_forma_irr']):>6} "
            f"{(m['score'] or 0):.3f}  {head}"
        )
    if not rows:
        L.append("  (no markets matched the filters)")
    L.append("=" * 72)
    return "\n".join(L)


def export_screens(rows, path) -> int:
    """Write screen results to a CSV (rank, county, state, metrics, verdict). Returns row count."""
    fields = ["rank", "county", "state", "region", "population", "pop_growth_t12",
              "sf_per_capita", "dev_pipeline", "op_ex_ratio", "pro_forma_irr",
              "yield_on_cost", "score", "passed", "testable", "percentile", "verdict"]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for m, s in rows:
            w.writerow({
                "rank": m["rank"], "county": m["county"], "state": m["state"],
                "region": m["region"], "population": m["population"],
                "pop_growth_t12": m["pop_growth_t12"], "sf_per_capita": m["sf_per_capita"],
                "dev_pipeline": m["dev_pipeline"], "op_ex_ratio": m["op_ex_ratio"],
                "pro_forma_irr": m["pro_forma_irr"], "yield_on_cost": m["yield_on_cost"],
                "score": m["score"], "passed": s["passed"], "testable": s["testable"],
                "percentile": round(s["percentile"], 4),
                "verdict": s["verdict"].split(" \u2014 ")[0],
            })
    return len(rows)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="IC Agent Toolkit \u2014 RFQ screening gate")
    ap.add_argument("market", nargs="*", help="Market name(s) to screen (omit for discovery mode)")
    ap.add_argument(
        "--append-log", action="store_true",
        help="Append screen result to deal_log.csv (skips markets already present)",
    )
    # Discovery / leaderboard mode
    ap.add_argument("--top", type=int, metavar="N",
                    help="Discovery mode: rank the whole model and show the top N markets")
    ap.add_argument("--state", metavar="ST", help="Filter discovery to a state (e.g. NY)")
    ap.add_argument("--region", metavar="R", help="Filter discovery to an economic region substring")
    ap.add_argument("--advance", action="store_true", help="Discovery: only ADVANCE verdicts")
    ap.add_argument("--consider", action="store_true",
                    help="Discovery: only ADVANCE or CONSIDER verdicts")
    ap.add_argument("--export", metavar="CSV", help="Discovery: also write results to this CSV")
    ap.add_argument("--polish", action="store_true",
                    help="Add an LLM narrative to a single-market screen (needs ANTHROPIC_API_KEY)")
    a = ap.parse_args()

    discovery = bool(a.top or a.state or a.region or a.advance or a.consider or a.export)

    if discovery:
        verdicts = None
        if a.advance:
            verdicts = {"ADVANCE"}
        elif a.consider:
            verdicts = {"ADVANCE", "CONSIDER"}
        top = a.top if a.top is not None else 25
        print(leaderboard(top=top, state=a.state, region=a.region, verdicts=verdicts))
        if a.export:
            rows = rank_markets(top=top, state=a.state, region=a.region, verdicts=verdicts)
            n = export_screens(rows, a.export)
            print(f"\n  exported {n} screen result(s) -> {a.export}")
    elif a.market:
        query = " ".join(a.market)
        print(report(query, polish=a.polish))
        if a.append_log:
            hits = f.lookup_market(query)
            if hits:
                m = hits[0]
                s = screen(m)
                wrote = append_to_log(m, s)
                status_msg = "appended" if wrote else "market already present \u2014 skipped"
                print(f"\n  deal_log: {status_msg}")
    else:
        ap.error("give a market name to screen, or use --top/--state/--region for discovery mode")
