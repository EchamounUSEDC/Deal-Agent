#!/usr/bin/env python3
"""IC Analyst engine — deterministic Go/No-Go underwriting.

The subagent (.claude/agents/ic-analyst.md) orchestrates; the reproducible math lives
here. Reads a deal workbook (arbitrary layout), maps metric synonyms, scores the IC
rubric, runs the downside stress test, and writes a formatted report workbook.

Usage:
    python scripts/ic_engine.py --inbox                       # process deals/inbox/*
    python scripts/ic_engine.py path/to/deal.xlsx             # score one file
    python scripts/ic_engine.py --selftest                    # build + score 2 test deals
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX = os.path.join(ROOT, "deals", "inbox")
PROCESSED = os.path.join(ROOT, "deals", "processed")
REPORTS = os.path.join(ROOT, "deals", "reports")

# ============================================================================
# Canonical metrics + synonym map (searched case-insensitively; first hit wins,
# most-specific patterns listed first). Rate fields are normalised to fractions.
# ============================================================================
RATE_FIELDS = {"going_in_cap", "exit_cap", "yield_on_cost", "opex_ratio",
               "unlevered_irr", "levered_irr", "market_pop_growth_5yr",
               "market_pipeline_pct", "ltv"}

SYNONYMS = [
    ("exit_cap", ["exit cap", "cap rate at sale", "sale cap rate", "terminal cap",
                  "reversion cap", "cap at exit", "disposition cap"]),
    ("going_in_cap", ["going-in cap", "going in cap", "in-place cap", "year 1 cap",
                      "entry cap", "current cap", "syndicated cap rate", "acquisition cap"]),
    ("noi", ["net operating income", "stabilized noi", "noi"]),
    ("yield_on_cost", ["yield on cost", "yield-on-cost", "stabilized yield", "return on cost",
                       "development yield", "yoc"]),
    ("levered_irr", ["levered irr", "leveraged irr", "equity irr", "irr to equity", "lirr"]),
    ("unlevered_irr", ["unlevered irr", "unleveraged irr", "property irr", "uirr"]),
    ("total_cost", ["total project cost", "total capitalization", "total cost", "purchase price",
                    "all-in cost", "development budget", "partnership level budget", "tdc"]),
    ("debt", ["permanent debt", "construction financing", "construction debt", "loan amount",
              "mortgage", "debt"]),
    ("equity", ["total equity", "equity"]),
    ("opex_ratio", ["op-ex ratio", "opex ratio", "operating expense ratio", "expense ratio"]),
    ("nrsf", ["net rentable", "rentable sf", "nrsf"]),
    ("market_pop_growth_5yr", ["5-yr pop growth", "5 year population growth", "5-year population growth",
                               "population growth", "pop growth", "population growth (5-yr)"]),
    ("market_population", ["market population", "msa population", "county population", "population"]),
    ("market_pipeline_pct", ["supply pipeline", "development pipeline", "new supply", "pipeline"]),
    ("market_rank", ["market rank", "rank"]),
    ("ltv", ["ltv", "loan to value", "loan-to-value"]),
    ("deal_type", ["deal type", "asset type", "strategy"]),
]
# derived-if-missing companions for op-ex
INCOME_KEYS = ["operating revenue", "total revenue", "effective gross income", "gross income"]
OPEX_KEYS = ["total operating expenses", "operating expenses", "total expenses"]


def _num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip().replace(",", "").replace("$", "").replace("%", "")
        try:
            f = float(s)
            return f / 100.0 if "%" in v else f
        except ValueError:
            return None
    return None


def _norm_rate(field, val):
    if val is None:
        return None
    return val / 100.0 if field in RATE_FIELDS and abs(val) > 1.5 else val


# ============================================================================
# Loading + extraction
# ============================================================================
def _pdf_rows(text):
    """Turn a page of extracted PDF text into label/value rows the scanner can read."""
    import re
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            lab, val = line.split(":", 1)
            rows.append([lab.strip(), val.strip()])
            continue
        m = re.search(r"-?\$?[\d,]+\.?\d*\s*%?", line)
        if m and m.start() > 0:
            rows.append([line[:m.start()].strip(), line[m.start():].strip()])
        else:
            rows.append([line])
    return rows


def _load_sheets(path):
    """Return {sheet: rows} where rows is a list of cell-value lists."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        import csv
        with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
            return {"csv": [list(r) for r in csv.reader(f)]}
    if ext == ".pdf":
        import pypdf
        reader = pypdf.PdfReader(path)
        rows = []
        for page in reader.pages:
            rows.extend(_pdf_rows(page.extract_text() or ""))
        return {"pdf": rows}
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    out = {}
    for ws in wb.worksheets:
        out[ws.title] = [list(r) for r in ws.iter_rows(max_row=800, max_col=60, values_only=True)]
    wb.close()
    return out


