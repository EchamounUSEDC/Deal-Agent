"""
build_market_cache.py \u2014 one-time build step
============================================
Pre-extracts the WeightedRanking sheet from market_model.xlsx (16 MB, 14 sheets)
into a flat CSV (~80 KB, data/market_ranking.csv).

The screening agent reads the CSV on every run instead of reopening the full
workbook, giving a 10\u201320\u00d7 speed-up per market lookup.

Run this once whenever market_model.xlsx is updated.
The pipeline orchestrator also exposes this as: python pipeline.py --rebuild-cache

Usage:
    python build_market_cache.py
    python build_market_cache.py --model /path/to/market_model.xlsx
    python build_market_cache.py --out /path/to/market_ranking.csv
"""
import argparse
import icframework as f


def main():
    ap = argparse.ArgumentParser(
        description="Pre-extract WeightedRanking sheet to a flat CSV cache"
    )
    ap.add_argument(
        "--model", default=f.MARKET_MODEL,
        help="source workbook (default: data/market_model.xlsx)",
    )
    ap.add_argument(
        "--out", default=f.MARKET_CSV,
        help="output CSV path (default: data/market_ranking.csv)",
    )
    a = ap.parse_args()

    import os
    print(f"Reading {os.path.basename(a.model)} ...")
    out, n = f.export_market_csv(path=a.model, out=a.out)
    print(f"Written: {out}  ({n} markets)")
    print("Next run of screening_agent.py / pipeline.py will use the CSV cache.")


if __name__ == "__main__":
    main()
