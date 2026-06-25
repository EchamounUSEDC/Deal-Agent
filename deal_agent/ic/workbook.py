"""Build the live IC Go/No-Go Excel dashboard.

The workbook is self-contained: pick a deal from the **dropdown** on the Dashboard sheet
and every comparison, gate score, and the GO / CONDITIONAL / NO-GO verdict recalculates
instantly — no API key, no add-in. The gate formulas reproduce `schema.py` exactly.

Sheets
------
Read Me · Dashboard (dropdown) · Deals (raw inputs) · Scores (live gate engine) ·
Ranking (all deals scored) · Market Ranking (top markets).
"""

from __future__ import annotations

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule

from .schema import Deal
from .market import COL, MarketRanking

# ---- styling ---------------------------------------------------------------------
NAVY = "1F3A5F"
WHITE = "FFFFFF"
GREEN = "C6EFCE"; GREEN_T = "006100"
AMBER = "FFEB9C"; AMBER_T = "9C6500"
RED = "FFC7CE"; RED_T = "9C0006"
GREY = "F2F2F2"
H = Font(bold=True, color=WHITE, size=11)
TITLE = Font(bold=True, color=WHITE, size=16)
B = Font(bold=True)
thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
HEADFILL = PatternFill("solid", fgColor=NAVY)
GREYFILL = PatternFill("solid", fgColor=GREY)
CENTER = Alignment(horizontal="center", vertical="center")
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)

# (row, field, label, kind) — order defines the Deals sheet layout.
METRICS = [
    ("deal_type", "Deal type", "text"),
    ("is_development", "Is development (1/0)", "int"),
    ("total_cost", "Total cost", "money"),
    ("equity", "Equity", "money"),
    ("debt", "Debt", "money"),
    ("ltv", "LTV", "pct"),
    ("going_in_cap", "Going-in cap", "pct"),
    ("exit_cap", "Exit cap", "pct"),
    ("noi", "NOI", "money"),
    ("opex_ratio", "Op-ex ratio", "pct"),
    ("yield_on_cost", "Yield on cost", "pct"),
    ("dev_spread", "Dev. spread", "pct"),
    ("unlevered_irr", "Unlevered IRR", "pct"),
    ("levered_irr", "Levered IRR", "pct"),
    ("nrsf", "NRSF", "num"),
    ("site_acreage", "Site acreage", "num"),
    ("units", "Units", "num"),
    ("avg_rate_per_nrsf", "Avg rate $/NRSF", "num2"),
    ("market_population", "Market population", "num"),
    ("market_pop_growth_5yr", "5-yr pop growth", "pct"),
    ("market_pipeline_pct", "Supply pipeline %", "pct"),
    ("market_rank", "Market rank", "int"),
    ("market_score", "Market weighted score", "num2"),
    ("best_irr", "Best IRR (calc)", "pct"),
    ("underwriting_yield", "Underwriting yield (calc)", "pct"),
]
MROW = {f: i + 2 for i, (f, _, _) in enumerate(METRICS)}  # field -> Deals row
FMT = {"money": '$#,##0', "pct": '0.0%', "num": '#,##0', "num2": '#,##0.00', "int": '0'}

# Scores sheet rows (gate label, row). Mirrors schema.GATES weights/thresholds.
SCORE_ROWS = [
    ("IRR beats exit cap", 2), ("Yield clears floor", 3), ("Op-ex in range", 4),
    ("Population ≥ 200k", 5), ("Positive pop growth", 6), ("Pipeline contained", 7),
    ("Return clears target", 8), ("Market upper half", 9), ("Size near 75k NRSF", 10),
]
S_TOTAL, S_CRIT, S_VERDICT = 12, 13, 14


