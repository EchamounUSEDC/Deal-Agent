"""Turnkey 'drop a spreadsheet in' importer — no command line, no Excel macros.

Double-click a launcher (launchers/Import Deal.command on macOS/Linux, Import Deal.bat on
Windows) — or drag a pro forma onto it — and this:

  1. opens a file picker if no file was dropped,
  2. reads each pro forma, auto-detects its market (fuzzy-matched to the ranking),
  3. scores it GO / CONDITIONAL / NO-GO against Springfield & Hamburg,
  4. adds it to IC_GoNoGo_Dashboard.xlsx and opens the dashboard.

Run directly too:  python -m deal_agent.ic.desktop [file1.xlsx file2.xlsx ...]
"""

from __future__ import annotations

import os
import subprocess
import sys

from .benchmarks import load_benchmarks
from .extract import extract_deal
from .schema import evaluate
from .workbook import build_workbook
from . import cli as _cli  # reuse candidate store + market loader

OUT = os.path.join(_cli._ROOT, "IC_GoNoGo_Dashboard.xlsx")
_EXTS = (".xlsx", ".xlsm", ".xls")


def _pick_files() -> list[str]:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk(); root.withdraw(); root.update()
        paths = filedialog.askopenfilenames(
            title="Select pro forma spreadsheet(s) to import",
            filetypes=[("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")])
        root.destroy()
        return list(paths)
    except Exception:
        return []


def _notify(title: str, msg: str) -> None:
    print(msg)
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk(); root.withdraw(); root.update()
        messagebox.showinfo(title, msg); root.destroy()
    except Exception:
        pass


def _open(path: str) -> None:
    try:
        if sys.platform.startswith("darwin"):
            subprocess.run(["open", path], check=False)
        elif os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]  # noqa: S606
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception:
        pass


def import_files(paths: list[str]) -> tuple[str, list[str]]:
    """Extract, auto-match market, score, and (re)build the dashboard. Returns (out, summary)."""
    benchmarks = load_benchmarks()
    market = _cli._market()
    cands = _cli._load_candidates()
    summary: list[str] = []
    for p in paths:
        deal, _notes = extract_deal(p)
        if market is not None:
            market.enrich(deal)  # uses the location auto-read from the file
        res = evaluate(deal)
        cands = [c for c in cands if c.name != deal.name]
        cands.append(deal)
        if deal.market_rank:
            mk = f"market: {deal.market_label} → rank #{deal.market_rank}"
        elif deal.market_label:
            mk = f"market '{deal.market_label}' not matched — pick the county on the slot"
        else:
            mk = "no market found in file — pick the county on the slot"
        summary.append(f"• {deal.name}: {res['verdict']} ({res['score']}/100)  ·  {mk}")
    _cli._save_candidates(cands)
    out = build_workbook(OUT, benchmarks, cands, market)
    return out, summary


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    paths = [a for a in argv if a.lower().endswith(_EXTS) and os.path.exists(a)]
    if not paths:
        paths = _pick_files()
    if not paths:
        _notify("IC Go/No-Go", "No spreadsheet selected — nothing to import.")
        return 1
    out, summary = import_files(paths)
    _notify("IC Go/No-Go — imported",
            "\n".join(summary) + f"\n\nOpening {os.path.basename(out)} …")
    _open(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
