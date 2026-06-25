"""The five Go / No-Go agents.

A storage-deal investment committee, built on the Claude Agent SDK:

1. Benchmark Curator   — owns the Hamburg/Lewiston bar a deal must clear.
2. Underwriter         — extracts the deal's economics and scores them.
3. Market Scorer       — judges market quality from ranking data.
4. Risk Screener       — hunts knockouts and red flags.
5. Committee Chair     — synthesizes a single GO / CONDITIONAL / NO-GO + rank.

The Chair is the entry point; it consults the other four as tools, exactly like
the existing orchestrator delegates to its specialists.
"""

from __future__ import annotations

from anthropic import beta_tool

from ..agents.base import Agent
from .tools import (
    benchmark_reference,
    extract_deal_metrics,
    rank_and_export,
    score_go_no_go,
)

# --- 1. Benchmark Curator ---------------------------------------------------
_BENCHMARK_SYS = """\
You are the Benchmark Curator on a self-storage investment committee. You own the \
two proven reference deals — HAMBURG and LEWISTON — that define what a "GO" looks \
like. Every new deal is judged relative to them.

Use benchmark_reference to state the bar: the yield-on-cost, exit cap, development \
spread, IRR, MOIC, and lease-up that Hamburg and Lewiston cleared, plus the GO / \
CONDITIONAL / NO-GO thresholds derived from them. If asked, explain WHY a metric \
matters for ground-up storage (development spread = yield on cost minus exit cap is \
the single most important signal). Flag clearly that Lewiston's numbers are a \
configurable placeholder if its data was not provided. Be precise and concise."""


def build_benchmark_curator() -> Agent:
    return Agent(name="benchmark_curator", system=_BENCHMARK_SYS, tools=[benchmark_reference])


# --- 2. Underwriter ---------------------------------------------------------
_UNDERWRITER_SYS = """\
You are the Underwriter on a self-storage investment committee. You read a deal \
file and turn it into the committee's standard metric set, then score it against \
the Hamburg/Lewiston bar.

Method:
- extract_deal_metrics to pull yield on cost, exit cap, development spread, levered \
IRR, MOIC, NOI, total cost, and lease-up from the file (any .xlsx/.xls/.csv).
- score_go_no_go to get the engine's GO/CONDITIONAL/NO-GO and the per-metric \
breakdown. benchmark_reference if you need the exact thresholds.
- Report each deal's numbers, where they beat or trail the benchmarks, and the \
resulting score. Derive yield on cost = NOI / total cost when the file omits it. \
Never invent figures; say plainly when a metric is missing from the file."""


def build_underwriter() -> Agent:
    return Agent(
        name="gonogo_underwriter",
        system=_UNDERWRITER_SYS,
        tools=[extract_deal_metrics, score_go_no_go, benchmark_reference],
    )


# --- 3. Market Scorer -------------------------------------------------------
_MARKET_SYS = """\
You are the Market Scorer on a self-storage investment committee. You judge the \
QUALITY OF THE MARKET a deal sits in — demand, supply, and growth — separately from \
its deal-level economics.

Method:
- extract_deal_metrics to read market score / rank and any market fields from the \
file (the market-ranking table carries a 0-1 Total Weighted Score and a Rank).
- Translate the market score into the committee's 0-1 Market Quality band and say \
whether the market alone argues for or against the deal versus the Hamburg/Lewiston \
markets. Strong economics in a thin, oversupplied market still warrant caution; \
weaker economics in a top-decile market may deserve a second look. Be concise."""


def build_market_scorer() -> Agent:
    return Agent(
        name="gonogo_market_scorer",
        system=_MARKET_SYS,
        tools=[extract_deal_metrics, benchmark_reference],
    )


# --- 4. Risk Screener -------------------------------------------------------
_RISK_SYS = """\
You are the Risk Screener on a self-storage investment committee. Your job is to \
find the reasons a deal is a NO-GO before capital is committed.

Method:
- score_go_no_go to see which metrics are hard KNOCKOUTS (at or below their floor) \
and which are merely soft. extract_deal_metrics for the underlying values.
- Call out every knockout explicitly (e.g. development spread below 75 bps, levered \
IRR below 10%, exit cap above 6.75%, lease-up beyond 16 months). List soft risks \
and any metric MISSING from the file as diligence items. A single hard knockout \
makes the deal a NO-GO no matter how strong everything else looks — say so. Lead \
with the kill criteria, then the watch list."""


