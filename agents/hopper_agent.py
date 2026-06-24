"""
AGENT 3 \u2014 Hopper / Dashboard Agent
-----------------------------------
Reads the deal log (data/deal_log.csv) and builds the master pipeline
dashboard in house standard: a vertical \u00d7 status matrix, summary callouts,
a deal list, and a stage chart.  Drop new deals into the CSV (or have the
screening agent append via --append-log) and re-run to refresh.

Usage:
    python hopper_agent.py
    python hopper_agent.py --out /path/to/custom_dir/
Output: out/hopper_dashboard.xlsx
"""
import os, csv
import icframework as f
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference

THIN   = Side(style="thin", color="D5DCE3")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HDR_FILL  = PatternFill("solid", fgColor=f.NAVY)
SUB_FILL  = PatternFill("solid", fgColor=f.STEEL)
ALT_FILL  = PatternFill("solid", fgColor=f.LIGHT)
GOLD_FILL = PatternFill("solid", fgColor=f.GOLD)


def load_deals(path=f.DEAL_LOG):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def build(path=f.DEAL_LOG, out=None):
    """Build the hopper dashboard and return (out_path, total_deals, active_deals)."""
    out      = out or os.path.join(f.OUT, "hopper_dashboard.xlsx")
    deals    = load_deals(path)
    statuses = f.DEAL_STATUSES
    verticals = f.VERTICALS

    wb = Workbook()
    ws = wb.active
    ws.title = "Hopper Dashboard"
    ws.sheet_view.showGridLines = False

    def style(cell, *, bold=False, color="000000", fill=None, size=11,
              align="left", border=True, font=f.BODY_FONT):
        cell.font      = Font(name=font, bold=bold, color=color, size=size)
        if fill:
            cell.fill  = fill
        if border:
            cell.border = BORDER
        cell.alignment = Alignment(horizontal=align, vertical="center", wrap_text=True)

    # Title
    ws.merge_cells("A1:I1")
    style(ws["A1"], bold=True, color="FFFFFF", fill=HDR_FILL, size=16,
          font=f.HEAD_FONT, border=False)
    ws["A1"] = "D1 Real Estate \u2014 Deal Hopper Dashboard"
    ws.merge_cells("A2:I2")
    style(ws["A2"], color=f.STEEL, size=10, border=False)
    ws["A2"] = f"Pipeline by vertical and stage  \u00b7  {len(deals)} active deals"
    ws.row_dimensions[1].height = 28

    # Vertical \u00d7 status matrix
    r0 = 4
    ws.cell(r0, 1, "Vertical \u2193  /  Stage \u2192")
    style(ws.cell(r0, 1), bold=True, color="FFFFFF", fill=HDR_FILL, size=10)
    for j, st in enumerate(statuses):
        c = ws.cell(r0, 2 + j, st)
        style(c, bold=True, color="FFFFFF", fill=HDR_FILL, size=10, align="center")
    ws.cell(r0, 2 + len(statuses), "Total")
    style(ws.cell(r0, 2 + len(statuses)), bold=True, color="FFFFFF",
          fill=GOLD_FILL, size=10, align="center")

    for i, v in enumerate(verticals):
        rr = r0 + 1 + i
        style(ws.cell(rr, 1, v), bold=True, color=f.INK,
              fill=(ALT_FILL if i % 2 else None), size=10)
        for j, st in enumerate(statuses):
            n = sum(1 for d in deals if d["vertical"] == v and d["status"] == st)
            c = ws.cell(rr, 2 + j, n if n else None)
            style(c, color=f.INK, fill=(ALT_FILL if i % 2 else None), align="center")
            if n:
                c.font = Font(name=f.BODY_FONT, bold=True, color=f.NAVY)
        first = ws.cell(rr, 2).coordinate
        last  = ws.cell(rr, 1 + len(statuses)).coordinate
        tc    = ws.cell(rr, 2 + len(statuses))
        tc.value = f"=SUM({first}:{last})"
        style(tc, bold=True, color=f.NAVY, fill=(ALT_FILL if i % 2 else None), align="center")

    # Totals row
    tr = r0 + 1 + len(verticals)
    style(ws.cell(tr, 1, "Total"), bold=True, color="FFFFFF", fill=SUB_FILL, size=10)
    for j in range(len(statuses) + 1):
        col = ws.cell(tr, 2 + j).column_letter
        c   = ws.cell(tr, 2 + j)
        c.value = f"=SUM({col}{r0+1}:{col}{tr-1})"
        style(c, bold=True, color="FFFFFF", fill=SUB_FILL, align="center")

    # Summary callouts
    sr     = tr + 2
    active = [d for d in deals if d["status"] not in ("Approved", "Rejected")]
    summ   = [
        ("In hopper (active)", len(active)),
        ("Approved",           sum(1 for d in deals if d["status"] == "Approved")),
        ("Rejected",           sum(1 for d in deals if d["status"] == "Rejected")),
        ("At IC / DD",         sum(1 for d in deals if d["status"] in ("IC Review", "Due Diligence"))),
    ]
    for k, (lab, val) in enumerate(summ):
        cc = sr + k
        style(ws.cell(cc, 1, lab), bold=True, color=f.STEEL, size=10, border=False)
        style(ws.cell(cc, 2, val), bold=True, color=f.NAVY, size=12, border=False, align="left")

    # Deal list
    dl = sr + len(summ) + 2
    headers = ["Deal", "Vertical", "Market", "Stage", "Score", "IRR", "Notes"]
    for j, h in enumerate(headers):
        style(ws.cell(dl, 1 + j, h), bold=True, color="FFFFFF", fill=HDR_FILL, size=10)
    for i, d in enumerate(deals):
        rr   = dl + 1 + i
        vals = [
            d["deal"], d["vertical"], d["market"], d["status"],
            (f"{float(d['score']):.3f}" if d["score"] else "\u2014"),
            (f"{float(d['irr'])*100:.1f}%" if d["irr"] else "\u2014"),
            d["notes"],
        ]
        for j, val in enumerate(vals):
            c = ws.cell(rr, 1 + j, val)
            style(c, color=f.INK, fill=(ALT_FILL if i % 2 else None), size=9,
                  align=("center" if j in (4, 5) else "left"))
            if j == 3:   # status colour coding
                if d["status"] == "Approved":
                    c.font = Font(name=f.BODY_FONT, bold=True, color="2E7D52")
                elif d["status"] == "Rejected":
                    c.font = Font(name=f.BODY_FONT, bold=True, color="B23A3A")

    # Column widths
    for col, w in {
        "A": 22, "B": 18, "C": 26, "D": 14,
        "E": 9,  "F": 8,  "G": 34, "H": 10, "I": 10,
    }.items():
        ws.column_dimensions[col].width = w

    # Bar chart: deals by stage
    chart          = BarChart()
    chart.type     = "col"
    chart.title    = "Deals by stage"
    chart.height   = 7
    chart.width    = 16
    data = Reference(ws, min_col=2, max_col=1 + len(statuses), min_row=tr, max_row=tr)
    cats = Reference(ws, min_col=2, max_col=1 + len(statuses), min_row=r0, max_row=r0)
    chart.add_data(data, from_rows=True)
    chart.set_categories(cats)
    chart.legend = None
    ws.add_chart(chart, f"A{dl + len(deals) + 3}")

    wb.save(out)
    return out, len(deals), len(active)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="IC Agent Toolkit \u2014 deal hopper dashboard")
    ap.add_argument("--out", default=None, help="Output directory (default: agents/out/)")
    a = ap.parse_args()
    out_path = os.path.join(a.out, "hopper_dashboard.xlsx") if a.out else None
    out, n, active = build(out=out_path)
    print(f"Hopper dashboard built: {os.path.basename(out)}")
    print(f"  {n} deals  \u00b7  {active} in hopper (active)")
