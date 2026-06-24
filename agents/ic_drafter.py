"""
AGENT 2 \u2014 IC Memo + Deck Drafter
---------------------------------
Reads a project workbook, extracts a structured deal record (deal.json),
and drives the house-standard generators (memo.js \u2192 .docx, deck.js \u2192 .pptx).

deal.json is the contract between extraction (Python) and rendering (the
house templates): point the drafter at a different workbook and you get a
different IC package without touching the templates.

Usage:
    python ic_drafter.py                       # uses data/hamburg_cashflow.xlsx
    python ic_drafter.py /path/to/project.xlsx
Output: deal.json, IC_Memo_<name>.docx, IC_Review_<name>.pptx

Changelog vs. original:
  - render() is now genuinely concurrent (ThreadPoolExecutor, not sequential subprocess.run)
  - out_dir parameter threads through both build_deal_json() and render()
  - deal name / location come from icframework._infer_deal_name() (no Hamburg hardcoding)
"""
import sys, os, json, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import icframework as f

# Directory that contains memo.js + deck.js
ICR = f.HERE if os.path.exists(os.path.join(f.HERE, "deck.js")) else os.path.dirname(f.HERE)


def build_deal_json(path=f.HAMBURG, out_dir=None):
    """Extract deal data from the workbook and write deal.json.

    Returns (disp_dict, json_path).
    """
    d       = f.extract_deal(path)
    nrsf    = d["nrsf"]
    out_dir = out_dir or ICR

    disp = {
        "name":          d["name"],
        "subtitle":      d["subtitle"],
        "asset_type":    d["asset_type"],
        "location":      d["location"],
        "levered_irr":   f"~{d['levered_irr']*100:.1f}%" if d["levered_irr"] else "[TBD]",
        "unlevered_irr": f"~{d['unlevered_irr']*100:.1f}%" if d["unlevered_irr"] else "[TBD]",
        "total_cap":     f.usd(d["total_cap"], m=True),
        "equity":        f.usd(d["equity"], m=True),
        "debt":          f.usd(d["perm_debt"], m=True),
        "debt_rate":     f.pct(d["debt_rate"], 1),
        "gp_pct":        f"{d['gp_pct']*100:.0f}%" if d["gp_pct"] else "[TBD]",
        "lp_pct":        f"{d['lp_pct']*100:.0f}%" if d["lp_pct"] else "[TBD]",
        "noi":           f"${d['noi']/1000:.0f}K" if d["noi"] else "[TBD]",
        "exit_value":    f.usd(d["exit_value"], m=True),
        "exit_cap":      f.pct(d["exit_cap"], 1),
        "dev_budget":    f.usd(d["dev_budget"], m=True),
        "committed":     f.usd(d["committed"], m=True),
        "remaining":     f.usd(d["remaining"], m=True),
        "pct_complete":  f"{d['costs_incurred_pct']*100:.0f}%" if d["costs_incurred_pct"] else "[TBD]",
        "change_orders": f"~${d['change_orders']/1000:.0f}K" if d.get("change_orders") else "[TBD]",
        "acres":         f"{d['site_acres']:.2f}" if d["site_acres"] else "[TBD]",
        "nrsf":          f"{nrsf:,.0f}" if nrsf else "[TBD]",
        "units":         f"{d['units']:.0f}" if d["units"] else "[TBD]",
        "cc_sf":         f"{d['cc_sf']:,.0f}" if d["cc_sf"] else "[TBD]",
        "ncc_sf":        f"{d['ncc_sf']:,.0f}" if d["ncc_sf"] else "[TBD]",
        "cc_rate":       f"${d['cc_rate']:.2f}" if d["cc_rate"] else "[TBD]",
        "ncc_rate":      f"${d['ncc_rate']:.2f}" if d["ncc_rate"] else "[TBD]",
        "irr_stages":    {k: round(v * 100, 1) for k, v in d["irr_stages"].items() if v},
    }
    jpath = os.path.join(out_dir, "deal.json")
    with open(jpath, "w") as fh:
        json.dump(disp, fh, indent=2)
    return disp, jpath


def render(disp, out_dir=None):
    """Invoke memo.js and deck.js concurrently; return {label: (ok, msg)} dict.

    Both Node processes run in parallel via ThreadPoolExecutor(max_workers=2),
    so total render time \u2248 max(memo_time, deck_time) instead of their sum.
    """
    cwd = out_dir or ICR

    def _run(script):
        p    = subprocess.run(["node", script], cwd=cwd, capture_output=True, text=True)
        lines = (p.stdout + p.stderr).strip().splitlines()
        msg  = lines[-1] if lines else ""
        return script.replace(".js", ""), (p.returncode == 0, msg)

    results = {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(_run, s): s for s in ("memo.js", "deck.js")}
        for fut in as_completed(futures):
            label, outcome = fut.result()
            results[label] = outcome
    return results


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else f.HAMBURG
    disp, jpath = build_deal_json(path)
    print(f"Extracted deal record -> {os.path.basename(jpath)}")
    print(f"  {disp['name']}  \u00b7  {disp['location']}")
    print(
        f"  Levered IRR {disp['levered_irr']}  \u00b7  total cap {disp['total_cap']}  "
        f"\u00b7  exit {disp['exit_value']}  \u00b7  {disp['pct_complete']} complete"
    )
    res = render(disp)
    for label, (ok, msg) in res.items():
        print(f"  {label}: {'OK' if ok else 'FAILED'}  {msg}")
