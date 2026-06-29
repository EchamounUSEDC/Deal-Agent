"""Best-effort metric extraction from a candidate file — pro forma OR operating statement.

Handles many shapes the import button gets dropped on it:
  * `.xlsx` / `.xlsm` pro formas (labelled line items)
  * `.xls` legacy workbooks and `.csv`
  * `.zip` packages of financials (picks the most relevant statement inside)
  * T-12 / rolling-12 operating statements with monthly columns + a Total column

It returns a partly-filled :class:`Deal` plus notes on what it could and couldn't find.
Investment metrics that an operating statement simply doesn't contain (price/cap, IRR,
market) are left blank for the user to supply — they surface as gate failures, not guesses.
"""

from __future__ import annotations

import csv
import os
import zipfile
from typing import Optional

from .schema import Deal, INCOME, DEVELOPMENT

_RATE_FIELDS = {"going_in_cap", "exit_cap", "yield_on_cost", "dev_spread",
                "unlevered_irr", "levered_irr", "ltv", "opex_ratio"}
_LOC = ("county", "market", "location", "city", "msa", "cbsa", "submarket", "address")

# --- pro-forma line items: keyword(s) -> Deal field (first numeric on the row) ---
_PATTERNS = [
    (["exit cap"], "exit_cap"),
    (["syndicated cap rate"], "going_in_cap"),
    (["going-in cap", "going in cap", "year 1 cap", "in-place cap"], "going_in_cap"),
    (["net operating income", "noi"], "noi"),
    (["yield on cost", "yield-on-cost"], "yield_on_cost"),
    (["development spread", "dev. spread", "dev spread"], "dev_spread"),
    (["unlevered irr"], "unlevered_irr"),
    (["levered irr"], "levered_irr"),
    (["irr"], "unlevered_irr"),
    (["partnership level budget", "development budget", "total project cost",
      "total capitalization", "total cost"], "total_cost"),
    (["permanent debt", "construction financing", "mortgage", "loan amount", "debt"], "debt"),
    (["equity"], "equity"),
    (["net rentable", "nrsf"], "nrsf"),
    (["site acreage", "acreage", "acres"], "site_acreage"),
]

_SUPPORTED = (".xlsx", ".xlsm", ".xls", ".csv")
# When picking a file out of a .zip, prefer these name hints (earlier = better).
_ZIP_PRIORITY = ["rolling 12", "rolling12", "t-12", "t12", "trailing", "ttm", "annual",
                 "year to date", "ytd", "pro forma", "proforma", "underwriting",
                 "cash flow", "cashflow", "operating statement", "income statement"]
_EXT_RANK = {".xlsx": 0, ".xlsm": 1, ".xls": 2, ".csv": 3}


# Pro formas and operating statements live in the first few hundred rows / dozens of
# columns. Capping the scan keeps imports fast even on huge market-data workbooks.
_MAX_ROWS = 600
_MAX_COLS = 40


