"""
utils/ai.py — one thin door to the LLM, with an offline demo fallback.

- Demo mode (default, no OPENAI_API_KEY): `generate()` / `generate_json()`
  return the caller-supplied deterministic fallback, so the whole app
  demos offline with realistic content.
- Live mode (OPENAI_API_KEY set): the same calls hit the OpenAI API.
  If the API errors mid-demo, we quietly fall back rather than crash.

Both Ayan's and Asa's tabs should call these two functions and nothing else.
"""

from __future__ import annotations

import json
import os
from typing import Any

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

COACH_SYSTEM = (
    "You are an elite B2C sales coach for USEDC, a US energy development "
    "company whose reps sell energy investment programs (income funds, "
    "drilling partnerships, 1031 exchanges) to accredited investors by phone. "
    "You are direct, specific, and encouraging. Ground every point in the "
    "call statistics you are given — never invent numbers."
)


def is_live() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _chat(prompt: str, system: str, temperature: float, json_mode: bool) -> str:
    from openai import OpenAI

    kwargs: dict[str, Any] = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = OpenAI().chat.completions.create(
        model=DEFAULT_MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        **kwargs,
    )
    return resp.choices[0].message.content or ""


def generate(
    prompt: str,
    system: str = COACH_SYSTEM,
    fallback: str = "",
    temperature: float = 0.7,
) -> str:
    """Free-text generation. Returns `fallback` in demo mode or on API error."""
    if not is_live():
        return fallback
    try:
        return _chat(prompt, system, temperature, json_mode=False) or fallback
    except Exception:
        return fallback


def generate_json(
    prompt: str,
    system: str = COACH_SYSTEM,
    fallback: dict | None = None,
    temperature: float = 0.7,
) -> dict:
    """JSON generation. The prompt must describe the exact keys wanted.
    Returns `fallback` in demo mode, on API error, or on unparseable output."""
    fallback = fallback or {}
    if not is_live():
        return fallback
    try:
        raw = _chat(prompt, system, temperature, json_mode=True)
        data = json.loads(raw)
        return data if isinstance(data, dict) else fallback
    except Exception:
        return fallback