def _colletter(i):
    from openpyxl.utils import get_column_letter
    return get_column_letter(i)


def _match_field(label):
    lab = str(label).strip().lower()
    if not lab:
        return None
    for field, pats in SYNONYMS:
        for p in pats:
            if p in lab:
                return field
    return None


def _classify_type(metrics, blob):
    dt = metrics.get("deal_type")
    if isinstance(dt, str) and dt.strip():
        return "Development" if "develop" in dt.lower() else dt
    dev_signals = ("development", "construction", "yield on cost", "hard cost",
                   "lease up", "lease-up", "ground-up", "pay app")
    return "Development" if any(s in blob for s in dev_signals) else "Income/Core"


def _detect_matrix(rows):
    """A master-dashboard sheet: metric labels down column A, deals across row 1.

    Returns (label_col_idx, {deal_col_idx: deal_name}) or None.
    """
    if not rows or len(rows) < 6:
        return None
    # column that has the most metric-label matches
    best_col, best_hits = None, 0
    for ci in range(min(3, max(len(r) for r in rows))):
        hits = sum(1 for r in rows if ci < len(r) and _match_field(r[ci]))
        if hits > best_hits:
            best_col, best_hits = ci, hits
    if best_hits < 5:
        return None
    header = rows[0]
    deals = {ci: str(header[ci]).strip() for ci in range(best_col + 1, len(header))
             if ci < len(header) and isinstance(header[ci], str) and header[ci].strip()}
    # Require a genuine matrix: ≥2 named deal columns (a plain label/value pro forma
    # has only one value column and must go through the single-deal scanner instead).
    return (best_col, deals) if len(deals) >= 2 else None


def _extract_matrix(rows, sheet, label_col, deal_cols):
    """Extract one metrics/provenance/blob set per deal column."""
    label_rows = {}  # field -> row index (first match)
    for ri, r in enumerate(rows):
        if label_col < len(r):
            f = _match_field(r[label_col])
            if f and f not in label_rows:
                label_rows[f] = ri
    blob = " ".join(str(c).lower() for r in rows for c in r if isinstance(c, str))
    results = []
    for ci, name in deal_cols.items():
        metrics, prov = {}, {}
        for field, ri in label_rows.items():
            if ci < len(rows[ri]):
                val = rows[ri][ci]
                if field == "deal_type":
                    if isinstance(val, str) and val.strip():
                        metrics[field] = val.strip()
                        prov[field] = f"{sheet}!{_colletter(ci+1)}{ri+1}"
                    continue
                n = _norm_rate(field, _num(val))
                if n is not None:
                    metrics[field] = n
                    prov[field] = f"{sheet}!{_colletter(ci+1)}{ri+1}"
        results.append((name, metrics, prov, blob, ci))
    return results


def _extract_scan(sheets):
    """Single-deal label scan across all sheets."""
    metrics, prov = {}, {}
    blob_parts, income_amt, opex_amt = [], None, None
    for sheet, rows in sheets.items():
        for ri, r in enumerate(rows):
            label = None
            for ci, v in enumerate(r):
                if isinstance(v, str) and v.strip():
                    blob_parts.append(v.lower())
                    if label is None:
                        label = (ci, v)
            if not label:
                continue
            lci, ltext = label
            low = ltext.strip().lower()
            # first numeric to the right of the label
            numval, numcell = None, None
            for ci in range(lci + 1, len(r)):
                n = _num(r[ci])
                if n is not None:
                    numval, numcell = n, f"{sheet}!{_colletter(ci+1)}{ri+1}"
                    break
            if any(k in low for k in INCOME_KEYS) and income_amt is None and numval:
                income_amt = numval
            if any(k in low for k in OPEX_KEYS) and opex_amt is None and numval:
                opex_amt = numval
            field = _match_field(ltext)
            if field and field not in metrics:
                if field == "deal_type":
                    # the type value is usually text to the right
                    txt = next((str(c) for c in r[lci+1:] if isinstance(c, str) and c.strip()), None)
                    if txt:
                        metrics[field] = txt.strip(); prov[field] = f"{sheet}!R{ri+1}"
                    continue
                if numval is not None:
                    metrics[field] = _norm_rate(field, numval); prov[field] = numcell
    if "opex_ratio" not in metrics and income_amt and opex_amt:
        metrics["opex_ratio"] = opex_amt / income_amt
        prov["opex_ratio"] = "derived: op-ex / income"
    return metrics, prov, " ".join(blob_parts)


