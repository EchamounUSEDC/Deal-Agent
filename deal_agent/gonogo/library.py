"""A queryable deal library: resolve a name like "Hamburg" or "TX" to a live
Go/No-Go verdict, so you can *ask a question* instead of pointing at a file.

The library indexes:
- the benchmark deals (Hamburg, Lewiston), and
- every deal found in the files listed by `GONOGO_DEAL_FILES` (a comma/semicolon
  separated list) or in the `GONOGO_DEALS_DIR` folder (default: ./deals).

Everything is recomputed on each call, so edits to the underlying files or to
benchmarks.py show up immediately — that is what makes an Excel cell "live".
"""

from __future__ import annotations

import glob
import os
import re

from .benchmarks import BENCHMARKS
from .engine import Verdict, score_deal
from .metrics import DealMetrics, extract_deals

_DEFAULT_DIR = "deals"
_FILLER = re.compile(r"\b(is|the|a|an|deal|go|no|nogo|or|not|will|work|works|"
                     r"this|that|should|we|do|does|status|on|of|for|me|my|please)\b",
                     re.IGNORECASE)


def deal_files() -> list[str]:
    """Resolve the configured deal files (env list first, then the deals dir)."""
    env = os.getenv("GONOGO_DEAL_FILES", "").strip()
    if env:
        return [p.strip() for p in re.split(r"[;,]", env) if p.strip()]
    d = os.getenv("GONOGO_DEALS_DIR", _DEFAULT_DIR)
    if os.path.isdir(d):
        out: list[str] = []
        for ext in ("xlsx", "xls", "csv"):
            out.extend(sorted(glob.glob(os.path.join(d, f"*.{ext}"))))
        return out
    return []


def _benchmark_metrics() -> list[DealMetrics]:
    out = []
    for b in BENCHMARKS.values():
        out.append(DealMetrics(
            name=b.name, source="benchmark",
            yield_on_cost=b.yield_on_cost, exit_cap=b.exit_cap,
            dev_spread_bps=b.dev_spread_bps, levered_irr=b.levered_irr,
            unlevered_irr=b.unlevered_irr, moic=b.moic,
            lease_up_months=b.lease_up_months, noi=b.noi, total_cost=b.total_cost,
        ))
    return out


def load_library(extra_files: list[str] | None = None) -> dict[str, Verdict]:
    """Build {deal_name_lower: Verdict} from benchmarks + configured + extra files."""
    deals: list[DealMetrics] = _benchmark_metrics()
    seen_files: set[str] = set()
    for path in (deal_files() + list(extra_files or [])):
        if path in seen_files or not os.path.exists(path):
            continue
        seen_files.add(path)
        try:
            deals.extend(extract_deals(path))
        except Exception:  # noqa: BLE001 - a bad file shouldn't break the library
            continue
    library: dict[str, Verdict] = {}
    for d in deals:
        library[d.name.strip().lower()] = score_deal(d)
    return library


def _normalize(q: str) -> str:
    q = _FILLER.sub(" ", q)
    return re.sub(r"\s+", " ", q).strip().lower()


def resolve(query: str, library: dict[str, Verdict] | None = None) -> Verdict | None:
    """Find the deal a free-text query refers to. Exact, then substring, then token."""
    lib = library if library is not None else load_library()
    if not lib:
        return None
    q = query.strip().lower()

    if q in lib:
        return lib[q]
    # if the query is a path, score it directly
    if os.path.exists(query):
        from .ranker import rank_files
        ranked = rank_files([query])
        return ranked[0] if ranked else None

    cleaned = _normalize(query)
    # whole cleaned query is a name
    if cleaned in lib:
        return lib[cleaned]
    # a known deal name appears inside the question
    hits = [name for name in lib if name and name in cleaned]
    if hits:
        return lib[max(hits, key=len)]
    # the cleaned query appears inside a deal name (e.g. "springfield" in
    # "uspd_springfield_dst_proforma")
    if cleaned:
        contained = [name for name in lib if cleaned in name]
        if contained:
            return lib[min(contained, key=len)]
    # token overlap, splitting names on spaces/underscores/hyphens/punctuation
    q_tokens = {t for t in re.split(r"[\s_\-/]+", cleaned) if len(t) > 1}
    best, best_overlap = None, 0
    for name in lib:
        n_tokens = {t for t in re.split(r"[\s_\-/]+", name) if len(t) > 1}
        overlap = len(q_tokens & n_tokens)
        if overlap > best_overlap:
            best, best_overlap = name, overlap
    return lib[best] if best else None


def answer(question: str, library: dict[str, Verdict] | None = None) -> str:
    """One-sentence live answer to 'is X a go/no-go?'-style questions."""
    v = resolve(question, library)
    if v is None:
        names = ", ".join(sorted(n.title() for n in (library or load_library()))) or "none configured"
        return (f"Couldn't find a deal matching {question!r}. Known deals: {names}. "
                "Add deal files via GONOGO_DEAL_FILES or the ./deals folder, or pass a file path.")
    return f"{v.name}: {v.decision} ({v.score:.0f}/100). {v.rationale}"
