"""
pipeline.py \u2014 IC Agent Toolkit orchestrator
============================================
Runs the whole IC pipeline in ONE process so optimizations are shared:

  * market data       -> CSV cache + memoized load_market
  * project workbook  -> memoized extract_deal, parsed once and reused by
                         both the drafter (stage 2) and the monitor (stage 4)
  * memo.js + deck.js -> rendered concurrently via ThreadPoolExecutor

Running the four agents as four separate processes can\u2019t share any of this;
an orchestrator can.  Each stage is independently skippable.

Usage:
    python pipeline.py
    python pipeline.py --project data/hamburg_cashflow.xlsx
    python pipeline.py --screen "Niagara County" "Monroe County"
    python pipeline.py --screen-log
    python pipeline.py --screen-log --append-log
    python pipeline.py --rebuild-cache
    python pipeline.py --no-render
    python pipeline.py --output-dir /tmp/ic_out
    python pipeline.py --only hopper monitor

Changelog vs. original:
  - --append-log  : writes screen verdicts to deal_log.csv
  - --rebuild-cache : re-extracts market_ranking.csv and exits
  - --output-dir  : sends all file outputs to a custom directory
  - stage_screen  : passes append_log through to screening_agent.append_to_log
  - All stages accept out_dir so --output-dir threads through everywhere
  - pipeline summary now references f.MARKET_CSV (from the merged icframework)
"""
from __future__ import annotations
import argparse, time, os, csv, re

import icframework as f
import screening_agent
import ic_drafter
import hopper_agent
import monitor_agent
import platform_agent

STAGES = ("screen", "draft", "hopper", "monitor", "platform")


def _rule(label):
    print("\n" + "=" * 64)
    print(f"  {label}")
    print("=" * 64)


def _deal_log_markets():
    """Front-of-funnel markets from the deal log (not yet approved/rejected)."""
    try:
        with open(f.DEAL_LOG, newline="") as fh:
            rows = list(csv.DictReader(fh))
    except FileNotFoundError:
        return []
    keep = {"Sourced", "Screening", "Qualified"}
    return [r["market"] for r in rows if r.get("status") in keep]


def _resolve_market(label):
    """Freeform deal-log labels -> (query_used, market_dict | None).

    Tries candidates in priority order:
      1. \u2018X County\u2019 token via regex
      2. Parenthetical substring
      3. Text before the first comma
      4. Raw label
    """
    cands = []
    m = re.search(r"([A-Z][A-Za-z.]+(?:\s+[A-Z][A-Za-z.]+)*\s+County)", label)
    if m:
        cands.append(m.group(1))
    p = re.search(r"\(([^)]+)\)", label)
    if p:
        cands.append(p.group(1))
    cands.append(label.split(",")[0].strip())
    cands.append(label)
    seen = set()
    for c in cands:
        key = c.lower().strip()
        if not key or key in seen:
            continue
        seen.add(key)
        hits = f.lookup_market(c)
        if hits:
            return c, hits[0]
    return label, None


# ---------------------------------------------------------------- stages

def stage_screen(markets, append_log=False):
    _rule(f"STAGE 1 \u00b7 SCREEN  ({len(markets)} market(s))")
    verdicts = []
    for q in markets:
        used, m = _resolve_market(q)
        if m is None:
            print(f"  {q[:34]:34}  not in model")
            verdicts.append((q, None))
            continue
        s    = screening_agent.screen(m)
        head = s["verdict"].split(" \u2014 ")[0]   # ADVANCE / CONSIDER / PASS
        via  = "" if used.lower() == q.lower() else f"  (via \u201c{used}\u201d)"
        print(
            f"  {m['county'][:28]:28}  #{m['rank']:>3}/{m['total_markets']}  "
            f"{s['passed']}/{s['testable']} pass  ->  {head}{via}"
        )
        verdicts.append((m["county"], head))

        if append_log:
            wrote = screening_agent.append_to_log(m, s)
            if wrote:
                print(f"    deal_log: appended {m['county']}")
    return verdicts


def stage_draft(project, do_render, out_dir=None):
    _rule("STAGE 2 \u00b7 DRAFT  (deal.json + memo + deck)")
    effective_dir = out_dir or f.HERE
    disp, jpath   = ic_drafter.build_deal_json(project, out_dir=effective_dir)
    print(f"  extracted -> {os.path.basename(jpath)}")
    print(
        f"  {disp['name']}  \u00b7  levered IRR {disp['levered_irr']}  \u00b7  "
        f"total cap {disp['total_cap']}  \u00b7  {disp['pct_complete']} complete"
    )
    if not do_render:
        print("  render: skipped (--no-render)")
        return disp, {}
    res = ic_drafter.render(disp, out_dir=effective_dir)
    for label, (ok, msg) in res.items():
        print(f"  {label}: {'OK' if ok else 'FAILED'}  {msg}")
    return disp, res


def stage_hopper(out_dir=None):
    _rule("STAGE 3 \u00b7 HOPPER  (pipeline dashboard)")
    out_path = os.path.join(out_dir or f.OUT, "hopper_dashboard.xlsx")
    out, n, active = hopper_agent.build(out=out_path)
    print(f"  {os.path.basename(out)}  \u00b7  {n} deals  \u00b7  {active} in hopper (active)")
    return out