def _gate_formula(row: int, dc: str) -> str:
    """Return the Scores-sheet formula for gate `row`, candidate in Deals column `dc`."""
    d = lambda r: f"Deals!{dc}{r}"
    irr, cap = d(MROW["best_irr"]), d(MROW["exit_cap"])
    yld = d(MROW["underwriting_yield"])
    opex = d(MROW["opex_ratio"]); pop = d(MROW["market_population"])
    grw = d(MROW["market_pop_growth_5yr"]); pipe = d(MROW["market_pipeline_pct"])
    isdev = d(MROW["is_development"]); rank = d(MROW["market_rank"]); nrsf = d(MROW["nrsf"])
    return {
        2: f'=IF(OR({irr}="",{cap}=""),0,IF({irr}>{cap},15,0))',
        3: f'=IF({yld}="",0,IF({yld}>=0.075,15,IF({yld}>=0.065,7.5,0)))',
        4: f'=IF({opex}="",0,IF({opex}<=0.3,10,IF({opex}<=0.35,5,0)))',
        5: f'=IF({pop}="",0,IF({pop}>=200000,12,0))',
        6: f'=IF({grw}="",5,IF({grw}>=0.05,10,IF({grw}>0,5,0)))',
        7: f'=IF({pipe}="",5,IF({pipe}<=0.05,10,IF({pipe}<=0.1,5,0)))',
        8: f'=IF({irr}="",0,IF({irr}>=IF({isdev}=1,0.15,0.1),13,IF({irr}>=IF({isdev}=1,0.12,0.07),6.5,0)))',
        9: f'=IF({rank}="",4,IF({rank}<=123,8,IF({rank}<=184,4,0)))',
        10: f'=IF({nrsf}="",3.5,IF(AND({nrsf}>=40000,{nrsf}<=120000),7,IF(AND({nrsf}>=25000,{nrsf}<=150000),3.5,0)))',
    }[row]


def _critical_formula(dc: str) -> str:
    d = lambda r: f"Deals!{dc}{r}"
    irr, cap = d(MROW["best_irr"]), d(MROW["exit_cap"])
    yld, pop = d(MROW["underwriting_yield"]), d(MROW["market_population"])
    irr_fail = f'IF(OR({irr}="",{cap}=""),1,IF({irr}>{cap},0,1))'
    yld_fail = f'IF({yld}="",1,IF({yld}>=0.065,0,1))'
    pop_fail = f'IF({pop}="",1,IF({pop}>=200000,0,1))'
    return f'=IF(OR({irr_fail}=1,{yld_fail}=1,{pop_fail}=1),1,0)'


def _set(ws, coord, value, *, font=None, fill=None, fmt=None, align=None, border=True):
    c = ws[coord]
    c.value = value
    if font: c.font = font
    if fill: c.fill = fill
    if fmt: c.number_format = fmt
    if align: c.alignment = align
    if border: c.border = BORDER
    return c


def build_workbook(out_path: str, benchmarks: list[Deal], candidates: list[Deal],
                   market: MarketRanking | None = None) -> str:
    deals = list(benchmarks) + list(candidates)
    n = len(deals)
    last_col = get_column_letter(1 + n)            # last candidate column
    last_letter = last_col
    cols = [get_column_letter(2 + i) for i in range(n)]  # B, C, ...

    wb = Workbook()
    wb.calculation.fullCalcOnLoad = True

    # ============================ Deals (raw inputs) ============================
    dz = wb.active
    dz.title = "Deals"
    _set(dz, "A1", "Metric", font=H, fill=HEADFILL, align=LEFT)
    for j, deal in enumerate(deals):
        c = cols[j]
        _set(dz, f"{c}1", deal.name, font=H, fill=HEADFILL, align=CENTER)
        for field, label, kind in METRICS:
            r = MROW[field]
            if field == "is_development":
                val = 1 if deal.is_development else 0
            elif field in ("best_irr", "underwriting_yield"):
                continue  # written as formulas below
            else:
                val = getattr(deal, field, None)
            cell = _set(dz, f"{c}{r}", val, fmt=FMT.get(kind), align=CENTER)
        # calculated rows
        _set(dz, f"{c}{MROW['best_irr']}",
             f'=IF(COUNT({c}{MROW["unlevered_irr"]}:{c}{MROW["levered_irr"]})=0,"",'
             f'MAX({c}{MROW["unlevered_irr"]}:{c}{MROW["levered_irr"]}))',
             fmt=FMT["pct"], align=CENTER)
        _set(dz, f"{c}{MROW['underwriting_yield']}",
             f'=IF({c}{MROW["is_development"]}=1,{c}{MROW["yield_on_cost"]},{c}{MROW["going_in_cap"]})',
             fmt=FMT["pct"], align=CENTER)
    for field, label, kind in METRICS:
        _set(dz, f"A{MROW[field]}", label, font=B, fill=GREYFILL, align=LEFT)
    dz.column_dimensions["A"].width = 24
    for c in cols:
        dz.column_dimensions[c].width = 18
    dz.freeze_panes = "B2"

    # ============================ Scores (live engine) ==========================
    sc = wb.create_sheet("Scores")
    _set(sc, "A1", "Gate", font=H, fill=HEADFILL, align=LEFT)
    weights = {2: 15, 3: 15, 4: 10, 5: 12, 6: 10, 7: 10, 8: 13, 9: 8, 10: 7}
    for label, r in SCORE_ROWS:
        _set(sc, f"A{r}", f"{label} (max {weights[r]})", font=B, fill=GREYFILL, align=LEFT)
    _set(sc, f"A{S_TOTAL}", "TOTAL SCORE", font=B, fill=GREYFILL, align=LEFT)
    _set(sc, f"A{S_CRIT}", "Critical fail (1=veto)", font=B, fill=GREYFILL, align=LEFT)
    _set(sc, f"A{S_VERDICT}", "VERDICT", font=B, fill=GREYFILL, align=LEFT)
    for j, deal in enumerate(deals):
        c = cols[j]
        _set(sc, f"{c}1", f"=Deals!{c}1", font=H, fill=HEADFILL, align=CENTER)
        for _, r in SCORE_ROWS:
            _set(sc, f"{c}{r}", _gate_formula(r, c), align=CENTER)
        _set(sc, f"{c}{S_TOTAL}", f"=SUM({c}2:{c}10)", font=B, align=CENTER)
        _set(sc, f"{c}{S_CRIT}", _critical_formula(c), align=CENTER)
        _set(sc, f"{c}{S_VERDICT}",
             f'=IF({c}{S_CRIT}=1,"NO-GO",IF({c}{S_TOTAL}>=70,"GO",'
             f'IF({c}{S_TOTAL}>=50,"CONDITIONAL GO","NO-GO")))', font=B, align=CENTER)
    sc.column_dimensions["A"].width = 26
    for c in cols:
        sc.column_dimensions[c].width = 16
    _verdict_cf(sc, f"{cols[0]}{S_VERDICT}:{cols[-1]}{S_VERDICT}")

    # ============================ Dashboard (dropdown) ==========================
    db = wb.create_sheet("Dashboard")
    wb.move_sheet("Dashboard", -(len(wb.sheetnames) - 1))  # make it first
    _build_dashboard(db, deals, cols, last_letter)

    # ============================ Ranking =======================================
    rk = wb.create_sheet("Ranking")
    _build_ranking(rk, deals, cols)

    # ============================ Market Ranking ================================
    if market is not None:
        _build_market(wb.create_sheet("Market Ranking"), market)

    # ============================ Read Me =======================================
    _build_readme(wb.create_sheet("Read Me"))
    wb.move_sheet("Read Me", -(len(wb.sheetnames) - 2))  # second tab

    wb.save(out_path)
    return out_path