# ----------------------------- loading any format --------------------------------
def _iter_sheets(path: str):
    """Yield (sheet_name, rows) for a workbook/csv; rows are lists of cell values.

    Bounded to the top-left ``_MAX_ROWS`` x ``_MAX_COLS`` of each sheet for speed.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xlsm"):
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        for ws in wb.worksheets:
            rows = ws.iter_rows(max_row=_MAX_ROWS, max_col=_MAX_COLS, values_only=True)
            yield ws.title, [list(r) for r in rows]
        wb.close()
    elif ext == ".xls":
        import xlrd
        with open(os.devnull, "w") as devnull:
            book = xlrd.open_workbook(path, logfile=devnull, on_demand=True)
        for sh in book.sheets():
            nr, nc = min(sh.nrows, _MAX_ROWS), min(sh.ncols, _MAX_COLS)
            yield sh.name, [[sh.cell_value(r, c) for c in range(nc)] for r in range(nr)]
    elif ext == ".csv":
        def _num(x):
            try:
                return float(str(x).replace(",", "").replace("$", ""))
            except ValueError:
                return x
        with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
            rows = []
            for i, r in enumerate(csv.reader(f)):
                if i >= _MAX_ROWS:
                    break
                rows.append([_num(x) for x in r[:_MAX_COLS]])
            yield "csv", rows
    else:
        raise ValueError(f"Unsupported file type {ext!r}. Use .xlsx, .xls, .csv, or .zip.")


def _is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _norm_rate(field: str, v: float) -> float:
    return v / 100.0 if field in _RATE_FIELDS and abs(v) > 1.5 else v


# ----------------------------- operating statements ------------------------------
def _total_col(rows: list[list]) -> Optional[int]:
    """Find a 'Total / TTM / Year' summary column from the header rows."""
    for row in rows[:12]:
        for ci, v in enumerate(row):
            if isinstance(v, str) and any(k in v.lower()
                                          for k in ("total", "ttm", "trailing", "year")):
                return ci
    return None


def _operating_value(row: list, total_ci: Optional[int]) -> Optional[float]:
    """The annual figure for a statement row: the Total column, else sum the months."""
    if total_ci is not None and total_ci < len(row) and _is_number(row[total_ci]):
        return float(row[total_ci])
    nums = [float(v) for v in row if _is_number(v)]
    if not nums:
        return None
    return sum(nums[:-1]) if len(nums) > 1 else nums[0]  # sum months, drop a trailing total


def _extract_operating(rows: list[list], deal: Deal) -> list[str]:
    """Pull revenue / NOI / op-ex from an income statement (T-12 or single period)."""
    total_ci = _total_col(rows)
    grab: dict[str, float] = {}
    # label keyword -> bucket (priority handled by first-wins ordering below)
    wants = [
        (["total operating revenue", "total revenue", "effective gross income",
          "gross income", "total income", "total revenues"], "revenue"),
        (["net operating income"], "noi"),
        (["income before non-oper", "income before non oper", "net operating profit"], "noi2"),
        (["gross operating profit"], "noi3"),
        (["ebitda"], "noi4"),
        (["total operating expenses", "total expenses"], "opex"),
    ]
    for row in rows:
        label = next((str(c).strip().lower() for c in row if isinstance(c, str) and c.strip()), "")
        if not label:
            continue
        for keys, bucket in wants:
            if bucket not in grab and any(k in label for k in keys):
                val = _operating_value(row, total_ci)
                if val is not None:
                    grab[bucket] = val
                break

    revenue = grab.get("revenue")
    noi = grab.get("noi") or grab.get("noi2") or grab.get("noi3") or grab.get("noi4")
    if noi is None and revenue is not None and "opex" in grab:
        noi = revenue - grab["opex"]
    deal.noi = noi
    notes = []
    if revenue and noi is not None:
        deal.opex_ratio = max(0.0, (revenue - noi) / revenue)
    elif revenue and "opex" in grab:
        deal.opex_ratio = grab["opex"] / revenue
    if noi is None:
        notes.append("operating statement: could not locate NOI/EBITDA")
    notes.append("operating statement has no price/cap, IRR, or market — supply those to score")
    return notes


# ----------------------------- pro formas ----------------------------------------
def _extract_proforma(rows_by_sheet, deal: Deal) -> None:
    found: dict[str, float] = {}
    for _name, rows in rows_by_sheet:
        for row in rows:
            label = None
            values = []
            for v in row:
                if isinstance(v, str) and v.strip() and label is None:
                    label = v.strip().lower()
                elif _is_number(v):
                    values.append(float(v))
            if not label or not values:
                continue
            for keywords, field in _PATTERNS:
                if field in found:
                    continue
                if any(k in label for k in keywords):
                    found[field] = _norm_rate(field, values[0])
                    break
    for field, val in found.items():
        setattr(deal, field, val)


# ----------------------------- public API ----------------------------------------
def extract_deal(path: str, name: str | None = None) -> tuple[Deal, list[str]]:
    """Extract a Deal from a single workbook/csv (pro forma or operating statement)."""
    rows_by_sheet = list(_iter_sheets(path))

    blob, market_label, prop_name = [], "", ""
    for _name, rows in rows_by_sheet:
        for row in rows:
            texts = [v.strip() for v in row if isinstance(v, str) and v.strip()]
            for t in texts:
                blob.append(t.lower())
            if texts:
                low = texts[0].lower()
                if not prop_name and low.startswith("for property"):
                    prop_name = texts[0].split(":", 1)[-1].strip()
                if not market_label and any(k in low for k in _LOC) and len(texts) > 1:
                    market_label = texts[1]
    text = " ".join(blob)

    is_operating = any(s in text for s in (
        "total operating revenue", "gross operating profit", "departmental expenses",
        "income statement", "ebitda")) and "exit cap" not in text
    is_dev = any(t in text for t in ("development budget", "construction", "yield on cost",
                                     "hard cost", "pay app", "lease up"))
    deal_type = DEVELOPMENT if (is_dev and not is_operating) else INCOME

    base = name or prop_name or os.path.splitext(os.path.basename(path))[0]
    deal = Deal(name=base, deal_type=deal_type, market_label=market_label)

    if is_operating:
        notes = _extract_operating(_flatten(rows_by_sheet), deal)
    else:
        _extract_proforma(rows_by_sheet, deal)
        notes = []

    # derive what we can
    if deal.total_cost is None and deal.equity is not None and deal.debt is not None:
        deal.total_cost = deal.equity + deal.debt
    if deal.equity and deal.total_cost and deal.debt is None:
        deal.debt = max(0.0, deal.total_cost - deal.equity)
    if deal.debt is not None and deal.total_cost:
        deal.ltv = deal.debt / deal.total_cost
    if deal.yield_on_cost is None and deal.noi and deal.total_cost:
        deal.yield_on_cost = deal.noi / deal.total_cost
    if deal.is_development and deal.dev_spread is None and deal.yield_on_cost and deal.exit_cap:
        deal.dev_spread = deal.yield_on_cost - deal.exit_cap

    for field in ("noi", "exit_cap", "total_cost"):
        if getattr(deal, field) is None and not is_operating:
            notes.append(f"could not locate '{field}' — supply manually")
    if deal.best_irr is None and not is_operating:
        notes.append("no IRR found — supply unlevered/levered IRR manually")
    return deal, notes


def _flatten(rows_by_sheet) -> list[list]:
    return [row for _name, rows in rows_by_sheet for row in rows]


def pick_from_zip(zip_path: str, dest_dir: str) -> Optional[str]:
    """Extract a .zip and return the path of the most relevant statement inside."""
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest_dir)
    candidates = []
    for root, _dirs, files in os.walk(dest_dir):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in _SUPPORTED:
                low = fn.lower()
                pri = next((i for i, k in enumerate(_ZIP_PRIORITY) if k in low), len(_ZIP_PRIORITY))
                candidates.append(((pri, _EXT_RANK.get(ext, 9)), os.path.join(root, fn)))
    if not candidates:
        return None
    return min(candidates, key=lambda c: c[0])[1]


def extract_from_path(path: str, name: str | None = None) -> tuple[Deal, list[str]]:
    """Top-level: handle a workbook/csv, or a .zip package (picks the best file inside)."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".zip":
        import tempfile
        dest = tempfile.mkdtemp(prefix="ic_zip_")
        chosen = pick_from_zip(path, dest)
        if not chosen:
            base = name or os.path.splitext(os.path.basename(path))[0]
            return Deal(name=base), [
                "no .xlsx/.xls/.csv statement found in the archive (PDF-only?) — "
                "provide a spreadsheet version of the pro forma or rolling-12 statement"]
        deal, notes = extract_deal(chosen, name=name)
        notes.insert(0, f"imported from archive: {os.path.basename(chosen)}")
        return deal, notes
    return extract_deal(path, name=name)