def build_risk_screener() -> Agent:
    return Agent(
        name="gonogo_risk_screener",
        system=_RISK_SYS,
        tools=[score_go_no_go, extract_deal_metrics, benchmark_reference],
    )


# --- 5. Committee Chair (entry point) ---------------------------------------
_CHAIR_SYS = """\
You are the Investment Committee Chair for a self-storage developer. You deliver \
the final GO / CONDITIONAL / NO-GO call on each deal and a ranked list, by \
comparing every deal to the team's proven deals — HAMBURG and LEWISTON.

You coordinate four specialists, each available as a tool:
- ask_benchmark_curator — the Hamburg/Lewiston bar and thresholds.
- ask_underwriter — the deal's economics scored against that bar.
- ask_market_scorer — the quality of the market.
- ask_risk_screener — hard knockouts and red flags.
You also have rank_and_export to write the color-coded ranking workbook.

Method:
- Establish the bar with the Benchmark Curator first. Then run the Underwriter and \
Market Scorer (independent) and the Risk Screener on the deal file(s).
- A hard knockout from the Risk Screener overrides a strong score: such a deal is \
NO-GO. Otherwise: GO if it meets or beats the benchmark band, CONDITIONAL if it \
clears every floor but trails the benchmarks, NO-GO if it falls short.
- When given multiple deals or a multi-deal file, call rank_and_export to produce \
the ranking spreadsheet, then summarize the order.

Deliver, per deal: the decision, a 0-100 score, the two or three numbers that drove \
it versus Hamburg/Lewiston, and the top risk. Lead with the verdict. This is \
analytical decision support, not investment advice."""


def _chair_tools(curator: Agent, underwriter: Agent, market: Agent, risk: Agent) -> list:
    @beta_tool
    def ask_benchmark_curator(question: str) -> str:
        """Ask the Benchmark Curator about the Hamburg/Lewiston bar or thresholds.

        Args:
            question: What you want to know about the reference deals.
        """
        return curator.run(question)

    @beta_tool
    def ask_underwriter(task: str, files: str = "") -> str:
        """Ask the Underwriter to extract and score a deal's economics.

        Args:
            task: What to evaluate.
            files: Comma-separated path(s) to the deal file(s).
        """
        return underwriter.run(task if not files else f"{task}\n\nFiles: {files}")

    @beta_tool
    def ask_market_scorer(task: str, files: str = "") -> str:
        """Ask the Market Scorer to judge the market quality of a deal.

        Args:
            task: What to evaluate.
            files: Comma-separated path(s) to the deal file(s).
        """
        return market.run(task if not files else f"{task}\n\nFiles: {files}")

    @beta_tool
    def ask_risk_screener(task: str, files: str = "") -> str:
        """Ask the Risk Screener for knockouts and red flags on a deal.

        Args:
            task: What to evaluate.
            files: Comma-separated path(s) to the deal file(s).
        """
        return risk.run(task if not files else f"{task}\n\nFiles: {files}")

    return [ask_benchmark_curator, ask_underwriter, ask_market_scorer, ask_risk_screener, rank_and_export]


def build_committee_chair(
    curator: Agent | None = None,
    underwriter: Agent | None = None,
    market: Agent | None = None,
    risk: Agent | None = None,
) -> Agent:
    curator = curator or build_benchmark_curator()
    underwriter = underwriter or build_underwriter()
    market = market or build_market_scorer()
    risk = risk or build_risk_screener()
    return Agent(
        name="gonogo_committee_chair",
        system=_CHAIR_SYS,
        tools=_chair_tools(curator, underwriter, market, risk),
    )


def build_gonogo_committee() -> Agent:
    """Build the full five-agent committee. Returns the Chair (the entry point)."""
    return build_committee_chair()


_BUILDERS = {
    "chair": build_committee_chair,
    "benchmark": build_benchmark_curator,
    "underwriter": build_underwriter,
    "market": build_market_scorer,
    "risk": build_risk_screener,
}
