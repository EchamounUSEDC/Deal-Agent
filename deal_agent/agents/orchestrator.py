"""Agent 4 — Orchestrator. Coordinates the three specialists end-to-end.

The orchestrator does not parse data itself. It delegates to the Financial Analyst,
the Land Surveyor, and the Deal Strategist via tools, then synthesizes their findings
into a single recommendation.
"""

from __future__ import annotations

from anthropic import beta_tool

from .base import Agent
from .deal_strategist import build_deal_strategist
from .financial_analyst import build_financial_analyst
from .land_surveyor import build_land_surveyor

SYSTEM = """\
You are the Lead Dealmaker coordinating a team of three specialists:
- consult_financial_analyst — interprets financial spreadsheets.
- consult_land_surveyor — interprets maps and parcel/land areas.
- consult_deal_strategist — researches the market and drafts deal terms.

Your job is to break the user's objective into specialist tasks, delegate each with \
the exact file paths and a precise question, and then synthesize the results.

Method:
- Run the Financial Analyst and the Land Surveyor first (they are independent — \
delegate to both before synthesizing). Pass each the relevant file paths verbatim.
- Hand their findings to the Deal Strategist to value the asset and formulate terms.
- Resolve conflicts between specialists explicitly rather than averaging them.

Deliver one integrated brief: the asset (financials + land), an indicative \
valuation, a recommended offer and structure, key contingencies, and the top risks. \
Lead with the recommendation. Make clear this is analysis, not legal/investment \
advice."""


def _delegation_tools(financial: Agent, land: Agent, strategist: Agent) -> list:
    @beta_tool
    def consult_financial_analyst(task: str, files: str = "") -> str:
        """Delegate a financial-analysis task to the Financial Analyst agent.

        Args:
            task: A precise instruction or question about the financials.
            files: Comma-separated paths to the relevant spreadsheet(s).
        """
        prompt = task if not files else f"{task}\n\nRelevant files: {files}"
        return financial.run(prompt)

    @beta_tool
    def consult_land_surveyor(task: str, files: str = "") -> str:
        """Delegate a land/map task to the Land Surveyor agent.

        Args:
            task: A precise instruction or question about the land or maps.
            files: Comma-separated paths to parcel data and/or map images/PDFs.
        """
        prompt = task if not files else f"{task}\n\nRelevant files: {files}"
        return land.run(prompt)

    @beta_tool
    def consult_deal_strategist(task: str) -> str:
        """Delegate deal formulation to the Deal Strategist agent. Include the
        Financial Analyst's and Land Surveyor's findings in the task text.

        Args:
            task: The synthesis brief: financial findings, land findings, and what
                deal to formulate.
        """
        return strategist.run(task)

    return [consult_financial_analyst, consult_land_surveyor, consult_deal_strategist]


def build_orchestrator(
    financial: Agent | None = None,
    land: Agent | None = None,
    strategist: Agent | None = None,
) -> Agent:
    financial = financial or build_financial_analyst()
    land = land or build_land_surveyor()
    strategist = strategist or build_deal_strategist()
    return Agent(
        name="orchestrator",
        system=SYSTEM,
        tools=_delegation_tools(financial, land, strategist),
    )