def _find_cashflows(sheets, deal_col=None):
    """Find an annual cash-flow stream (Year 0 negative). Returns list or None."""
    for sheet, rows in sheets.items():
        if "cash" not in sheet.lower() and "flow" not in sheet.lower():
            continue
        for ci in ([deal_col] if deal_col is not None else range(1, 30)):
            col = []
            for r in rows:
                if ci is not None and ci < len(r):
                    col.append(_num(r[ci]))
            nums = [x for x in col if x is not None]
            if len(nums) >= 3 and nums[0] < 0 and any(x > 0 for x in nums[1:]):
                # trim trailing zeros
                while len(nums) > 2 and nums[-1] == 0:
                    nums.pop()
                return nums
    return None


def extract_deals(path):
    """Return a list of dicts: {name, metrics, provenance, missing, deal_type, irr_source}."""
    sheets = _load_sheets(path)
    base = os.path.splitext(os.path.basename(path))[0]
    out = []
    matrix = None
    for sheet, rows in sheets.items():
        m = _detect_matrix(rows)
        if m:
            matrix = (sheet, *m)
            break
    if matrix:
        sheet, label_col, deal_cols = matrix
        for name, metrics, prov, blob, ci in _extract_matrix(sheets[sheet], sheet, label_col, deal_cols):
            # match each deal to ITS OWN cash-flow column (same column index in the CF sheet)
            out.append(_finalize(name, metrics, prov, blob, sheets, matrix_col=ci))
    else:
        metrics, prov, blob = _extract_scan(sheets)
        out.append(_finalize(base, metrics, prov, blob, sheets, matrix_col=None))
    return out


def _finalize(name, metrics, prov, blob, sheets, matrix_col):
    metrics = dict(metrics)
    metrics["deal_type"] = _classify_type(metrics, blob)
    is_dev = "develop" in str(metrics["deal_type"]).lower()
    # derive companions
    if metrics.get("total_cost") is None and metrics.get("equity") and metrics.get("debt") is not None:
        metrics["total_cost"] = metrics["equity"] + metrics["debt"]
    if metrics.get("yield_on_cost") is None and metrics.get("noi") and metrics.get("total_cost"):
        metrics["yield_on_cost"] = metrics["noi"] / metrics["total_cost"]
    # IRR: prefer calculated from cash flows
    irr_source = "stated"
    cfs = _find_cashflows(sheets, deal_col=matrix_col)
    if cfs:
        calc = irr_from_cashflows(cfs)
        if calc is not None:
            metrics["levered_irr"] = calc
            irr_source = "calculated from cash flows"
    equity_irr = metrics.get("levered_irr") if metrics.get("levered_irr") is not None else metrics.get("unlevered_irr")
    metrics["equity_irr"] = equity_irr
    metrics["is_dev"] = is_dev
    metrics["underwriting_yield"] = metrics.get("yield_on_cost") if is_dev else metrics.get("going_in_cap")
    missing = [f for f in ("total_cost", "exit_cap", "noi", "equity_irr", "underwriting_yield",
                           "market_population") if metrics.get(f) is None]
    return {"name": name, "metrics": metrics, "provenance": prov, "missing": missing,
            "deal_type": metrics["deal_type"], "irr_source": irr_source}


# ============================================================================
# IRR
# ============================================================================
def irr_from_cashflows(cashflows):
    try:
        import numpy_financial as nf
        r = nf.irr(cashflows)
        return None if r is None or (isinstance(r, float) and (r != r)) else float(r)
    except Exception:
        # Newton fallback
        r = 0.1
        for _ in range(200):
            npv = sum(c / (1 + r) ** t for t, c in enumerate(cashflows))
            d = sum(-t * c / (1 + r) ** (t + 1) for t, c in enumerate(cashflows))
            if abs(d) < 1e-9:
                break
            rn = r - npv / d
            if abs(rn - r) < 1e-10:
                return rn
            r = rn
        return r


# ============================================================================
# Scoring rubric (Section 3) — implemented exactly
# ============================================================================
def _g(cond_full, cond_partial, partial_pts, full_pts):
    if cond_full:
        return full_pts
    if cond_partial:
        return partial_pts
    return 0.0


