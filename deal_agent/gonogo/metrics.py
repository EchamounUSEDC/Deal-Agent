"""Pull the storage-deal metrics the Go/No-Go engine needs out of any file.

A new deal can arrive in many shapes, so `extract_deals(path)` handles three:

1. **Market-ranking CSV/sheet** — one row per market, named columns
   (`Stabilized Yield on Cost`, `Dev. Spread`, `Exit Cap %`, `Pro Forma IRR`,
   `Total Weighted Score`, `Rank (1 = Best)`). -> one deal per row.
2. **Side-by-side model** — metrics down column 0, one deal per following column
   (the `dev_model_11_markets.xlsx` "Side-by-Side Comparison" layout).
3. **Generic proforma** — any other workbook: scan every cell for metric
   keywords and grab the nearest numeric value on the same row. Handles the
   Springfield DST proforma, the Hamburg cashflow, and most attached one-offs.

Every path yields a list of `DealMetrics`. Missing fields stay `None`; the
engine fills `dev_spread_bps` from `yield_on_cost - exit_cap` when it can.
"""

from __future__ import annotations

import os
import re
from dataclasses import asdict, dataclass, field

# Strip a leading upload-hash prefix like "c690e414-" from a file's base name.
_HASH_PREFIX = re.compile(r"^[0-9a-f]{6,}-", re.IGNORECASE)


def _clean_base(name: str) -> str:
    return _HASH_PREFIX.sub("", name).strip()


@dataclass
class DealMetrics:
    """Normalized storage-deal metrics. All economics optional (None = unknown)."""

    name: str
    source: str = ""
    yield_on_cost: float | None = None
    exit_cap: float | None = None
    dev_spread_bps: float | None = None
    levered_irr: float | None = None
    unlevered_irr: float | None = None
    moic: float | None = None
    lease_up_months: float | None = None
    noi: float | None = None
    total_cost: float | None = None
    equity: float | None = None
    market_score: float | None = None   # 0-1 normalized market quality
    market_rank: float | None = None
    premium_market: bool | None = None
    tier: str | None = None             # T1..T4 if the source labels one
    extra: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)


# --- helpers ----------------------------------------------------------------

