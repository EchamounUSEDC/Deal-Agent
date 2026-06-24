"""
AGENT 5 — Platform Agent (capital allocation across the housing platform)
-------------------------------------------------------------------------
The IC toolkit shipped two production workbooks — the 11-market Captive Dev
Model and the Factory (HF) P&L + Fund Waterfall — and loaders for both
(``icframework.load_dev_model`` / ``load_factory_model``), but *nothing*
consumed them.  This agent turns that data into an IC-ready view:

  * a capital-allocation leaderboard of the 11 workforce-housing markets,
    ranked by LP IRR, with the Phase 1 anchor set called out;
  * platform roll-up economics (TPC, LP equity to raise, blended LP IRR);
  * risk flags (markets at / below the 8% pref hurdle, sub-platform laggards);
  * the Factory Fund engine — the captive kit supplier that underwrites GP
    economics — with its P&L ramp and 10-year waterfall;
  * a two-panel chart (LP IRR by market vs. hurdle & platform avg; Factory
    EBITDA ramp).

Usage:
    python platform_agent.py                     # full platform + factory report
    python platform_agent.py --markets-only      # just the 11-market leaderboard
    python platform_agent.py --factory-only       # just the Factory Fund engine
    python platform_agent.py --no-chart
    python platform_agent.py --out /path/to/dir/
    python platform_agent.py --polish             # LLM narrative (needs API key)

Every number traces to a workbook cell via the icframework loaders, so the
output is auditable.  --polish only rewords the deterministic summary.
"""
import os
import icframework as f

try:
    import llm
except Exception:  # llm is optional
    llm = None

PREF_HURDLE = 0.08   # LP preferred return; markets at/below this barely clear pref


# ---------------------------------------------------------------- dev model

def analyze_dev(path=None):
    """Structured read of the 11-market dev platform: ranked markets + flags."""
    dm        = f.load_dev_model(path) if path else f.load_dev_model()
    markets   = list(dm["markets"])            # already sorted by project IRR desc
    platform  = dm["platform"]
    avg_lp    = platform.get("avg_lp_irr")

    ranked = sorted(markets, key=lambda m: (m["lp_irr"] or 0), reverse=True)
    phase1 = [m for m in ranked if m["phase1"]]

    flags = []
    at_hurdle = [m for m in ranked if (m["lp_irr"] or 0) <= PREF_HURDLE + 1e-9]
    if at_hurdle:
        names = ", ".join(f"{m['code']} ({f.pct(m['lp_irr'])})" for m in at_hurdle)
        flags.append(
            f"{len(at_hurdle)} market(s) at/below the {f.pct(PREF_HURDLE,0)} pref hurdle: "
            f"{names} — LP capital barely clears preferred; little promote upside."
        )
    if avg_lp is not None:
        laggards = [m for m in ranked if (m["lp_irr"] or 0) < avg_lp and m not in at_hurdle]
        if laggards:
            flags.append(
                f"{len(laggards)} market(s) below the platform average LP IRR "
                f"({f.pct(avg_lp)}): " + ", ".join(m["code"] for m in laggards) + "."
            )
    if phase1:
        ph1_irrs = [m["lp_irr"] for m in phase1 if m["lp_irr"] is not None]
        ph1_blend = sum(ph1_irrs) / len(ph1_irrs) if ph1_irrs else None
        if ph1_blend is not None and avg_lp is not None and ph1_blend < avg_lp:
            flags.append(
                f"Phase 1 anchor set ({', '.join(m['code'] for m in phase1)}) blends to "
                f"{f.pct(ph1_blend)} LP IRR — below the full-platform average "
                f"({f.pct(avg_lp)}); sequencing trades early proof-of-concept for yield."
            )

    return {
        "markets":  ranked,
        "phase1":   phase1,
        "platform": platform,
        "meta":     dm["meta"],
        "flags":    flags,
    }