def score(m):
    is_dev = bool(m.get("is_dev"))
    irr = m.get("equity_irr")
    cap = m.get("exit_cap")
    yld = m.get("underwriting_yield")
    opex = m.get("opex_ratio")
    pop = m.get("market_population")
    grw = m.get("market_pop_growth_5yr")
    pipe = m.get("market_pipeline_pct")
    rank = m.get("market_rank")
    nrsf = m.get("nrsf")
    gates = []

    def add(key, label, pts, mx, value, threshold, status):
        gates.append({"key": key, "label": label, "points": pts, "max": mx,
                      "value": value, "threshold": threshold, "status": status})

    # 1 IRR beats exit cap (critical)
    ok = irr is not None and cap is not None and irr > cap
    add("irr_beats_cap", "IRR beats exit cap", 15.0 if ok else 0.0, 15,
        irr, cap, "PASS" if ok else "FAIL")
    # 2 Yield clears floor (critical)
    p2 = 15.0 if (yld is not None and yld >= 0.075) else (7.5 if (yld is not None and yld >= 0.065) else 0.0)
    add("yield_floor", "Yield clears floor", p2, 15, yld, "≥7.5% / ≥6.5%",
        "PASS" if p2 == 15 else ("PARTIAL" if p2 else "FAIL"))
    # 3 Op-ex in range
    if opex is None:
        p3 = 0.0
    elif opex <= 0.30:
        p3 = 10.0
    elif opex <= 0.35:
        p3 = 5.0
    elif opex <= 0.45:
        p3 = 2.5
    else:
        p3 = 0.0
    add("opex", "Op-ex in range", p3, 10, opex, "≤30/35/45%",
        "PASS" if p3 == 10 else ("PARTIAL" if p3 else "FAIL"))
    # 4 Population ≥ 200k (critical)
    ok4 = pop is not None and pop >= 200_000
    add("population", "Population ≥ 200k", 12.0 if ok4 else 0.0, 12, pop, "≥200,000",
        "PASS" if ok4 else "FAIL")
    # 5 Positive pop growth (missing → 5 neutral)
    if grw is None:
        p5 = 5.0
    elif grw >= 0.05:
        p5 = 10.0
    elif grw > 0:
        p5 = 5.0
    else:
        p5 = 0.0
    add("growth", "Positive pop growth", p5, 10, grw, "≥5% / >0%",
        "PASS" if p5 == 10 else ("PARTIAL" if p5 else "FAIL"))
    # 6 Pipeline contained (missing → 5 neutral)
    if pipe is None:
        p6 = 5.0
    elif pipe <= 0.05:
        p6 = 10.0
    elif pipe <= 0.10:
        p6 = 5.0
    else:
        p6 = 0.0
    add("pipeline", "Pipeline contained", p6, 10, pipe, "≤5% / ≤10%",
        "PASS" if p6 == 10 else ("PARTIAL" if p6 else "FAIL"))
    # 7 Return clears target
    if irr is None:
        p7 = 0.0
    else:
        hi, lo = (0.15, 0.12) if is_dev else (0.10, 0.07)
        p7 = 13.0 if irr >= hi else (6.5 if irr >= lo else 0.0)
    add("return_target", "Return clears target", p7, 13, irr,
        "dev ≥15/12% · else ≥10/7%", "PASS" if p7 == 13 else ("PARTIAL" if p7 else "FAIL"))
    # 8 Market upper half (missing → 4 neutral)
    if rank is None:
        p8 = 4.0
    elif rank <= 123:
        p8 = 8.0
    elif rank <= 184:
        p8 = 4.0
    else:
        p8 = 0.0
    add("market_rank", "Market upper half", p8, 8, rank, "≤123 / ≤184",
        "PASS" if p8 == 8 else ("PARTIAL" if p8 else "FAIL"))
    # 9 Size near 75k NRSF (else/missing → 3.5)
    p9 = 7.0 if (nrsf is not None and 40_000 <= nrsf <= 120_000) else 3.5
    add("size", "Size near 75k NRSF", p9, 7, nrsf, "40k–120k",
        "PASS" if p9 == 7 else "N/A")

    total = round(sum(g["points"] for g in gates), 1)
    vetoes = []
    if not (irr is not None and cap is not None and irr > cap):
        vetoes.append("Equity IRR does not beat exit cap (or missing)")
    if not (yld is not None and yld >= 0.065):
        vetoes.append("Underwriting yield < 6.5% (or missing)")
    if not (pop is not None and pop >= 200_000):
        vetoes.append("Market population < 200,000 (or missing)")
    if vetoes:
        verdict = "NO-GO"
    elif total >= 70:
        verdict = "GO"
    elif total >= 50:
        verdict = "CONDITIONAL GO"
    else:
        verdict = "NO-GO"
    return {"gates": gates, "total": total, "vetoes": vetoes, "verdict": verdict}


