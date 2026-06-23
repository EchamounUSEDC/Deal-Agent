"""Shared Anthropic client. One instance is reused across all agents and tools."""

from __future__ import annotations

import anthropic

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    """Return a process-wide Anthropic client (resolves ANTHROPIC_API_KEY from env)."""
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client
