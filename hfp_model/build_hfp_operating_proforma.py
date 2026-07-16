#!/usr/bin/env python3
"""
HFP — EXECUTIVE OPERATING PRO FORMA (Armor-style)
==================================================
Generates HFP_Operating_ProForma.xlsx: ONE clean operating pro forma modeled
on the "2026 Armor Operating Pro Forma" layout — vertical single-flow sheet,
bold navy section headers in col A, line items in col C, size-9 accounting
numbers, filled Total column, minimal color, no supporting-schedule sprawl.

Three sheets only:
  1. HFP Pro Forma           — Key Assumptions -> Rollout -> Revenue -> COGS ->
                               OpEx -> EBITDA -> CapEx -> Cash Flow -> Platform ->
                               Consolidated Summary.  Columns = 2026-2036 + Total.
  2. OKC Year 1 Monthly      — Armor's exact monthly geometry (Jan-Dec 2026),
                               OKC special capitalization on top.
  3. Standard Region Template— the repeatable region: one raise, Factory 2 from
                               retained earnings, no second raise (Years 1-10, 2026$).

Assumptions exist ONCE (Key Assumptions section); every formula references them.
Anything not present in the HFP source materials is marked
"Management Input Required" (red) with a transparent placeholder so the model
still calculates. Values carry over from the validated master model
(build_hfp_model.py) — the two workbooks tie.
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

NAVY = "FF002060"
F_T1  = Font(bold=True, size=11)
F_T2  = Font(bold=True, size=10)
F_SEC = Font(bold=True, size=10, color=NAVY)
F_LBL = Font(size=10)
F_LBI = Font(size=10, italic=True, color="FF595959")
F_NUM = Font(size=9)
F_NUMB= Font(size=9, bold=True)
F_IN  = Font(size=9, color="FF0070C0", bold=True)
F_MIR = Font(size=9, color="FFC00000", bold=True)
FILL_TOT = PatternFill("solid", fgColor="FFEDE4D3")   # tan total column (Armor)
FILL_HDR = PatternFill("solid", fgColor="FFF2F2F2")   # light grey year header
FILL_SUB = PatternFill("solid", fgColor="FFF7F4EC")   # subtotal band
FILL_MIRV= PatternFill("solid", fgColor="FFFDEADA")   # MIR value cell
ACC  = '_(* #,##0_);_(* \\(#,##0\\);_(* "-"??_);_(@_)'
ACC0 = '#,##0'
PCT  = '0.0%'
MIR  = "Management Input Required"

YRS = list(range(2026, 2037))         # F..P
FC = 6                                 # first year col = F
def YL(i): return get_column_letter(FC + i)
TOTC = FC + len(YRS)                   # Q = total col (17)
TL = get_column_letter(TOTC)

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "HFP Pro Forma"

def put(w, r, c, v, font=F_LBL, fill=None, fmt=None, align=None):
    cell = w.cell(row=r, column=c, value=v)
    cell.font = font
    if fill: cell.fill = fill
    if fmt: cell.number_format = fmt
    if align: cell.alignment = Alignment(horizontal=align)
    return cell

def sechdr(w, r, txt):
    put(w, r, 1, txt, font=F_SEC)

def yearhdr(w, r):
    for i, y in enumerate(YRS):
        put(w, r, FC+i, y, font=F_NUMB, fill=FILL_HDR, fmt='0', align="center")
    put(w, r, TOTC, "Total", font=F_NUMB, fill=FILL_TOT, align="center")

def yrow(w, r, label, fn, hdr, fmt=ACC, bold=False, total=True, fill=None, note=None):
    """One time-series row. fn(i, col_letter, hdr_row) -> formula/value."""
    put(w, r, 3, label, font=(F_T2 if bold else F_LBL))
    fo = F_NUMB if bold else F_NUM
    for i in range(len(YRS)):
        cl = YL(i)
        put(w, r, FC+i, fn(i, cl, hdr), font=fo, fill=fill, fmt=fmt)
    if total:
        put(w, r, TOTC, f"=SUM(F{r}:P{r})", font=F_NUMB, fill=FILL_TOT, fmt=fmt)
    if note:
        put(w, r, TOTC+1, note, font=F_LBI)

# ============================================================ title block
put(ws, 1, 1, "House Factory Platform", font=F_T1)
put(ws, 2, 1, "Operating Pro Forma — 2026-2036", font=F_T2)
put(ws, 3, 1, "5 Regions · 10 Factories · Oklahoma City Launch 2026", font=F_T2)
put(ws, 4, 1, "All facilities leased · Each region an independent C-corp · No dividends — earnings fund Factory 2", font=F_LBL)
put(ws, 5, 1, "Blue = input.  Red = " + MIR + " (placeholder shown so the model calculates; confirm before investor use).", font=F_LBI)

# ============================================================ 1. KEY ASSUMPTIONS
sechdr(ws, 7, "1.  KEY ASSUMPTIONS")
A = {}  # short key -> row
def arow(r, label, value, fmt, key, status="", formula=False):
    put(ws, r, 3, label)
    v = put(ws, r, 6, value, font=(F_NUM if formula else (F_MIR if status == MIR else F_IN)),
            fill=(FILL_MIRV if status == MIR else None), fmt=fmt)
    if status:
        put(ws, r, 8, status, font=(F_MIR if status == MIR else F_LBI))
    A[key] = r
    return r

put(ws, 8, 3, "Pricing & Production", font=F_T2)
arow(9,  "Average Selling Price — Single-Section Home", 85000, ACC0, "asp1", "Transcript / business plan (factory wholesale, home only)")
arow(10, "Average Selling Price — 3-Bedroom Home", 175000, ACC0, "asp3", "Transcript / business plan")
arow(11, "Product Mix — % Single-Section", 0.70, PCT, "mix", MIR)
arow(12, "Blended Average Selling Price", "=F11*F9+(1-F11)*F10", ACC0, "asp", "Calculated", formula=True)
arow(13, "Factory Capacity (homes / yr, single shift)", 500, ACC0, "cap", "Regional Factory Model v2.0")
arow(14, "Production Ramp — Year 1", 0.50, PCT, "r1", "Business plan: Yr-1 ~50-60% of nameplate")
arow(15, "Production Ramp — Year 2", 0.80, PCT, "r2", "Calibrated to source EBITDA ramp $2M/$6M/$12M")
arow(16, "Production Ramp — Year 3+", 1.00, PCT, "r3", "Steady state")
arow(17, "OKC Year-1 Ramp (relaunch of existing plant)", 0.60, PCT, "okr", MIR)
put(ws, 18, 3, "Cost of Goods Sold", font=F_T2)
arow(19, "Materials (% of revenue)", 0.47, PCT, "mat", MIR)
arow(20, "Direct Labor (% of revenue)", 0.15, PCT, "lab", MIR)
arow(21, "Freight (% of revenue)", 0.04, PCT, "frt", MIR)
arow(22, "Utilities & Equipment Maintenance (% of revenue)", 0.04, PCT, "utl", MIR)
arow(23, "Factory Overhead ($ / factory / yr)", 2000000, ACC0, "foh", MIR)
arow(24, "Facility Lease Expense ($ / factory / yr)", 1200000, ACC0, "lease", MIR)
put(ws, 25, 3, "Operating Expenses", font=F_T2)
arow(26, "Regional Office & Administration ($ / region / yr)", 1200000, ACC0, "regadm", MIR)
arow(27, "Regional General Manager Salary (one per region)", 250000, ACC0, "gm", MIR)
arow(28, "Founders' Payroll — carried by OKC until 2nd factory opens", 750000, ACC0, "found", MIR)
arow(29, "Sales & Marketing (% of revenue)", 0.015, PCT, "sm", MIR)
arow(30, "Corporate (Platform) Payroll ($ / yr, from 2nd factory)", 1500000, ACC0, "corp", MIR)
arow(31, "Engineering ($ / yr)", 200000, ACC0, "eng", MIR)
arow(32, "Professional Fees — legal, accounting, audit ($ / yr)", 300000, ACC0, "prof", MIR)
arow(33, "Insurance ($ / yr)", 150000, ACC0, "ins", MIR)
arow(34, "Office Expense ($ / yr)", 50000, ACC0, "off", MIR)
arow(35, "Technology — ERP & IT ($ / yr)", 300000, ACC0, "tech", MIR)
arow(36, "Administrative Expenses (% of revenue)", 0.005, PCT, "adm", MIR)
arow(37, "Pre-Opening Cost per New Factory", 2000000, ACC0, "pre", MIR)
put(ws, 38, 3, "Capital & Working Capital", font=F_T2)
arow(39, "Equipment per Factory", 12000000, ACC0, "equip", MIR)
arow(40, "Leasehold Improvements & Technology per Factory", 5000000, ACC0, "lhi", MIR)
arow(41, "Maintenance CapEx (% of revenue)", 0.015, PCT, "mcap", MIR)
arow(42, "Accounts Receivable (days)", 15, ACC0, "dso", MIR)
arow(43, "Inventory (days of COGS)", 45, ACC0, "dio", MIR)
arow(44, "Accounts Payable (days of COGS)", 30, ACC0, "dpo", MIR)
put(ws, 45, 3, "Structure, Macro & Exit", font=F_T2)
arow(46, "Management Fee (% of regional revenue)", 0.07, PCT, "fee", "Transcript / business plan — scenario lever")
arow(47, "Platform Ownership — Standard Region (for no cash)", 0.10, PCT, "pown", "Transcript / business plan (investors 90%)")
arow(48, "Standard Region Equity Raise (one only, indexed at launch)", 30000000, ACC0, "raise", "Plan range $25-30M; $30M required by cash test")
arow(49, "Inflation — General", 0.025, PCT, "infl", MIR)
arow(50, "Inflation — Wages", 0.03, PCT, "winfl", MIR)
arow(51, "ASP Escalation", 0.02, PCT, "aesc", MIR)
arow(52, "Corporate Tax Rate (21% federal + state)", 0.25, PCT, "tax", "State portion " + MIR)
arow(53, "Depreciation Life (years, straight-line)", 10, ACC0, "dlife", MIR)
arow(54, "Exit Multiple (EV / EBITDA, Year-10)", 10, '0.0"x"', "xm", "Regional Factory Model v2.0 (Y5 alt = 8x)")
put(ws, 55, 3, "Oklahoma City (special launch capitalization)", font=F_T2)
arow(56, "OKC — Founder Asset Contribution (equipment, lifts, IP)", 8000000, ACC0, "okasset", MIR + " — independent appraisal")
arow(57, "OKC — New Investor Cash", 20000000, ACC0, "okcash", MIR)
arow(58, "OKC — Plant Modernization CapEx (2026)", 10000000, ACC0, "okmod", "Regional Factory Model v2.0")
arow(59, "OKC — Platform Ownership (pro-rata to contribution)", "=F56/(F56+F57)", PCT, "okpo", "Derived — final split is negotiated", formula=True)

def a(key):   return f"$F${A[key]}"

# ============================================================ 2. FACTORY ROLLOUT
sechdr(ws, 62, "2.  FACTORY ROLLOUT SCHEDULE")
hdrs = [(3,"Region"),(4,"Factory"),(6,"Opening Year"),(7,"Status"),(8,"Capacity"),(9,"Annual Production (steady)"),(10,"Capital Required"),(11,"Year-1 Ramp"),(12,"Funding")]
for c,h in hdrs: put(ws, 63, c, h, font=F_T2, fill=FILL_HDR)
ROLL = [  # (region, fac#, open, is_okc)
    ("Central — Oklahoma City", 1, 2026, True),
    ("Central — Oklahoma City", 2, 2029, False),
    ("Region 2 (" + MIR + ")", 1, 2027, False),
    ("Region 2", 2, 2030, False),
    ("Region 3 — Texas (DFW)", 1, 2028, False),
    ("Region 3 — Texas (Houston)", 2, 2031, False),
    ("Region 4 (" + MIR + ")", 1, 2030, False),
    ("Region 4", 2, 2033, False),
    ("Region 5 (" + MIR + ")", 1, 2031, False),
    ("Region 5", 2, 2034, False),
]
R0 = 64                                   # rollout rows 64-73
for k, (rg, fno, oy, okc) in enumerate(ROLL):
    r = R0 + k
    put(ws, r, 3, rg, font=F_LBL)
    put(ws, r, 4, fno, font=F_NUM, fmt='0')
    put(ws, r, 6, oy, font=F_IN, fmt='0')
    put(ws, r, 7, f'=IF($F{r}<=2026,"Operational","Opens "&$F{r})', font=F_NUM)
    put(ws, r, 8, f"={a('cap')}", font=F_NUM, fmt=ACC0)
    put(ws, r, 9, f"={a('cap')}", font=F_NUM, fmt=ACC0)
    if okc:
        put(ws, r, 10, f"={a('okcash')}+{a('okasset')}", font=F_NUM, fmt=ACC)
        put(ws, r, 11, f"={a('okr')}", font=F_NUM, fmt=PCT)
        put(ws, r, 12, "Founder assets + investor cash", font=F_LBI)
    else:
        if fno == 1:
            put(ws, r, 10, f"={a('raise')}*(1+{a('infl')})^($F{r}-2026)", font=F_NUM, fmt=ACC)
            put(ws, r, 12, "Single 90/10 equity raise", font=F_LBI)
        else:
            put(ws, r, 10, f"=({a('equip')}+{a('lhi')})*(1+{a('infl')})^($F{r}-2026)", font=F_NUM, fmt=ACC)
            put(ws, r, 12, "Retained earnings — no new raise", font=F_LBI)
        put(ws, r, 11, f"={a('r1')}", font=F_NUM, fmt=PCT)
RL, RH = R0, R0 + 9                        # 64..73
put(ws, 74, 3, "Total — 10 factories", font=F_T2)
put(ws, 74, 10, f"=SUM(J{RL}:J{RH})", font=F_NUMB, fmt=ACC, fill=FILL_TOT)

# ============================================================ 3. REVENUE
sechdr(ws, 77, "3.  REVENUE")
yearhdr(ws, 78)
H3 = 78
yrow(ws, 79, "Operational Factories", lambda i,cl,h: f"=SUMPRODUCT(($F${RL}:$F${RH}<={cl}${h})*1)", H3, fmt=ACC0, total=False)
yrow(ws, 80, "Active Regions", lambda i,cl,h: f"=SUMPRODUCT(($F${RL}:$F${RH}<={cl}${h})*($D${RL}:$D${RH}=1))", H3, fmt=ACC0, total=False)
put(ws, 81, 3, "Homes Produced", font=F_T2)
for k in range(10):
    rr = RL + k
    r = 82 + k                             # 82..91
    lbl = f"{ROLL[k][0].replace(' ('+MIR+')','')} — Factory {ROLL[k][1]}"
    yrow(ws, r, lbl, lambda i,cl,h,rr=rr: f"=IF({cl}${h}<$F{rr},0,$H{rr}*IF({cl}${h}=$F{rr},$K{rr},IF({cl}${h}=$F{rr}+1,{a('r2')},{a('r3')})))", H3, fmt=ACC0)
yrow(ws, 92, "Total Homes Produced", lambda i,cl,h: f"=SUM({cl}82:{cl}91)", H3, fmt=ACC0, bold=True, fill=FILL_SUB)
yrow(ws, 93, "Blended Average Selling Price", lambda i,cl,h: f"={a('asp')}*(1+{a('aesc')})^({cl}${h}-2026)", H3, fmt=ACC0, total=False)
yrow(ws, 94, "Factory Revenue", lambda i,cl,h: f"={cl}92*{cl}93", H3, bold=True)
yrow(ws, 95, "Platform Management Fees (7% — paid by regions to Platform)", lambda i,cl,h: f"={a('fee')}*{cl}94", H3)
yrow(ws, 96, "Intercompany Elimination (fee nets out in consolidation)", lambda i,cl,h: f"=-{cl}95", H3)
yrow(ws, 97, "Total Revenue (consolidated)", lambda i,cl,h: f"={cl}94+{cl}95+{cl}96", H3, bold=True, fill=FILL_SUB)

# ============================================================ 4. COGS
sechdr(ws, 100, "4.  COST OF GOODS SOLD")
yearhdr(ws, 101)
H4 = 101
yrow(ws, 102, "Materials", lambda i,cl,h: f"={a('mat')}*{cl}$94", H4)
yrow(ws, 103, "Direct Labor", lambda i,cl,h: f"={a('lab')}*{cl}$94", H4)
yrow(ws, 104, "Freight", lambda i,cl,h: f"={a('frt')}*{cl}$94", H4)
yrow(ws, 105, "Utilities & Equipment Maintenance", lambda i,cl,h: f"={a('utl')}*{cl}$94", H4)
yrow(ws, 106, "Factory Overhead", lambda i,cl,h: f"={cl}$79*{a('foh')}*(1+{a('infl')})^({cl}${h}-2026)", H4)
yrow(ws, 107, "Facility Leases", lambda i,cl,h: f"={cl}$79*{a('lease')}*(1+{a('infl')})^({cl}${h}-2026)", H4)
yrow(ws, 108, "Total COGS", lambda i,cl,h: f"=SUM({cl}102:{cl}107)", H4, bold=True, fill=FILL_SUB)
yrow(ws, 109, "Gross Profit", lambda i,cl,h: f"={cl}94-{cl}108", H4, bold=True)
yrow(ws, 110, "Gross Margin", lambda i,cl,h: f"=IF({cl}94=0,0,{cl}109/{cl}94)", H4, fmt=PCT, total=False)

# ============================================================ 5. OPERATING EXPENSES
sechdr(ws, 113, "5.  OPERATING EXPENSES")
yearhdr(ws, 114)
H5 = 114
w = f"(1+{a('winfl')})^"
g = f"(1+{a('infl')})^"
yrow(ws, 115, "Corporate Payroll (Platform — from 2nd factory onward)", lambda i,cl,h: f"=IF({cl}$79>=2,{a('corp')}*{w}({cl}${h}-2026),0)", H5)
yrow(ws, 116, "Regional Payroll (founders at OKC, then one GM per region)", lambda i,cl,h: f"=IF({cl}$79<2,{a('found')},{cl}$80*{a('gm')})*{w}({cl}${h}-2026)", H5)
yrow(ws, 117, "Regional Office & Administration", lambda i,cl,h: f"={cl}$80*{a('regadm')}*{g}({cl}${h}-2026)", H5)
yrow(ws, 118, "Sales & Marketing", lambda i,cl,h: f"={a('sm')}*{cl}$94", H5)
yrow(ws, 119, "Engineering", lambda i,cl,h: f"={a('eng')}*{g}({cl}${h}-2026)", H5)
yrow(ws, 120, "Professional Fees", lambda i,cl,h: f"={a('prof')}*{g}({cl}${h}-2026)", H5)
yrow(ws, 121, "Insurance", lambda i,cl,h: f"={a('ins')}*{g}({cl}${h}-2026)", H5)
yrow(ws, 122, "Office Expense", lambda i,cl,h: f"={a('off')}*{g}({cl}${h}-2026)", H5)
yrow(ws, 123, "Technology", lambda i,cl,h: f"={a('tech')}*{g}({cl}${h}-2026)", H5)
yrow(ws, 124, "Administrative Expenses", lambda i,cl,h: f"={a('adm')}*{cl}$94", H5)
yrow(ws, 125, "Pre-Opening Costs (new factories)", lambda i,cl,h: f"=SUMPRODUCT(($F${RL}:$F${RH}={cl}${h})*1)*{a('pre')}*{g}({cl}${h}-2026)", H5)
yrow(ws, 126, "Total Operating Expenses", lambda i,cl,h: f"=SUM({cl}115:{cl}125)", H5, bold=True, fill=FILL_SUB)

# ============================================================ 6. EBITDA
sechdr(ws, 129, "6.  EBITDA")
yearhdr(ws, 130)
H6 = 130
yrow(ws, 131, "Total Revenue", lambda i,cl,h: f"={cl}97", H6)
yrow(ws, 132, "Less:  Cost of Goods Sold", lambda i,cl,h: f"=-{cl}108", H6)
yrow(ws, 133, "Gross Profit", lambda i,cl,h: f"={cl}131+{cl}132", H6, bold=True)
yrow(ws, 134, "Less:  Operating Expenses", lambda i,cl,h: f"=-{cl}126", H6)
yrow(ws, 135, "EBITDA", lambda i,cl,h: f"={cl}133+{cl}134", H6, bold=True, fill=FILL_TOT)
yrow(ws, 136, "EBITDA Margin", lambda i,cl,h: f"=IF({cl}131=0,0,{cl}135/{cl}131)", H6, fmt=PCT, total=False)

# ============================================================ 7. CAPITAL EXPENDITURES
sechdr(ws, 139, "7.  CAPITAL EXPENDITURES")
yearhdr(ws, 140)
H7 = 140
yrow(ws, 141, "Equipment & Manufacturing Assets (new factories)", lambda i,cl,h: f"=SUMPRODUCT(($F${RL+1}:$F${RH}={cl}${h})*1)*{a('equip')}*{g}({cl}${h}-2026)", H7)
yrow(ws, 142, "Leasehold Improvements & Technology (new factories)", lambda i,cl,h: f"=SUMPRODUCT(($F${RL+1}:$F${RH}={cl}${h})*1)*{a('lhi')}*{g}({cl}${h}-2026)", H7)
yrow(ws, 143, "OKC Plant Modernization", lambda i,cl,h: f"=IF({cl}${h}=$F${RL},{a('okmod')},0)", H7)
yrow(ws, 144, "Maintenance CapEx", lambda i,cl,h: f"={a('mcap')}*{cl}$94", H7)
yrow(ws, 145, "Total CapEx", lambda i,cl,h: f"=SUM({cl}141:{cl}144)", H7, bold=True, fill=FILL_SUB)
yrow(ws, 146, "Memo:  Founder Contributed Equipment (non-cash)", lambda i,cl,h: f"=IF({cl}${h}=$F${RL},{a('okasset')},0)", H7)

# ============================================================ 8. CASH FLOW
sechdr(ws, 149, "8.  CASH FLOW")
yearhdr(ws, 150)
H8 = 150
yrow(ws, 151, "EBITDA", lambda i,cl,h: f"={cl}135", H8)
yrow(ws, 152, "Memo:  Depreciation (auto from CapEx, straight-line)", lambda i,cl,h: f"=(SUM($F$145:{cl}145)+SUM($F$146:{cl}146))/{a('dlife')}", H8, total=False)
yrow(ws, 153, "Less:  Cash Taxes (on EBITDA less depreciation)", lambda i,cl,h: f"=-{a('tax')}*MAX(0,{cl}151-{cl}152)", H8)
yrow(ws, 154, "Less:  CapEx", lambda i,cl,h: f"=-{cl}145", H8)
yrow(ws, 155, "Memo:  Net Working Capital (AR + inventory - AP)", lambda i,cl,h: f"={a('dso')}/365*{cl}$94+({a('dio')}-{a('dpo')})/365*{cl}$108", H8, total=False)
yrow(ws, 156, "Less:  Working Capital Changes", lambda i,cl,h: (f"=-{cl}155" if i==0 else f"=-({cl}155-{YL(i-1)}155)"), H8)
yrow(ws, 157, "Operating Cash Flow", lambda i,cl,h: f"={cl}151+{cl}153+{cl}154+{cl}156", H8, bold=True)
yrow(ws, 158, "Plus:  Investor Equity Raises (one per region)", lambda i,cl,h:
     f"=IF({cl}${h}=$F${RL},{a('okcash')},0)+{a('raise')}*{g}({cl}${h}-2026)*(($F${RL+2}={cl}${h})+($F${RL+4}={cl}${h})+($F${RL+6}={cl}${h})+($F${RL+8}={cl}${h}))", H8)
yrow(ws, 159, "Net Cash Flow", lambda i,cl,h: f"={cl}157+{cl}158", H8, bold=True)
yrow(ws, 160, "Beginning Cash", lambda i,cl,h: ("=0" if i==0 else f"={YL(i-1)}161"), H8, total=False)
yrow(ws, 161, "Ending Cash", lambda i,cl,h: f"={cl}159+{cl}160", H8, bold=True, fill=FILL_TOT, total=False)
put(ws, 162, 3, "Taxes shown without loss carryforward for simplicity; each region actually pays tax separately (see master model).", font=F_LBI)

# ============================================================ 9. PLATFORM REVENUE
sechdr(ws, 165, "9.  PLATFORM REVENUE (House Factory Platform LLC — parent, standalone)")
yearhdr(ws, 166)
H9 = 166
yrow(ws, 167, "Management Fee Revenue (7% of regional revenue)", lambda i,cl,h: f"={cl}95", H9, bold=True)
yrow(ws, 168, "Memo:  Fee Revenue per Operational Factory", lambda i,cl,h: f"=IF({cl}$79=0,0,{cl}167/{cl}$79)", H9, total=False)
yrow(ws, 169, "Less:  Platform Payroll", lambda i,cl,h: f"=-{cl}115", H9)
yrow(ws, 170, "Less:  Platform Operating Expenses", lambda i,cl,h: f"=-SUM({cl}119:{cl}124)", H9)
yrow(ws, 171, "Platform EBITDA", lambda i,cl,h: f"={cl}167+{cl}169+{cl}170", H9, bold=True, fill=FILL_TOT)
yrow(ws, 172, "Platform EBITDA Margin", lambda i,cl,h: f"=IF({cl}167=0,0,{cl}171/{cl}167)", H9, fmt=PCT, total=False)
put(ws, 173, 3, "Platform also owns 10% of every standard region (OKC per contribution split) for no cash — monetized at exit, not in EBITDA.", font=F_LBI)
put(ws, 174, 3, "Platform expenses above are the corporate lines from Section 5 — shown here to present the parent standalone; no double count.", font=F_LBI)

# ============================================================ 10. CONSOLIDATED SUMMARY
sechdr(ws, 177, "10.  CONSOLIDATED SUMMARY")
yearhdr(ws, 178)
HS = 178
yrow(ws, 179, "Total Factories", lambda i,cl,h: f"={cl}79", HS, fmt=ACC0, total=False)
yrow(ws, 180, "Homes Produced", lambda i,cl,h: f"={cl}92", HS, fmt=ACC0)
yrow(ws, 181, "Cumulative Homes", lambda i,cl,h: f"=SUM($F$92:{cl}92)", HS, fmt=ACC0, total=False)
yrow(ws, 182, "Total Revenue", lambda i,cl,h: f"={cl}97", HS)
yrow(ws, 183, "Gross Profit", lambda i,cl,h: f"={cl}109", HS)
yrow(ws, 184, "EBITDA", lambda i,cl,h: f"={cl}135", HS, bold=True)
yrow(ws, 185, "Operating Cash Flow", lambda i,cl,h: f"={cl}157", HS)
yrow(ws, 186, "Ending Cash", lambda i,cl,h: f"={cl}161", HS, total=False)
yrow(ws, 187, "Platform Revenue", lambda i,cl,h: f"={cl}167", HS)
yrow(ws, 188, "Platform EBITDA", lambda i,cl,h: f"={cl}171", HS)
yrow(ws, 189, "Capital Invested (cumulative, incl. contributed assets)", lambda i,cl,h: f"=SUM($F$158:{cl}158)+SUM($F$146:{cl}146)", HS, total=False)
put(ws, 191, 3, "Valuation (Year-10 exit)", font=F_T2)
put(ws, 192, 3, "Enterprise Value — 10x 2036 EBITDA")
put(ws, 192, 6, f"=$P$135*{a('xm')}", font=F_NUMB, fmt=ACC)
put(ws, 193, 3, "Total Capital Invested")
put(ws, 193, 6, "=P189", font=F_NUM, fmt=ACC)
put(ws, 194, 3, "Investor Equity Value (≈90% gross, before promote)")
put(ws, 194, 6, "=0.9*F192", font=F_NUM, fmt=ACC)
put(ws, 195, 3, "Investor MOIC (gross)")
put(ws, 195, 6, "=F194/F193", font=F_NUMB, fmt='0.00"x"')
put(ws, 196, 3, "Investor IRR (10-year, gross)")
put(ws, 196, 6, "=(F194/F193)^(1/10)-1", font=F_NUMB, fmt=PCT)
put(ws, 197, 3, "Gross of the 8% pref / 20% promote waterfall and §1202 benefits — full exit waterfall lives in the master model (HFP_Master_Model.xlsx).", font=F_LBI)

# column widths + freeze
ws.column_dimensions['A'].width = 4
ws.column_dimensions['B'].width = 2
ws.column_dimensions['C'].width = 52
ws.column_dimensions['D'].width = 8
ws.column_dimensions['E'].width = 2
for i in range(len(YRS)):
    ws.column_dimensions[YL(i)].width = 12.5
ws.column_dimensions[TL].width = 14.5
ws.column_dimensions[get_column_letter(TOTC+1)].width = 60
ws.freeze_panes = "F8"

# ============================================================ SHEET 2 — OKC YEAR 1 MONTHLY
ok = wb.create_sheet("OKC Year 1 Monthly")
P = "'HFP Pro Forma'!"
put(ok, 1, 1, "House Factory Platform — Oklahoma City (House Factory Central)", font=F_T1)
put(ok, 2, 1, "2026 Launch-Year Monthly Operating Pro Forma", font=F_T2)
put(ok, 3, 1, "Relaunch of the existing OKC plant — special capitalization; all later regions follow the Standard Region Template", font=F_LBL)
MOS = ["Jan-26","Feb-26","Mar-26","Apr-26","May-26","Jun-26","Jul-26","Aug-26","Sep-26","Oct-26","Nov-26","Dec-26"]
for m, lbl in enumerate(MOS):
    put(ok, 5, FC+m, lbl, font=F_NUMB, fill=FILL_HDR, align="center")
OT = FC + 12                                # total col R
OTL = get_column_letter(OT)
put(ok, 5, OT, "Total", font=F_NUMB, fill=FILL_TOT, align="center")

def orow(r, label, fn, fmt=ACC, bold=False, total=True, fill=None):
    put(ok, r, 3, label, font=(F_T2 if bold else F_LBL))
    fo = F_NUMB if bold else F_NUM
    for m in range(12):
        cl = get_column_letter(FC+m)
        put(ok, r, FC+m, fn(m, cl), font=fo, fill=fill, fmt=fmt)
    if total:
        put(ok, r, OT, f"=SUM(F{r}:Q{r})", font=F_NUMB, fill=FILL_TOT, fmt=fmt)

sechdr(ok, 7, "CAPITALIZATION & OWNERSHIP (from Key Assumptions)")
cap_rows = [
    ("Founder Asset Contribution (equipment, lifts, IP)", f"={P}$F${A['okasset']}", ACC, MIR + " — independent appraisal"),
    ("New Investor Cash", f"={P}$F${A['okcash']}", ACC, MIR),
    ("Total Capitalization", "=F8+F9", ACC, ""),
    ("Platform Ownership (pro-rata to contribution)", f"={P}$F${A['okpo']}", PCT, "Final split negotiated"),
    ("Investor Ownership", "=1-F11", PCT, ""),
    ("Plant Modernization CapEx", f"={P}$F${A['okmod']}", ACC, ""),
    ("Pre-Opening / Startup Costs", f"={P}$F${A['pre']}", ACC, MIR),
]
for k,(lbl,f,fm,st) in enumerate(cap_rows):
    put(ok, 8+k, 3, lbl)
    put(ok, 8+k, 6, f, font=F_NUM, fmt=fm)
    if st: put(ok, 8+k, 8, st, font=(F_MIR if MIR in st else F_LBI))

sechdr(ok, 16, "PRODUCTION")
orow(17, "Capacity Utilization (ramps 20% to 100%; averages the 60% Year-1 ramp)",
     lambda m,cl: f"=0.2+{m}*0.8/11", fmt=PCT, total=False)
orow(18, "Homes Produced", lambda m,cl: f"={P}$F${A['cap']}/12*{cl}17", fmt='0.0', bold=True)
sechdr(ok, 20, "REVENUE")
orow(21, "Factory Revenue (homes x blended ASP)", lambda m,cl: f"={cl}18*{P}$F${A['asp']}", bold=True)
sechdr(ok, 23, "COST OF GOODS SOLD")
orow(24, "Materials", lambda m,cl: f"={P}$F${A['mat']}*{cl}$21")
orow(25, "Direct Labor", lambda m,cl: f"={P}$F${A['lab']}*{cl}$21")
orow(26, "Freight", lambda m,cl: f"={P}$F${A['frt']}*{cl}$21")
orow(27, "Utilities & Equipment Maintenance", lambda m,cl: f"={P}$F${A['utl']}*{cl}$21")
orow(28, "Factory Overhead", lambda m,cl: f"={P}$F${A['foh']}/12")
orow(29, "Facility Lease", lambda m,cl: f"={P}$F${A['lease']}/12")
orow(30, "Total COGS", lambda m,cl: f"=SUM({cl}24:{cl}29)", bold=True, fill=FILL_SUB)
orow(31, "Gross Profit", lambda m,cl: f"={cl}21-{cl}30", bold=True)
sechdr(ok, 33, "OPERATING EXPENSES")
orow(34, "Founders' Payroll (Lance & Craig — OKC employees in Year 1)", lambda m,cl: f"={P}$F${A['found']}/12")
orow(35, "Regional Office & Administration", lambda m,cl: f"={P}$F${A['regadm']}/12")
orow(36, "Sales & Marketing", lambda m,cl: f"={P}$F${A['sm']}*{cl}$21")
orow(37, "Management Fee to Platform (7%)", lambda m,cl: f"={P}$F${A['fee']}*{cl}$21")
orow(38, "Pre-Opening Costs (spread across Year 1)", lambda m,cl: f"={P}$F${A['pre']}/12")
orow(39, "Total Operating Expenses", lambda m,cl: f"=SUM({cl}34:{cl}38)", bold=True, fill=FILL_SUB)
sechdr(ok, 41, "EBITDA")
orow(42, "EBITDA (OKC standalone — after management fee)", lambda m,cl: f"={cl}31-{cl}39", bold=True, fill=FILL_TOT)
sechdr(ok, 44, "CASH")
orow(45, "Plant Modernization CapEx (in service Q1)", lambda m,cl: (f"=-{P}$F${A['okmod']}/3" if m < 3 else "=0"))
orow(46, "Investor Cash In", lambda m,cl: (f"={P}$F${A['okcash']}" if m == 0 else "=0"))
orow(47, "Net Cash Flow", lambda m,cl: f"={cl}42+{cl}45+{cl}46", bold=True)
orow(48, "Ending Cash", lambda m,cl: (f"={cl}47" if m == 0 else f"={get_column_letter(FC+m-1)}48+{cl}47"), bold=True, fill=FILL_TOT, total=False)
put(ok, 50, 3, "Working capital and taxes are annual items — see the consolidated Cash Flow section on the HFP Pro Forma sheet.", font=F_LBI)
put(ok, 51, 3, "Check — Year-1 homes vs annual model (300 = 500 x 60%):", font=F_LBI)
put(ok, 51, 6, f"=R18-{P}$F${A['cap']}*{P}$F${A['okr']}", font=F_NUM, fmt=ACC0)
ok.column_dimensions['A'].width = 4; ok.column_dimensions['B'].width = 2
ok.column_dimensions['C'].width = 56; ok.column_dimensions['D'].width = 2; ok.column_dimensions['E'].width = 2
for m in range(12): ok.column_dimensions[get_column_letter(FC+m)].width = 11.5
ok.column_dimensions[OTL].width = 13.5
ok.column_dimensions[get_column_letter(OT+1)].width = 44
ok.freeze_panes = "F6"

# ============================================================ SHEET 3 — STANDARD REGION TEMPLATE
st = wb.create_sheet("Standard Region Template")
put(st, 1, 1, "House Factory Platform — Standard Region Template", font=F_T1)
put(st, 2, 1, "The repeatable model for every region after Oklahoma City (constant 2026 dollars)", font=F_T2)
put(st, 3, 1, "One equity raise · Investors 90% / Platform 10% for no cash · 7% management fee · Factory 2 in Year 4 funded entirely from retained earnings · No second raise", font=F_LBL)
NY = 10
for y in range(NY):
    put(st, 5, FC+y, f"Year {y+1}", font=F_NUMB, fill=FILL_HDR, align="center")
STT = FC + NY                              # total col P
put(st, 5, STT, "Total", font=F_NUMB, fill=FILL_TOT, align="center")
put(st, 6, 3, "Factory 2 opens in Year", font=F_LBL); put(st, 6, 6, 4, font=F_IN, fmt='0')

def srow(r, label, fn, fmt=ACC, bold=False, total=True, fill=None):
    put(st, r, 3, label, font=(F_T2 if bold else F_LBL))
    fo = F_NUMB if bold else F_NUM
    for y in range(NY):
        cl = get_column_letter(FC+y)
        put(st, r, FC+y, fn(y, cl), font=fo, fill=fill, fmt=fmt)
    if total:
        put(st, r, STT, f"=SUM(F{r}:O{r})", font=F_NUMB, fill=FILL_TOT, fmt=fmt)

ramp = lambda age: f"IF({age}=1,{P}$F${A['r1']},IF({age}=2,{P}$F${A['r2']},{P}$F${A['r3']}))"
sechdr(st, 8, "PRODUCTION")
srow(9,  "Homes — Factory 1", lambda y,cl: f"={P}$F${A['cap']}*{ramp(y+1)}", fmt=ACC0)
srow(10, "Homes — Factory 2 (opens Year 4, self-funded)", lambda y,cl: f"=IF({y+1}<$F$6,0,{P}$F${A['cap']}*{ramp(f'{y+1}-$F$6+1')})", fmt=ACC0)
srow(11, "Total Homes", lambda y,cl: f"={cl}9+{cl}10", fmt=ACC0, bold=True, fill=FILL_SUB)
sechdr(st, 13, "PROFIT & LOSS")
srow(14, "Revenue", lambda y,cl: f"={cl}11*{P}$F${A['asp']}", bold=True)
srow(15, "Variable COGS (materials, labor, freight, utilities)", lambda y,cl: f"=({P}$F${A['mat']}+{P}$F${A['lab']}+{P}$F${A['frt']}+{P}$F${A['utl']})*{cl}14")
srow(16, "Factory Overhead & Leases", lambda y,cl: f"=(1+({y+1}>=$F$6))*({P}$F${A['foh']}+{P}$F${A['lease']})")
srow(17, "Gross Profit", lambda y,cl: f"={cl}14-{cl}15-{cl}16", bold=True)
srow(18, "Operating Expenses (GM, office, S&M, pre-opening)", lambda y,cl:
     f"={P}$F${A['gm']}+{P}$F${A['regadm']}+{P}$F${A['sm']}*{cl}14+{P}$F${A['pre']}*(({y+1}=1)+({y+1}=$F$6))")
srow(19, "Management Fee to Platform (7%)", lambda y,cl: f"={P}$F${A['fee']}*{cl}14")
srow(20, "EBITDA", lambda y,cl: f"={cl}17-{cl}18-{cl}19", bold=True, fill=FILL_TOT)
srow(21, "Memo:  EBITDA per factory before fee (source anchor ~$12M)", lambda y,cl: f"=({cl}20+{cl}19)/(1+({y+1}>=$F$6))", total=False)
sechdr(st, 23, "CASH FLOW")
srow(24, "CapEx (Factory 1 Year 1, Factory 2 at open, + maintenance)", lambda y,cl:
     f"=({P}$F${A['equip']}+{P}$F${A['lhi']})*(({y+1}=1)+({y+1}=$F$6))+{P}$F${A['mcap']}*{cl}14")
srow(25, "Memo:  Depreciation (straight-line from CapEx)", lambda y,cl: f"=SUM($F$24:{cl}24)/{P}$F${A['dlife']}", total=False)
srow(26, "Cash Taxes (on EBITDA less depreciation)", lambda y,cl: f"={P}$F${A['tax']}*MAX(0,{cl}20-{cl}25)")
srow(27, "Memo:  Net Working Capital", lambda y,cl: f"={P}$F${A['dso']}/365*{cl}14+({P}$F${A['dio']}-{P}$F${A['dpo']})/365*({cl}15+{cl}16)", total=False)
srow(28, "Working Capital Changes", lambda y,cl: (f"={cl}27" if y==0 else f"={cl}27-{get_column_letter(FC+y-1)}27"))
srow(29, "Equity Raise (ONE only — Year 1)", lambda y,cl: (f"={P}$F${A['raise']}" if y==0 else "=0"))
srow(30, "Net Cash Flow", lambda y,cl: f"={cl}20-{cl}24-{cl}26-{cl}28+{cl}29", bold=True)
srow(31, "Ending Cash", lambda y,cl: (f"={cl}30" if y==0 else f"={get_column_letter(FC+y-1)}31+{cl}30"), bold=True, fill=FILL_TOT, total=False)
sechdr(st, 33, "CHECKS")
put(st, 34, 3, "Minimum cash over 10 years (must be ≥ 0 — proves the single raise is sufficient)")
put(st, 34, 6, "=MIN(F31:O31)", font=F_NUMB, fmt=ACC)
put(st, 34, 8, '=IF(MIN(F31:O31)>=0,"PASS — one raise; Factory 2 self-funded","REVIEW — raise or timing")', font=F_T2)
srow(32, "Memo:  cumulative years of positive operating cash flow", lambda y,cl:
     (f"=IF({cl}30-{cl}29>0,1,0)" if y==0 else f"={get_column_letter(FC+y-1)}32+IF({cl}30-{cl}29>0,1,0)"), fmt=ACC0, total=False)
put(st, 35, 3, "First cash-flow-positive year, before the raise (target ~Year 2 per business plan)")
put(st, 35, 6, "=MATCH(1,F32:O32,0)", font=F_NUMB, fmt='0')
st.column_dimensions['A'].width = 4; st.column_dimensions['B'].width = 2
st.column_dimensions['C'].width = 58; st.column_dimensions['D'].width = 2; st.column_dimensions['E'].width = 2
for y in range(NY): st.column_dimensions[get_column_letter(FC+y)].width = 11.5
st.column_dimensions[get_column_letter(STT)].width = 13.5
st.column_dimensions[get_column_letter(STT+2)].width = 40
st.freeze_panes = "F6"

out = __file__.rsplit("/", 1)[0] + "/HFP_Operating_ProForma.xlsx"
wb.save(out)
print("saved", out)