# ============================================================================
# Stress test (Section 4) + sensitivity
# ============================================================================
def stress(m):
    cap = m.get("exit_cap")
    noi = m.get("noi")
    cost = m.get("total_cost")
    irr = m.get("equity_irr")
    is_dev = bool(m.get("is_dev"))
    if None in (cap, noi, cost):
        return {"ok": None, "rows": [], "verdict": "n/a — missing exit cap / NOI / cost"}
    s_cap = cap + 0.005
    s_noi = noi * 0.95
    s_yoc = s_noi / cost
    s_val = s_noi / s_cap
    s_spread = s_yoc - s_cap
    survives = (s_yoc >= 0.065) and (s_spread >= 0 if is_dev else True) and (irr is not None and irr > s_cap)
    rows = [
        ("Exit cap", cap, s_cap, "pct"),
        ("NOI", noi, s_noi, "money"),
        ("Yield on cost", (noi / cost), s_yoc, "pct"),
        ("Implied value", (noi / cap), s_val, "money"),
        ("Dev spread", ((noi / cost) - cap), s_spread, "pct"),
    ]
    return {"ok": survives, "rows": rows,
            "verdict": "YES — robust" if survives else "FRAGILE — fails under stress"}


def sensitivity(m):
    """Verdict/score grid: exit cap ±25/±50bps × NOI ±5%."""
    cap0, noi0 = m.get("exit_cap"), m.get("noi")
    cost = m.get("total_cost")
    if None in (cap0, noi0, cost):
        return None
    cap_deltas = [-0.005, -0.0025, 0.0, 0.0025, 0.005]
    noi_factors = [1.05, 1.0, 0.95]
    grid = []
    for nf_ in noi_factors:
        row = []
        for cd in cap_deltas:
            mm = dict(m)
            mm["exit_cap"] = cap0 + cd
            mm["noi"] = noi0 * nf_
            mm["yield_on_cost"] = (noi0 * nf_) / cost
            mm["underwriting_yield"] = mm["yield_on_cost"] if m.get("is_dev") else m.get("going_in_cap")
            s = score(mm)
            row.append((s["verdict"], s["total"]))
        grid.append((nf_, row))
    return {"cap_deltas": cap_deltas, "noi_factors": noi_factors, "grid": grid}


# ============================================================================
# Report writer
# ============================================================================
def _analyst_narrative(deal, sc, st):
    strong = [g["label"] for g in sc["gates"] if g["points"] == g["max"]]
    weak = [g["label"] for g in sc["gates"] if g["points"] < g["max"] * 0.5]
    v = sc["verdict"]
    parts = [f"{deal['name']} ({deal['deal_type']}) scores {sc['total']}/100 → {v}."]
    if sc["vetoes"]:
        parts.append("Critical veto tripped: " + "; ".join(sc["vetoes"]) + ".")
    if strong:
        parts.append("Strengths: " + ", ".join(strong[:4]) + ".")
    if weak:
        parts.append("Watch-items: " + ", ".join(weak[:4]) + ".")
    parts.append(f"Downside stress (exit +50bps, NOI −5%): {st['verdict']}.")
    if deal["missing"]:
        parts.append("Missing inputs: " + ", ".join(deal["missing"]) + " (not fabricated).")
    return " ".join(parts)