def _dev_report_lines(a):
    p, meta = a["platform"], a["meta"]
    L = []
    L.append("=" * 70)
    L.append(f"  HOUSING PLATFORM — CAPITAL ALLOCATION  ·  {meta['title']}")
    L.append(f"  {meta['version']}  ·  {meta['date']}  ·  {p.get('n_markets')} markets")
    L.append("=" * 70)

    L.append("\n  PLATFORM ROLL-UP")
    L.append(f"    Total project cost   {f.usd(p.get('total_project_cost'), m=True)}")
    L.append(f"    LP equity to raise   {f.usd(p.get('lp_equity_total'), m=True)}")
    L.append(f"    Stabilized NOI       {f.usd(p.get('stabilized_noi_total'), m=True)}")
    L.append(f"    Y5 exit value        {f.usd(p.get('exit_value_total'), m=True)}")
    L.append(
        f"    LP IRR (blended)     {f.pct(p.get('avg_lp_irr'))}  "
        f"(min {f.pct(p.get('min_lp_irr'))} · max {f.pct(p.get('max_lp_irr'))})"
    )
    L.append(
        f"    Phase 1              {f.pct(p.get('phase1_avg_lp_irr'))} LP IRR · "
        f"{p.get('phase1_avg_lp_moic'):.2f}× MOIC · "
        f"{f.usd(p.get('phase1_lp_equity'), m=True)} LP equity"
        if p.get("phase1_avg_lp_irr") else "    Phase 1              [n/a]"
    )

    L.append("\n  MARKET LEADERBOARD  (ranked by LP IRR)")
    L.append(f"    {'#':>2}  {'Mkt':3} {'Name':22} {'Tier':4} {'LP IRR':>7} "
             f"{'MOIC':>5} {'TPC':>8}  Phase")
    avg_lp = a["platform"].get("avg_lp_irr")
    for i, m in enumerate(a["markets"], 1):
        ph = "1" if m["phase1"] else ("2" if m.get("phase2") else ("3" if m.get("phase3") else "—"))
        mark = "★" if m in a["phase1"] else (" " if (m["lp_irr"] or 0) >= (avg_lp or 0) else "·")
        name = (m["name"] or m["code"])[:22]
        L.append(
            f"  {mark} {i:>2}  {m['code']:3} {name:22} {str(m['tier'] or ''):4} "
            f"{f.pct(m['lp_irr']):>7} {(m['lp_moic'] or 0):.2f}× "
            f"{f.usd(m['total_project_cost'], m=True):>8}  {ph:>5}"
        )
    L.append("    ★ = Phase 1 anchor   · = below platform-avg LP IRR")

    if a["flags"]:
        L.append("\n  FLAGS")
        for fl in a["flags"]:
            L.append(f"    ⚠  {fl}")
    return L


# ---------------------------------------------------------------- factory model

def analyze_factory(path=None):
    """Structured read of the Factory Fund engine: P&L ramp + waterfall + flags."""
    fm   = f.load_factory_model(path) if path else f.load_factory_model()
    pnl  = fm["pnl"]
    wf   = fm["waterfall"]
    ass  = fm["assumptions"]

    flags = []
    y1m = pnl.get("Y1", {}).get("ebitda_margin")
    y5m = pnl.get("Y5", {}).get("ebitda_margin")
    if y1m is not None and y5m is not None:
        flags.append(
            f"EBITDA margin ramps {f.pct(y1m)} (Y1) → {f.pct(y5m)} (Y5); "
            f"early-year returns depend on hitting the production ramp."
        )
    startup = ass.get("total_startup_cost")
    y5e     = pnl.get("Y5", {}).get("ebitda")
    if startup and y5e:
        flags.append(
            f"{f.usd(startup, m=True)} startup cost vs. {f.usd(y5e, m=True)} Y5 EBITDA "
            f"— roughly {startup / y5e:.1f}× steady-state EBITDA to stand the factory up."
        )
    return {"pnl": pnl, "waterfall": wf, "assumptions": ass,
            "meta": fm["meta"], "flags": flags}