def _verdict_cf(ws, rng: str):
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"GO"'],
        fill=PatternFill("solid", fgColor=GREEN), font=Font(bold=True, color=GREEN_T)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"CONDITIONAL GO"'],
        fill=PatternFill("solid", fgColor=AMBER), font=Font(bold=True, color=AMBER_T)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"NO-GO"'],
        fill=PatternFill("solid", fgColor=RED), font=Font(bold=True, color=RED_T)))


def _build_dashboard(db, deals, cols, last_letter):
    bench_cols = cols[:2] if len(cols) >= 2 else cols  # Springfield, Hamburg = first two
    db.sheet_view.showGridLines = False
    db.column_dimensions["A"].width = 26
    for c in ("B", "C", "D", "E"):
        db.column_dimensions[c].width = 19

    db.merge_cells("A1:E1")
    _set(db, "A1", "INVESTMENT COMMITTEE  ·  GO / NO-GO DASHBOARD", font=TITLE,
         fill=HEADFILL, align=CENTER, border=False)
    db.row_dimensions[1].height = 30

    _set(db, "A3", "Select a deal ▼", font=B, fill=GREYFILL, align=LEFT)
    sel = _set(db, "B3", deals[-1].name, font=Font(bold=True, size=12), align=CENTER)
    sel.fill = PatternFill("solid", fgColor="FFF2CC")
    # hidden helper: selected column index (B..) within Deals row 1 (placed off to the
    # side so it is clear of the merged title band and the visible comparison tables)
    _set(db, "H1", "=MATCH($B$3,Deals!$1:$1,0)", align=CENTER, border=False)
    db["H1"].font = Font(color="FFFFFF")  # hide the helper visually
    db.column_dimensions["H"].hidden = True

    drange = f"Deals!$A$1:${last_letter}${max(MROW.values())}"
    srange = f"Scores!$A$1:${last_letter}${S_VERDICT}"
    isel = "$H$1"

    # headline verdict + score
    _set(db, "A5", "VERDICT", font=B, fill=GREYFILL, align=CENTER)
    _set(db, "B5", f"=INDEX({srange},{S_VERDICT},{isel})",
         font=Font(bold=True, size=14), align=CENTER)
    _set(db, "A6", "Score / 100", font=B, fill=GREYFILL, align=CENTER)
    _set(db, "B6", f"=INDEX({srange},{S_TOTAL},{isel})",
         font=Font(bold=True, size=14), align=CENTER)
    _set(db, "C5", "Closest archetype", font=B, fill=GREYFILL, align=CENTER)
    _set(db, "C6", f'=IF(INDEX({drange},{MROW["is_development"]},{isel})=1,'
                   f'"Hamburg (Development)","Springfield (Income/Core)")',
         font=B, align=CENTER)
    _verdict_cf(db, "B5")

    # comparison table header
    r0 = 8
    _set(db, f"A{r0}", "Metric", font=H, fill=HEADFILL, align=LEFT)
    _set(db, f"B{r0}", "Selected deal", font=H, fill=HEADFILL, align=CENTER)
    for k, bc in enumerate(bench_cols):
        _set(db, f"{get_column_letter(3+k)}{r0}", f"=Deals!{bc}1", font=H, fill=HEADFILL, align=CENTER)

    show = ["deal_type", "total_cost", "equity", "debt", "ltv", "going_in_cap", "exit_cap",
            "noi", "opex_ratio", "yield_on_cost", "dev_spread", "unlevered_irr", "levered_irr",
            "nrsf", "market_population", "market_pop_growth_5yr", "market_pipeline_pct",
            "market_rank", "best_irr"]
    kind_of = {f: k for f, _, k in METRICS}
    label_of = {f: l for f, l, _ in METRICS}
    for i, field in enumerate(show):
        r = r0 + 1 + i
        mr = MROW[field]
        fmt = FMT.get(kind_of[field])
        _set(db, f"A{r}", label_of[field], font=B, fill=GREYFILL, align=LEFT)
        _set(db, f"B{r}", f"=INDEX({drange},{mr},{isel})", fmt=fmt, align=CENTER)
        for k, bc in enumerate(bench_cols):
            _set(db, f"{get_column_letter(3+k)}{r}", f"=Deals!{bc}{mr}", fmt=fmt, align=CENTER)

    # gate breakdown
    g0 = r0 + len(show) + 3
    _set(db, f"A{g0}", "Gate", font=H, fill=HEADFILL, align=LEFT)
    _set(db, f"B{g0}", "Points (selected)", font=H, fill=HEADFILL, align=CENTER)
    _set(db, f"C{g0}", "Max", font=H, fill=HEADFILL, align=CENTER)
    weights = {2: 15, 3: 15, 4: 10, 5: 12, 6: 10, 7: 10, 8: 13, 9: 8, 10: 7}
    for i, (label, sr) in enumerate(SCORE_ROWS):
        r = g0 + 1 + i
        _set(db, f"A{r}", label, font=B, fill=GREYFILL, align=LEFT)
        _set(db, f"B{r}", f"=INDEX({srange},{sr},{isel})", align=CENTER)
        _set(db, f"C{r}", weights[sr], align=CENTER)
        db.conditional_formatting.add(f"B{r}", CellIsRule(operator="greaterThanOrEqual",
            formula=[f"C{r}"], fill=PatternFill("solid", fgColor=GREEN)))
        db.conditional_formatting.add(f"B{r}", CellIsRule(operator="equal",
            formula=["0"], fill=PatternFill("solid", fgColor=RED)))

    # dropdown data validation (named range for reliability)
    names_ref = f"Deals!$B$1:${last_letter}$1"
    dv = DataValidation(type="list", formula1=names_ref, allow_blank=False)
    dv.error = "Pick a deal from the list"; dv.prompt = "Choose a deal to evaluate"
    db.add_data_validation(dv)
    dv.add(db["B3"])


