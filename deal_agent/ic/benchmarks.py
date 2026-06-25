"""Load the two proven-winner benchmark profiles.

Real economics live in ``ic_data/benchmarks.json`` (git-ignored). A committed
``ic_data/benchmarks.example.json`` documents the schema with placeholder numbers so the
engine is runnable without the confidential client data.
"""

from __future__ import annotations

import json
import os

from .schema import Deal

_HERE = os.path.dirname(__file__)
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_REAL = os.path.join(_ROOT, "ic_data", "benchmarks.json")
_EXAMPLE = os.path.join(_ROOT, "ic_data", "benchmarks.example.json")


def benchmarks_path() -> str:
    """Prefer the real (git-ignored) profiles; fall back to the committed example."""
    return _REAL if os.path.exists(_REAL) else _EXAMPLE


def load_benchmarks(path: str | None = None) -> list[Deal]:
    p = path or benchmarks_path()
    with open(p) as f:
        data = json.load(f)
    return [Deal.from_dict(d) for d in data["benchmarks"]]