def write_report(deal, out_path):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    m = deal["metrics"]
    sc = score(m)
    st = stress(m)
    sens = sensitivity(m)

    NAVY = "1F3A5F"; GREEN = "C6EFCE"; AMBER = "FFEB9C"; RED = "FFC7CE"; GREY = "F2F2F2"
    H = Font(bold=True, color="FFFFFF", size=11); TITLE = Font(bold=True, color="FFFFFF", size=16)
    B = Font(bold=True); thin = Side(style="thin", color="BFBFBF")
    BORDER = Border(thin, thin, thin, thin)
    C = Alignment(horizontal="center", vertical="center")
    L = Alignment(horizontal="left", vertical="center", wrap_text=True)
    vfill = {"GO": GREEN, "CONDITIONAL GO": AMBER, "NO-GO": RED}[sc["verdict"]]
    PCT = "0.0%"; MONEY = "$#,##0"

    def s(ws, coord, val, font=None, fill=None, fmt=None, align=None, border=True):
        c = ws[coord]; c.value = val
        if font: c.font = font
        if fill: c.fill = PatternFill("solid", fgColor=fill)
        if fmt: c.number_format = fmt
        if align: c.alignment = align
        if border: c.border = BORDER
        return c

    wb = openpyxl.Workbook()

    # ---- Verdict ----
    vd = wb.active; vd.title = "Verdict"; vd.sheet_view.showGridLines = False
    vd.column_dimensions["A"].width = 26; vd.column_dimensions["B"].width = 90
    vd.merge_cells("A1:B1"); s(vd, "A1", "IC GO / NO-GO REPORT", TITLE, NAVY, align=C, border=False)
    vd.row_dimensions[1].height = 30
    s(vd, "A3", "Deal", B, GREY); s(vd, "B3", deal["name"], align=L)
    s(vd, "A4", "Deal type", B, GREY); s(vd, "B4", deal["deal_type"], align=L)
    s(vd, "A5", "Date", B, GREY); s(vd, "B5", _dt.date.today().isoformat(), align=L)
    s(vd, "A6", "VERDICT", B, GREY); s(vd, "B6", sc["verdict"], Font(bold=True, size=14), vfill, align=L)
    s(vd, "A7", "Score", B, GREY); s(vd, "B7", f"{sc['total']} / 100", Font(bold=True, size=12), align=L)
    s(vd, "A8", "Veto status", B, GREY)
    s(vd, "B8", ("None" if not sc["vetoes"] else " · ".join(sc["vetoes"])), align=L)
    s(vd, "A9", "IRR source", B, GREY); s(vd, "B9", deal["irr_source"], align=L)
    s(vd, "A11", "Analyst narrative", B, GREY)
    s(vd, "B11", _analyst_narrative(deal, sc, st), align=L)
    vd.row_dimensions[11].height = 90

    # ---- Scorecard ----
    scw = wb.create_sheet("Scorecard")
    heads = ["#", "Gate", "Points", "Max", "Input value", "Threshold", "Status"]
    for j, h in enumerate(heads):
        s(scw, f"{_colletter(j+1)}1", h, H, NAVY, align=C)
    for i, g in enumerate(sc["gates"], 1):
        r = i + 1
        val = g["value"]
        vtxt = "—" if val is None else (f"{val:.1%}" if g["key"] in ("irr_beats_cap", "yield_floor", "opex",
                 "growth", "pipeline", "return_target") and isinstance(val, float) and abs(val) < 5
                 else (f"{val:,.0f}" if isinstance(val, (int, float)) else str(val)))
        s(scw, f"A{r}", i, align=C); s(scw, f"B{r}", g["label"], align=L)
        s(scw, f"C{r}", g["points"], align=C); s(scw, f"D{r}", g["max"], align=C)
        s(scw, f"E{r}", vtxt, align=C); s(scw, f"F{r}", g["threshold"], align=L)
        st_cell = s(scw, f"G{r}", g["status"], B, align=C)
        st_cell.fill = PatternFill("solid", fgColor={"PASS": GREEN, "PARTIAL": AMBER,
                                                     "FAIL": RED, "N/A": GREY}.get(g["status"], GREY))
    tr = len(sc["gates"]) + 2
    s(scw, f"B{tr}", "TOTAL", B, GREY); s(scw, f"C{tr}", sc["total"], B, GREY)
    s(scw, f"D{tr}", 100, B, GREY)
    for col, w in zip("ABCDEFG", [4, 26, 8, 6, 14, 26, 10]):
        scw.column_dimensions[col].width = w

    # ---- Deal Metrics ----
    dm = wb.create_sheet("Deal Metrics")
    for j, h in enumerate(["Metric", "Value", "Source (sheet!cell / note)"]):
        s(dm, f"{_colletter(j+1)}1", h, H, NAVY, align=C)
    order = ["deal_type", "total_cost", "equity", "debt", "ltv", "going_in_cap", "exit_cap",
             "noi", "opex_ratio", "yield_on_cost", "unlevered_irr", "levered_irr", "equity_irr",
             "underwriting_yield", "nrsf", "market_population", "market_pop_growth_5yr",
             "market_pipeline_pct", "market_rank"]
    pct_fields = {"ltv", "going_in_cap", "exit_cap", "opex_ratio", "yield_on_cost",
                  "unlevered_irr", "levered_irr", "equity_irr", "underwriting_yield",
                  "market_pop_growth_5yr", "market_pipeline_pct"}
    money_fields = {"total_cost", "equity", "debt", "noi"}
    r = 2
    for f in order:
        val = m.get(f)
        s(dm, f"A{r}", f.replace("_", " ").title(), B, GREY, align=L)
        cell = s(dm, f"B{r}", ("—" if val is None else val), align=C)
        if isinstance(val, (int, float)):
            cell.number_format = PCT if f in pct_fields else (MONEY if f in money_fields else "#,##0")
        s(dm, f"C{r}", deal["provenance"].get(f, "— (missing)" if val is None else "derived"), align=L)
        r += 1
    if deal["missing"]:
        s(dm, f"A{r+1}", "MISSING (critical-affecting)", B, RED, align=L)
        s(dm, f"B{r+1}", ", ".join(deal["missing"]), align=L)
    for col, w in zip("ABC", [26, 18, 40]):
        dm.column_dimensions[col].width = w

    # ---- Stress Test ----
    stw = wb.create_sheet("Stress Test")
    s(stw, "A1", "DOWNSIDE STRESS — exit cap +50bps · NOI −5%", H, NAVY, align=L)
    stw.merge_cells("A1:C1")
    for j, h in enumerate(["Metric", "Base", "Stressed"]):
        s(stw, f"{_colletter(j+1)}2", h, H, NAVY, align=C)
    for i, (lab, base, strv, kind) in enumerate(st["rows"], 3):
        s(stw, f"A{i}", lab, B, GREY, align=L)
        fmt = PCT if kind == "pct" else MONEY
        s(stw, f"B{i}", base, fmt=fmt, align=C); s(stw, f"C{i}", strv, fmt=fmt, align=C)
    rr = len(st["rows"]) + 3
    s(stw, f"A{rr}", "Survives stress?", B, GREY, align=L)
    sc_cell = s(stw, f"B{rr}", st["verdict"], B, align=C)
    sc_cell.fill = PatternFill("solid", fgColor=GREEN if st["ok"] else RED)
    stw.merge_cells(f"B{rr}:C{rr}")
    for col, w in zip("ABC", [22, 18, 18]):
        stw.column_dimensions[col].width = w

    # ---- Sensitivity ----
    sw = wb.create_sheet("Sensitivity")
    s(sw, "A1", "SENSITIVITY — verdict & score by exit cap Δ (cols) × NOI (rows)", H, NAVY, align=L)
    sw.merge_cells("A1:F1")
    if sens:
        s(sw, "A2", "NOI ↓ / Exit cap Δ →", B, GREY, align=C)
        for j, cd in enumerate(sens["cap_deltas"]):
            s(sw, f"{_colletter(j+2)}2", f"{cd*10000:+.0f} bps", H, NAVY, align=C)
        for i, (nf_, row) in enumerate(sens["grid"], 3):
            s(sw, f"A{i}", f"{(nf_-1)*100:+.0f}% NOI", B, GREY, align=C)
            for j, (verd, tot) in enumerate(row):
                cell = s(sw, f"{_colletter(j+2)}{i}", f"{verd}\n{tot}", align=C)
                cell.fill = PatternFill("solid", fgColor={"GO": GREEN, "CONDITIONAL GO": AMBER,
                                                          "NO-GO": RED}[verd])
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for col in "ABCDEF":
            sw.column_dimensions[col].width = 15
    else:
        s(sw, "A2", "Insufficient inputs for sensitivity (need exit cap, NOI, total cost).", align=L)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    wb.save(out_path)
    return {"verdict": sc["verdict"], "score": sc["total"], "stress": st["verdict"],
            "vetoes": sc["vetoes"], "narrative": _analyst_narrative(deal, sc, st), "out": out_path}


