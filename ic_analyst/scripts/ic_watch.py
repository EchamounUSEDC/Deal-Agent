#!/usr/bin/env python3
"""IC Analyst — real-time inbox watcher.

Run it once and leave it running. Drop a deal file (.xlsx / .xlsm / .csv / .pdf) into
deals/inbox/ and it scores it the instant it lands: prints the GO / NO-GO verdict, writes
the report to deals/reports/, and moves the input to deals/processed/.

    python3 scripts/ic_watch.py            # watch forever (Ctrl+C to stop)
    python3 scripts/ic_watch.py --once     # process what's there now, then exit
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ic_engine as E  # noqa: E402

EXT = (".xlsx", ".xlsm", ".csv", ".pdf")
ICON = {"GO": "🟢", "CONDITIONAL GO": "🟡", "NO-GO": "🔴"}


def _stable(path, wait=0.5):
    """True once the file has finished being written (size stops changing)."""
    try:
        s1 = os.path.getsize(path)
        time.sleep(wait)
        return s1 == os.path.getsize(path) and s1 > 0
    except OSError:
        return False


def _process(path):
    ts = time.strftime("%H:%M:%S")
    name = os.path.basename(path)
    print(f"[{ts}] ▶ analyzing {name} …", flush=True)
    try:
        results = E.analyze_file(path)
        for deal, res in results:
            v = res["verdict"]
            print(f"[{ts}] {ICON.get(v, '')} {deal['name']}: {v}  {res['score']}/100"
                  f"  ·  stress {res['stress']}", flush=True)
            print(f"          {res['narrative']}", flush=True)
            print(f"          report → {res['out']}", flush=True)
        if not results:
            print(f"[{ts}]    (no scorable deal found in {name})", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"[{ts}] ⚠ error on {name}: {exc}", flush=True)
    finally:
        try:
            shutil.move(path, os.path.join(E.PROCESSED, name))
        except Exception:
            pass


def watch(poll=1.5, once=False):
    for d in (E.INBOX, E.PROCESSED, E.REPORTS):
        os.makedirs(d, exist_ok=True)
    print(f"👁  IC Analyst watching  {E.INBOX}")
    print("   Drop a deal (.xlsx / .xlsm / .csv / .pdf) — results appear here in real time."
          + ("" if once else "  (Ctrl+C to stop)"))
    print("-" * 78, flush=True)
    while True:
        try:
            for f in sorted(os.listdir(E.INBOX)):
                if f.startswith(".") or not f.lower().endswith(EXT):
                    continue
                p = os.path.join(E.INBOX, f)
                if _stable(p):
                    _process(p)
            if once:
                return
            time.sleep(poll)
        except KeyboardInterrupt:
            print("\n👋  stopped.")
            return


def main(argv=None):
    ap = argparse.ArgumentParser(description="IC Analyst real-time inbox watcher")
    ap.add_argument("--once", action="store_true", help="process current files then exit")
    ap.add_argument("--poll", type=float, default=1.5, help="poll interval seconds")
    a = ap.parse_args(argv)
    watch(poll=a.poll, once=a.once)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