def stage_monitor(project, out_dir=None, polish=False):
    _rule("STAGE 4 \u00b7 MONITOR  (progress / variance / flags)")
    txt    = monitor_agent.report(project, out_dir=out_dir or f.OUT, polish=polish)
    d      = f.extract_deal(project)   # cache hit \u2014 no extra parse
    flags  = [line for line in txt.splitlines() if line.strip().startswith("\u26a0")]
    print(
        f"  {d['name']}  \u00b7  latest snapshot {d['latest_snapshot']}  \u00b7  "
        f"{d['costs_incurred_pct']*100:.0f}% costs incurred"
    )
    for fl in flags:
        print(f" {fl.strip()}")
    return flags


def stage_platform(out_dir=None, do_chart=True, polish=False):
    _rule("STAGE 5 · PLATFORM  (11-market allocation + Factory Fund)")
    dev = platform_agent.analyze_dev()
    p   = dev["platform"]
    top = dev["markets"][0]
    print(
        f"  {p.get('n_markets')} markets  ·  blended LP IRR {f.pct(p.get('avg_lp_irr'))}  ·  "
        f"top {top['code']} {f.pct(top['lp_irr'])}  ·  Phase 1 {f.pct(p.get('phase1_avg_lp_irr'))}"
    )
    fac = platform_agent.analyze_factory()
    wf  = fac["waterfall"]
    print(
        f"  Factory Fund  ·  {f.pct(wf.get('fund_irr_10yr'))} 10-yr IRR  ·  "
        f"LP {wf.get('lp_moic'):.1f}× / GP {wf.get('gp_moic'):.1f}× MOIC"
    )
    # Write the full report + chart to the output directory
    txt = platform_agent.report(out_dir=out_dir, do_chart=do_chart, polish=polish)
    rpt = os.path.join(out_dir or f.OUT, "platform_report.txt")
    with open(rpt, "w") as fh:
        fh.write(txt)
    print(f"  report -> {os.path.basename(rpt)}")
    for fl in dev["flags"] + fac["flags"]:
        print(f"  ⚠  {fl}")
    return dev, fac


def run(project, screens, do_render, only, append_log=False, out_dir=None, polish=False):
    t0     = time.time()
    stages = only or STAGES

    if "screen" in stages and screens:
        stage_screen(screens, append_log=append_log)
    if "draft" in stages:
        stage_draft(project, do_render, out_dir=out_dir)
    if "hopper" in stages:
        stage_hopper(out_dir=out_dir)
    if "monitor" in stages:
        stage_monitor(project, out_dir=out_dir, polish=polish)
    if "platform" in stages:
        stage_platform(out_dir=out_dir, do_chart=do_render, polish=polish)

    _rule("PIPELINE SUMMARY")
    dt = time.time() - t0
    print(f"  wall time: {dt:.2f}s")
    ed = f.extract_deal.cache_info()
    lm = f.load_market.cache_info()
    print(
        f"  extract_deal cache : {ed.hits} hit(s), {ed.misses} miss(es)  "
        f"-> project workbook parsed {ed.misses} time(s)"
    )
    print(
        f"  load_market  cache : {lm.hits} hit(s), {lm.misses} miss(es)  "
        f"-> market data parsed {lm.misses} time(s)"
    )
    src = "CSV cache" if os.path.exists(f.MARKET_CSV) else "xlsx (run --rebuild-cache to speed up)"
    print(f"  market source      : {src}")
    if out_dir:
        print(f"  output directory   : {out_dir}")
    print("=" * 64)


def main():
    ap = argparse.ArgumentParser(description="IC Agent Toolkit pipeline orchestrator")
    ap.add_argument("--project",       default=f.HAMBURG,
                    help="project workbook (default: Hamburg)")
    ap.add_argument("--screen",        nargs="*", default=[], metavar="MARKET",
                    help="markets to screen in stage 1")
    ap.add_argument("--screen-log",    action="store_true",
                    help="screen every resolvable front-of-funnel market in the deal log")
    ap.add_argument("--append-log",    action="store_true",
                    help="write screen verdicts to deal_log.csv (skips existing markets)")
    ap.add_argument("--rebuild-cache", action="store_true",
                    help="re-extract market_ranking.csv from market_model.xlsx and exit")
    ap.add_argument("--no-render",     action="store_true",
                    help="skip Node memo/deck generation")
    ap.add_argument("--output-dir",    default=None, metavar="DIR",
                    help="write all file outputs to this directory (default: agents/out/)")
    ap.add_argument("--only",          nargs="+", choices=STAGES, metavar="STAGE",
                    help=f"run only these stages ({', '.join(STAGES)})")
    ap.add_argument("--polish",        action="store_true",
                    help="add LLM narrative to supported stages (needs ANTHROPIC_API_KEY)")
    a = ap.parse_args()

    # --rebuild-cache: one-shot utility, then exit
    if a.rebuild_cache:
        print(f"Reading {os.path.basename(f.MARKET_MODEL)} ...")
        out, n = f.export_market_csv()
        print(f"Cache rebuilt: {os.path.basename(out)}  ({n} markets)")
        print("Next pipeline run will use the CSV fast-path.")
        return

    if a.output_dir:
        os.makedirs(a.output_dir, exist_ok=True)

    screens = list(a.screen)
    if a.screen_log:
        screens += _deal_log_markets()

    run(
        project    = a.project,
        screens    = screens,
        do_render  = not a.no_render,
        only       = tuple(a.only) if a.only else None,
        append_log = a.append_log,
        out_dir    = a.output_dir,
        polish     = a.polish,
    )


if __name__ == "__main__":
    main()