# ============================================================================
# Orchestration
# ============================================================================
def _safe_name(name):
    return "".join(ch if ch.isalnum() or ch in " -_" else "_" for ch in str(name)).strip() or "Deal"


def analyze_file(path, reports_dir=REPORTS):
    deals = extract_deals(path)
    results = []
    for deal in deals:
        if str(deal["name"]).startswith("New Deal") and all(
                deal["metrics"].get(k) is None for k in ("total_cost", "noi", "exit_cap")):
            continue  # skip empty template columns
        out = os.path.join(reports_dir,
                           f"{_safe_name(deal['name'])}_IC-GoNoGo_{_dt.date.today().isoformat()}.xlsx")
        results.append((deal, write_report(deal, out)))
    if len(results) > 1:
        _write_ranking(results, reports_dir, os.path.splitext(os.path.basename(path))[0])
    return results


def _write_ranking(results, reports_dir, source):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Ranking"
    NAVY = "1F3A5F"
    H = Font(bold=True, color="FFFFFF"); HEAD = PatternFill("solid", fgColor=NAVY)
    for j, h in enumerate(["Rank", "Deal", "Verdict", "Score", "Stress"]):
        c = ws.cell(1, j + 1, h); c.font = H; c.fill = HEAD
        c.alignment = Alignment(horizontal="center")
    ranked = sorted(results, key=lambda r: r[1]["score"], reverse=True)
    fillmap = {"GO": "C6EFCE", "CONDITIONAL GO": "FFEB9C", "NO-GO": "FFC7CE"}
    for i, (deal, res) in enumerate(ranked, 1):
        ws.cell(i + 1, 1, i); ws.cell(i + 1, 2, deal["name"])
        vc = ws.cell(i + 1, 3, res["verdict"]); vc.fill = PatternFill("solid", fgColor=fillmap[res["verdict"]])
        ws.cell(i + 1, 4, res["score"]); ws.cell(i + 1, 5, res["stress"])
    for col, w in zip("ABCDE", [6, 30, 16, 8, 26]):
        ws.column_dimensions[col].width = w
    out = os.path.join(reports_dir, f"{_safe_name(source)}_Ranking_{_dt.date.today().isoformat()}.xlsx")
    wb.save(out)
    return out