def _build_ranking(rk, deals, cols):
    _set(rk, "A1", "Go/No-Go Ranking — sort by Score (descending) to rank candidates",
         font=B, border=False)
    hdr = 3
    for j, t in enumerate(["Deal", "Type", "Score", "Verdict"]):
        _set(rk, f"{get_column_letter(1+j)}{hdr}", t, font=H, fill=HEADFILL, align=CENTER)
    for i, (deal, c) in enumerate(zip(deals, cols)):
        r = hdr + 1 + i
        _set(rk, f"A{r}", f"=Deals!{c}1", align=LEFT)
        _set(rk, f"B{r}", deal.deal_type, align=LEFT)
        _set(rk, f"C{r}", f"=Scores!{c}{S_TOTAL}", align=CENTER)
        _set(rk, f"D{r}", f"=Scores!{c}{S_VERDICT}", font=B, align=CENTER)
    _verdict_cf(rk, f"D{hdr+1}:D{hdr+len(deals)}")
    rk.column_dimensions["A"].width = 22
    rk.column_dimensions["B"].width = 30
    for c in ("C", "D"):
        rk.column_dimensions[c].width = 16


def _build_market(ms, market: MarketRanking):
    headers = ["Rank", "State", "CBSA", "County / City", "Population", "5-yr Growth",
               "Pipeline %", "Op-ex", "Exit Cap", "Yield/Cost", "Dev Spread", "IRR", "Score"]
    keys = ["rank", "state", "cbsa", "county", "population", "growth_5yr", "pipeline",
            "opex", "exit_cap", "yield_on_cost", "dev_spread", "irr", "score"]
    fmts = {"Population": '#,##0', "5-yr Growth": '0.0%', "Pipeline %": '0.0%',
            "Op-ex": '0.0%', "Exit Cap": '0.0%', "Yield/Cost": '0.0%',
            "Dev Spread": '0.0%', "IRR": '0.0%', "Score": '0.000'}
    for j, hname in enumerate(headers):
        _set(ms, f"{get_column_letter(1+j)}1", hname, font=H, fill=HEADFILL, align=CENTER)
    for i, row in enumerate(market.top(60)):
        r = 2 + i
        for j, key in enumerate(keys):
            raw = row.get(COL[key], "")
            try:
                val = float(raw)
            except (TypeError, ValueError):
                val = raw
            _set(ms, f"{get_column_letter(1+j)}{r}", val,
                 fmt=fmts.get(headers[j]), align=CENTER if key != "county" else LEFT)
    widths = [6, 14, 30, 26, 12, 11, 11, 9, 9, 11, 11, 9, 9]
    for j, w in enumerate(widths):
        ms.column_dimensions[get_column_letter(1+j)].width = w
    ms.freeze_panes = "A2"


