"""
AGENT 4 \u2014 Construction Monitoring Agent
----------------------------------------
Ingests a project cash-flow workbook (Hamburg-style: monthly CF snapshots +
Budget History) and reports progress over time, budget evolution, return
compression, and change-order creep, with rule-based flags.

Usage:
    python monitor_agent.py                      # uses data/hamburg_cashflow.xlsx
    python monitor_agent.py /path/to/project.xlsx

Changelog vs. original:
  - matplotlib imported lazily inside chart() so the module can be safely
    imported by pipeline.py without forcing the Agg backend at import time
  - Output PNG filename derived from deal name (not always 'hamburg_monitor.png')
  - report() accepts out_dir to support --output-dir in pipeline.py
"""
import sys, os
import icframework as f

try:
    import llm
except Exception:  # llm is optional; monitoring is fully deterministic without it
    llm = None


def monitor(path=f.HAMBURG):
    d     = f.extract_deal(path)
    flags = []

    # IRR compression
    st = {k: v for k, v in d["irr_stages"].items() if v}
    if "Initial feas." in st and "Current" in st:
        drop = st["Initial feas."] - st["Current"]
        if drop > 0.005:
            flags.append(
                f"Levered IRR compressed {drop*100:.1f} pts since initial "
                f"feasibility ({f.pct(st['Initial feas.'])} \u2192 {f.pct(st['Current'])})."
            )

    # Change-order creep
    if d.get("change_orders"):
        co         = d["change_orders"]
        pct_budget = co / d["dev_budget"] if d.get("dev_budget") else None
        msg = f"Change orders total {f.usd(co)}"
        if pct_budget:
            msg += f" ({pct_budget*100:.1f}% of dev budget)"
        msg += " \u2014 driven by unsuitable-soils / over-excavation."
        flags.append(msg)

    # Completion-basis discrepancy
    if d.get("costs_incurred_pct"):
        flags.append(
            f"Completion is {d['costs_incurred_pct']*100:.0f}% on a costs-incurred "
            f"basis (workbook).  The IC deck cites ~61% on a committed-minus-remaining "
            f"basis \u2014 confirm which definition the committee should see."
        )

    return d, flags


def chart(d, out_png):
    """Render a two-panel progress + IRR chart.

    matplotlib is imported here (not at module level) so that:
      1. The Agg backend call happens in the correct order (before pyplot).
      2. Importing monitor_agent in pipeline.py has no matplotlib side effects.
    """
    import matplotlib
    matplotlib.use("Agg")   # non-interactive; must precede pyplot import
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    fig.patch.set_facecolor("white")

    # Progress curve
    s      = d["snapshot_series"]
    labels = [x[0] for x in s]
    ratios = [x[2] * 100 for x in s]
    ax1.plot(labels, ratios, marker="o", color="#" + f.GOLD, linewidth=2.4, markersize=7)
    ax1.fill_between(range(len(labels)), ratios, color="#" + f.GOLD, alpha=0.12)
    ax1.set_title("Construction progress (costs incurred)", fontsize=11,
                  color="#" + f.NAVY, weight="bold")
    ax1.set_ylabel("% complete", fontsize=9, color="#" + f.MUTE)
    ax1.set_ylim(0, 100)
    ax1.tick_params(labelsize=8, colors="#" + f.MUTE)
    for sp in ("top", "right"):
        ax1.spines[sp].set_visible(False)
    ax1.grid(axis="y", color="#EAEEF2")

    # IRR evolution
    st   = {k: v * 100 for k, v in d["irr_stages"].items() if v}
    bars = ax2.bar(
        list(st.keys()), list(st.values()),
        color=["#" + f.STEEL] * (len(st) - 1) + ["#" + f.GOLD],
    )
    ax2.set_title("Levered IRR by underwriting stage", fontsize=11,
                  color="#" + f.NAVY, weight="bold")
    ax2.set_ylabel("Levered IRR %", fontsize=9, color="#" + f.MUTE)
    ax2.tick_params(labelsize=8, colors="#" + f.MUTE)
    for sp in ("top", "right"):
        ax2.spines[sp].set_visible(False)
    for b, v in zip(bars, st.values()):
        ax2.text(
            b.get_x() + b.get_width() / 2, v + 0.3, f"{v:.1f}%",
            ha="center", fontsize=8, color="#" + f.NAVY,
        )
    ax2.grid(axis="y", color="#EAEEF2")

    plt.tight_layout()
    plt.savefig(out_png, dpi=130, bbox_inches="tight")
    plt.close()


