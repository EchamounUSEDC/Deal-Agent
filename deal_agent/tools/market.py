"""Market-research tool: pull external data (comps, zoning, assessor, market trends)
via Claude's server-side web search."""

from __future__ import annotations

from anthropic import beta_tool

from ..client import get_client
from ..config import settings
from ..util import message_text


@beta_tool
def market_research(query: str) -> str:
    """Search the web for real-estate market data and return a cited summary.

    Use for comparable sales, asking prices, cap rates, zoning ordinances, county
    assessor records, demographic/market trends, and anything else that requires
    current information beyond the supplied documents.

    Args:
        query: A specific research question, e.g. "2024 industrial land sale comps
            per acre near Reno NV 89506" or "Washoe County zoning code for IGL".
    """
    client = get_client()
    resp = client.messages.create(
        model=settings.model,
        max_tokens=4096,
        system=(
            "You are a commercial real-estate research analyst. Use web search to find "
            "current, relevant data. Report concrete figures with their sources and dates, "
            "and flag anything you could not verify."
        ),
        tools=[{"type": "web_search_20260209", "name": "web_search"}],
        messages=[{"role": "user", "content": query}],
    )
    return message_text(resp) or "No results were found for that query."
