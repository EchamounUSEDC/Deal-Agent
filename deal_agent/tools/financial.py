"""Financial-document tools: read and interpret spreadsheets (.xlsx/.xls/.csv)."""

from __future__ import annotations

import json
import os

from anthropic import beta_tool

_MAX_PREVIEW_ROWS = 25


def _load_frames(path: str, sheet: str = "") -> dict:
    """Return {sheet_name: DataFrame}. CSV yields a single 'csv' sheet."""
    import pandas as pd

    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return {"csv": pd.read_csv(path)}
    if ext in (".xlsx", ".xls"):
        sheet_arg = sheet if sheet else None
        frames = pd.read_excel(path, sheet_name=sheet_arg)
        # pandas returns a DataFrame when a single sheet is named, else a dict
        if not isinstance(frames, dict):
            frames = {sheet or "sheet0": frames}
        return frames
    raise ValueError(f"Unsupported spreadsheet type {ext!r}. Use .xlsx, .xls, or .csv.")


@beta_tool
def read_spreadsheet(path: str, sheet: str = "") -> str:
    """Read a financial spreadsheet and return its structure and a data preview.

    Use this first to understand what a financial workbook contains: sheet names,
    column headers, data types, row counts, and the first rows of each sheet.

    Args:
        path: Path to a .xlsx, .xls, or .csv file.
        sheet: Optional sheet name to read. Empty reads every sheet in the workbook.
    """
    try:
        frames = _load_frames(path, sheet)
    except FileNotFoundError:
        return f"Error: file not found at {path!r}."
    except Exception as exc:  # noqa: BLE001 - surface the parse error to the model
        return f"Error reading {path!r}: {exc}"

    out: dict = {"file": path, "sheets": []}
    for name, df in frames.items():
        out["sheets"].append(
            {
                "name": name,
                "rows": int(len(df)),
                "columns": [str(c) for c in df.columns],
                "dtypes": {str(c): str(t) for c, t in df.dtypes.items()},
                "preview": df.head(_MAX_PREVIEW_ROWS).to_dict(orient="records"),
            }
        )
    return json.dumps(out, indent=2, default=str)


@beta_tool
def financial_summary(path: str, sheet: str = "") -> str:
    """Summarize the numeric columns of a spreadsheet (sum, mean, min, max, count).

    Use this to get totals and ranges for revenue, expenses, NOI, prices, etc.,
    without loading every cell into context.

    Args:
        path: Path to a .xlsx, .xls, or .csv file.
        sheet: Optional sheet name. Empty summarizes every sheet.
    """
    try:
        frames = _load_frames(path, sheet)
    except FileNotFoundError:
        return f"Error: file not found at {path!r}."
    except Exception as exc:  # noqa: BLE001
        return f"Error reading {path!r}: {exc}"

    out: dict = {"file": path, "sheets": []}
    for name, df in frames.items():
        numeric = df.select_dtypes(include="number")
        cols = {}
        for col in numeric.columns:
            series = numeric[col].dropna()
            if series.empty:
                continue
            cols[str(col)] = {
                "sum": float(series.sum()),
                "mean": float(series.mean()),
                "min": float(series.min()),
                "max": float(series.max()),
                "count": int(series.count()),
            }
        out["sheets"].append({"name": name, "numeric_columns": cols})
    return json.dumps(out, indent=2, default=str)


@beta_tool
def find_line_items(path: str, keywords: str, sheet: str = "") -> str:
    """Find rows whose text cells match any of the given keywords.

    Useful for locating specific financial line items (e.g. "rent, NOI, tax,
    insurance, debt service") inside a large workbook.

    Args:
        path: Path to a .xlsx, .xls, or .csv file.
        keywords: Comma-separated terms to search for, case-insensitive.
        sheet: Optional sheet name. Empty searches every sheet.
    """
    terms = [k.strip().lower() for k in keywords.split(",") if k.strip()]
    if not terms:
        return "Error: provide at least one keyword."
    try:
        frames = _load_frames(path, sheet)
    except FileNotFoundError:
        return f"Error: file not found at {path!r}."
    except Exception as exc:  # noqa: BLE001
        return f"Error reading {path!r}: {exc}"

    matches: list[dict] = []
    for name, df in frames.items():
        for idx, row in df.iterrows():
            joined = " ".join(str(v) for v in row.values).lower()
            if any(term in joined for term in terms):
                matches.append(
                    {"sheet": name, "row": int(idx), "values": row.to_dict()}
                )
            if len(matches) >= 100:
                break
    return json.dumps(
        {"file": path, "keywords": terms, "match_count": len(matches), "matches": matches},
        indent=2,
        default=str,
    )