def _num(value) -> float | None:
    """Coerce a cell to float, handling %, $, commas, parentheses-negatives."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        v = float(value)
        return None if v != v else v  # drop NaN
    s = str(value).strip()
    if not s or s in {"-", "—", "–", "n/a", "N/A", "NaN"}:
        return None
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace("$", "").replace(",", "").replace("%", "").strip()
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


def _as_rate(value) -> float | None:
    """Normalize a percentage-ish value to a 0-1 fraction (12 or 0.12 -> 0.12)."""
    v = _num(value)
    if v is None:
        return None
    return v / 100.0 if abs(v) > 1.5 else v


# Keyword -> (field, kind). kind: 'rate' (0-1), 'bps', 'num', 'months', 'moic'.
_KEYS: list[tuple[tuple[str, ...], str, str]] = [
    (("stabilized yield on cost", "yield on cost", "yoc", "untrended yield"), "yield_on_cost", "rate"),
    (("dev. spread", "dev spread", "development spread", "yield spread"), "dev_spread_bps", "bps"),
    (("exit cap",), "exit_cap", "rate"),
    (("levered irr", "lp irr", "project irr", "pro forma irr", "proforma irr", "irr"), "levered_irr", "rate"),
    (("unlevered irr", "unlev irr"), "unlevered_irr", "rate"),
    (("project moic", "lp moic", "moic", "equity multiple"), "moic", "moic"),
    (("lease-up months", "lease up months", "leaseup", "months to stabiliz"), "lease_up_months", "months"),
    (("net operating income", "stabilized noi", "noi"), "noi", "num"),
    (("total project cost", "total development cost", "development budget", "total cost"), "total_cost", "num"),
    (("lp equity", "equity required", "total equity", "equity"), "equity", "num"),
    (("total weighted score", "weighted score"), "market_score", "num"),
    (("rank (1 = best)", "market rank", "rank"), "market_rank", "num"),
]


def _assign(deal: DealMetrics, field_name: str, kind: str, raw) -> bool:
    """Set deal.field from a raw cell per its kind. Return True if it took."""
    if getattr(deal, field_name) is not None:
        return False  # first match wins (labels are ordered most-specific first)
    if kind == "rate":
        v = _as_rate(raw)
    elif kind == "bps":
        v = _num(raw)
        if v is not None and abs(v) < 1.0:   # a fraction like 0.019 -> bps
            v *= 10000.0
    else:
        v = _num(raw)
    if v is None:
        return False
    setattr(deal, field_name, v)
    return True


def _match_field(label: str) -> tuple[str, str] | None:
    low = label.lower()
    for needles, field_name, kind in _KEYS:
        if any(n in low for n in needles):
            return field_name, kind
    return None


# --- format 1: market-ranking table (CSV or DataFrame) ----------------------

_RANKING_SIGNALS = {"stabilized yield on cost", "rank (1 = best)", "total weighted score", "dev. spread"}


def _looks_like_ranking(columns) -> bool:
    low = {str(c).strip().lower() for c in columns}
    return len(low & _RANKING_SIGNALS) >= 2


def _deals_from_ranking(df, source: str) -> list[DealMetrics]:
    cols = {str(c).strip().lower(): c for c in df.columns}

    def col(*names):
        for n in names:
            if n in cols:
                return cols[n]
        return None

    name_col = col("county / city", "cbsa", "market", "economic region")
    deals: list[DealMetrics] = []
    for _, row in df.iterrows():
        nm = str(row[name_col]).strip() if name_col is not None else f"row {len(deals)}"
        d = DealMetrics(name=nm, source=source)
        d.yield_on_cost = _as_rate(row.get(col("stabilized yield on cost")))
        d.exit_cap = _as_rate(row.get(col("exit cap %", "exit cap")))
        d.unlevered_irr = _as_rate(row.get(col("pro forma irr")))
        d.levered_irr = d.unlevered_irr
        ds = _num(row.get(col("dev. spread", "dev spread")))
        if ds is not None:
            d.dev_spread_bps = ds * 10000.0 if abs(ds) < 1.0 else ds
        d.market_score = _num(row.get(col("total weighted score")))
        d.market_rank = _num(row.get(col("rank (1 = best)")))
        deals.append(d)
    return deals


# --- format 2: side-by-side model (metrics in col 0, deals in cols) ---------

def _deals_from_side_by_side(df, source: str) -> list[DealMetrics] | None:
    """Detect a 'Market' header row whose following cells name the deals."""
    import pandas as pd  # noqa: F401

    header_idx = None
    for i in range(min(12, len(df))):
        first = str(df.iloc[i, 0]).strip().lower()
        if first in {"market", "deal", "property"}:
            header_idx = i
            break
    if header_idx is None:
        return None

    header = df.iloc[header_idx]
    deal_cols = [c for c in range(1, df.shape[1]) if str(header[c]).strip() not in {"", "nan", "None"}]
    if not deal_cols:
        return None

    deals = {c: DealMetrics(name=str(header[c]).strip(), source=source) for c in deal_cols}
    tier_row = None
    premium_row = None
    for i in range(len(df)):
        label = str(df.iloc[i, 0]).strip()
        if not label or label.lower() == "nan":
            continue
        low = label.lower()
        if low == "tier":
            tier_row = i
            continue
        if "premium market" in low:
            premium_row = i
            continue
        m = _match_field(label)
        if not m:
            continue
        field_name, kind = m
        for c in deal_cols:
            _assign(deals[c], field_name, kind, df.iloc[i, c])
    if tier_row is not None:
        for c in deal_cols:
            t = str(df.iloc[tier_row, c]).strip()
            deals[c].tier = t if t and t.lower() != "nan" else None
    if premium_row is not None:
        for c in deal_cols:
            deals[c].premium_market = str(df.iloc[premium_row, c]).strip().upper() in {"YES", "Y", "TRUE"}
    return list(deals.values())


# --- format 3: generic label/value scan -------------------------------------

def _deals_from_generic(df, source: str, name: str) -> DealMetrics:
    """Scan every row; for each metric keyword grab the nearest numeric cell."""
    deal = DealMetrics(name=name, source=source)
    n_rows, n_cols = df.shape
    for i in range(n_rows):
        for j in range(n_cols):
            cell = df.iloc[i, j]
            if not isinstance(cell, str):
                continue
            m = _match_field(cell)
            if not m:
                continue
            field_name, kind = m
            # nearest numeric to the right on this row, then below
            picked = None
            for jj in range(j + 1, n_cols):
                if _num(df.iloc[i, jj]) is not None:
                    picked = df.iloc[i, jj]
                    break
            if picked is None and i + 1 < n_rows and _num(df.iloc[i + 1, j]) is not None:
                picked = df.iloc[i + 1, j]
            if picked is not None:
                _assign(deal, field_name, kind, picked)
    return deal


_CORE = ("yield_on_cost", "exit_cap", "dev_spread_bps", "levered_irr",
         "unlevered_irr", "moic", "lease_up_months", "noi", "total_cost",
         "market_score", "market_rank", "tier", "premium_market")


def _populated(d: DealMetrics) -> int:
    return sum(getattr(d, f) is not None for f in _CORE)


def _merge_by_name(deals: list[DealMetrics]) -> list[DealMetrics]:
    """Collapse same-named deals into one, filling gaps from the richer copies."""
    groups: dict[str, list[DealMetrics]] = {}
    for d in deals:
        groups.setdefault(d.name.strip().lower(), []).append(d)
    out: list[DealMetrics] = []
    for members in groups.values():
        members.sort(key=_populated, reverse=True)
        winner = members[0]
        for other in members[1:]:
            for f in _CORE:
                if getattr(winner, f) is None and getattr(other, f) is not None:
                    setattr(winner, f, getattr(other, f))
        out.append(winner)
    return out


def finalize_metrics(d: DealMetrics) -> DealMetrics:
    """Derive YoC (NOI/cost) and dev spread (YoC - exit cap) when absent."""
    if d.yield_on_cost is None and d.noi and d.total_cost:
        d.yield_on_cost = d.noi / d.total_cost
    if d.dev_spread_bps is None and d.yield_on_cost is not None and d.exit_cap is not None:
        d.dev_spread_bps = (d.yield_on_cost - d.exit_cap) * 10000.0
    return d


# --- dispatcher -------------------------------------------------------------

def extract_deals(path: str) -> list[DealMetrics]:
    """Read `path` and return one or more DealMetrics. Never raises on bad data.

    Prefers rich layouts (ranking table, side-by-side model) and only falls back
    to a generic label/value scan when neither is present (single proforma).
    Same-named deals across sheets are merged.
    """
    import pandas as pd

    ext = os.path.splitext(path)[1].lower()
    base = _clean_base(os.path.splitext(os.path.basename(path))[0])

    if ext == ".csv":
        df = pd.read_csv(path)
        if _looks_like_ranking(df.columns):
            deals = _deals_from_ranking(df, path)
        else:
            deals = [_deals_from_generic(pd.read_csv(path, header=None), path, base)]
        return [finalize_metrics(d) for d in _merge_by_name(deals)]

    if ext not in {".xlsx", ".xls"}:
        raise ValueError(f"Unsupported file type {ext!r}. Use .xlsx, .xls, or .csv.")

    book = pd.read_excel(path, sheet_name=None, header=None)
    n_sheets = len(book)
    rich: list[DealMetrics] = []      # ranking + side-by-side deals
    generic: list[DealMetrics] = []
    for sheet_name, raw in book.items():
        if raw.empty:
            continue
        headered = pd.read_excel(path, sheet_name=sheet_name)
        if _looks_like_ranking(headered.columns):
            rich.extend(_deals_from_ranking(headered, f"{path}::{sheet_name}"))
            continue
        sbs = _deals_from_side_by_side(raw, f"{path}::{sheet_name}")
        if sbs and sum(_populated(d) >= 2 for d in sbs) >= 2:
            rich.extend(sbs)
            continue
        # Single-proforma workbooks: name the deal after the file, not the sheet.
        deal_name = base if n_sheets == 1 else f"{base} — {sheet_name}"
        g = _deals_from_generic(raw, f"{path}::{sheet_name}", deal_name)
        if _populated(g) >= 2:
            generic.append(g)

    deals = rich if rich else generic
    # A single proforma may scatter metrics across sheets — collapse to one deal.
    if not rich and len(generic) > 1:
        best = max(generic, key=_populated)
        for other in generic:
            for f in _CORE:
                if getattr(best, f) is None and getattr(other, f) is not None:
                    setattr(best, f, getattr(other, f))
        best.name = base
        deals = [best]
    if not deals:
        deals.append(DealMetrics(name=base, source=path))
    deals = _merge_by_name(deals)
    return [finalize_metrics(d) for d in deals]
