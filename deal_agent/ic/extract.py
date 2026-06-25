"""Best-effort metric extraction from a candidate pro forma workbook.

Pro formas vary in layout, so this scans every sheet for labelled line items and pulls
the first numeric value on the row. It returns a partly-filled :class:`Deal` plus notes
on what it could and couldn't find — the Benchmarker agent refines the rest.
"""

from __future__ import annotations

import os
from typing import Optional

from .schema import Deal, INCOME, DEVELOPMENT

# label keyword(s) -> Deal field. First numeric on a matching row wins.
_RATE_FIELDS = {"going_in_cap", "exit_cap", "yield_on_cost", "dev_spread",
                "unlevered_irr", "levered_irr", "ltv", "opex_ratio"}

_PATTERNS = [
    (["exit cap"], "exit_cap"),
    (["syndicated cap rate"], "going_in_cap"),
    (["going-in cap", "going in cap", "year 1 cap", "in-place cap"], "going_in_cap"),
    (["net operating income", "noi"], "noi"),
    (["yield on cost", "yield-on-cost"], "yield_on_cost"),
    (["development spread", "dev. spread", "dev spread"], "dev_spread"),
    (["unlevered irr"], "unlevered_irr"),
    (["levered irr"], "levered_irr"),
    (["irr"], "unlevered_irr"),  # generic fallback for pro formas that label a single "IRR"
    (["partnership level budget", "development budget", "total project cost",
      "total capitalization", "total cost"], "total_cost"),
    (["permanent debt", "construction financing", "mortgage", "loan amount", "debt"], "debt"),
    (["equity"], "equity"),
    (["net rentable", "nrsf"], "nrsf"),
    (["site acreage", "acreage", "acres"], "site_acreage"),
]


def _norm_rate(field: str, v: float) -> float:
    if field in _RATE_FIELDS and abs(v) > 1.5:
        return v / 100.0
    return v


def _first_number(cells) -> Optional[float]:
    for c in cells:
        if isinstance(c, (int, float)) and not isinstance(c, bool):
            return float(c)
    return None


def extract_deal(path: str, name: str | None = None) -> tuple[Deal, list[str]]:
    import openpyxl

    wb = openpyxl.load_workbook(path, data_only=True)
    found: dict[str, float] = {}
    blob = []  # lowercased text of every cell, to classify the archetype
    market_label = ""
    _LOC = ("county", "market", "location", "city", "msa", "cbsa", "submarket", "address")

    for ws in wb.worksheets:
        for row in ws.iter_rows():
            label = None
            texts = []   # trailing string cells (for location capture)
            values = []
            for cell in row:
                v = cell.value
                if isinstance(v, str):
                    blob.append(v.lower())
                    if label is None and v.strip():
                        label = v.strip().lower()
                    elif v.strip():
                        texts.append(v.strip())
                elif isinstance(v, (int, float)) and not isinstance(v, bool):
                    values.append(v)
            # capture a market/location label -> the text to its right
            if not market_label and label and any(k in label for k in _LOC) and texts:
                market_label = texts[0]
            if not label or not values:
                continue
            for keywords, field in _PATTERNS:
                if field in found:
                    continue
                if any(k in label for k in keywords):
                    num = _first_number(values)
                    if num is not None:
                        found[field] = _norm_rate(field, num)
                    break
    wb.close()

    text = " ".join(blob)
    is_dev = any(t in text for t in ("development budget", "construction", "yield on cost",
                                     "hard cost", "pay app", "lease up"))
    deal_type = DEVELOPMENT if is_dev else INCOME

    deal = Deal(name=name or os.path.splitext(os.path.basename(path))[0], deal_type=deal_type)
    deal.market_label = market_label
    for field, val in found.items():
        setattr(deal, field, val)

    # derive what we can
    if deal.total_cost is None and deal.equity is not None and deal.debt is not None:
        deal.total_cost = deal.equity + deal.debt  # capital stack = equity + debt
    if deal.equity and deal.total_cost and deal.debt is None:
        deal.debt = max(0.0, deal.total_cost - deal.equity)
    if deal.debt is not None and deal.total_cost:
        deal.ltv = deal.debt / deal.total_cost
    if deal.yield_on_cost is None and deal.noi and deal.total_cost:
        deal.yield_on_cost = deal.noi / deal.total_cost
    if deal.is_development and deal.dev_spread is None and deal.yield_on_cost and deal.exit_cap:
        deal.dev_spread = deal.yield_on_cost - deal.exit_cap

    notes = []
    for field in ("noi", "exit_cap", "total_cost", "equity"):
        if getattr(deal, field) is None:
            notes.append(f"could not locate '{field}' — supply manually")
    if deal.best_irr is None:
        notes.append("no IRR found — supply unlevered/levered IRR manually")
    return deal, notes