def _factory_report_lines(a):
    wf, ass, meta = a["waterfall"], a["assumptions"], a["meta"]
    L = []
    L.append("\n" + "=" * 70)
    L.append(f"  FACTORY FUND ENGINE — {meta['title']}")
    L.append(f"  {meta['version']}  ·  {meta['date']}  ·  captive kit supplier to the platform")
    L.append("=" * 70)

    L.append("\n  P&L RAMP (Year 1 → 5)")
    L.append(f"    {'Year':5} {'Revenue':>10} {'EBITDA':>10} {'Margin':>8}")
    for yr, d in a["pnl"].items():
        L.append(
            f"    {yr:5} {f.usd(d.get('revenue'), m=True):>10} "
            f"{f.usd(d.get('ebitda'), m=True):>10} {f.pct(d.get('ebitda_margin')):>8}"
        )

    L.append("\n  FUND WATERFALL (10-year)")
    L.append(f"    Fund equity          {f.usd(wf.get('fund_equity'), m=True)}")
    L.append(f"    Fund IRR (10-yr)     {f.pct(wf.get('fund_irr_10yr'))}")
    L.append(
        f"    Total distributable  {f.usd(wf.get('total_distributable'), m=True)}  "
        f"(LP {f.usd(wf.get('lp_total'), m=True)} · GP {f.usd(wf.get('gp_total'), m=True)})"
    )
    lp_moic = wf.get("lp_moic"); gp_moic = wf.get("gp_moic")
    L.append(
        f"    MOIC                 LP {lp_moic:.2f}× · GP {gp_moic:.2f}×"
        if lp_moic and gp_moic else "    MOIC                 [n/a]"
    )
    L.append(
        f"    Structure            {f.pct(ass.get('hurdle'),0)} pref · "
        f"{f.pct(ass.get('promote'),0)} promote · {ass.get('hold_years')}-yr hold · "
        f"{ass.get('exit_multiple')}× exit"
    )

    if a["flags"]:
        L.append("\n  FLAGS")
        for fl in a["flags"]:
            L.append(f"    ⚠  {fl}")
    return L


# ---------------------------------------------------------------- chart

