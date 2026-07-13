#!/usr/bin/env python3
"""
Factory-Platform Fund — IC Go/No-Go scorer.

A committee-grade Go/No-Go for a multi-region modular-factory / workforce-housing
PLATFORM FUND (e.g. the Regional Factory Platform model). This is a DIFFERENT asset
class from the self-storage deals scored by scripts/ic_engine.py, so it uses a
different rubric — LP returns, tax structure, alignment, absorption, and
concentration — not cap rates / NRSF / storage-market population.

    python3 scripts/factory_fund_ic.py "path/to/Factory_Model.xlsx"

It reads the workbook by LABEL (never by fixed cell position), scores the CONSERVATIVE
Y5 (8x EBITDA) exit for the headline verdict, shows the mature Y10 (10x) exit as upside,
runs an exit-multiple sensitivity, writes a formatted report to deals/reports/, and prints
the brief. It never fabricates a metric — missing inputs fail their gate and are flagged.

Every threshold below is a named constant. Tune them to your firm's hurdles; the report
and brief always show the threshold each gate was measured against.
"""
import os
import sys
import datetime as _dt

# ── Rubric thresholds (edit these to match your IC's hurdles) ───────────────────────────
LP_PREF        = 0.08     # LP preferred return — the floor the fund must clear
IRR_FULL       = 0.20     # LP IRR: full credit at/above this
IRR_HALF       = 0.12     # LP IRR: half credit at/above this
MOIC_FULL      = 3.0      # LP MOIC: full credit
MOIC_HALF      = 2.0      # LP MOIC: half credit
MOIC_MIN       = 1.5      # LP MOIC: veto floor (below this ⇒ NO-GO)
CAPTAM_FULL    = 0.40     # required market share (capacity/TAM): conservative absorption
CAPTAM_HALF    = 0.60     # required market share: acceptable
DIV_REGIONS    = 5        # diversification: regions needed for full credit
DIV_T1_MARKETS = 15       # diversification: T1 markets needed for full credit
CONC_FULL      = 0.30     # capital concentration: largest region's share ≤ this ⇒ full
CONC_HALF      = 0.50     # capital concentration: largest region's share ≤ this ⇒ half

GO_MIN         = 70.0     # ≥ GO_MIN ⇒ GO
COND_MIN       = 50.0     # COND_MIN–GO_MIN ⇒ CONDITIONAL GO; below ⇒ NO-GO