def _polish_monitor(d, flags, fallback):
    """Optional LLM narrative for the monitor — rewords the flags, no new figures."""
    if llm is None or not llm.available():
        return fallback
    facts = (
        f"Project: {d['name']} ({d['location']}). Latest snapshot {d['latest_snapshot']}. "
        f"Committed {f.usd(d['committed'])}, completed {f.usd(d['completed'])} "
        f"({d['costs_incurred_pct']*100:.0f}% costs incurred), remaining {f.usd(d['remaining'])}, "
        f"change orders {f.usd(d['change_orders'])}. "
        f"Levered IRR by stage: "
        + ", ".join(f"{k} {v*100:.1f}%" for k, v in d["irr_stages"].items() if v) + ". "
        + ("Flags: " + " | ".join(flags) if flags else "No flags.")
    )
    prose = llm.polish(
        system=llm.IC_SYSTEM,
        user=("Write a 1-2 paragraph construction-monitoring update for the IC using "
              "ONLY these figures. Lead with progress and budget, then the flags.\n\n"
              + facts),
        max_tokens=400, fallback="",
    )
    if not prose:
        return fallback
    return fallback + "\n\n  MONITOR NOTE (LLM narrative)\n    " + prose.replace("\n", "\n    ")


def report(path=f.HAMBURG, out_dir=None, polish=False):
    """Run monitor, save chart, return the formatted text report."""
    out_dir  = out_dir or f.OUT
    d, flags = monitor(path)

    # Output PNG named after the deal (not always 'hamburg_monitor.png')
    safe_name = d["name"].replace(" ", "_").lower()
    png       = os.path.join(out_dir, f"{safe_name}_monitor.png")
    chart(d, png)

    L = []
    L.append("=" * 64)
    L.append(f"  CONSTRUCTION MONITOR \u2014 {d['name']}")
    L.append(f"  {d['location']}  \u00b7  latest snapshot: {d['latest_snapshot']}")
    L.append("=" * 64)
    L.append("\n  STATUS")
    L.append(f"    Committed cost       {f.usd(d['committed'])}")
    L.append(
        f"    Completed to date    {f.usd(d['completed'])}  "
        f"({d['costs_incurred_pct']*100:.0f}% costs incurred)"
    )
    L.append(f"    Remaining            {f.usd(d['remaining'])}")
    L.append(f"    Change orders        {f.usd(d['change_orders'])}")
    L.append("\n  PROGRESS OVER TIME (costs incurred)")
    for snap, committed, ratio in d["snapshot_series"]:
        bar = "\u2588" * int(ratio * 30)
        L.append(f"    {snap:9} {ratio*100:5.1f}%  {bar}")
    L.append("\n  RETURN EVOLUTION (levered IRR)")
    for stage, v in d["irr_stages"].items():
        if v:
            L.append(f"    {stage:14} {v*100:5.1f}%")
    L.append("\n  FLAGS")
    for fl in flags:
        L.append(f"    \u26a0  {fl}")
    L.append(f"\n  Chart saved: {os.path.basename(png)}")
    L.append("=" * 64)
    text = "\n".join(L)
    if polish:
        text = _polish_monitor(d, flags, text)
    return text


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="IC Agent Toolkit — construction monitor")
    ap.add_argument("project", nargs="?", default=f.HAMBURG,
                    help="project workbook (default: Hamburg)")
    ap.add_argument("--polish", action="store_true",
                    help="add an LLM narrative (needs ANTHROPIC_API_KEY)")
    a = ap.parse_args()
    print(report(a.project, polish=a.polish))