def chart(dev, fac, out_png):
    """Two-panel PNG: LP IRR by market (w/ hurdle & platform avg) + Factory EBITDA ramp."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.4))
    fig.patch.set_facecolor("white")

    # Panel 1 — LP IRR by market
    if dev:
        codes = [m["code"] for m in dev["markets"]]
        irrs  = [(m["lp_irr"] or 0) * 100 for m in dev["markets"]]
        colors = ["#" + (f.GOLD if m["phase1"] else f.STEEL) for m in dev["markets"]]
        ax1.bar(codes, irrs, color=colors)
        avg = dev["platform"].get("avg_lp_irr")
        if avg:
            ax1.axhline(avg * 100, color="#" + f.NAVY, ls="--", lw=1.2,
                        label=f"platform avg {avg*100:.1f}%")
        ax1.axhline(PREF_HURDLE * 100, color="#B23A3A", ls=":", lw=1.2,
                    label=f"{PREF_HURDLE*100:.0f}% pref")
        ax1.set_title("LP IRR by market (gold = Phase 1)", fontsize=11,
                      color="#" + f.NAVY, weight="bold")
        ax1.set_ylabel("LP IRR %", fontsize=9, color="#" + f.MUTE)
        ax1.tick_params(labelsize=8, colors="#" + f.MUTE)
        ax1.legend(fontsize=7, frameon=False)
        for sp in ("top", "right"):
            ax1.spines[sp].set_visible(False)
        ax1.grid(axis="y", color="#EAEEF2")

    # Panel 2 — Factory EBITDA ramp
    if fac:
        yrs = list(fac["pnl"].keys())
        rev = [(fac["pnl"][y].get("revenue") or 0) / 1e6 for y in yrs]
        ebt = [(fac["pnl"][y].get("ebitda") or 0) / 1e6 for y in yrs]
        ax2.bar(yrs, rev, color="#" + f.LIGHT, label="revenue")
        ax2.bar(yrs, ebt, color="#" + f.GOLD, label="EBITDA")
        ax2.set_title("Factory Fund — revenue & EBITDA ramp", fontsize=11,
                      color="#" + f.NAVY, weight="bold")
        ax2.set_ylabel("$M", fontsize=9, color="#" + f.MUTE)
        ax2.tick_params(labelsize=8, colors="#" + f.MUTE)
        ax2.legend(fontsize=7, frameon=False)
        for sp in ("top", "right"):
            ax2.spines[sp].set_visible(False)
        ax2.grid(axis="y", color="#EAEEF2")

    plt.tight_layout()
    plt.savefig(out_png, dpi=130, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------- report

def report(out_dir=None, do_chart=True, markets_only=False,
           factory_only=False, polish=False):
    """Run the platform analysis and return the formatted text report."""
    out_dir = out_dir or f.OUT
    dev = None if factory_only else analyze_dev()
    fac = None if markets_only else analyze_factory()

    L = []
    if dev:
        L += _dev_report_lines(dev)
    if fac:
        L += _factory_report_lines(fac)

    png = None
    if do_chart and (dev or fac):
        png = os.path.join(out_dir, "platform_overview.png")
        chart(dev, fac, png)
        L.append(f"\n  Chart saved: {os.path.basename(png)}")
    L.append("=" * 70)
    text = "\n".join(L)

    if polish:
        text = _polish(dev, fac, text)
    return text


def _polish(dev, fac, fallback):
    """Optional LLM narrative — rewords the deterministic findings only."""
    if llm is None or not llm.available():
        return fallback
    facts = []
    if dev:
        p = dev["platform"]
        facts.append(
            f"Platform: {p.get('n_markets')} markets, blended LP IRR "
            f"{f.pct(p.get('avg_lp_irr'))} (min {f.pct(p.get('min_lp_irr'))}, "
            f"max {f.pct(p.get('max_lp_irr'))}), "
            f"{f.usd(p.get('lp_equity_total'), m=True)} LP equity, Phase 1 anchors "
            f"{', '.join(m['code'] for m in dev['phase1'])}."
        )
        facts += [f"  - {fl}" for fl in dev["flags"]]
    if fac:
        wf = fac["waterfall"]
        facts.append(
            f"Factory Fund: {f.pct(wf.get('fund_irr_10yr'))} 10-yr fund IRR, "
            f"LP {wf.get('lp_moic'):.1f}× / GP {wf.get('gp_moic'):.1f}× MOIC, "
            f"{f.usd(wf.get('total_distributable'), m=True)} distributable."
        )
        facts += [f"  - {fl}" for fl in fac["flags"]]
    prose = llm.polish(
        system=llm.IC_SYSTEM,
        user=(
            "Write a 2–3 paragraph IC briefing on the workforce-housing platform "
            "and its captive Factory Fund, using ONLY these figures:\n\n"
            + "\n".join(facts)
            + "\n\nPresent the capital-allocation case and the risks; do not make the "
            "Go/No-Go call."
        ),
        max_tokens=600,
        fallback="",
    )
    if not prose:
        return fallback
    return (
        fallback
        + "\n\n" + "=" * 70
        + "\n  IC BRIEFING (LLM narrative)\n" + "=" * 70 + "\n\n"
        + prose + "\n" + "=" * 70
    )


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(
        description="IC Agent Toolkit — housing platform & Factory Fund allocation")
    ap.add_argument("--out", default=None, help="output directory (default: agents/out/)")
    ap.add_argument("--markets-only", action="store_true", help="only the 11-market leaderboard")
    ap.add_argument("--factory-only", action="store_true", help="only the Factory Fund engine")
    ap.add_argument("--no-chart", action="store_true", help="skip the PNG chart")
    ap.add_argument("--polish", action="store_true", help="add an LLM narrative (needs API key)")
    a = ap.parse_args()
    print(report(
        out_dir=a.out,
        do_chart=not a.no_chart,
        markets_only=a.markets_only,
        factory_only=a.factory_only,
        polish=a.polish,
    ))
