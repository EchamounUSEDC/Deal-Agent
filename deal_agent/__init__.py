"""Deal-Agent — a 4-agent system for interpreting financial documents and land/parcel
data, then formulating a deal with a company.

Agents:
    - financial_analyst : reads & interprets financial spreadsheets
    - land_surveyor     : studies & interprets maps and parcel/land areas
    - deal_strategist   : researches the market and formulates the deal terms
    - orchestrator      : coordinates the three specialists end-to-end
"""

from .config import settings

__all__ = [
    "settings",
    "build_financial_analyst",
    "build_land_surveyor",
    "build_deal_strategist",
    "build_orchestrator",
]

# Agent builders are imported lazily: they pull in the Anthropic SDK, which the
# self-contained IC Go/No-Go engine (deal_agent.ic) does not need.
_AGENT_BUILDERS = {
    "build_financial_analyst",
    "build_land_surveyor",
    "build_deal_strategist",
    "build_orchestrator",
}


def __getattr__(name: str):
    if name in _AGENT_BUILDERS:
        from . import agents

        return getattr(agents, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