def analyze_inbox():
    os.makedirs(INBOX, exist_ok=True); os.makedirs(PROCESSED, exist_ok=True); os.makedirs(REPORTS, exist_ok=True)
    files = [f for f in os.listdir(INBOX) if f.lower().endswith((".xlsx", ".xlsm", ".csv", ".pdf"))]
    if not files:
        print("No new deal files in deals/inbox/."); return []
    allres = []
    for f in sorted(files):
        path = os.path.join(INBOX, f)
        print(f"\n=== {f} ===")
        for deal, res in analyze_file(path):
            allres.append(res)
            print(f"  {deal['name']}: {res['verdict']} ({res['score']}/100) · stress {res['stress']}")
            print(f"    → {os.path.basename(res['out'])}")
        shutil.move(path, os.path.join(PROCESSED, f))
    return allres


# ============================================================================
# Self-test: a GO deal and a veto deal
# ============================================================================
def _make_test_deal(path, rows):
    import openpyxl
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Proforma"
    for i, (k, v) in enumerate(rows, 1):
        ws.cell(i, 1, k); ws.cell(i, 2, v)
    wb.save(path)


def selftest():
    os.makedirs(INBOX, exist_ok=True)
    go = os.path.join(INBOX, "TEST_Go_Deal.xlsx")
    veto = os.path.join(INBOX, "TEST_Veto_Deal.xlsx")
    _make_test_deal(go, [
        ("Deal Type", "Development"), ("Total Project Cost", 10_000_000), ("Equity", 6_000_000),
        ("Permanent Debt", 4_000_000), ("Exit Cap", 0.06), ("NOI", 780_000), ("Op-ex Ratio", 0.30),
        ("Levered IRR", 0.17), ("NRSF", 78_000), ("Market Population", 260_000),
        ("5-yr Pop Growth", 0.06), ("Supply Pipeline", 0.04), ("Market Rank", 30)])
    _make_test_deal(veto, [
        ("Deal Type", "Income/Core"), ("Purchase Price", 12_000_000), ("Equity", 12_000_000),
        ("Cap Rate at Sale", 0.05), ("Going-in Cap", 0.05), ("NOI", 600_000), ("Op-ex Ratio", 0.45),
        ("Equity IRR", 0.045), ("Market Population", 150_000), ("Supply Pipeline", 0.15),
        ("Market Rank", 220)])
    print("Built test deals in deals/inbox/. Analyzing…")
    analyze_inbox()


def main(argv=None):
    p = argparse.ArgumentParser(description="IC Analyst engine")
    p.add_argument("file", nargs="?", help="A deal workbook to score (else use --inbox)")
    p.add_argument("--inbox", action="store_true", help="Process every file in deals/inbox/")
    p.add_argument("--selftest", action="store_true", help="Build & score a GO and a veto test deal")
    a = p.parse_args(argv)
    if a.selftest:
        selftest(); return 0
    if a.inbox:
        analyze_inbox(); return 0
    if a.file:
        for deal, res in analyze_file(a.file):
            print(f"{deal['name']}: {res['verdict']} ({res['score']}/100) · stress {res['stress']}")
            print(f"  {res['narrative']}")
            print(f"  → {res['out']}")
        return 0
    p.print_help(); return 1


if __name__ == "__main__":
    raise SystemExit(main())