def _build_readme(rd):
    rd.sheet_view.showGridLines = False
    rd.column_dimensions["A"].width = 110
    lines = [
        ("INVESTMENT COMMITTEE — GO / NO-GO DASHBOARD", TITLE, HEADFILL),
        ("", None, None),
        ("How to use", B, GREYFILL),
        ("1. Open the Dashboard tab.", None, None),
        ("2. Pick a deal from the dropdown (cell B3). The verdict, comparison, and gate", None, None),
        ("   scores recalculate instantly against Springfield and Hamburg.", None, None),
        ("3. To evaluate a NEW pro forma, add a column on the Deals tab (copy a benchmark", None, None),
        ("   column and overwrite the inputs), or run:", None, None),
        ("       python -m deal_agent.ic.cli add --proforma NewDeal.xlsx --market <county>", None, None),
        ("", None, None),
        ("The two proven winners", B, GREYFILL),
        ("• Springfield (Income/Core DST): all-equity, ~7% going-in & exit cap, ~14% op-ex,", None, None),
        ("  ~11% IRR. Works because: durable in-place yield, no leverage or lease-up risk,", None, None),
        ("  predictable distributions — the conservative core benchmark.", None, None),
        ("• Hamburg (Development): ~40% LTV, ~7.4% stabilized yield-on-cost vs ~5.5% exit cap", None, None),
        ("  (~190 bps development spread), ~17% IRR. Works because: value is created at a yield", None, None),
        ("  well above the exit cap in a supply-constrained, growing market — the value-add benchmark.", None, None),
        ("", None, None),
        ("The gates (methodology)", B, GREYFILL),
        ("Critical (any fail ⇒ NO-GO): IRR > exit cap · stabilized yield ≥ 6.5% · population ≥ 200k.", None, None),
        ("Scored: op-ex ≤ 35% · positive 5-yr growth (pref ≥5%) · pipeline ≤ 10% (pref ≤5%) ·", None, None),
        ("IRR clears archetype target (Income ≥10% / Dev ≥15%) · market in upper half of ranking ·", None, None),
        ("project ~75k NRSF.  Score ≥ 70 = GO · 50–69 = CONDITIONAL GO · <50 or critical fail = NO-GO.", None, None),
        ("", None, None),
        ("Not investment advice. Verify all figures independently.", Font(italic=True), None),
    ]
    for i, (txt, font, fill) in enumerate(lines):
        c = _set(rd, f"A{i+1}", txt, font=font, fill=fill, align=LEFT, border=False)
        if fill is HEADFILL:
            rd.row_dimensions[i+1].height = 26
