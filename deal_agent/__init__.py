"""Deal-Agent — a 4-agent system for interpreting financial documents and land/parcel
data, then formulating a deal with a company.

Agents:
    - financial_analyst : reads & interprets financial spreadsheets
    - land_surveyor     : studies & interprets maps and parcel/land areas
    - deal_strategist   : researches the market and formulates the deal terms
    - orchestrator      : coordinates the three specialists end-to-end
"""

from .config import settings
from .agents import (
    build_financial_analyst,
    build_land_surveyor,
    build_deal_strategist,
    build_orchestrator,
)

__all__ = [
    "settings",
    "build_financial_analyst",
    "build_land_surveyor",
    "build_deal_strategist",
    "build_orchestrator",
]
