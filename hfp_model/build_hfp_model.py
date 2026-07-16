#!/usr/bin/env python3
"""
HOUSE FACTORY PLATFORM (HFP) — MASTER PRO FORMA BUILDER
========================================================
Generates HFP_Master_Model.xlsx : a single integrated, fully dynamic,
institutional-grade operating model covering:
  Parent Platform / OKC launch factory / Standard Regional archetype /
  Regional rollout / Platform rollup / Development overlay hooks / Exit model.

DESIGN RULES (per management + IB modeling standards)
  1. Every driver lives ONCE on 'Global Assumptions' (named ranges). No
     hard-coded numbers anywhere downstream.
  2. Operating model first (EBITDA / cash), investment overlay last.
  3. Lease-only facilities. No land/building purchase. Base case = zero debt.
  4. Two region archetypes: OKC (asset contribution) and Standard (90/10,
     one raise, Factory 2 self-funded from retained earnings).
  5. Assumptions not present in ANY source file carry status
     '<<Management Input Required>>' with a transparent placeholder so the
     model still calculates; sourced items cite their source.
  6. No circular references. Tax uses closed-form NOL carryforward.

Sources reverse-engineered (see 'Cover & Sources' tab):
  S1 = House_Factory_Platform.xlsx           (org / fee / ownership structure)
  S2 = 07.08.26_19_Regional_Factory_Model.xlsx (v2.0 capacity, capital, exits)
  S3 = 07.08.26_21_Dev_Model_25_Markets.xlsx (downstream dev-fund; kit prices)
  S4 = HFP_Business_Model_Report.docx        (governing normalization doc)
  S5 = Management meeting transcript          (July 2026)
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.chart import LineChart, BarChart, Reference

# ----------------------------------------------------------------- constants
YRS = list(range(2026, 2037))            # 11 annual columns C..M
C0 = 3                                   # first year column = C
def YL(i): return get_column_letter(C0 + i)
YRNG = f"$C$4:${YL(len(YRS)-1)}$4"       # year header range on grid tabs

MIR = "<<Management Input Required>>"
CONF = "CONFIRMED"
DERV = "DERIVED"

# palette
NAVY   = "1F3864"; STEEL = "D6E4F0"; GOLD  = "FFF2CC"; ORANGE = "F8CBAD"
GREEN  = "E2EFDA"; GREY  = "F2F2F2"; RED   = "FCE4E4"
F_TITLE = Font(bold=True, size=14, color=NAVY)
F_SUB   = Font(italic=True, size=9, color="595959")
F_SEC   = Font(bold=True, color="FFFFFF")
F_HDR   = Font(bold=True, color=NAVY)
F_IN    = Font(color="0070C0", bold=True)          # inputs = blue (IB standard)
F_CALC  = Font(color="000000")
FILL_SEC  = PatternFill("solid", fgColor=NAVY)
FILL_HDR  = PatternFill("solid", fgColor=STEEL)
FILL_IN   = PatternFill("solid", fgColor=GOLD)
FILL_MIR  = PatternFill("solid", fgColor=ORANGE)
FILL_OK   = PatternFill("solid", fgColor=GREEN)
FILL_TOT  = PatternFill("solid", fgColor=GREY)
NUM  = '#,##0;(#,##0)'
NUM0 = '#,##0'
PCT  = '0.0%'
MULT = '0.00"x"'
USD  = '$#,##0;($#,##0)'

wb = openpyxl.Workbook()
wb.remove(wb.active)

def name_ref(nm, sheet, cell):
    wb.defined_names[nm] = DefinedName(nm, attr_text=f"'{sheet}'!${cell[0]}${cell[1:]}" if cell[0].isalpha() else None) if False else None
def define(nm, sheet, cell):
    wb.defined_names[nm] = DefinedName(nm, attr_text=f"'{sheet}'!{cell}")

def put(ws, r, c, v, font=None, fill=None, fmt=None, align=None):
    cell = ws.cell(row=r, column=c, value=v)
    if font: cell.font = font
    if fill: cell.fill = fill
    if fmt:  cell.number_format = fmt
    if align: cell.alignment = Alignment(horizontal=align)
    return cell

def title(ws, text, note=""):
    put(ws, 1, 1, text, font=F_TITLE)
    if note: put(ws, 2, 1, note, font=F_SUB)

def sec(ws, r, text, width=13):
    put(ws, r, 1, text, font=F_SEC, fill=FILL_SEC)
    for c in range(2, width+1):
        ws.cell(row=r, column=c).fill = FILL_SEC

def yearhdr(ws, r=4, label="($ unless noted)"):
    put(ws, r, 1, label, font=F_HDR, fill=FILL_HDR)
    put(ws, r, 2, "", fill=FILL_HDR)
    for i, y in enumerate(YRS):
        put(ws, r, C0+i, y, font=F_HDR, fill=FILL_HDR, fmt='0', align="center")

def yrow(ws, r, label, formula_fn, fmt=NUM, font=F_CALC, indent=0, fill=None):
    """Write a label + one formula per year column. formula_fn(i, col_letter)->str"""
    put(ws, r, 1, ("    "*indent)+label)
    for i, y in enumerate(YRS):
        cl = YL(i)
        put(ws, r, C0+i, formula_fn(i, cl), font=font, fill=fill, fmt=fmt)

def widen(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

T = "(C$4-Model_Start)"        # elapsed-years exponent term used everywhere

# =====================================================================
# TAB 2 — GLOBAL ASSUMPTIONS  (built first: everything references it)
# =====================================================================
ga = wb.create_sheet("Global Assumptions")
title(ga, "HOUSE FACTORY PLATFORM — GLOBAL ASSUMPTIONS",
      "Single source of truth. Blue+gold = input. Orange = "+MIR+" (placeholder; model runs, value must be confirmed). Every downstream formula references these named cells.")
put(ga, 3, 1, "Assumption", font=F_HDR, fill=FILL_HDR); put(ga, 3, 2, "Value", font=F_HDR, fill=FILL_HDR)
put(ga, 3, 3, "Unit", font=F_HDR, fill=FILL_HDR); put(ga, 3, 4, "Status", font=F_HDR, fill=FILL_HDR)
put(ga, 3, 5, "Source / rationale", font=F_HDR, fill=FILL_HDR)

GA = {}   # name -> row
def ga_row(r, label, value, unit, status, source, nm=None, fmt=NUM, formula=False):
    put(ga, r, 1, label)
    v = put(ga, r, 2, value, fmt=fmt)
    if status == MIR:
        v.font, v.fill = F_IN, FILL_MIR
    elif formula:
        v.font = F_CALC
    else:
        v.font, v.fill = F_IN, FILL_IN
    put(ga, r, 3, unit)
    s = put(ga, r, 4, status)
    if status == MIR: s.fill = FILL_MIR
    put(ga, r, 5, source)
    if nm:
        define(nm, "Global Assumptions", f"$B${r}")
        GA[nm] = r

sec(ga, 4, "1. TIMING & STRUCTURE", 5)
ga_row(5,  "Model start year", 2026, "yr", CONF, "S5 transcript / S2: OKC + Factory #1 anchor 2026", "Model_Start", '0')
ga_row(6,  "Forecast horizon", 11, "yrs", CONF, "2026-2036 covers full rollout + Y10 exit (S2)", None, '0')
ga_row(7,  "Exit year (Y10 convention)", 2036, "yr", CONF, "S2 '§1202 Exit': anchor 2026 → Y10 exit 2036; 10× EBITDA", "Exit_Year", '0')
ga_row(8,  "Number of regions", 5, "#", CONF, "S1 org chart; S4 §1: 'approximately five' regions", "N_Regions", '0')
ga_row(9,  "Factories per region (base case)", 2, "#", CONF, "S5: 'let's just do two factories in each region'; S4 §13", None, '0')

sec(ga, 11, "2. PLATFORM ECONOMICS", 5)
ga_row(12, "Management / admin fee (% regional revenue)", 0.07, "%", CONF, "S5 + S4 Table 1: 7% of regional revenue, a scenario lever", "MgmtFee_Pct", fmt=PCT)
ga_row(13, "Platform ownership — standard region", 0.10, "%", CONF, "S5 + S4 Table 3: ~10% retained for no cash", "Plat_Own", fmt=PCT)
ga_row(14, "Investor ownership — standard region", 0.90, "%", CONF, "S5 + S4 Table 3: ~90% common for cash", "Inv_Own", fmt=PCT)
ga_row(15, "Parent split — Lance-related entity", 0.60, "%", CONF, "S4 §22.A.1: 60/40 (resolves 16% mis-transcription in S5)", "Lance_Pct", fmt=PCT)
ga_row(16, "Parent split — USPD / USEDC", 0.40, "%", CONF, "S4 Table 2", "USPD_Pct", fmt=PCT)
ga_row(17, "Investor preferred return (cumulative)", 0.08, "%", CONF, "S2 'Regional Factory Fund': 8% cumulative compounded", "Pref_Rate", fmt=PCT)
ga_row(18, "GP / Platform promote", 0.20, "%", CONF, "S2 + S5: 20%, 100% catch-up, 80/20 residual", "Promote_Pct", fmt=PCT)
ga_row(19, "Platform fee-stream exit multiple", 10, "x", MIR, "Placeholder = regional 10x (S2). Capital-light fee streams often price higher — management to set", "Plat_Fee_Mult", '0.0"x"')

sec(ga, 21, "3. REGIONAL CAPITALIZATION (STANDARD REGION — one raise only)", 5)
ga_row(22, "Standard region equity raise", 30000000, "$", CONF, "S4 §10 / S5: $25-30M range, indexed to inflation at each launch (S4 §10). $30M (top of range) REQUIRED by liquidity validation: at $25M the region breaches minimum cash before Factory 2 self-funds — see Regional Rollup checks", "Region_Raise", USD)
ga_row(23, "Production equipment per factory", 12000000, "$", MIR, "Split of raise not in sources. Needed to size CapEx/depreciation. From founders' factory pro forma (not provided)", "Equip_Cost", USD)
ga_row(24, "Leasehold improvements per factory", 5000000, "$", MIR, "Fit-out of leased shell. Lease-only policy per S5/S4 — no building purchase", "Leasehold_Cost", USD)
ga_row(25, "Pre-opening / startup cost per factory", 2000000, "$", MIR, "Hiring, training, line commissioning. Expensed in open year", "Startup_Cost", USD)
ga_row(26, "Facility lease per factory / yr", 1200000, "$", MIR, "S4 §22.A.12: lease terms required. Placeholder ≈150k sf @ $8 NNN", "Lease_Cost", USD)

sec(ga, 28, "4. FACTORY OPERATIONS", 5)
ga_row(29, "Nameplate capacity — single shift", 500, "u/yr", CONF, "S2 deployment schedules: 500 u/yr standard (anchors 700; 2-shift up to 1,400)", "Factory_Capacity", '0')
ga_row(30, "Ramp — Year 1 (% of nameplate)", 0.50, "%", DERV, "S4 §22.B: 'Yr1 ~50-60%'; consistent w/ S2 EBITDA ramp $2M→$6M→$12M", "Ramp_Y1", fmt=PCT)
ga_row(31, "Ramp — Year 2", 0.80, "%", DERV, "Interpolated to hit S2 Y2 EBITDA ~$6M; cash-positive ~Y2 (S4/S5)", "Ramp_Y2", fmt=PCT)
ga_row(32, "Ramp — Year 3+", 1.00, "%", CONF, "S2: steady state Y3+", "Ramp_Y3", fmt=PCT)
ga_row(33, "Steady-state utilization (of 1-shift nameplate)", 1.00, "%", MIR, "1.0 = full single shift. >1.0 models partial 2nd shift (S2: 2-shift cap 700-1,400)", "Util_Steady", fmt=PCT)
ga_row(34, "OKC Year-1 ramp (relaunch, existing plant)", 0.60, "%", MIR, "S2: OKC plant 'already operational'; S4: relaunch. Faster than greenfield — confirm", "OKC_Ramp_Y1", fmt=PCT)
ga_row(35, "Monthly ramp to full rate (months)", 18, "mo", MIR, "Drives monthly view only; annual model uses Y1/Y2/Y3 ramp", "Ramp_Months", '0')

sec(ga, 37, "5. PRODUCT & PRICING (factory-wholesale, home-only — see S4 price-scope bridge)", 5)
ga_row(38, "ASP — single-section home", 85000, "$", CONF, "S5/S4 §5: ~$85K preliminary factory wholesale, home-only", "ASP_Single", USD)
ga_row(39, "ASP — 3-bedroom home", 175000, "$", CONF, "S5/S4 §5: ~$175K preliminary", "ASP_3BR", USD)
ga_row(40, "Product mix — % single-section", 0.70, "%", MIR, "No factory sales mix in sources. Placeholder = S3 Dev Model 70/30 unit mix analog", "Mix_Single", fmt=PCT)
ga_row(41, "Blended ASP (2026$)", "=Mix_Single*ASP_Single+(1-Mix_Single)*ASP_3BR", "$", DERV, "Calculated", "Blend_ASP0", USD, formula=True)
ga_row(42, "Avg sq ft — single-section", 800, "sf", MIR, "Needed for sq-ft KPIs & $/sf benchmarking vs competitors", "SqFt_Single", '0')
ga_row(43, "Avg sq ft — 3BR", 1400, "sf", MIR, "", "SqFt_3BR", '0')
ga_row(44, "Blended avg sq ft", "=Mix_Single*SqFt_Single+(1-Mix_Single)*SqFt_3BR", "sf", DERV, "Calculated", "Avg_SqFt", '0', formula=True)

sec(ga, 46, "6. COST OF GOODS SOLD (founders' factory pro forma NOT provided — all placeholders calibrated to S2's ~$12M steady-state factory EBITDA)", 5)
ga_row(47, "Materials (% of revenue)", 0.47, "%", MIR, "From founders' cost-per-sq-ft model (S4 App.C — not provided)", "Mat_Pct", fmt=PCT)
ga_row(48, "Direct labor (% of revenue)", 0.15, "%", MIR, "", "Lab_Pct", fmt=PCT)
ga_row(49, "Freight / delivery (% of revenue)", 0.04, "%", MIR, "Confirm whether freight sits in region or separate entity (S4 §22.A.9)", "Frt_Pct", fmt=PCT)
ga_row(50, "Other variable mfg — utilities, maint., consumables (%)", 0.04, "%", MIR, "", "VarMfg_Pct", fmt=PCT)
ga_row(51, "Total variable cost (% of revenue)", "=Mat_Pct+Lab_Pct+Frt_Pct+VarMfg_Pct", "%", DERV, "Calculated", "Var_Pct", PCT, formula=True)
ga_row(52, "Fixed factory overhead ex-lease / factory / yr", 2000000, "$", MIR, "Plant mgmt, QC, fixed indirect labor, insurance", "Fixed_OH", USD)
ga_row(53, "Average fully-loaded factory wage", 70000, "$", MIR, "Drives headcount KPI only", "Avg_Wage", USD)

sec(ga, 55, "7. SG&A", 5)
ga_row(56, "Regional fixed SG&A / region / yr (ex-GM)", 1200000, "$", MIR, "Regional accounting, sales admin, insurance, IT (S1 org rows)", "Reg_SGA", USD)
ga_row(57, "Regional GM salary (one per region — S5)", 250000, "$", MIR, "S5: one GM runs both factories; bonus upside not modeled", "GM_Sal", USD)
ga_row(58, "Sales & marketing (% of regional revenue)", 0.015, "%", MIR, "", "SalesMkt_Pct", fmt=PCT)
ga_row(59, "CEO salary (Lance)", 400000, "$", MIR, "On OKC payroll until transition (S5/S4 §15)", "CEO_Sal", USD)
ga_row(60, "CFO salary", 300000, "$", MIR, "Platform payroll from transition year", "CFO_Sal", USD)
ga_row(61, "COO salary (Craig)", 350000, "$", MIR, "On OKC payroll until transition", "COO_Sal", USD)
ga_row(62, "National Sales lead", 250000, "$", MIR, "S1 org chart role", "NatSales_Sal", USD)
ga_row(63, "National Marketing lead", 200000, "$", MIR, "S1 org chart role", "NatMktg_Sal", USD)
ga_row(64, "Platform exec payroll (total)", "=SUM(B59:B63)", "$", DERV, "Calculated", "Plat_Payroll", USD, formula=True)
ga_row(65, "  ERP / production systems", 200000, "$", MIR, "Platform shared service (S4 §6)", "Opx_ERP", USD)
ga_row(66, "  Engineering / product design", 200000, "$", MIR, "", "Opx_Eng", USD)
ga_row(67, "  Insurance", 150000, "$", MIR, "", "Opx_Ins", USD)
ga_row(68, "  Accounting / audit", 100000, "$", MIR, "", "Opx_Acct", USD)
ga_row(69, "  Legal", 100000, "$", MIR, "", "Opx_Legal", USD)
ga_row(70, "  Professional fees", 100000, "$", MIR, "", "Opx_Prof", USD)
ga_row(71, "  IT", 100000, "$", MIR, "", "Opx_IT", USD)
ga_row(72, "  Travel", 50000, "$", MIR, "", "Opx_Trav", USD)
ga_row(73, "Platform other opex (fixed, total)", "=SUM(B65:B72)", "$", DERV, "Calculated", "Plat_Opex", USD, formula=True)
ga_row(74, "Platform variable opex (% consolidated revenue)", 0.005, "%", MIR, "Scales shared services with network size", "Plat_Opex_Pct", fmt=PCT)

sec(ga, 76, "8. WORKING CAPITAL & CAPEX", 5)
ga_row(77, "Accounts receivable days (DSO)", 15, "days", MIR, "Factory-wholesale to developers; confirm deposit policy", "DSO", '0')
ga_row(78, "Inventory days (DIO, on COGS)", 45, "days", MIR, "Raw material + WIP + finished goods", "DIO", '0')
ga_row(79, "Accounts payable days (DPO, on COGS)", 30, "days", MIR, "", "DPO", '0')
ga_row(80, "Maintenance capex (% of revenue)", 0.015, "%", MIR, "", "Maint_Pct", fmt=PCT)
ga_row(81, "Asset depreciable life (equipment & leasehold)", 10, "yrs", MIR, "Straight-line; matches lease term assumption. Depreciation is 100% derived from CapEx", "Equip_Life", '0')

sec(ga, 83, "9. TAX & MACRO", 5)
ga_row(84, "Federal corporate tax rate", 0.21, "%", CONF, "Statutory. Tax paid at regional C-corp level; no dividends (S5/S4)", "Fed_Tax", fmt=PCT)
ga_row(85, "Blended state corporate rate", 0.04, "%", MIR, "Region-specific (OK/TX/etc.) — confirm per final region map", "State_Tax", fmt=PCT)
ga_row(86, "Combined cash tax rate", "=Fed_Tax+State_Tax", "%", DERV, "Calculated; applied with full NOL carryforward", "Tax_Rate", PCT, formula=True)
ga_row(87, "General inflation", 0.025, "%", MIR, "S4 §10 requires inflation on later launches — rate not specified", "Infl_Gen", fmt=PCT)
ga_row(88, "Wage inflation", 0.03, "%", MIR, "", "Infl_Wage", fmt=PCT)
ga_row(89, "Material inflation (pass-through assumed)", 0.025, "%", MIR, "Variable costs modeled as % of revenue ⇒ pass-through; shock via Sensitivity", "Infl_Mat", fmt=PCT)
ga_row(90, "ASP escalation", 0.02, "%", MIR, "", "Infl_ASP", fmt=PCT)

sec(ga, 92, "10. EXIT & VALUATION", 5)
ga_row(93, "Exit multiple — Y10 (EV / EBITDA)", 10, "x", CONF, "S2 'Regional Factory Fund': 10× Y10 EBITDA", "Exit_Mult", '0.0"x"')
ga_row(94, "Exit multiple — Y5 alternative", 8, "x", CONF, "S2 '§1202 Exit': 8× for shorter operating history", "Exit_Mult_Y5", '0.0"x"')
ga_row(95, "Discount rate (NPV)", 0.12, "%", MIR, "S5: no hurdle given ('well above whatever IRR hurdle'). Placeholder > 8% pref", "Disc_Rate", fmt=PCT)
ga_row(96, "QSBS federal rate avoided (LTCG+NIIT)", 0.238, "%", CONF, "S2: 23.8% (20% LTCG + 3.8% NIIT); 100% §1202 exclusion, per-investor caps apply", "QSBS_Rate", fmt=PCT)
ga_row(97, "Include region cash in exit equity value (1=yes)", 0, "flag", DERV, "0 matches S2 convention (value = multiple × EBITDA only). Set 1 for equity-value build-up", "Incl_Cash_Exit", '0')

sec(ga, 99, "11. OKC / HOUSE FACTORY CENTRAL (special launch capitalization)", 5)
ga_row(100, "Founder contributed assets (lifts, mfg equipment, IP)", 8000000, "$", MIR, "S4 §22.A.6: independent appraisal REQUIRED. Placeholder pending valuation", "OKC_Asset_Val", USD)
ga_row(101, "OKC new investor cash", 20000000, "$", MIR, "S5: OKC total 'might be 20' vs $30M standard. Placeholder $12M cash + $8M assets = $20M", "OKC_Cash", USD)
ga_row(102, "OKC total capitalization", "=OKC_Asset_Val+OKC_Cash", "$", DERV, "Calculated", "OKC_TotCap", USD, formula=True)
ga_row(103, "OKC Platform ownership (pro-rata to contribution)", "=OKC_Asset_Val/OKC_TotCap", "%", DERV, "Structure per S4 §9: split follows independently supported values. Pro-rata placeholder", "OKC_Plat_Own", PCT, formula=True)
ga_row(104, "OKC investor ownership", "=OKC_Cash/OKC_TotCap", "%", DERV, "Calculated", "OKC_Inv_Own", PCT, formula=True)
ga_row(105, "OKC plant modernization capex", 10000000, "$", CONF, "S2 South Central: '$12M raise = $10M modernization + reserve'", "OKC_Modern", USD)

widen(ga, {"A": 52, "B": 16, "C": 7, "D": 30, "E": 95})
ga.freeze_panes = "A4"

# =====================================================================
# TAB 3 — FACTORY ROLLOUT SCHEDULE
# =====================================================================
ro = wb.create_sheet("Factory Rollout")
title(ro, "TAB 3 — FACTORY ROLLOUT SCHEDULE",
      "Opening years are INPUTS (gold), sequenced to S4 §21 roadmap: OKC 2026 → new region each 1-2 yrs; Factory 2 opens ~2 yrs after Factory 1 once cash-flow positive. "
      "Region names beyond Central/Texas are placeholders pending management's final region map (S4 §22.A.2).")
hdrs = ["Factory #","Region","Region #","Factory-in-Region","Opening Year (INPUT)","Capacity (u/yr, 1-shift)",
        "Capital Required ($)","Annual Lease Cost ($)","Equipment + Leasehold Investment ($)","Steady Direct FTEs","Y1 Ramp","Status","Funding Source"]
for j,h in enumerate(hdrs, start=1):
    put(ro, 4, j, h, font=F_HDR, fill=FILL_HDR)
FACTORIES = [
    (1, "Central (OKC)", 1, 1, 2026, "Founder assets + investor cash (special)"),
    (2, "Central (OKC)", 1, 2, 2029, "Retained earnings — no new raise"),
    (3, "Region 2 — East/Plains "+MIR, 2, 1, 2027, "Single 90/10 equity raise"),
    (4, "Region 2 — East/Plains "+MIR, 2, 2, 2030, "Retained earnings — no new raise"),
    (5, "Region 3 — Texas (DFW)", 3, 1, 2028, "Single 90/10 equity raise"),
    (6, "Region 3 — Texas (Houston)", 3, 2, 2031, "Retained earnings — no new raise"),
    (7, "Region 4 — "+MIR, 4, 1, 2030, "Single 90/10 equity raise"),
    (8, "Region 4 — "+MIR, 4, 2, 2033, "Retained earnings — no new raise"),
    (9, "Region 5 — "+MIR, 5, 1, 2031, "Single 90/10 equity raise"),
    (10,"Region 5 — "+MIR, 5, 2, 2034, "Retained earnings — no new raise"),
]
for f, rn, ridx, fir, oy, fund in FACTORIES:
    r = 5 + f
    put(ro, r, 1, f, fmt='0')
    put(ro, r, 2, rn)
    put(ro, r, 3, ridx, fmt='0')
    put(ro, r, 4, fir, fmt='0')
    put(ro, r, 5, oy, font=F_IN, fill=FILL_IN, fmt='0')
    put(ro, r, 6, "=Factory_Capacity", fmt=NUM0)
    if f == 1:
        put(ro, r, 7, "=OKC_Modern+OKC_Asset_Val", fmt=USD)   # capital deployed at OKC F1
    elif fir == 1:
        put(ro, r, 7, "=(Equip_Cost+Leasehold_Cost+Startup_Cost)*(1+Infl_Gen)^($E{}-Model_Start)".format(r), fmt=USD)
    else:
        put(ro, r, 7, "=(Equip_Cost+Leasehold_Cost+Startup_Cost)*(1+Infl_Gen)^($E{}-Model_Start)".format(r), fmt=USD)
    put(ro, r, 8, "=Lease_Cost*(1+Infl_Gen)^($E{}-Model_Start)".format(r), fmt=USD)
    put(ro, r, 9, ("=OKC_Modern" if f==1 else "=(Equip_Cost+Leasehold_Cost)*(1+Infl_Gen)^($E{}-Model_Start)".format(r)), fmt=USD)
    put(ro, r, 10, "=ROUND(Factory_Capacity*Util_Steady*Blend_ASP0*Lab_Pct/Avg_Wage,0)", fmt=NUM0)
    put(ro, r, 11, ("=OKC_Ramp_Y1" if f==1 else "=Ramp_Y1"), fmt=PCT)
    put(ro, r, 12, f'=IF($E{r}<=Model_Start,"Operational (launch)","Opens "&$E{r})')
    put(ro, r, 13, fund)
# factory count / active regions by year
put(ro, 18, 1, "NETWORK BY YEAR", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): ro.cell(row=18, column=c).fill = FILL_SEC
put(ro, 19, 1, "Year", font=F_HDR, fill=FILL_HDR)
for i, y in enumerate(YRS): put(ro, 19, C0+i, y, font=F_HDR, fill=FILL_HDR, fmt='0')
put(ro, 20, 1, "Operational factories")
put(ro, 21, 1, "Active regions")
for i, y in enumerate(YRS):
    cl = YL(i)
    put(ro, 20, C0+i, f"=SUMPRODUCT(($E$6:$E$15<={cl}$19)*1)", fmt='0')
    put(ro, 21, C0+i, f"=SUMPRODUCT(($D$6:$D$15=1)*($E$6:$E$15<={cl}$19))", fmt='0')
put(ro, 23, 1, "Management transition year (platform payroll starts — first year network ≥ 2 factories, per S5/S4 §15)")
put(ro, 23, 2, '=INDEX($C$19:$M$19,COUNTIF($C$20:$M$20,"<2")+1)', font=F_CALC, fmt='0')
define("Trans_Year", "Factory Rollout", "$B$23")
widen(ro, {"A":10,"B":34,"C":9,"D":15,"E":18,"F":20,"G":22,"H":18,"I":30,"J":16,"K":9,"L":20,"M":38})

# =====================================================================
# TAB 4 — PRODUCTION MODEL
# =====================================================================
pm = wb.create_sheet("Production Model")
title(pm, "TAB 4 — PRODUCTION MODEL",
      "Units by factory driven by Rollout opening year x capacity x ramp curve (Global Assumptions). OKC uses its own Y1 ramp (relaunch). Monthly/quarterly ramp view below.")
yearhdr(pm)
put(pm, 5, 1, "Blended ASP ($/home, escalated)")
for i, y in enumerate(YRS):
    cl = YL(i)
    put(pm, 5, C0+i, f"=Blend_ASP0*(1+Infl_ASP)^({cl}$4-Model_Start)", fmt=USD)
put(pm, 7, 1, "HOMES PRODUCED BY FACTORY (units)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): pm.cell(row=7, column=c).fill = FILL_SEC
for f, rn, ridx, fir, oy, fund in FACTORIES:
    r = 7 + f            # rows 8..17
    ror = 5 + f          # rollout row
    put(pm, r, 1, f"F#{f} — {rn.replace(MIR,'TBC')}")
    put(pm, r, 2, f, fmt='0')
    for i, y in enumerate(YRS):
        cl = YL(i)
        ramp1 = "OKC_Ramp_Y1" if f == 1 else "Ramp_Y1"
        put(pm, r, C0+i,
            f"=IF({cl}$4<'Factory Rollout'!$E{ror},0,Factory_Capacity*Util_Steady*"
            f"IF({cl}$4-'Factory Rollout'!$E{ror}=0,{ramp1},"
            f"IF({cl}$4-'Factory Rollout'!$E{ror}=1,Ramp_Y2,Ramp_Y3)))", fmt=NUM0)
yrow(pm, 18, "TOTAL HOMES PRODUCED", lambda i, cl: f"=SUM({cl}8:{cl}17)", fmt=NUM0, font=F_HDR, fill=FILL_TOT)
yrow(pm, 19, "Cumulative homes", lambda i, cl: f"=SUM($C$18:{cl}18)", fmt=NUM0)
yrow(pm, 21, "Operational nameplate capacity (1-shift)", lambda i, cl: f"='Factory Rollout'!{cl}20*Factory_Capacity", fmt=NUM0)
yrow(pm, 22, "Capacity utilization", lambda i, cl: f"=IF({cl}21=0,0,{cl}18/{cl}21)", fmt=PCT)
yrow(pm, 24, "Square feet produced", lambda i, cl: f"={cl}18*Avg_SqFt", fmt=NUM0)
yrow(pm, 25, "Revenue generated (memo — see Revenue Model)", lambda i, cl: f"={cl}18*{cl}$5", fmt=USD)

put(pm, 28, 1, "MONTHLY RAMP VIEW — STANDARD FACTORY, MONTHS 1-36 (linear ramp to full rate over Ramp_Months; reconciliation to annual ramp shown)", font=F_SEC, fill=FILL_SEC)
put(pm, 29, 1, "Month", font=F_HDR)
put(pm, 30, 1, "Utilization %")
put(pm, 31, 1, "Homes / month")
put(pm, 32, 1, "Cumulative homes")
for m in range(1, 37):
    c = 2 + m
    cl = get_column_letter(c)
    put(pm, 29, c, m, fmt='0', font=F_HDR)
    put(pm, 30, c, f"=MIN(1,{cl}29/Ramp_Months)*Util_Steady", fmt=PCT)
    put(pm, 31, c, f"=Factory_Capacity/12*{cl}30", fmt='0.0')
    put(pm, 32, c, f"=SUM($C$31:{cl}31)", fmt='0.0')
put(pm, 34, 1, "Quarter", font=F_HDR)
put(pm, 35, 1, "Homes / quarter")
for q in range(1, 13):
    c = 2 + q
    c1 = get_column_letter(3*q); c2 = get_column_letter(2 + 3*q)
    put(pm, 34, c, f"Q{q}", font=F_HDR)
    put(pm, 35, c, f"=SUM({c1}31:{c2}31)", fmt='0.0')
put(pm, 37, 1, "Monthly-view Year-1 homes vs annual model (Ramp_Y1 x capacity) — variance flags calibration of Ramp_Months vs Ramp_Y1:")
put(pm, 37, 8, "=SUM(C31:N31)-Factory_Capacity*Util_Steady*Ramp_Y1", fmt=NUM)
widen(pm, {"A": 44, "B": 6})
pm.freeze_panes = "C5"

# =====================================================================
# TAB 5 — REVENUE MODEL
# =====================================================================
rv = wb.create_sheet("Revenue Model")
title(rv, "TAB 5 — REVENUE MODEL",
      "Revenue by factory, region, product type; platform management fee; intercompany elimination. Consolidated revenue = external (regional) sales only.")
yearhdr(rv)
put(rv, 5, 1, "REVENUE BY FACTORY", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): rv.cell(row=5, column=c).fill = FILL_SEC
for f, rn, ridx, fir, oy, fund in FACTORIES:
    r = 5 + f            # rows 6..15
    put(rv, r, 1, f"F#{f} — {rn.replace(MIR,'TBC')}")
    for i, y in enumerate(YRS):
        cl = YL(i)
        put(rv, r, C0+i, f"='Production Model'!{cl}{f+7}*'Production Model'!{cl}$5", fmt=USD)
put(rv, 16, 1, "REVENUE BY REGION", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): rv.cell(row=16, column=c).fill = FILL_SEC
REGIONS = ["Central (OKC)", "Region 2 — East/Plains (TBC)", "Region 3 — Texas", "Region 4 (TBC)", "Region 5 (TBC)"]
for rg in range(1, 6):
    r = 16 + rg          # rows 17..21
    f1r, f2r = 4 + 2*rg, 5 + 2*rg    # factory revenue rows
    put(rv, r, 1, f"Region {rg} — {REGIONS[rg-1]}")
    for i, y in enumerate(YRS):
        cl = YL(i)
        put(rv, r, C0+i, f"={cl}{f1r}+{cl}{f2r}", fmt=USD)
yrow(rv, 23, "TOTAL REGIONAL REVENUE (external)", lambda i, cl: f"=SUM({cl}17:{cl}21)", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(rv, 24, "Platform management fee revenue (7% lever)", lambda i, cl: f"=MgmtFee_Pct*{cl}23", fmt=USD)
yrow(rv, 25, "Intercompany elimination", lambda i, cl: f"=-{cl}24", fmt=USD)
yrow(rv, 26, "CONSOLIDATED REVENUE", lambda i, cl: f"={cl}23+{cl}24+{cl}25", fmt=USD, font=F_HDR, fill=FILL_TOT)
put(rv, 28, 1, "REVENUE BY PRODUCT TYPE", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): rv.cell(row=28, column=c).fill = FILL_SEC
yrow(rv, 29, "Single-section homes", lambda i, cl: f"='Production Model'!{cl}18*Mix_Single*ASP_Single*(1+Infl_ASP)^({cl}$4-Model_Start)", fmt=USD)
yrow(rv, 30, "3-bedroom homes", lambda i, cl: f"='Production Model'!{cl}18*(1-Mix_Single)*ASP_3BR*(1+Infl_ASP)^({cl}$4-Model_Start)", fmt=USD)
yrow(rv, 31, "Check: product split ties to total (=0)", lambda i, cl: f"={cl}29+{cl}30-{cl}23", fmt=NUM)
widen(rv, {"A": 44})
rv.freeze_panes = "C5"

# =====================================================================
# TAB 6 — COGS
# =====================================================================
cg = wb.create_sheet("COGS")
title(cg, "TAB 6 — COST OF GOODS SOLD",
      "Variable costs are % of revenue (materials pass-through); fixed factory overhead + lease inflate with general inflation and switch on per operational factory. "
      "All rates are "+MIR+" placeholders calibrated so a steady-state factory produces ~$12M pre-fee EBITDA (S2 anchor).")
yearhdr(cg)
put(cg, 5, 1, "COGS BY REGION", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): cg.cell(row=5, column=c).fill = FILL_SEC
for rg in range(1, 6):
    r = 5 + rg           # rows 6..10
    put(cg, r, 1, f"Region {rg} — {REGIONS[rg-1]}")
    for i, y in enumerate(YRS):
        cl = YL(i)
        put(cg, r, C0+i,
            f"='Revenue Model'!{cl}{16+rg}*Var_Pct+"
            f"SUMPRODUCT(('Factory Rollout'!$C$6:$C$15={rg})*('Factory Rollout'!$E$6:$E$15<={cl}$4))"
            f"*(Fixed_OH+Lease_Cost)*(1+Infl_Gen)^({cl}$4-Model_Start)", fmt=USD)
yrow(cg, 12, "TOTAL COGS", lambda i, cl: f"=SUM({cl}6:{cl}10)", fmt=USD, font=F_HDR, fill=FILL_TOT)
put(cg, 14, 1, "COGS BY COMPONENT (consolidated)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): cg.cell(row=14, column=c).fill = FILL_SEC
yrow(cg, 15, "Materials", lambda i, cl: f"=Mat_Pct*'Revenue Model'!{cl}23", fmt=USD)
yrow(cg, 16, "Direct labor", lambda i, cl: f"=Lab_Pct*'Revenue Model'!{cl}23", fmt=USD)
yrow(cg, 17, "Freight / delivery", lambda i, cl: f"=Frt_Pct*'Revenue Model'!{cl}23", fmt=USD)
yrow(cg, 18, "Utilities, equipment maintenance & consumables", lambda i, cl: f"=VarMfg_Pct*'Revenue Model'!{cl}23", fmt=USD)
yrow(cg, 19, "Total variable costs", lambda i, cl: f"=SUM({cl}15:{cl}18)", fmt=USD, font=F_HDR)
yrow(cg, 20, "Fixed factory overhead (ex-lease)", lambda i, cl: f"='Factory Rollout'!{cl}20*Fixed_OH*(1+Infl_Gen)^({cl}$4-Model_Start)", fmt=USD)
yrow(cg, 21, "Facility leases", lambda i, cl: f"='Factory Rollout'!{cl}20*Lease_Cost*(1+Infl_Gen)^({cl}$4-Model_Start)", fmt=USD)
yrow(cg, 22, "Total fixed costs", lambda i, cl: f"={cl}20+{cl}21", fmt=USD, font=F_HDR)
yrow(cg, 23, "Check: components tie to regional COGS (=0)", lambda i, cl: f"={cl}19+{cl}22-{cl}12", fmt=NUM)
yrow(cg, 25, "GROSS PROFIT", lambda i, cl: f"='Revenue Model'!{cl}23-{cl}12", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(cg, 26, "Gross margin %", lambda i, cl: f"=IF('Revenue Model'!{cl}23=0,0,{cl}25/'Revenue Model'!{cl}23)", fmt=PCT)
widen(cg, {"A": 46})
cg.freeze_panes = "C5"

# =====================================================================
# TAB 7 — SG&A
# =====================================================================
sg = wb.create_sheet("SG&A")
title(sg, "TAB 7 — SG&A",
      "Regional SG&A per region + platform overhead. OKC carries CEO+COO salaries until the transition year (network ≥2 factories), then they move to Platform payroll "
      "and OKC hires a GM behind them (S5 / S4 §15) — salaries are never double-counted. Pre-opening costs expensed in each factory's opening year.")
yearhdr(sg)
put(sg, 5, 1, "SG&A BY REGION", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): sg.cell(row=5, column=c).fill = FILL_SEC
for rg in range(1, 6):
    r = 5 + rg
    f1ror, f2ror = 4 + 2*rg, 5 + 2*rg    # rollout rows of F1 / F2 of region rg
    put(sg, r, 1, f"Region {rg} — {REGIONS[rg-1]}")
    for i, y in enumerate(YRS):
        cl = YL(i)
        t = f"({cl}$4-Model_Start)"
        if rg == 1:
            staff = f"IF({cl}$4<Trans_Year,(CEO_Sal+COO_Sal),GM_Sal)*(1+Infl_Wage)^{t}"
        else:
            staff = f"GM_Sal*(1+Infl_Wage)^{t}"
        put(sg, r, C0+i,
            f"=IF({cl}$4>='Factory Rollout'!$E${f1ror},Reg_SGA*(1+Infl_Gen)^{t}+{staff},0)"
            f"+SalesMkt_Pct*'Revenue Model'!{cl}{16+rg}"
            f"+Startup_Cost*(1+Infl_Gen)^{t}*(({cl}$4='Factory Rollout'!$E${f1ror})+({cl}$4='Factory Rollout'!$E${f2ror}))", fmt=USD)
yrow(sg, 11, "Total regional SG&A", lambda i, cl: f"=SUM({cl}6:{cl}10)", fmt=USD, font=F_HDR, fill=FILL_TOT)
put(sg, 13, 1, "PLATFORM OVERHEAD", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): sg.cell(row=13, column=c).fill = FILL_SEC
yrow(sg, 14, "Platform executive payroll (CEO, CFO, COO, Nat'l Sales, Nat'l Mktg)",
     lambda i, cl: f"=IF({cl}$4>=Trans_Year,Plat_Payroll*(1+Infl_Wage)^({cl}$4-Model_Start),0)", fmt=USD)
yrow(sg, 15, "Platform other opex (fixed + % of network revenue)",
     lambda i, cl: f"=Plat_Opex*(1+Infl_Gen)^({cl}$4-Model_Start)+Plat_Opex_Pct*'Revenue Model'!{cl}23", fmt=USD)
yrow(sg, 16, "Total platform overhead", lambda i, cl: f"={cl}14+{cl}15", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(sg, 18, "TOTAL CONSOLIDATED SG&A", lambda i, cl: f"={cl}11+{cl}16", fmt=USD, font=F_HDR, fill=FILL_TOT)
put(sg, 20, 1, "PLATFORM OPEX COMPONENTS (memo — each is an input on Global Assumptions)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): sg.cell(row=20, column=c).fill = FILL_SEC
comps = [("ERP / production systems","Opx_ERP"),("Engineering / product design","Opx_Eng"),("Insurance","Opx_Ins"),
         ("Accounting / audit","Opx_Acct"),("Legal","Opx_Legal"),("Professional fees","Opx_Prof"),("IT","Opx_IT"),("Travel","Opx_Trav")]
for k,(lbl,nm) in enumerate(comps):
    yrow(sg, 21+k, lbl, lambda i, cl, nm=nm: f"={nm}*(1+Infl_Gen)^({cl}$4-Model_Start)", fmt=USD, indent=1)
widen(sg, {"A": 60})
sg.freeze_panes = "C5"

# =====================================================================
# TAB 8 — PLATFORM REVENUE
# =====================================================================
pr = wb.create_sheet("Platform Revenue")
title(pr, "TAB 8 — PLATFORM REVENUE",
      "The compounding engine: 7% management fee scales with every factory added, with near-zero incremental platform cost; the 10%/negotiated equity stakes accrue value "
      "without cash outlay and are monetized at exit (Tab 20).")
yearhdr(pr)
put(pr, 5, 1, "MANAGEMENT FEE BY REGION", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): pr.cell(row=5, column=c).fill = FILL_SEC
for rg in range(1, 6):
    r = 5 + rg
    put(pr, r, 1, f"Region {rg} — {REGIONS[rg-1]}")
    for i, y in enumerate(YRS):
        cl = YL(i)
        put(pr, r, C0+i, f"=MgmtFee_Pct*'Revenue Model'!{cl}{16+rg}", fmt=USD)
yrow(pr, 12, "TOTAL MANAGEMENT FEE REVENUE", lambda i, cl: f"=SUM({cl}6:{cl}10)", fmt=USD, font=F_HDR, fill=FILL_TOT)
put(pr, 13, 1, "Administrative / other platform revenue")
for i, y in enumerate(YRS):
    v = put(pr, 13, C0+i, 0, fmt=USD, font=F_IN, fill=FILL_MIR)
put(pr, 13, 2, MIR)
yrow(pr, 14, "TOTAL PLATFORM REVENUE", lambda i, cl: f"={cl}12+{cl}13", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(pr, 16, "Memo: fee revenue per operational factory", lambda i, cl: f"=IF('Factory Rollout'!{cl}20=0,0,{cl}12/'Factory Rollout'!{cl}20)", fmt=USD)
put(pr, 18, 1, "EQUITY VALUE ACCRUAL (memo — non-cash; realized at exit)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): pr.cell(row=18, column=c).fill = FILL_SEC
yrow(pr, 19, "Platform share of regional net income (accrual)",
     lambda i, cl: f"=OKC_Plat_Own*'Regional Rollup'!{cl}16+Plat_Own*('Regional Rollup'!{cl}36+'Regional Rollup'!{cl}56+'Regional Rollup'!{cl}76+'Regional Rollup'!{cl}96)", fmt=USD)
yrow(pr, 20, "Cumulative accrued (memo)", lambda i, cl: f"=SUM($C$19:{cl}19)", fmt=USD)
widen(pr, {"A": 46})
pr.freeze_panes = "C5"

# =====================================================================
# TAB 9 — WORKING CAPITAL
# =====================================================================
wc = wb.create_sheet("Working Capital")
title(wc, "TAB 9 — WORKING CAPITAL",
      "AR/Inventory/AP on days conventions (all "+MIR+"). Regional NWC feeds each region's cash flow; consolidated equals sum of regions (uniform days).")
yearhdr(wc)
yrow(wc, 6, "Accounts receivable (DSO)", lambda i, cl: f"=DSO/365*'Revenue Model'!{cl}23", fmt=USD)
yrow(wc, 7, "Inventory (DIO on COGS)", lambda i, cl: f"=DIO/365*COGS!{cl}12", fmt=USD)
yrow(wc, 8, "Accounts payable (DPO on COGS)", lambda i, cl: f"=DPO/365*COGS!{cl}12", fmt=USD)
yrow(wc, 9, "NET WORKING CAPITAL", lambda i, cl: f"={cl}6+{cl}7-{cl}8", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(wc, 10, "Change in NWC (cash outflow +)", lambda i, cl: f"={cl}9" if i == 0 else f"={cl}9-{YL(i-1)}9", fmt=USD)
put(wc, 12, 1, "NWC BY REGION", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): wc.cell(row=12, column=c).fill = FILL_SEC
for rg in range(1, 6):
    r = 12 + rg          # 13..17
    put(wc, r, 1, f"Region {rg} NWC")
    for i, y in enumerate(YRS):
        cl = YL(i)
        put(wc, r, C0+i, f"=DSO/365*'Revenue Model'!{cl}{16+rg}+(DIO-DPO)/365*COGS!{cl}{5+rg}", fmt=USD)
put(wc, 18, 1, "ΔNWC BY REGION", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): wc.cell(row=18, column=c).fill = FILL_SEC
for rg in range(1, 6):
    r = 18 + rg          # 19..23
    put(wc, r, 1, f"Region {rg} ΔNWC")
    for i, y in enumerate(YRS):
        cl = YL(i)
        put(wc, r, C0+i, f"={cl}{12+rg}" if i == 0 else f"={cl}{12+rg}-{YL(i-1)}{12+rg}", fmt=USD)
yrow(wc, 25, "Check: Σ regional ΔNWC − consolidated ΔNWC (=0)", lambda i, cl: f"=SUM({cl}19:{cl}23)-{cl}10", fmt=NUM)
widen(wc, {"A": 46})
wc.freeze_panes = "C5"

# =====================================================================
# TAB 10 — CAPITAL EXPENDITURES
# =====================================================================
cx = wb.create_sheet("Capital Expenditures")
title(cx, "TAB 10 — CAPITAL EXPENDITURES",
      "Growth capex (equipment + leasehold improvements at each factory opening; OKC = $10M modernization), maintenance capex (% of revenue), and OKC founder asset "
      "contribution (non-cash). Lease-only policy: no land or building purchase anywhere (S5/S4).")
yearhdr(cx)
put(cx, 5, 1, "GROWTH / EXPANSION CAPEX BY REGION (cash)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): cx.cell(row=5, column=c).fill = FILL_SEC
for rg in range(1, 6):
    r = 5 + rg
    f1ror, f2ror = 4 + 2*rg, 5 + 2*rg
    put(cx, r, 1, f"Region {rg} — {REGIONS[rg-1]}")
    for i, y in enumerate(YRS):
        cl = YL(i)
        t = f"({cl}$4-Model_Start)"
        if rg == 1:
            f1 = f"IF({cl}$4='Factory Rollout'!$E${f1ror},OKC_Modern,0)"
        else:
            f1 = f"IF({cl}$4='Factory Rollout'!$E${f1ror},(Equip_Cost+Leasehold_Cost)*(1+Infl_Gen)^{t},0)"
        f2 = f"IF({cl}$4='Factory Rollout'!$E${f2ror},(Equip_Cost+Leasehold_Cost)*(1+Infl_Gen)^{t},0)"
        put(cx, r, C0+i, f"={f1}+{f2}", fmt=USD)
put(cx, 11, 1, "MAINTENANCE / REPLACEMENT CAPEX BY REGION", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): cx.cell(row=11, column=c).fill = FILL_SEC
for rg in range(1, 6):
    r = 11 + rg          # 12..16
    put(cx, r, 1, f"Region {rg} maintenance capex")
    for i, y in enumerate(YRS):
        cl = YL(i)
        put(cx, r, C0+i, f"=Maint_Pct*'Revenue Model'!{cl}{16+rg}", fmt=USD)
put(cx, 17, 1, "TOTAL CASH CAPEX BY REGION", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): cx.cell(row=17, column=c).fill = FILL_SEC
for rg in range(1, 6):
    r = 17 + rg          # 18..22
    put(cx, r, 1, f"Region {rg} total cash capex")
    for i, y in enumerate(YRS):
        cl = YL(i)
        put(cx, r, C0+i, f"={cl}{5+rg}+{cl}{11+rg}", fmt=USD)
yrow(cx, 24, "Total growth capex", lambda i, cl: f"=SUM({cl}6:{cl}10)", fmt=USD, font=F_HDR)
yrow(cx, 25, "Total maintenance capex", lambda i, cl: f"=SUM({cl}12:{cl}16)", fmt=USD, font=F_HDR)
yrow(cx, 26, "TOTAL CASH CAPEX", lambda i, cl: f"=SUM({cl}18:{cl}22)", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(cx, 28, "OKC founder asset contribution (non-cash)", lambda i, cl: f"=IF({cl}$4='Factory Rollout'!$E$6,OKC_Asset_Val,0)", fmt=USD)
yrow(cx, 29, "TOTAL PP&E ADDITIONS (incl. non-cash)", lambda i, cl: f"={cl}26+{cl}28", fmt=USD, font=F_HDR, fill=FILL_TOT)
put(cx, 31, 1, "Memo split of growth capex", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): cx.cell(row=31, column=c).fill = FILL_SEC
yrow(cx, 32, "Equipment / manufacturing assets", lambda i, cl: f"={cl}24*Equip_Cost/(Equip_Cost+Leasehold_Cost)", fmt=USD, indent=1)
yrow(cx, 33, "Technology & leasehold improvements", lambda i, cl: f"={cl}24*Leasehold_Cost/(Equip_Cost+Leasehold_Cost)", fmt=USD, indent=1)
put(cx, 35, 1, "TOTAL PP&E ADDITIONS BY REGION (incl. non-cash — feeds Depreciation)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): cx.cell(row=35, column=c).fill = FILL_SEC
for rg in range(1, 6):
    r = 35 + rg          # 36..40
    put(cx, r, 1, f"Region {rg} PP&E additions")
    for i, y in enumerate(YRS):
        cl = YL(i)
        extra = f"+{cl}28" if rg == 1 else ""
        put(cx, r, C0+i, f"={cl}{17+rg}{extra}", fmt=USD)
widen(cx, {"A": 46})
cx.freeze_panes = "C5"

# =====================================================================
# TAB 11 — DEBT SCHEDULE (dormant — fully equity funded base case)
# =====================================================================
db = wb.create_sheet("Debt Schedule")
title(db, "TAB 11 — DEBT SCHEDULE",
      "BASE CASE = FULLY EQUITY FUNDED. S5: lease-only, strip principal & interest wherever lease expense exists; S4 §22.B: no mortgage debt. "
      "Structure retained (draws input row) so bridge/equipment debt can be activated without re-architecting; S2 references optional debt in its flywheel — "
      "a deliberate conservatism vs. source (flagged in Blueprint).")
yearhdr(db)
yrow(db, 6, "Beginning balance", lambda i, cl: "=0" if i == 0 else f"={YL(i-1)}10", fmt=USD)
put(db, 7, 1, "Draws (INPUT — 0 in base case)")
for i, y in enumerate(YRS):
    put(db, 7, C0+i, 0, fmt=USD, font=F_IN, fill=FILL_IN)
yrow(db, 8, "Principal repayments", lambda i, cl: "=0", fmt=USD)
put(db, 9, 1, "Interest rate (INPUT)")
put(db, 9, 3, 0.08, fmt=PCT, font=F_IN, fill=FILL_IN)
yrow(db, 10, "Ending balance", lambda i, cl: f"={cl}6+{cl}7-{cl}8", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(db, 11, "Interest expense (avg balance)", lambda i, cl: f"=($C$9)*({cl}6+{cl}10)/2", fmt=USD)
widen(db, {"A": 40})

# =====================================================================
# TAB 12 — DEPRECIATION SCHEDULE (100% derived from CapEx)
# =====================================================================
dp = wb.create_sheet("Depreciation Schedule")
title(dp, "TAB 12 — DEPRECIATION SCHEDULE",
      "Automatically generated from the CapEx tab (incl. OKC contributed assets): straight-line over Equip_Life from year placed in service. NO manual depreciation inputs.")
yearhdr(dp)
put(dp, 5, 1, "DEPRECIATION BY REGION", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): dp.cell(row=5, column=c).fill = FILL_SEC
for rg in range(1, 6):
    r = 5 + rg
    put(dp, r, 1, f"Region {rg} — {REGIONS[rg-1]}")
    for i, y in enumerate(YRS):
        cl = YL(i)
        put(dp, r, C0+i,
            f"=SUMPRODUCT(('Capital Expenditures'!$C{35+rg}:$M{35+rg})*($C$4:$M$4<={cl}$4)*(({cl}$4-$C$4:$M$4)<Equip_Life))/Equip_Life", fmt=USD)
yrow(dp, 12, "TOTAL DEPRECIATION & AMORTIZATION", lambda i, cl: f"=SUM({cl}6:{cl}10)", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(dp, 14, "Gross PP&E (cumulative additions)", lambda i, cl: f"=SUM('Capital Expenditures'!$C$29:{cl}29)", fmt=USD)
yrow(dp, 15, "Accumulated depreciation", lambda i, cl: f"=SUM($C$12:{cl}12)", fmt=USD)
yrow(dp, 16, "Net PP&E", lambda i, cl: f"={cl}14-{cl}15", fmt=USD, font=F_HDR, fill=FILL_TOT)
widen(dp, {"A": 46})
dp.freeze_panes = "C5"

# =====================================================================
# TAB 18 — REGIONAL ROLLUP (the consolidation engine: 5 region blocks)
# Row map per region rg (block start S = 6 + 20*(rg-1)):
#  S+0 Rev, +1 COGS, +2 GP, +3 SG&A, +4 Fee, +5 EBITDA, +6 D&A, +7 EBIT/EBT,
#  +8 cumEBT, +9 Tax(NOL), +10 NI, +11 Raise, +12 CapEx, +13 dNWC, +14 OpFCF,
#  +15 NetCF, +16 Cash EOY, +17 Homes, +18 Factories
# =====================================================================
rr = wb.create_sheet("Regional Rollup")
title(rr, "TAB 18 — REGIONAL ROLLUP",
      "Full standalone economics per regional C-corp: single equity raise at Factory 1, corporate tax paid (closed-form NOL carryforward), no dividends, "
      "retained earnings fund Factory 2. Regions are legally independent (QSBS) — no cross-region cash movement anywhere in this tab.")
yearhdr(rr)
def region_block(rg):
    S = 6 + 20*(rg-1)
    f1ror = 4 + 2*rg
    put(rr, S-1, 1, f"REGION {rg} — {REGIONS[rg-1]}" + ("  (OKC special capitalization)" if rg == 1 else "  (standard 90/10 archetype)"), font=F_SEC, fill=FILL_SEC)
    for c in range(2, 14): rr.cell(row=S-1, column=c).fill = FILL_SEC
    yrow(rr, S+0,  "Revenue", lambda i, cl: f"='Revenue Model'!{cl}{16+rg}", fmt=USD)
    yrow(rr, S+1,  "COGS", lambda i, cl: f"=COGS!{cl}{5+rg}", fmt=USD)
    yrow(rr, S+2,  "Gross profit", lambda i, cl: f"={cl}{S}-{cl}{S+1}", fmt=USD)
    yrow(rr, S+3,  "SG&A (incl. pre-opening)", lambda i, cl: f"='SG&A'!{cl}{5+rg}", fmt=USD)
    yrow(rr, S+4,  "Management fee to Platform (7%)", lambda i, cl: f"='Platform Revenue'!{cl}{5+rg}", fmt=USD)
    yrow(rr, S+5,  "EBITDA", lambda i, cl: f"={cl}{S+2}-{cl}{S+3}-{cl}{S+4}", fmt=USD, font=F_HDR, fill=FILL_TOT)
    yrow(rr, S+6,  "D&A", lambda i, cl: f"='Depreciation Schedule'!{cl}{5+rg}", fmt=USD)
    yrow(rr, S+7,  "EBIT = EBT (no debt)", lambda i, cl: f"={cl}{S+5}-{cl}{S+6}", fmt=USD)
    yrow(rr, S+8,  "Cumulative EBT (NOL base)", lambda i, cl: f"=SUM($C${S+7}:{cl}{S+7})", fmt=USD)
    yrow(rr, S+9,  "Cash taxes (NOL carryforward)",
         lambda i, cl: (f"=Tax_Rate*MAX(0,{cl}{S+8})" if i == 0 else f"=Tax_Rate*(MAX(0,{cl}{S+8})-MAX(0,{YL(i-1)}{S+8}))"), fmt=USD)
    yrow(rr, S+10, "Net income (retained — no dividends)", lambda i, cl: f"={cl}{S+7}-{cl}{S+9}", fmt=USD, font=F_HDR)
    if rg == 1:
        yrow(rr, S+11, "Equity raise (investor cash — single)", lambda i, cl: f"=IF({cl}$4='Factory Rollout'!$E$6,OKC_Cash,0)", fmt=USD)
    else:
        yrow(rr, S+11, "Equity raise (single, inflation-indexed to launch yr — S4 §10)", lambda i, cl: f"=IF({cl}$4='Factory Rollout'!$E${f1ror},Region_Raise*(1+Infl_Gen)^({cl}$4-Model_Start),0)", fmt=USD)
    yrow(rr, S+12, "Cash capex", lambda i, cl: f"='Capital Expenditures'!{cl}{17+rg}", fmt=USD)
    yrow(rr, S+13, "Change in NWC", lambda i, cl: f"='Working Capital'!{cl}{18+rg}", fmt=USD)
    yrow(rr, S+14, "Operating free cash flow", lambda i, cl: f"={cl}{S+10}+{cl}{S+6}-{cl}{S+12}-{cl}{S+13}", fmt=USD)
    yrow(rr, S+15, "Net cash flow (incl. raise)", lambda i, cl: f"={cl}{S+14}+{cl}{S+11}", fmt=USD)
    yrow(rr, S+16, "Cash — end of year", lambda i, cl: (f"={cl}{S+15}" if i == 0 else f"={YL(i-1)}{S+16}+{cl}{S+15}"), fmt=USD, font=F_HDR, fill=FILL_TOT)
    yrow(rr, S+17, "Homes produced", lambda i, cl: f"='Production Model'!{cl}{2*rg+6}+'Production Model'!{cl}{2*rg+7}", fmt=NUM0)
    yrow(rr, S+18, "Factories operational", lambda i, cl: f"=SUMPRODUCT(('Factory Rollout'!$C$6:$C$15={rg})*('Factory Rollout'!$E$6:$E$15<={cl}$4))", fmt='0')
for rg in range(1, 6):
    region_block(rg)
# Consolidated regions total block
TS = 106
put(rr, TS-1, 1, "ALL REGIONS — CONSOLIDATED (sum of 5 independent C-corps)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): rr.cell(row=TS-1, column=c).fill = FILL_SEC
tot_labels = ["Revenue","COGS","Gross profit","SG&A","Management fee to Platform","EBITDA","D&A","EBIT = EBT",
              "Cumulative EBT","Cash taxes","Net income","Equity raises","Cash capex","Change in NWC",
              "Operating free cash flow","Net cash flow","Cash — end of year","Homes produced","Factories operational"]
for k, lbl in enumerate(tot_labels):
    fm = NUM0 if k >= 17 else USD
    yrow(rr, TS+k, lbl, lambda i, cl, k=k: f"={cl}{6+k}+{cl}{26+k}+{cl}{46+k}+{cl}{66+k}+{cl}{86+k}",
         fmt=fm, font=(F_HDR if lbl in ("EBITDA","Net income","Cash — end of year") else F_CALC),
         fill=(FILL_TOT if lbl in ("EBITDA","Net income","Cash — end of year") else None))
# Self-funding & liquidity checks
put(rr, 127, 1, "LIQUIDITY & FLYWHEEL CHECKS (each region must fund Factory 2 internally — no second raise)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): rr.cell(row=127, column=c).fill = FILL_SEC
for rg in range(1, 6):
    S = 6 + 20*(rg-1)
    f2ror = 5 + 2*rg
    r = 127 + rg
    put(rr, r, 1, f"Region {rg}: minimum cash balance / Factory-2 self-funding")
    put(rr, r, 3, f"=MIN(C{S+16}:M{S+16})", fmt=USD)
    put(rr, r, 5, f'=IF(MIN(C{S+16}:M{S+16})>=0,"PASS — single raise sufficient","REVIEW — raise insufficient or F2 too early")')
    put(rr, r, 9, f"=INDEX(C{S+16}:M{S+16},MATCH('Factory Rollout'!$E${f2ror},$C$4:$M$4,0)-1)", fmt=USD)
    put(rr, r, 11, f'=IF(MIN(C{S+16}:M{S+16})>=0,"PASS — F2 self-funded (no raise after launch; cash never negative)","REVIEW — F2 timing")')
put(rr, 133, 1, "Memo: 2036 pre-fee EBITDA per factory — NOMINAL incl. inflation (compare 2026$ figure on Standard Regional Model vs S2 ~$12M anchor)")
put(rr, 133, 3, "=(M111+M110)/M124", fmt=USD)
widen(rr, {"A": 44})
rr.freeze_panes = "C5"

# =====================================================================
# TAB 19 — PLATFORM ROLLUP
# =====================================================================
pl = wb.create_sheet("Platform Rollup")
title(pl, "TAB 19 — PLATFORM ROLLUP",
      "House Factory Platform LLC standalone (fee income less platform overhead; LLC = pass-through, no entity-level tax — members taxed directly, flagged), "
      "plus network-wide consolidated summary. Platform pays no factory capex and holds no factory debt: capital-light by design.")
yearhdr(pl)
yrow(pl, 6,  "Management fee revenue", lambda i, cl: f"='Platform Revenue'!{cl}12", fmt=USD)
yrow(pl, 7,  "Administrative / other revenue", lambda i, cl: f"='Platform Revenue'!{cl}13", fmt=USD)
yrow(pl, 8,  "Total platform revenue", lambda i, cl: f"={cl}6+{cl}7", fmt=USD, font=F_HDR)
yrow(pl, 9,  "Executive payroll (post-transition)", lambda i, cl: f"='SG&A'!{cl}14", fmt=USD)
yrow(pl, 10, "Other platform opex", lambda i, cl: f"='SG&A'!{cl}15", fmt=USD)
yrow(pl, 11, "PLATFORM EBITDA", lambda i, cl: f"={cl}8-{cl}9-{cl}10", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(pl, 12, "Platform EBITDA margin", lambda i, cl: f"=IF({cl}8=0,0,{cl}11/{cl}8)", fmt=PCT)
yrow(pl, 13, "Entity tax (LLC pass-through = 0; member-level)", lambda i, cl: "=0", fmt=USD)
yrow(pl, 14, "Platform net income", lambda i, cl: f"={cl}11-{cl}13", fmt=USD)
yrow(pl, 15, "Platform cumulative cash", lambda i, cl: (f"={cl}14" if i == 0 else f"={YL(i-1)}15+{cl}14"), fmt=USD)
put(pl, 17, 1, "CONSOLIDATED NETWORK SUMMARY (5 regional C-corps + Platform LLC, intercompany fee eliminated)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): pl.cell(row=17, column=c).fill = FILL_SEC
yrow(pl, 18, "Consolidated revenue (external)", lambda i, cl: f"='Revenue Model'!{cl}26", fmt=USD)
yrow(pl, 19, "Consolidated EBITDA (regions + platform)", lambda i, cl: f"='Regional Rollup'!{cl}111+{cl}11", fmt=USD, font=F_HDR)
yrow(pl, 20, "Consolidated net income", lambda i, cl: f"='Regional Rollup'!{cl}116+{cl}14", fmt=USD)
yrow(pl, 21, "Consolidated operating FCF", lambda i, cl: f"='Regional Rollup'!{cl}120+{cl}14", fmt=USD)
yrow(pl, 22, "Consolidated cash", lambda i, cl: f"='Regional Rollup'!{cl}122+{cl}15", fmt=USD)
yrow(pl, 24, "Memo: platform equity accrual in regions (non-cash)", lambda i, cl: f"='Platform Revenue'!{cl}20", fmt=USD)
widen(pl, {"A": 52})
pl.freeze_panes = "C5"

# =====================================================================
# TAB 13 — INCOME STATEMENT (consolidated)
# =====================================================================
ist = wb.create_sheet("Income Statement")
title(ist, "TAB 13 — CONSOLIDATED INCOME STATEMENT (2026-2036)",
      "Regions + Platform with intercompany management fee eliminated. Monthly granularity for the launch phase lives on the Standard Regional Model tab "
      "(months 1-24); this statement is annual per institutional convention for a 10-year rollout.")
yearhdr(ist)
yrow(ist, 6,  "Regional revenue (external)", lambda i, cl: f"='Revenue Model'!{cl}23", fmt=USD)
yrow(ist, 7,  "Platform management fee revenue", lambda i, cl: f"='Revenue Model'!{cl}24", fmt=USD)
yrow(ist, 8,  "Intercompany elimination", lambda i, cl: f"='Revenue Model'!{cl}25", fmt=USD)
yrow(ist, 9,  "TOTAL REVENUE", lambda i, cl: f"={cl}6+{cl}7+{cl}8", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(ist, 11, "Cost of goods sold", lambda i, cl: f"=COGS!{cl}12", fmt=USD)
yrow(ist, 12, "GROSS PROFIT", lambda i, cl: f"={cl}9-{cl}11", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(ist, 13, "Gross margin %", lambda i, cl: f"=IF({cl}9=0,0,{cl}12/{cl}9)", fmt=PCT)
yrow(ist, 15, "Regional SG&A", lambda i, cl: f"='SG&A'!{cl}11", fmt=USD)
yrow(ist, 16, "Platform overhead", lambda i, cl: f"='SG&A'!{cl}16", fmt=USD)
yrow(ist, 18, "EBITDA", lambda i, cl: f"={cl}12-{cl}15-{cl}16", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(ist, 19, "EBITDA margin %", lambda i, cl: f"=IF({cl}9=0,0,{cl}18/{cl}9)", fmt=PCT)
yrow(ist, 20, "Depreciation & amortization", lambda i, cl: f"='Depreciation Schedule'!{cl}12", fmt=USD)
yrow(ist, 21, "EBIT", lambda i, cl: f"={cl}18-{cl}20", fmt=USD, font=F_HDR)
yrow(ist, 22, "Interest expense", lambda i, cl: f"='Debt Schedule'!{cl}11", fmt=USD)
yrow(ist, 23, "Pre-tax income", lambda i, cl: f"={cl}21-{cl}22", fmt=USD)
yrow(ist, 24, "Cash taxes (regional C-corps, NOL c/f)", lambda i, cl: f"='Regional Rollup'!{cl}115", fmt=USD)
yrow(ist, 25, "NET INCOME", lambda i, cl: f"={cl}23-{cl}24", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(ist, 26, "Net margin %", lambda i, cl: f"=IF({cl}9=0,0,{cl}25/{cl}9)", fmt=PCT)
yrow(ist, 28, "Check: EBITDA ties to Σ region + platform (=0)", lambda i, cl: f"={cl}18-('Regional Rollup'!{cl}111+'Platform Rollup'!{cl}11)", fmt=NUM)
widen(ist, {"A": 46})
ist.freeze_panes = "C5"

# =====================================================================
# TAB 14 — CASH FLOW STATEMENT
# =====================================================================
cf = wb.create_sheet("Cash Flow")
title(cf, "TAB 14 — CONSOLIDATED CASH FLOW STATEMENT",
      "Indirect method, fully linked to Income Statement and Balance Sheet. OKC founder asset contribution is non-cash (supplemental disclosure).")
yearhdr(cf)
yrow(cf, 6,  "Net income", lambda i, cl: f"='Income Statement'!{cl}25", fmt=USD)
yrow(cf, 7,  "  + Depreciation & amortization", lambda i, cl: f"='Depreciation Schedule'!{cl}12", fmt=USD)
yrow(cf, 8,  "  − Increase in net working capital", lambda i, cl: f"=-'Working Capital'!{cl}10", fmt=USD)
yrow(cf, 9,  "CASH FROM OPERATIONS", lambda i, cl: f"=SUM({cl}6:{cl}8)", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(cf, 11, "  − Capital expenditures (cash)", lambda i, cl: f"=-'Capital Expenditures'!{cl}26", fmt=USD)
yrow(cf, 12, "CASH FROM INVESTING", lambda i, cl: f"={cl}11", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(cf, 14, "  + Investor equity raises (one per region)", lambda i, cl: f"='Regional Rollup'!{cl}117", fmt=USD)
yrow(cf, 15, "  + Net debt draws / (repayments)", lambda i, cl: f"='Debt Schedule'!{cl}7-'Debt Schedule'!{cl}8", fmt=USD)
yrow(cf, 16, "  − Dividends (none — retained per QSBS strategy)", lambda i, cl: "=0", fmt=USD)
yrow(cf, 17, "CASH FROM FINANCING", lambda i, cl: f"=SUM({cl}14:{cl}16)", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(cf, 19, "NET CHANGE IN CASH", lambda i, cl: f"={cl}9+{cl}12+{cl}17", fmt=USD, font=F_HDR)
yrow(cf, 20, "Beginning cash", lambda i, cl: ("=0" if i == 0 else f"={YL(i-1)}21"), fmt=USD)
yrow(cf, 21, "ENDING CASH", lambda i, cl: f"={cl}19+{cl}20", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(cf, 23, "Supplemental: non-cash founder asset contribution (OKC)", lambda i, cl: f"='Capital Expenditures'!{cl}28", fmt=USD)
yrow(cf, 24, "Check: ending cash ties to entity cash (=0)", lambda i, cl: f"={cl}21-'Platform Rollup'!{cl}22", fmt=NUM)
widen(cf, {"A": 50})
cf.freeze_panes = "C5"

# =====================================================================
# TAB 15 — BALANCE SHEET
# =====================================================================
bs = wb.create_sheet("Balance Sheet")
title(bs, "TAB 15 — CONSOLIDATED BALANCE SHEET",
      "Fully integrated; balances automatically. Paid-in capital = investor cash raises + OKC founder asset contribution. No dividends — retained earnings compound.")
yearhdr(bs)
yrow(bs, 6,  "Cash", lambda i, cl: f"='Cash Flow'!{cl}21", fmt=USD)
yrow(bs, 7,  "Accounts receivable", lambda i, cl: f"='Working Capital'!{cl}6", fmt=USD)
yrow(bs, 8,  "Inventory", lambda i, cl: f"='Working Capital'!{cl}7", fmt=USD)
yrow(bs, 9,  "Total current assets", lambda i, cl: f"=SUM({cl}6:{cl}8)", fmt=USD, font=F_HDR)
yrow(bs, 10, "Gross PP&E", lambda i, cl: f"='Depreciation Schedule'!{cl}14", fmt=USD)
yrow(bs, 11, "Accumulated depreciation", lambda i, cl: f"=-'Depreciation Schedule'!{cl}15", fmt=USD)
yrow(bs, 12, "Net PP&E", lambda i, cl: f"={cl}10+{cl}11", fmt=USD, font=F_HDR)
yrow(bs, 13, "TOTAL ASSETS", lambda i, cl: f"={cl}9+{cl}12", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(bs, 15, "Accounts payable", lambda i, cl: f"='Working Capital'!{cl}8", fmt=USD)
yrow(bs, 16, "Debt", lambda i, cl: f"='Debt Schedule'!{cl}10", fmt=USD)
yrow(bs, 17, "TOTAL LIABILITIES", lambda i, cl: f"={cl}15+{cl}16", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(bs, 19, "Paid-in capital (cash raises + contributed assets)",
     lambda i, cl: f"=SUM('Regional Rollup'!$C$117:{cl}117)+SUM('Capital Expenditures'!$C$28:{cl}28)", fmt=USD)
yrow(bs, 20, "Retained earnings", lambda i, cl: f"=SUM('Income Statement'!$C$25:{cl}25)", fmt=USD)
yrow(bs, 21, "TOTAL EQUITY", lambda i, cl: f"={cl}19+{cl}20", fmt=USD, font=F_HDR, fill=FILL_TOT)
yrow(bs, 22, "TOTAL LIABILITIES + EQUITY", lambda i, cl: f"={cl}17+{cl}21", fmt=USD, font=F_HDR)
yrow(bs, 23, "CHECK: Assets − (L+E) = 0", lambda i, cl: f"={cl}13-{cl}22", fmt=NUM, font=F_HDR, fill=FILL_OK)
widen(bs, {"A": 50})
bs.freeze_panes = "C5"

# =====================================================================
# TAB 16 — OKLAHOMA CITY FACTORY MODEL (special launch region)
# =====================================================================
ok = wb.create_sheet("OKC Factory Model")
title(ok, "TAB 16 — OKLAHOMA CITY (HOUSE FACTORY CENTRAL) — SPECIAL LAUNCH MODEL",
      "OKC differs from every later region: capitalized partly by founder hard-asset/IP contribution (independent appraisal REQUIRED), pro-rata ownership placeholder, "
      "$10M plant modernization instead of greenfield build, faster relaunch ramp, and Lance/Craig on OKC payroll until the network reaches 2 factories.")
sec(ok, 4, "A. CAPITALIZATION & OWNERSHIP (all values flow from Global Assumptions §11)", 8)
cap_rows = [
    ("Founder contributed assets (lifts, mfg equipment, IP)", "=OKC_Asset_Val", USD, MIR+" — independent appraisal"),
    ("New investor cash", "=OKC_Cash", USD, MIR+" — confirm sizing (S5: total 'might be 20')"),
    ("Total capitalization", "=OKC_TotCap", USD, "Derived"),
    ("Platform ownership (pro-rata to asset contribution)", "=OKC_Plat_Own", PCT, "DERIVED placeholder — final split is negotiated (S4 §9)"),
    ("Investor ownership", "=OKC_Inv_Own", PCT, "Derived"),
    ("Plant modernization capex (2026)", "=OKC_Modern", USD, "CONFIRMED — S2 South Central"),
    ("Working capital & reserve (cash raise less modernization)", "=OKC_Cash-OKC_Modern", USD, "Derived — must stay positive"),
]
for k, (lbl, f, fm, st) in enumerate(cap_rows):
    put(ok, 5+k, 1, lbl)
    put(ok, 5+k, 4, f, fmt=fm)
    put(ok, 5+k, 6, st)
sec(ok, 13, "B. EMPLOYEE / MANAGEMENT TRANSITION (one-time — salaries never double-counted)", 8)
put(ok, 14, 1, "Transition year (network reaches 2 operational factories)")
put(ok, 14, 4, "=Trans_Year", fmt='0')
put(ok, 15, 1, "Before transition: Lance (CEO) & Craig (COO) are OKC employees; Platform overhead ≈ $0 payroll")
put(ok, 16, 1, "From transition: both move to Platform payroll; OKC hires a Regional GM behind them (S5 / S4 §15)")
put(ok, 17, 1, "OKC executive cost carried (pre-transition, yr-1 $)"); put(ok, 17, 4, "=CEO_Sal+COO_Sal", fmt=USD)
put(ok, 18, 1, "OKC GM cost (post-transition, yr-1 $)"); put(ok, 18, 4, "=GM_Sal", fmt=USD)
sec(ok, 20, "C. OKC REGION OPERATING SUMMARY (pulled live from Regional Rollup — Region 1)", 13)
put(ok, 21, 1, "", fill=FILL_HDR)
for i, y in enumerate(YRS): put(ok, 21, C0+i, y, font=F_HDR, fill=FILL_HDR, fmt='0')
ok_rows = [("Homes produced", 23, NUM0), ("Revenue", 6, USD), ("EBITDA", 11, USD), ("Net income (retained)", 16, USD),
           ("Cash capex", 18, USD), ("Cash — end of year", 22, USD)]
src_off = {"Homes produced":23, "Revenue":6, "EBITDA":11, "Net income (retained)":16, "Cash capex":18, "Cash — end of year":22}
for k, (lbl, srow, fm) in enumerate(ok_rows):
    yrow(ok, 22+k, lbl, lambda i, cl, srow=srow: f"='Regional Rollup'!{cl}{srow}", fmt=fm)
put(ok, 29, 1, "Factory 2 (OKC) opens"); put(ok, 29, 4, "='Factory Rollout'!$E$7", fmt='0')
put(ok, 30, 1, "Check — Factory 2 self-funded"); put(ok, 30, 4, "='Regional Rollup'!$E$128" if False else "='Regional Rollup'!$K$128")
put(ok, 30, 4, '=IF(MIN(\'Regional Rollup\'!C22:M22)>=0,"PASS — single capitalization sufficient","REVIEW")')
sec(ok, 32, "D. OPEN ITEMS BLOCKING FINAL OKC MODEL (S4 §22.A)", 8)
for k, txt in enumerate([
    "1. Independent appraisal of contributed assets → final ownership split (currently pro-rata placeholder).",
    "2. Old-building tax-credit recapture treatment on Lance's wind-down (S5) — outside this entity but affects contribution timing.",
    "3. Liability treatment: which liabilities (if any) travel with contributed assets.",
    "4. Whether assets contribute to Platform first, then down to OKC C-corp, or direct (legal/tax counsel — S4 §9).",
    "5. Confirm OKC employee count transferring from prior operation (transition credit to pre-opening cost)."]):
    put(ok, 33+k, 1, txt)
widen(ok, {"A": 62, "D": 16, "F": 44})

# =====================================================================
# TAB 17 — STANDARD REGIONAL FACTORY MODEL (generic archetype, relative years)
# =====================================================================
sr = wb.create_sheet("Standard Regional Model")
title(sr, "TAB 17 — STANDARD REGIONAL FACTORY MODEL (ARCHETYPE — RELATIVE YEARS, 2026$)",
      "The repeatable template every post-OKC region follows: one $25M raise for 90% of the common (Platform keeps 10% for no cash), 7% management fee, "
      "Factory 2 funded entirely from retained earnings — NO second raise. Shown in constant 2026$ (launch-year inflation applied on Regional Rollup).")
put(sr, 4, 1, "Region year →", font=F_HDR, fill=FILL_HDR)
for i in range(11):
    put(sr, 4, C0+i, i+1, font=F_HDR, fill=FILL_HDR, fmt='0', align="center")
put(sr, 5, 1, "Factory 2 opens in region year (INPUT)")
put(sr, 5, 2, 4, font=F_IN, fill=FILL_IN, fmt='0')
define("F2_Offset", "Standard Regional Model", "$B$5")
def srow(r, label, fn, fmt=USD, font=F_CALC, fill=None):
    put(sr, r, 1, label)
    for i in range(11):
        cl = YL(i)
        put(sr, r, C0+i, fn(i, cl), font=font, fill=fill, fmt=fmt)
srow(7,  "Homes — Factory 1", lambda i, cl: f"=Factory_Capacity*Util_Steady*IF({cl}$4=1,Ramp_Y1,IF({cl}$4=2,Ramp_Y2,Ramp_Y3))", fmt=NUM0)
srow(8,  "Homes — Factory 2", lambda i, cl: f"=IF({cl}$4<F2_Offset,0,Factory_Capacity*Util_Steady*IF({cl}$4-F2_Offset+1=1,Ramp_Y1,IF({cl}$4-F2_Offset+1=2,Ramp_Y2,Ramp_Y3)))", fmt=NUM0)
srow(9,  "Total homes", lambda i, cl: f"={cl}7+{cl}8", fmt=NUM0, font=F_HDR)
srow(10, "Revenue", lambda i, cl: f"={cl}9*Blend_ASP0")
srow(11, "COGS (variable + fixed per operating factory)", lambda i, cl: f"={cl}10*Var_Pct+(1+({cl}$4>=F2_Offset))*(Fixed_OH+Lease_Cost)")
srow(12, "Gross profit", lambda i, cl: f"={cl}10-{cl}11", font=F_HDR)
srow(13, "Gross margin %", lambda i, cl: f"=IF({cl}10=0,0,{cl}12/{cl}10)", fmt=PCT)
srow(14, "SG&A (region fixed + GM + S&M + pre-opening)", lambda i, cl: f"=Reg_SGA+GM_Sal+SalesMkt_Pct*{cl}10+Startup_Cost*(({cl}$4=1)+({cl}$4=F2_Offset))")
srow(15, "Management fee to Platform (7%)", lambda i, cl: f"=MgmtFee_Pct*{cl}10")
srow(16, "EBITDA", lambda i, cl: f"={cl}12-{cl}14-{cl}15", font=F_HDR, fill=FILL_TOT)
srow(17, "Memo: pre-fee EBITDA per factory (vs S2 ~$12M)", lambda i, cl: f"=({cl}16+{cl}15)/(1+({cl}$4>=F2_Offset))")
srow(18, "CapEx (F1 yr1, F2 at open, + maintenance)", lambda i, cl: f"=(Equip_Cost+Leasehold_Cost)*(({cl}$4=1)+({cl}$4=F2_Offset))+Maint_Pct*{cl}10")
srow(19, "D&A (auto from CapEx, SL)", lambda i, cl: f"=SUMPRODUCT($C$18:$M$18*($C$4:$M$4<={cl}$4)*(({cl}$4-$C$4:$M$4)<Equip_Life))/Equip_Life")
srow(20, "EBT", lambda i, cl: f"={cl}16-{cl}19")
srow(21, "Cumulative EBT", lambda i, cl: f"=SUM($C$20:{cl}20)")
srow(22, "Cash taxes (NOL c/f)", lambda i, cl: (f"=Tax_Rate*MAX(0,{cl}21)" if i == 0 else f"=Tax_Rate*(MAX(0,{cl}21)-MAX(0,{YL(i-1)}21))"))
srow(23, "Net income (retained — no dividends)", lambda i, cl: f"={cl}20-{cl}22", font=F_HDR)
srow(24, "Net working capital", lambda i, cl: f"=DSO/365*{cl}10+(DIO-DPO)/365*{cl}11")
srow(25, "Change in NWC", lambda i, cl: (f"={cl}24" if i == 0 else f"={cl}24-{YL(i-1)}24"))
srow(26, "Equity raise (ONE only)", lambda i, cl: f"=IF({cl}$4=1,Region_Raise,0)")
srow(27, "Operating free cash flow", lambda i, cl: f"={cl}23+{cl}19-{cl}18-{cl}25")
srow(28, "Net cash flow", lambda i, cl: f"={cl}27+{cl}26")
srow(29, "CASH — END OF YEAR", lambda i, cl: (f"={cl}28" if i == 0 else f"={YL(i-1)}29+{cl}28"), font=F_HDR, fill=FILL_TOT)
srow(30, "Cumulative positive-FCF counter", lambda i, cl: (f"=IF({cl}27>0,1,0)" if i == 0 else f"={YL(i-1)}30+IF({cl}27>0,1,0)"), fmt='0')
put(sr, 32, 1, "KEY TEMPLATE OUTPUTS & CHECKS", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): sr.cell(row=32, column=c).fill = FILL_SEC
put(sr, 33, 1, "Minimum cash over horizon (single raise must cover)"); put(sr, 33, 3, "=MIN(C29:M29)", fmt=USD)
put(sr, 33, 5, '=IF(MIN(C29:M29)>=0,"PASS — one raise is sufficient","REVIEW — increase Region_Raise or delay F2")', font=F_HDR)
put(sr, 34, 1, "First year of positive operating FCF (target ≈ Year 2 per S4/S5)"); put(sr, 34, 3, "=MATCH(1,C30:M30,0)", fmt='0')
put(sr, 35, 1, "Cash available at start of Factory-2 year vs Factory-2 capex")
put(sr, 35, 3, "=INDEX(C29:M29,F2_Offset-1)", fmt=USD)
put(sr, 35, 5, "=Equip_Cost+Leasehold_Cost", fmt=USD)
put(sr, 35, 7, '=IF(MIN(C29:M29)>=0,"PASS — F2 self-funded from retained earnings (no cash breach, no second raise)","REVIEW — F2 timing too early")', font=F_HDR)
put(sr, 36, 1, "Steady-state pre-fee EBITDA per factory vs S2 anchor ($12M)"); put(sr, 36, 3, "=M17", fmt=USD)
put(sr, 36, 5, "=M17-12000000", fmt=USD)
put(sr, 38, 1, "MONTHLY OPERATING VIEW — FIRST 24 MONTHS (linear ramp; annual model governs)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 28): sr.cell(row=38, column=c).fill = FILL_SEC
put(sr, 39, 1, "Month", font=F_HDR)
labels_m = [("Homes / month", '0.0'), ("Revenue / month", USD), ("Variable COGS", USD), ("Fixed costs + lease / month", USD),
            ("SG&A + fee / month", USD), ("EBITDA / month", USD), ("Cumulative EBITDA", USD)]
for k, (lbl, fm) in enumerate(labels_m):
    put(sr, 40+k, 1, lbl)
for m in range(1, 25):
    c = 2 + m
    cl = get_column_letter(c)
    put(sr, 39, c, m, fmt='0', font=F_HDR)
    put(sr, 40, c, f"=Factory_Capacity/12*MIN(1,{cl}39/Ramp_Months)*Util_Steady", fmt='0.0')
    put(sr, 41, c, f"={cl}40*Blend_ASP0", fmt=NUM)
    put(sr, 42, c, f"=-{cl}41*Var_Pct", fmt=NUM)
    put(sr, 43, c, f"=-(Fixed_OH+Lease_Cost)/12", fmt=NUM)
    put(sr, 44, c, f"=-(Reg_SGA+GM_Sal)/12-(SalesMkt_Pct+MgmtFee_Pct)*{cl}41", fmt=NUM)
    put(sr, 45, c, f"=SUM({cl}41:{cl}44)", fmt=NUM)
    put(sr, 46, c, f"=SUM($C$45:{cl}45)", fmt=NUM)
widen(sr, {"A": 52})
sr.freeze_panes = "C7"

# =====================================================================
# TAB 20 — EXIT MODEL
# =====================================================================
ex = wb.create_sheet("Exit Model")
title(ex, "TAB 20 — EXIT MODEL — CONSOLIDATED ROLL-UP (Y10 BASE CASE @ 10x, Y5 ALTERNATIVE @ 8x)",
      "Single liquidity event ~10 years out buying all regions at once (PE recap or IPO — S4 §19). Waterfall per region: return capital → 8% cumulative pref → "
      "GP catch-up → 80/20 residual; Platform additionally holds its no-cash common equity and the capitalized fee stream. §1202: 100% federal exclusion, "
      "per-investor caps (greater of $10M or 10× basis) apply at investor level.")
put(ex, 4, 1, "A. Y10 BASE-CASE EXIT BY REGION", font=F_SEC, fill=FILL_SEC)
for c in range(2, 10): ex.cell(row=4, column=c).fill = FILL_SEC
put(ex, 5, 1, "Metric", font=F_HDR, fill=FILL_HDR)
for rg in range(1, 6):
    put(ex, 5, 2+rg, f"R{rg} — {REGIONS[rg-1][:22]}", font=F_HDR, fill=FILL_HDR)
put(ex, 5, 8, "TOTAL", font=F_HDR, fill=FILL_HDR)
EB_ROW = {1: 11, 2: 31, 3: 51, 4: 71, 5: 91}
CASH_ROW = {1: 22, 2: 42, 3: 62, 4: 82, 5: 102}
def exit_block(base_r, mult_nm, exit_expr, hold_expr):
    rows = [
        ("Factory-1 open year", lambda rg, cl: f"='Factory Rollout'!$E${4+2*rg}", '0'),
        ("Exit year", lambda rg, cl: exit_expr(rg), '0'),
        ("Hold period (yrs)", lambda rg, cl: hold_expr(rg, cl), '0'),
        ("Investor capital (single raise, indexed)", lambda rg, cl: ("=OKC_Cash" if rg == 1 else f"=Region_Raise*(1+Infl_Gen)^({cl}{base_r+1}-Model_Start)"), USD),
        ("Investor ownership %", lambda rg, cl: ("=OKC_Inv_Own" if rg == 1 else "=Inv_Own"), PCT),
        ("Platform ownership %", lambda rg, cl: ("=OKC_Plat_Own" if rg == 1 else "=Plat_Own"), PCT),
        ("Regional EBITDA at exit", lambda rg, cl: f"=INDEX('Regional Rollup'!$C${EB_ROW[rg]}:$M${EB_ROW[rg]},MATCH({cl}{base_r+2},'Regional Rollup'!$C$4:$M$4,0))", USD),
        ("Enterprise value (mult × EBITDA)", lambda rg, cl: f"={mult_nm}*{cl}{base_r+7}", USD),
        ("Region cash at exit (memo)", lambda rg, cl: f"=INDEX('Regional Rollup'!$C${CASH_ROW[rg]}:$M${CASH_ROW[rg]},MATCH({cl}{base_r+2},'Regional Rollup'!$C$4:$M$4,0))", USD),
        ("EQUITY VALUE", lambda rg, cl: f"={cl}{base_r+8}+Incl_Cash_Exit*{cl}{base_r+9}", USD),
        ("Investor gross (ownership × equity)", lambda rg, cl: f"={cl}{base_r+5}*{cl}{base_r+10}", USD),
        ("Profit over capital", lambda rg, cl: f"={cl}{base_r+11}-{cl}{base_r+4}", USD),
        ("Tier 2 — 8% cumulative pref", lambda rg, cl: f"={cl}{base_r+4}*((1+Pref_Rate)^{cl}{base_r+3}-1)", USD),
        ("Tier 3 — GP catch-up (to 20% of profits)", lambda rg, cl: f"=MIN(MAX(0,{cl}{base_r+12}-{cl}{base_r+13}),{cl}{base_r+13}*Promote_Pct/(1-Promote_Pct))", USD),
        ("Tier 4 — residual (split 80/20)", lambda rg, cl: f"=MAX(0,{cl}{base_r+12}-{cl}{base_r+13}-{cl}{base_r+14})", USD),
        ("INVESTOR PROCEEDS", lambda rg, cl: f"=MIN({cl}{base_r+11},{cl}{base_r+4}+MIN(MAX({cl}{base_r+12},0),{cl}{base_r+13})+(1-Promote_Pct)*{cl}{base_r+15})", USD),
        ("GP promote (to Platform)", lambda rg, cl: f"={cl}{base_r+11}-{cl}{base_r+16}", USD),
        ("PLATFORM PROCEEDS (equity + promote)", lambda rg, cl: f"={cl}{base_r+6}*{cl}{base_r+10}+{cl}{base_r+17}", USD),
        ("Investor MOIC", lambda rg, cl: f"={cl}{base_r+16}/{cl}{base_r+4}", MULT),
        ("Investor IRR (no interim dividends)", lambda rg, cl: f"=({cl}{base_r+16}/{cl}{base_r+4})^(1/{cl}{base_r+3})-1", PCT),
        ("Investor gain", lambda rg, cl: f"={cl}{base_r+16}-{cl}{base_r+4}", USD),
        ("§1202 federal tax saved @23.8% (pre-cap)", lambda rg, cl: f"=MAX(0,{cl}{base_r+21})*QSBS_Rate", USD),
    ]
    for k, (lbl, fn, fm) in enumerate(rows):
        r = base_r + 1 + k
        put(ex, r, 1, lbl, font=(F_HDR if "PROCEEDS" in lbl or "EQUITY VALUE" in lbl or "MOIC" in lbl or "IRR" in lbl else F_CALC))
        for rg in range(1, 6):
            cl = get_column_letter(2+rg)
            put(ex, r, 2+rg, fn(rg, cl), fmt=fm)
        # totals
        H = "H"
        if fm == USD:
            put(ex, r, 8, f"=SUM(C{r}:G{r})", fmt=USD, font=F_HDR)
        elif lbl == "Investor MOIC":
            put(ex, r, 8, f"=H{base_r+16}/H{base_r+4}", fmt=MULT, font=F_HDR)
    return base_r + len(rows)
end_a = exit_block(5, "Exit_Mult", lambda rg: "=Exit_Year", lambda rg, cl: f"=Exit_Year-{cl}6")
put(ex, 28, 1, "Cross-check vs S2 heuristic (LP share = 65% of value)", font=F_SUB)
for rg in range(1, 6):
    cl = get_column_letter(2+rg)
    put(ex, 28, 2+rg, f"=0.65*{cl}15-{cl}21", fmt=USD)
put(ex, 29, 1, "  Note: this model runs the actual LPA waterfall (capital → pref → catch-up → 80/20). S2 approximated LP share as a flat 65% of value; variance above is expected and disclosed.", font=F_SUB)

put(ex, 31, 1, "B. Y5 ALTERNATIVE EXIT BY REGION (8× — earlier §1202 crystallization)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 10): ex.cell(row=31, column=c).fill = FILL_SEC
put(ex, 32, 1, "Metric", font=F_HDR, fill=FILL_HDR)
for rg in range(1, 6):
    put(ex, 32, 2+rg, f"R{rg}", font=F_HDR, fill=FILL_HDR)
put(ex, 32, 8, "TOTAL", font=F_HDR, fill=FILL_HDR)
end_b = exit_block(32, "Exit_Mult_Y5", lambda rg: f"=MIN('Factory Rollout'!$E${4+2*rg}+5,2036)", lambda rg, cl: "=5")

put(ex, 58, 1, "C. PLATFORM VALUE AT EXIT (House Factory Platform LLC)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 10): ex.cell(row=58, column=c).fill = FILL_SEC
put(ex, 59, 1, "Σ Platform regional equity proceeds + promotes (Y10)"); put(ex, 59, 4, "=H23", fmt=USD)
put(ex, 60, 1, "Platform EBITDA at exit year"); put(ex, 60, 4, "=INDEX('Platform Rollup'!$C$11:$M$11,MATCH(Exit_Year,'Platform Rollup'!$C$4:$M$4,0))", fmt=USD)
put(ex, 61, 1, "Capitalized fee stream (Plat_Fee_Mult × platform EBITDA)"); put(ex, 61, 4, "=Plat_Fee_Mult*D60", fmt=USD)
put(ex, 62, 1, "Platform retained cash at exit"); put(ex, 62, 4, "=INDEX('Platform Rollup'!$C$15:$M$15,MATCH(Exit_Year,'Platform Rollup'!$C$4:$M$4,0))", fmt=USD)
put(ex, 63, 1, "TOTAL PLATFORM VALUE", font=F_HDR); put(ex, 63, 4, "=D59+D61+D62", fmt=USD, font=F_HDR)
put(ex, 64, 1, "  Lance-related entity (60%)"); put(ex, 64, 4, "=Lance_Pct*D63", fmt=USD)
put(ex, 65, 1, "  USPD / USEDC (40%)"); put(ex, 65, 4, "=USPD_Pct*D63", fmt=USD)

put(ex, 67, 1, "D. AGGREGATE INVESTOR CASH FLOWS, IRR, MOIC, NPV", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): ex.cell(row=67, column=c).fill = FILL_SEC
put(ex, 68, 1, "Year", font=F_HDR, fill=FILL_HDR)
for i, y in enumerate(YRS): put(ex, 68, C0+i, y, font=F_HDR, fill=FILL_HDR, fmt='0')
yrow(ex, 69, "Investor equity in (raises)", lambda i, cl: f"=-'Regional Rollup'!{cl}117", fmt=USD)
yrow(ex, 70, "Investor exit proceeds", lambda i, cl: f"=IF({cl}$68=Exit_Year,$H$21,0)", fmt=USD)
yrow(ex, 71, "Net investor cash flow", lambda i, cl: f"={cl}69+{cl}70", fmt=USD, font=F_HDR)
put(ex, 73, 1, "Blended investor IRR (all regions)"); put(ex, 73, 4, "=IRR(C71:M71)", fmt=PCT, font=F_HDR)
put(ex, 74, 1, "Blended investor MOIC"); put(ex, 74, 4, "=H21/(-SUM(C69:M69))", fmt=MULT, font=F_HDR)
put(ex, 75, 1, "Investor NPV @ discount rate"); put(ex, 75, 4, "=NPV(Disc_Rate,C71:M71)", fmt=USD, font=F_HDR)
put(ex, 77, 1, "E. PROJECT-LEVEL NPV (unlevered network FCF + terminal value @ Disc_Rate)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 14): ex.cell(row=77, column=c).fill = FILL_SEC
yrow(ex, 78, "Network operating FCF (regions + platform)", lambda i, cl: f"='Platform Rollup'!{cl}21", fmt=USD)
put(ex, 79, 1, "Terminal value at exit (Σ region equity + fee stream)")
put(ex, 79, 4, "=H15+D61", fmt=USD)
put(ex, 80, 1, "PROJECT NPV")
put(ex, 80, 4, "=NPV(Disc_Rate,C78:M78)+D79/(1+Disc_Rate)^(Exit_Year-Model_Start+1)", fmt=USD, font=F_HDR)
widen(ex, {"A": 46, "B": 6, "C": 15, "D": 16, "E": 15, "F": 15, "G": 15, "H": 16})

# =====================================================================
# TAB 21 — SENSITIVITY ANALYSIS
# =====================================================================
sn = wb.create_sheet("Sensitivity Analysis")
title(sn, "TAB 21 — SENSITIVITY ANALYSIS (steady-state standard region at exit-year prices)",
      "One-way sensitivities recomputed through a live mini-engine that mirrors the main model chain: region revenue → EBITDA → EV → LPA waterfall → investor MOIC/IRR. "
      "Convention: mature 2-factory standard region, exit-year price/cost levels, 10-yr hold, single $25M raise. Tornado ranking at bottom.")
hdr = ["Variable", "Level", "Shocked input", "Region revenue", "Region EBITDA", "Enterprise value", "Investor gross",
       "Pref (8% comp.)", "GP catch-up", "Residual", "INVESTOR PROCEEDS", "MOIC", "IRR", "Platform take"]
for j, h in enumerate(hdr, start=1):
    put(sn, 4, j, h, font=F_HDR, fill=FILL_HDR)
BASE = dict(
    asp="Blend_ASP0*(1+Infl_ASP)^(Exit_Year-Model_Start)",
    varp="Var_Pct", sm="SalesMkt_Pct", fee="MgmtFee_Pct",
    fixed="((2*(Fixed_OH+Lease_Cost)+Reg_SGA)*(1+Infl_Gen)^(Exit_Year-Model_Start)+GM_Sal*(1+Infl_Wage)^(Exit_Year-Model_Start))",
    cap="Factory_Capacity", util="Util_Steady", mult="Exit_Mult", C="Region_Raise",
    own="Inv_Own", plat="Plat_Own", n="(Exit_Year-Model_Start)")
ROW = [6]     # mutable row cursor
MOIC_CELLS = {}   # variable -> list of MOIC cell refs
def sens_row(varname, lvl, disp, ov):
    r = ROW[0]; ROW[0] += 1
    t = dict(BASE); t.update(ov)
    put(sn, r, 1, varname)
    put(sn, r, 2, lvl)
    put(sn, r, 3, disp, fmt=NUM)
    put(sn, r, 4, f"=2*{t['cap']}*{t['util']}*{t['asp']}", fmt=USD)
    put(sn, r, 5, f"=D{r}*(1-{t['varp']}-{t['sm']}-{t['fee']})-{t['fixed']}", fmt=USD)
    put(sn, r, 6, f"={t['mult']}*E{r}", fmt=USD)
    put(sn, r, 7, f"={t['own']}*F{r}", fmt=USD)
    put(sn, r, 8, f"={t['C']}*((1+Pref_Rate)^{t['n']}-1)", fmt=USD)
    put(sn, r, 9, f"=MIN(MAX(0,G{r}-{t['C']}-H{r}),H{r}*Promote_Pct/(1-Promote_Pct))", fmt=USD)
    put(sn, r, 10, f"=MAX(0,G{r}-{t['C']}-H{r}-I{r})", fmt=USD)
    put(sn, r, 11, f"=MIN(G{r},{t['C']}+MIN(MAX(G{r}-{t['C']},0),H{r})+(1-Promote_Pct)*J{r})", fmt=USD)
    put(sn, r, 12, f"=K{r}/{t['C']}", fmt=MULT, font=F_HDR)
    put(sn, r, 13, f"=(K{r}/{t['C']})^(1/{t['n']})-1", fmt=PCT)
    put(sn, r, 14, f"={t['plat']}*F{r}+G{r}-K{r}", fmt=USD)
    MOIC_CELLS.setdefault(varname, []).append(f"L{r}")
    return r
sens_row("BASE CASE", "Base", "=Blend_ASP0", {})
ROW[0] += 1
for f_ in (0.8, 0.9, 1.1, 1.2):
    sens_row("Home prices (blended ASP)", f"{f_:+.0%}"[:4] if f_ < 1 else f"+{(f_-1):.0%}", f"={f_}*Blend_ASP0",
             {"asp": f"({f_}*Blend_ASP0)*(1+Infl_ASP)^(Exit_Year-Model_Start)"})
for d in (-0.05, -0.025, 0.025, 0.05):
    sens_row("Materials % of revenue", f"{d:+.1%} pts", f"=Mat_Pct+({d})", {"varp": f"(Var_Pct+({d}))"})
for d in (-0.04, -0.02, 0.02, 0.04):
    sens_row("Direct labor % of revenue", f"{d:+.1%} pts", f"=Lab_Pct+({d})", {"varp": f"(Var_Pct+({d}))"})
for u in (0.8, 0.9, 1.1, 1.2):
    sens_row("Capacity utilization", f"{u:.0%}", f"={u}", {"util": str(u)})
for fe in (0.05, 0.06, 0.08, 0.09):
    sens_row("Management fee %", f"{fe:.0%}", f"={fe}", {"fee": str(fe)})
for p in (0.05, 0.075, 0.125, 0.15):
    sens_row("Platform ownership %", f"{p:.1%}", f"={p}", {"plat": str(p), "own": f"(1-{p})"})
for m in (6, 8, 12, 14):
    sens_row("Exit multiple", f"{m}x", f"={m}", {"mult": str(m)})
for c_ in (20000000, 30000000):
    sens_row("Regional raise (factory capital)", f"${c_/1e6:.0f}M", f"={c_}", {"C": str(c_)})
for g in (0.015, 0.02, 0.03, 0.035):
    sens_row("General inflation", f"{g:.1%}", f"={g}",
             {"fixed": f"((2*(Fixed_OH+Lease_Cost)+Reg_SGA)*(1+{g})^(Exit_Year-Model_Start)+GM_Sal*(1+Infl_Wage)^(Exit_Year-Model_Start))"})
sens_row("Exit timing", "Y5 exit @ 8x", "=Exit_Mult_Y5", {"mult": "Exit_Mult_Y5", "n": "5"})
r_ramp = ROW[0] + 1
put(sn, r_ramp, 1, "PRODUCTION RAMP — YEAR-1 REGION EBITDA IMPACT (path sensitivity; steady state unaffected)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 15): sn.cell(row=r_ramp, column=c).fill = FILL_SEC
for k, rmp in enumerate((0.4, 0.5, 0.6, 0.7)):
    r = r_ramp + 1 + k
    put(sn, r, 1, f"Year-1 ramp = {rmp:.0%}")
    put(sn, r, 4, f"=Factory_Capacity*Util_Steady*{rmp}*Blend_ASP0", fmt=USD)
    put(sn, r, 5, f"=D{r}*(1-Var_Pct-SalesMkt_Pct-MgmtFee_Pct)-(Fixed_OH+Lease_Cost)-(Reg_SGA+GM_Sal)-Startup_Cost", fmt=USD)
    put(sn, r, 6, "Year-1 factory EBITDA (2026$, incl. pre-opening)")
tor0 = r_ramp + 7
put(sn, tor0, 1, "TORNADO — INVESTOR MOIC RANGE BY VARIABLE (from tables above)", font=F_SEC, fill=FILL_SEC)
for c in range(2, 15): sn.cell(row=tor0, column=c).fill = FILL_SEC
put(sn, tor0+1, 1, "Variable", font=F_HDR, fill=FILL_HDR)
put(sn, tor0+1, 2, "MOIC low", font=F_HDR, fill=FILL_HDR)
put(sn, tor0+1, 3, "MOIC high", font=F_HDR, fill=FILL_HDR)
put(sn, tor0+1, 4, "Spread", font=F_HDR, fill=FILL_HDR)
tr = tor0 + 2
for vn, cells in MOIC_CELLS.items():
    if vn == "BASE CASE": continue
    put(sn, tr, 1, vn)
    put(sn, tr, 2, f"=MIN({','.join(cells)})", fmt=MULT)
    put(sn, tr, 3, f"=MAX({','.join(cells)})", fmt=MULT)
    put(sn, tr, 4, f"=C{tr}-B{tr}", fmt=MULT)
    tr += 1
tchart = BarChart(); tchart.type = "bar"; tchart.title = "Tornado — Investor MOIC range"
data = Reference(sn, min_col=2, max_col=3, min_row=tor0+1, max_row=tr-1)
cats = Reference(sn, min_col=1, min_row=tor0+2, max_row=tr-1)
tchart.add_data(data, titles_from_data=True); tchart.set_categories(cats)
tchart.height = 10; tchart.width = 18
sn.add_chart(tchart, f"P{tor0}")
widen(sn, {"A": 38, "B": 13, "C": 13, "K": 18})
sn.freeze_panes = "A5"

# =====================================================================
# TAB 1 — EXECUTIVE DASHBOARD
# =====================================================================
dash = wb.create_sheet("Executive Dashboard")
title(dash, "HOUSE FACTORY PLATFORM — EXECUTIVE DASHBOARD",
      "All figures live-linked. Orange inputs on Global Assumptions are "+MIR+" placeholders — see Cover & Sources for the full open-items register.")
sec(dash, 4, "A. INVESTMENT SUMMARY (Y10 base-case exit @ 10× EBITDA)", 8)
summary = [
    ("Total investor capital (5 single raises)", "='Exit Model'!H9", USD),
    ("Total enterprise value at exit", "='Exit Model'!H13", USD),
    ("Total equity value at exit", "='Exit Model'!H15", USD),
    ("Total investor proceeds (post-waterfall)", "='Exit Model'!H21", USD),
    ("Blended investor MOIC", "='Exit Model'!D74", MULT),
    ("Blended investor IRR", "='Exit Model'!D73", PCT),
    ("Investor NPV @ discount rate", "='Exit Model'!D75", USD),
    ("Project NPV (unlevered FCF + terminal)", "='Exit Model'!D80", USD),
    ("§1202 federal tax saved (pre-cap)", "='Exit Model'!H27", USD),
    ("PLATFORM VALUE at exit (equity + promotes + fee stream + cash)", "='Exit Model'!D63", USD),
    ("  Lance-related entity (60%)", "='Exit Model'!D64", USD),
    ("  USPD / USEDC (40%)", "='Exit Model'!D65", USD),
]
for k, (lbl, f, fm) in enumerate(summary):
    put(dash, 5+k, 1, lbl, font=(F_HDR if "PLATFORM" in lbl or "MOIC" in lbl or "IRR" in lbl else F_CALC))
    put(dash, 5+k, 5, f, fmt=fm, font=F_HDR)
sec(dash, 18, "B. NETWORK KPIs BY YEAR", 13)
put(dash, 19, 1, "", fill=FILL_HDR)
for i, y in enumerate(YRS): put(dash, 19, C0+i, y, font=F_HDR, fill=FILL_HDR, fmt='0')
kpis = [
    ("Operational factories", lambda cl: f"='Factory Rollout'!{cl}20", '0'),
    ("Active regions", lambda cl: f"='Factory Rollout'!{cl}21", '0'),
    ("Homes produced", lambda cl: f"='Production Model'!{cl}18", NUM0),
    ("Cumulative homes", lambda cl: f"='Production Model'!{cl}19", NUM0),
    ("Consolidated revenue", lambda cl: f"='Income Statement'!{cl}9", USD),
    ("Gross margin %", lambda cl: f"='Income Statement'!{cl}13", PCT),
    ("EBITDA", lambda cl: f"='Income Statement'!{cl}18", USD),
    ("EBITDA margin %", lambda cl: f"='Income Statement'!{cl}19", PCT),
    ("EBIT", lambda cl: f"='Income Statement'!{cl}21", USD),
    ("Net income", lambda cl: f"='Income Statement'!{cl}25", USD),
    ("Operating free cash flow", lambda cl: f"='Platform Rollup'!{cl}21", USD),
    ("Consolidated cash", lambda cl: f"='Platform Rollup'!{cl}22", USD),
    ("Platform revenue (fees)", lambda cl: f"='Platform Rollup'!{cl}8", USD),
    ("Platform EBITDA", lambda cl: f"='Platform Rollup'!{cl}11", USD),
]
for k, (lbl, fn, fm) in enumerate(kpis):
    put(dash, 20+k, 1, lbl)
    for i, y in enumerate(YRS):
        cl = YL(i)
        put(dash, 20+k, C0+i, fn(cl), fmt=fm)
sec(dash, 36, "C. ROLLOUT TIMELINE (● = operational)", 13)
put(dash, 37, 1, "", fill=FILL_HDR)
for i, y in enumerate(YRS): put(dash, 37, C0+i, y, font=F_HDR, fill=FILL_HDR, fmt='0')
for f, rn, ridx, fir, oy, fund in FACTORIES:
    r = 37 + f
    put(dash, r, 1, f"F#{f} — {rn.replace(MIR,'TBC')} (Factory {fir})")
    for i, y in enumerate(YRS):
        cl = YL(i)
        put(dash, r, C0+i, f"=IF({cl}$37>='Factory Rollout'!$E${5+f},\"●\",\"\")", align="center")
sec(dash, 49, "D. MODEL INTEGRITY CHECKS (all must be PASS / 0)", 13)
checks = [
    ("Balance sheet ties (Σ|assets − L−E|)", "=SUMPRODUCT(ABS('Balance Sheet'!C23:M23))", NUM),
    ("Cash flow ties to entity cash (Σ|Δ|)", "=SUMPRODUCT(ABS('Cash Flow'!C24:M24))", NUM),
    ("COGS components tie (Σ|Δ|)", "=SUMPRODUCT(ABS(COGS!C23:M23))", NUM),
    ("EBITDA ties: IS vs region+platform (Σ|Δ|)", "=SUMPRODUCT(ABS('Income Statement'!C28:M28))", NUM),
    ("Product-mix revenue split ties (Σ|Δ|)", "=SUMPRODUCT(ABS('Revenue Model'!C31:M31))", NUM),
    ("Regional ΔNWC ties to consolidated (Σ|Δ|)", "=SUMPRODUCT(ABS('Working Capital'!C25:M25))", NUM),
    ("Region 1 (OKC) single-raise sufficiency", "='Regional Rollup'!E128", None),
    ("Region 2 single-raise sufficiency", "='Regional Rollup'!E129", None),
    ("Region 3 single-raise sufficiency", "='Regional Rollup'!E130", None),
    ("Region 4 single-raise sufficiency", "='Regional Rollup'!E131", None),
    ("Region 5 single-raise sufficiency", "='Regional Rollup'!E132", None),
    ("Std template: F2 self-funded from retained earnings", "='Standard Regional Model'!G35", None),
    ("Std template: first positive-FCF year (target ~2)", "='Standard Regional Model'!C34", '0'),
    ("Steady per-factory pre-fee EBITDA 2026$ vs S2 ~$12M anchor", "='Standard Regional Model'!C36", USD),
]
for k, (lbl, f, fm) in enumerate(checks):
    put(dash, 50+k, 1, lbl)
    put(dash, 50+k, 5, f, fmt=fm)
# charts
ch1 = LineChart(); ch1.title = "Consolidated revenue & EBITDA"; ch1.height = 8; ch1.width = 20
ch1.add_data(Reference(dash, min_col=2, max_col=13, min_row=24, max_row=24), from_rows=True, titles_from_data=True)
ch1.add_data(Reference(dash, min_col=2, max_col=13, min_row=26, max_row=26), from_rows=True, titles_from_data=True)
ch1.set_categories(Reference(dash, min_col=3, max_col=13, min_row=19, max_row=19))
dash.add_chart(ch1, "O5")
ch2 = BarChart(); ch2.title = "Homes produced / yr"; ch2.height = 8; ch2.width = 20
ch2.add_data(Reference(dash, min_col=2, max_col=13, min_row=22, max_row=22), from_rows=True, titles_from_data=True)
ch2.set_categories(Reference(dash, min_col=3, max_col=13, min_row=19, max_row=19))
dash.add_chart(ch2, "O22")
ch3 = LineChart(); ch3.title = "Platform fee revenue & EBITDA (compounding)"; ch3.height = 8; ch3.width = 20
ch3.add_data(Reference(dash, min_col=2, max_col=13, min_row=32, max_row=32), from_rows=True, titles_from_data=True)
ch3.add_data(Reference(dash, min_col=2, max_col=13, min_row=33, max_row=33), from_rows=True, titles_from_data=True)
ch3.set_categories(Reference(dash, min_col=3, max_col=13, min_row=19, max_row=19))
dash.add_chart(ch3, "O39")
widen(dash, {"A": 52, "E": 18})
dash.freeze_panes = "A4"

# =====================================================================
# TAB 0 — COVER & SOURCES
# =====================================================================
cv = wb.create_sheet("Cover & Sources")
title(cv, "HOUSE FACTORY PLATFORM — MASTER PRO FORMA  ·  v1.0  ·  July 2026",
      "Integrated operating model: Parent Platform + OKC launch + Standard Regional archetype + 5-region rollout + consolidated statements + exit. CONFIDENTIAL — DRAFT FOR MANAGEMENT REVIEW.")
rows_txt = [
("", ""),
("HOW TO READ THIS WORKBOOK", ""),
("Inputs", "Live ONLY on 'Global Assumptions' (blue font: gold = sourced, orange = "+MIR+" placeholder). Factory opening years are the only other inputs (Factory Rollout col E, Debt draws, F2 offset)."),
("Flow", "Assumptions → Rollout → Production → Revenue/COGS/SG&A → Regional Rollup (5 independent C-corps) + Platform Rollup → Consolidated IS/CF/BS → Exit → Sensitivity."),
("Build order", "Per management: 1) factory economics, 2) regional economics, 3) platform economics, 4) consolidated statements, 5) investor returns, 6) exit."),
("", ""),
("SOURCE DOCUMENTS & SOURCE-OF-TRUTH MAP", ""),
("S1 House_Factory_Platform.xlsx", "Org structure: 5 QSBS regional C-corps; mgmt fee + ownership arrows; 2 factories/region; staggered holds. TRUTH FOR: entity structure."),
("S2 Regional_Factory_Model.xlsx (v2.0)", "Capacity 500-700 u/yr; $2M/$6M/$12M EBITDA ramp; LP terms (8% pref, 20% promote, 90/10); 8x/10x exit multiples; OKC $10M modernization. TRUTH FOR: capacity, ramp anchor, fund terms, exit multiples."),
("S3 Dev_Model_25_Markets.xlsx", "Downstream build-to-rent dev-fund model (kit $54-59.4K, 300-unit sites). DEFERRED to development-funds addendum per S5; used only as mix analog + demand-channel evidence."),
("S4 HFP_Business_Model_Report.docx", "GOVERNING NORMALIZATION DOCUMENT: 60/40 parent split; $25-30M raise; 90/10; 7% fee; lease-only; 2 factories/region; OKC relaunch; price scope bridge; open-items register."),
("S5 Meeting transcript (July 2026)", "Management intent: OKC first & special; one raise per region; no dividends; reinvest; ~10-yr consolidated exit; operating model before investment model."),
("", ""),
("KEY NORMALIZATION DECISIONS (conflicts resolved — full log in Blueprint doc)", ""),
("Regions & factories", "5 regions x 2 factories (10) per S4/S5 base case — NOT S2's 17-factory map (kept as upside addendum)."),
("Capitalization", "$25M standard raise (S5); OKC special ($12M cash + $8M assets placeholder). S2's $127M flywheel raise superseded."),
("Facilities", "Lease-only everywhere (S5/S4). S2/S3 land+building purchases stripped; no P&I because no mortgage."),
("Debt", "Zero-debt base case (S4 §22.B) — S2's 'retained CF + debt' flywheel retained as dormant Debt Schedule option."),
("Revenue driver", "Factory-wholesale home ASP $85K/$175K (S4/S5) — NOT S3 kit prices ($54K, a component of a different product) and NOT rents."),
("Waterfall", "Actual LPA waterfall (capital → 8% pref → catch-up → 80/20) replaces S2's flat 65% LP-share heuristic (variance disclosed on Exit tab)."),
("", ""),
("OPEN ITEMS — ALL "+MIR+" (orange on Global Assumptions; blocking items marked ⚑)", ""),
("⚑ OKC asset appraisal & ownership split", "GA §11 — drives OKC investor/platform split; currently pro-rata to contribution."),
("⚑ Founders' factory pro forma (S4 App. C)", "COGS structure (materials/labor/freight %, fixed overhead) — placeholders calibrated to S2's $12M/factory EBITDA anchor."),
("⚑ Product mix & price scope bridge", "70/30 mix is a Dev-Model analog; confirm factory-wholesale scope of $85K/$175K."),
("Capital split of the $25M raise", "Equipment / leasehold / pre-opening / working capital breakdown."),
("Lease terms", "$/yr per facility; term; escalators."),
("Working capital days, maintenance capex, asset lives", "DSO/DIO/DPO, % of revenue, 10-yr SL."),
("State tax, inflation set, discount rate", "GA §9-10."),
("Region 2/4/5 names & final opening years", "S4 §22.A.2 — final region map."),
("Salaries", "Exec suite, GM, platform opex components."),
("Platform fee-stream exit multiple", "Placeholder 10x = regional multiple."),
("", ""),
("DISCLAIMER", "Draft management tool. Not an offer of securities. §1202 outcomes require per-region counsel opinions (S4 §17)."),
]
for k, (a, b) in enumerate(rows_txt):
    put(cv, 4+k, 1, a, font=(F_HDR if b == "" and a else F_CALC))
    put(cv, 4+k, 3, b)
widen(cv, {"A": 44, "C": 130})

# ------------------------------------------------- final tab order & save
ORDER = ["Cover & Sources", "Executive Dashboard", "Global Assumptions", "Factory Rollout", "Production Model",
         "Revenue Model", "COGS", "SG&A", "Platform Revenue", "Working Capital", "Capital Expenditures",
         "Debt Schedule", "Depreciation Schedule", "Income Statement", "Cash Flow", "Balance Sheet",
         "OKC Factory Model", "Standard Regional Model", "Regional Rollup", "Platform Rollup",
         "Exit Model", "Sensitivity Analysis"]
wb._sheets = [wb[n] for n in ORDER]
out = __file__.rsplit("/", 1)[0] + "/HFP_Master_Model.xlsx"
wb.save(out)
print("saved", out)