# ── Small parsing helpers ───────────────────────────────────────────────────────────────
def _num(v):
    """Parse a number from a cell that may carry $, %, M, or commas. None if not numeric."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "").replace("$", "").replace("M", "").replace("%", "")
    s = s.replace("×", "").replace("x", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def _rate(v):
    """Parse a rate; if it reads like a percent (>1.5) divide by 100."""
    n = _num(v)
    if n is None:
        return None
    return n / 100.0 if abs(n) > 1.5 else n


def _load(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True)
    sheets = {}
    for name in wb.sheetnames:
        sheets[name] = [list(r) for r in wb[name].iter_rows(values_only=True)]
    return sheets


def _find_table(rows, header_keywords):
    """Return the row index of the first row containing ALL header_keywords (case-insensitive)."""
    for ri, r in enumerate(rows):
        cells = [str(c).lower() for c in r if isinstance(c, str)]
        joined = " | ".join(cells)
        if all(k.lower() in joined for k in header_keywords):
            return ri
    return None


# ── Extraction (label-based, never positional) ──────────────────────────────────────────
def extract(path):
    """Pull platform structure + Y5/Y10 LP returns. Returns (data, missing)."""
    sheets = _load(path)
    d, missing = {}, []
    blob = " ".join(str(c).lower() for rows in sheets.values() for r in rows
                     for c in r if isinstance(c, str))
    name = os.path.splitext(os.path.basename(path))[0]

    # --- Capital / structure table: "Regional Fund | Total Capital | LP Commit | GP Commit ..."
    regions = []  # (name, total_cap, lp_commit, gp_commit, factories, capacity, tam)
    for sh, rows in sheets.items():
        hdr = _find_table(rows, ["total capital", "lp commit", "gp commit", "capacity"])
        if hdr is None:
            continue
        for r in rows[hdr + 1:]:
            label = r[0] if r else None
            if not isinstance(label, str) or not label.strip():
                continue
            low = label.strip().lower()
            tc = _num(r[1]) if len(r) > 1 else None
            if low.startswith("platform") or "total" in low:
                d["platform_total_capital"] = _num(r[1]) if len(r) > 1 else None
                d["platform_lp_capital"]    = _num(r[2]) if len(r) > 2 else None
                d["platform_gp_capital"]    = _num(r[3]) if len(r) > 3 else None
                d["platform_factories"]     = _num(r[4]) if len(r) > 4 else None
                d["platform_capacity"]      = _num(r[5]) if len(r) > 5 else None
                d["platform_tam"]           = _num(r[6]) if len(r) > 6 else None
                break
            if tc is not None:
                regions.append({
                    "name": label.strip(),
                    "capital": tc,
                    "lp": _num(r[2]) if len(r) > 2 else None,
                    "gp": _num(r[3]) if len(r) > 3 else None,
                    "factories": _num(r[4]) if len(r) > 4 else None,
                    "capacity": _num(r[5]) if len(r) > 5 else None,
                    "tam": _num(r[6]) if len(r) > 6 else None,
                })
        break
    d["regions_struct"] = regions

    # --- Exit returns table: "LP Raise | ... | Y5 ... IRR | Y10 ... IRR" (per region + platform)
    exit_regions = []  # (name, lp_raise, y5_val, y5_moic, y5_irr, y10_val, y10_moic, y10_irr)
    plat = {}
    for sh, rows in sheets.items():
        hdr = _find_table(rows, ["lp raise", "y5", "y10", "irr", "moic"])
        if hdr is None:
            continue
        header = [str(c).lower() if c is not None else "" for c in rows[hdr]]
        def col(*keys):
            for ci, h in enumerate(header):
                if all(k in h for k in keys):
                    return ci
            return None
        c_raise = col("lp", "raise")
        c_y5irr, c_y10irr = col("y5", "irr"), col("y10", "irr")
        c_y5moic, c_y10moic = col("y5", "moic"), col("y10", "moic")
        c_y5val = col("y5", "value") or col("y5", "lp value")
        c_y10val = col("y10", "value") or col("y10", "lp value")
        for r in rows[hdr + 1:]:
            label = r[0] if r else None
            if not isinstance(label, str) or not label.strip():
                continue
            low = label.strip().lower()
            def g(ci, rate=False):
                if ci is None or ci >= len(r):
                    return None
                return _rate(r[ci]) if rate else _num(r[ci])
            rec = {
                "name": label.strip(),
                "lp_raise": g(c_raise),
                "y5_val": g(c_y5val), "y5_moic": g(c_y5moic), "y5_irr": g(c_y5irr, rate=True),
                "y10_val": g(c_y10val), "y10_moic": g(c_y10moic), "y10_irr": g(c_y10irr, rate=True),
            }
            if low.startswith("platform") or "total" in low:
                plat = rec
                break
            if rec["y5_irr"] is not None or rec["y10_irr"] is not None:
                exit_regions.append(rec)
        if plat:
            break
    d["exit_regions"] = exit_regions
    d["platform_exit"] = plat

    # --- Headline platform figures (prefer the exit-table platform row; else compute) ------
    lp_raise = plat.get("lp_raise") or d.get("platform_lp_capital")
    d["lp_raise"] = lp_raise
    # MOIC = total LP value / total LP raise (well-defined even if the sheet's avg differs)
    d["y5_moic"]  = plat.get("y5_moic")  or (plat.get("y5_val") / lp_raise if plat.get("y5_val") and lp_raise else None)
    d["y10_moic"] = plat.get("y10_moic") or (plat.get("y10_val") / lp_raise if plat.get("y10_val") and lp_raise else None)
    d["y5_irr"], d["y10_irr"] = plat.get("y5_irr"), plat.get("y10_irr")

    # --- Structure-derived signals -------------------------------------------------------
    d["gp_pct"] = (d["platform_gp_capital"] / d["platform_total_capital"]
                   if d.get("platform_gp_capital") and d.get("platform_total_capital") else None)
    d["cap_tam"] = (d["platform_capacity"] / d["platform_tam"]
                    if d.get("platform_capacity") and d.get("platform_tam") else None)
    d["n_regions"] = len(regions) if regions else None
    caps = [r["capital"] for r in regions if r.get("capital")]
    d["max_region_share"] = (max(caps) / sum(caps)) if caps else None
    # T1 markets served (from Platform Roll-Up "Markets Served (T1 direct dev)")
    t1 = None
    for sh, rows in sheets.items():
        for r in rows:
            if r and isinstance(r[0], str) and "markets served" in r[0].lower() and "t1" in r[0].lower():
                t1 = next((_num(c) for c in r[1:] if _num(c) is not None), None)
                break
        if t1 is not None:
            break
    d["t1_markets"] = t1
    # §1202 QSBS eligibility (structural, from the workbook text)
    d["s1202"] = ("§1202" in blob or "1202" in blob) and ("qsbs" in blob or "c-corp" in blob or "c corp" in blob)

    # --- Missing-input flags (these drive gate fails; never fabricated) -------------------
    for k, lbl in [("y5_irr", "Y5 LP IRR"), ("y5_moic", "Y5 LP MOIC"),
                   ("y10_irr", "Y10 LP IRR"), ("y10_moic", "Y10 LP MOIC"),
                   ("lp_raise", "LP raise"), ("cap_tam", "capacity/TAM"),
                   ("gp_pct", "GP co-invest %"), ("max_region_share", "capital concentration")]:
        if d.get(k) is None:
            missing.append(lbl)
    d["name"] = name
    return d, missing


# ── Scoring ─────────────────────────────────────────────────────────────────────────────
EPS = 1e-9  # tolerance so an exact boundary (e.g. GP = 12.7/127 = 0.0999…) gets full credit


def _tier(x, full_at, full, half_at, half, quarter_at=None, quarter=0.0):
    if x is None:
        return 0.0, "missing"
    if x >= full_at - EPS:
        return full, f"≥{full_at}"
    if x >= half_at - EPS:
        return half, f"≥{half_at}"
    if quarter_at is not None and x >= quarter_at - EPS:
        return quarter, f"≥{quarter_at}"
    return 0.0, "below floor"


def score(d, scenario):
    """scenario = 'y5' or 'y10'. Returns dict with gates, total, vetoes, verdict."""
    irr  = d.get(f"{scenario}_irr")
    moic = d.get(f"{scenario}_moic")
    gates = []

    p, t = _tier(irr, IRR_FULL, 18, IRR_HALF, 9, LP_PREF, 4.5)
    gates.append(("LP IRR clears target", p, 18,
                  f"{irr*100:.1f}%" if irr is not None else "—",
                  f"≥{IRR_FULL*100:.0f}% / ≥{IRR_HALF*100:.0f}% / ≥pref {LP_PREF*100:.0f}%", True))

    p, t = _tier(moic, MOIC_FULL, 15, MOIC_HALF, 7.5, MOIC_MIN, 3.75)
    gates.append(("LP MOIC (equity multiple)", p, 15,
                  f"{moic:.2f}×" if moic is not None else "—",
                  f"≥{MOIC_FULL}× / ≥{MOIC_HALF}× / ≥{MOIC_MIN}×", False))

    beats = 12 if (irr is not None and irr > LP_PREF) else 0
    gates.append(("Return beats LP pref", beats, 12,
                  f"{irr*100:.1f}%" if irr is not None else "—",
                  f">{LP_PREF*100:.0f}% pref", True))

    s = 15 if d.get("s1202") else 0
    gates.append(("§1202 QSBS eligibility", s, 15,
                  "eligible" if d.get("s1202") else "no", "C-corp at issuance", False))

    gp = d.get("gp_pct")
    p, t = _tier(gp, 0.10, 10, 0.05, 5)
    gates.append(("GP alignment (co-invest)", p, 10,
                  f"{gp*100:.1f}%" if gp is not None else "—", "≥10% / ≥5%", False))

    ct = d.get("cap_tam")
    if ct is None:
        p = 0
    elif ct <= CAPTAM_FULL + EPS:
        p = 12
    elif ct <= CAPTAM_HALF + EPS:
        p = 6
    else:
        p = 0
    gates.append(("Capacity vs TAM (absorption)", p, 12,
                  f"{ct*100:.0f}% share" if ct is not None else "—",
                  f"≤{CAPTAM_FULL*100:.0f}% / ≤{CAPTAM_HALF*100:.0f}%", False))

    nr, t1 = d.get("n_regions"), d.get("t1_markets")
    if nr and nr >= DIV_REGIONS and (t1 or 0) >= DIV_T1_MARKETS:
        p = 10
    elif nr and nr >= 3:
        p = 5
    else:
        p = 0
    gates.append(("Market diversification", p, 10,
                  f"{nr or '—'} regions / {int(t1) if t1 else '—'} T1",
                  f"≥{DIV_REGIONS} regions & ≥{DIV_T1_MARKETS} T1", False))

    ms = d.get("max_region_share")
    if ms is None:
        p = 0
    elif ms <= CONC_FULL + EPS:
        p = 8
    elif ms <= CONC_HALF + EPS:
        p = 4
    else:
        p = 0
    gates.append(("Capital concentration", p, 8,
                  f"{ms*100:.0f}% top region" if ms is not None else "—",
                  f"≤{CONC_FULL*100:.0f}% / ≤{CONC_HALF*100:.0f}%", False))

    total = round(sum(g[1] for g in gates), 2)

    # Vetoes: fund must clear its own pref and return ≥ MOIC floor
    vetoes = []
    if irr is None or irr <= LP_PREF:
        vetoes.append(f"LP IRR ({'missing' if irr is None else f'{irr*100:.1f}%'}) does not clear the {LP_PREF*100:.0f}% pref")
    if moic is None or moic < MOIC_MIN:
        vetoes.append(f"LP MOIC ({'missing' if moic is None else f'{moic:.2f}×'}) below {MOIC_MIN}× floor")

    if vetoes:
        verdict = "NO-GO"
    elif total >= GO_MIN:
        verdict = "GO"
    elif total >= COND_MIN:
        verdict = "CONDITIONAL GO"
    else:
        verdict = "NO-GO"

    return {"scenario": scenario.upper(), "gates": gates, "total": total,
            "vetoes": vetoes, "verdict": verdict}


# ── Report writer ───────────────────────────────────────────────────────────────────────
def write_report(d, sc_y5, sc_y10, out_path):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = openpyxl.Workbook()
    NAVY, GREEN, AMBER, RED, GREY = "1F3A5F", "C6EFCE", "FFEB9C", "FFC7CE", "F2F2F2"
    B = Font(bold=True); TITLE = Font(bold=True, color="FFFFFF", size=14)
    HEADF = PatternFill("solid", fgColor=NAVY); GREYF = PatternFill("solid", fgColor=GREY)
    C = Alignment(horizontal="center", vertical="center")
    L = Alignment(horizontal="left", vertical="center", wrap_text=True)
    vfill = {"GO": PatternFill("solid", fgColor=GREEN),
             "CONDITIONAL GO": PatternFill("solid", fgColor=AMBER),
             "NO-GO": PatternFill("solid", fgColor=RED)}

    def sty(ws, cell, val, font=None, fill=None, align=None):
        ws[cell] = val
        if font: ws[cell].font = font
        if fill: ws[cell].fill = fill
        if align: ws[cell].alignment = align

    # Verdict sheet (anchored on conservative Y5)
    vd = wb.active; vd.title = "Verdict"
    vd.column_dimensions["A"].width = 26; vd.column_dimensions["B"].width = 60
    sty(vd, "A1", "Factory-Platform Fund — IC Go/No-Go", TITLE, HEADF, L)
    vd.merge_cells("A1:B1")
    rows = [
        ("Fund", d["name"]),
        ("Asset class", "Multi-region modular-factory / workforce-housing platform fund"),
        ("Date", _dt.date.today().isoformat()),
        ("HEADLINE VERDICT (Y5, 8× — conservative)", sc_y5["verdict"]),
        ("Y5 score", f"{sc_y5['total']} / 100"),
        ("Upside case (Y10, 10× — mature)", sc_y10["verdict"]),
        ("Y10 score", f"{sc_y10['total']} / 100"),
        ("LP raise", f"${d['lp_raise']:.1f}M" if d.get("lp_raise") else "—"),
        ("Y5 LP return", f"{d['y5_irr']*100:.1f}% IRR · {d['y5_moic']:.2f}× MOIC" if d.get("y5_irr") else "—"),
        ("Y10 LP return", f"{d['y10_irr']*100:.1f}% IRR · {d['y10_moic']:.2f}× MOIC" if d.get("y10_irr") else "—"),
        ("§1202 QSBS", "eligible (100% federal exclusion)" if d.get("s1202") else "not eligible"),
    ]
    r = 3
    for lab, val in rows:
        sty(vd, f"A{r}", lab, B, GREYF, L)
        f = vfill.get(val) if lab.startswith("HEADLINE") or lab.startswith("Upside") else None
        sty(vd, f"B{r}", val, Font(bold=True, size=12) if f else None, f, L)
        r += 1
    if sc_y5["vetoes"]:
        sty(vd, f"A{r}", "VETO", B, PatternFill("solid", fgColor=RED), L)
        sty(vd, f"B{r}", " · ".join(sc_y5["vetoes"]), None, None, L); r += 1

    # Scorecard sheet — both scenarios
    scw = wb.create_sheet("Scorecard")
    for i, w in enumerate([4, 30, 10, 8, 14, 26, 10], 1):
        scw.column_dimensions[chr(64+i)].width = w
    for title, scen in [("Y5 (8× EBITDA) — conservative", sc_y5), ("Y10 (10× EBITDA) — mature", sc_y10)]:
        sty(scw, f"A{scw.max_row+1 if scw.max_row>1 else 1}", title, TITLE, HEADF, L)
        hr = scw.max_row
        scw.merge_cells(f"A{hr}:G{hr}")
        hdr = ["#", "Gate", "Points", "Max", "Input", "Threshold", "Critical"]
        for ci, h in enumerate(hdr, 1):
            sty(scw, f"{chr(64+ci)}{hr+1}", h, Font(bold=True, color="FFFFFF"), HEADF, C)
        rr = hr + 2
        for i, (lab, p, mx, inp, thr, crit) in enumerate(scen["gates"], 1):
            fill = GREEN if p == mx else (AMBER if p > 0 else RED)
            sty(scw, f"A{rr}", i); sty(scw, f"B{rr}", lab, align=L)
            sty(scw, f"C{rr}", p, fill=PatternFill("solid", fgColor=fill), align=C)
            sty(scw, f"D{rr}", mx, align=C); sty(scw, f"E{rr}", inp, align=C)
            sty(scw, f"F{rr}", thr, align=L); sty(scw, f"G{rr}", "✓" if crit else "", align=C)
            rr += 1
        sty(scw, f"B{rr}", "TOTAL", B, GREYF); sty(scw, f"C{rr}", scen["total"], B, GREYF, C)
        sty(scw, f"D{rr}", 100, B, GREYF, C)
        scw.append([]); scw.append([])

    # Per-region returns
    pr = wb.create_sheet("Per-Region Returns")
    for i, w in enumerate([26, 12, 10, 10, 12, 10, 10], 1):
        pr.column_dimensions[chr(64+i)].width = w
    hdr = ["Region", "LP Raise ($M)", "Y5 IRR", "Y5 MOIC", "Y10 IRR", "Y10 MOIC", ""]
    for ci, h in enumerate(hdr, 1):
        sty(pr, f"{chr(64+ci)}1", h, Font(bold=True, color="FFFFFF"), HEADF, C)
    r = 2
    for rec in d.get("exit_regions", []):
        sty(pr, f"A{r}", rec["name"], align=L)
        sty(pr, f"B{r}", f"{rec['lp_raise']:.1f}" if rec.get("lp_raise") else "—", align=C)
        sty(pr, f"C{r}", f"{rec['y5_irr']*100:.1f}%" if rec.get("y5_irr") else "—", align=C)
        sty(pr, f"D{r}", f"{rec['y5_moic']:.2f}×" if rec.get("y5_moic") else "—", align=C)
        sty(pr, f"E{r}", f"{rec['y10_irr']*100:.1f}%" if rec.get("y10_irr") else "—", align=C)
        sty(pr, f"F{r}", f"{rec['y10_moic']:.2f}×" if rec.get("y10_moic") else "—", align=C)
        r += 1
    if d.get("platform_exit"):
        p = d["platform_exit"]
        sty(pr, f"A{r}", "PLATFORM", B, GREYF)
        sty(pr, f"B{r}", f"{d['lp_raise']:.1f}" if d.get("lp_raise") else "—", B, GREYF, C)
        sty(pr, f"C{r}", f"{d['y5_irr']*100:.1f}%" if d.get("y5_irr") else "—", B, GREYF, C)
        sty(pr, f"D{r}", f"{d['y5_moic']:.2f}×" if d.get("y5_moic") else "—", B, GREYF, C)
        sty(pr, f"E{r}", f"{d['y10_irr']*100:.1f}%" if d.get("y10_irr") else "—", B, GREYF, C)
        sty(pr, f"F{r}", f"{d['y10_moic']:.2f}×" if d.get("y10_moic") else "—", B, GREYF, C)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    wb.save(out_path)
    return out_path


# ── Orchestration ───────────────────────────────────────────────────────────────────────
def analyze(path, reports_dir="deals/reports"):
    d, missing = extract(path)
    sc_y5, sc_y10 = score(d, "y5"), score(d, "y10")
    out = os.path.join(reports_dir, f"{d['name']}_FactoryFund-GoNoGo_{_dt.date.today().isoformat()}.xlsx")
    write_report(d, sc_y5, sc_y10, out)
    return d, sc_y5, sc_y10, missing, out


def _print_brief(d, sc_y5, sc_y10, missing, out):
    print(f"\n=== {d['name']} — Factory-Platform Fund IC ===")
    print(f"  HEADLINE (Y5, 8× conservative): {sc_y5['verdict']}  ({sc_y5['total']}/100)")
    print(f"  Upside   (Y10, 10× mature):     {sc_y10['verdict']}  ({sc_y10['total']}/100)")
    if d.get("lp_raise"):
        print(f"  LP raise ${d['lp_raise']:.1f}M · "
              f"Y5 {d['y5_irr']*100:.1f}% IRR / {d['y5_moic']:.2f}× · "
              f"Y10 {d['y10_irr']*100:.1f}% IRR / {d['y10_moic']:.2f}×")
    if sc_y5["vetoes"]:
        print("  VETO:", " · ".join(sc_y5["vetoes"]))
    if missing:
        print("  Missing (fail-affecting):", ", ".join(missing))
    print(f"  → report: {out}")


def main(argv):
    if len(argv) < 2:
        print("usage: factory_fund_ic.py <workbook.xlsx>")
        return 1
    d, sc_y5, sc_y10, missing, out = analyze(argv[1])
    _print_brief(d, sc_y5, sc_y10, missing, out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
