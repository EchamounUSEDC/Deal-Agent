"""Command-line entry point for Deal-Agent.

Examples
--------
# Full pipeline via the orchestrator (default):
python -m deal_agent.cli "Should we acquire this site? Formulate a deal." \\
    --files data/operating_statement.xlsx data/parcels.geojson data/plat.pdf

# Run a single specialist:
python -m deal_agent.cli "Interpret these financials" \\
    --agent financial --files data/t12.xlsx

python -m deal_agent.cli "What is the total acreage and zoning?" \\
    --agent land --files data/parcels.geojson data/zoning_map.png
"""

from __future__ import annotations

import argparse
import sys

from .agents import (
    build_deal_strategist,
    build_financial_analyst,
    build_land_surveyor,
    build_orchestrator,
)

_BUILDERS = {
    "orchestrator": build_orchestrator,
    "financial": build_financial_analyst,
    "land": build_land_surveyor,
    "strategist": build_deal_strategist,
}


def _build_prompt(instruction: str, files: list[str]) -> tuple[str, list[str]]:
    """Append file paths to the instruction; route image/PDF maps as attachments."""
    image_like = tuple([".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf"])
    attachments = [f for f in files if f.lower().endswith(image_like)]
    if files:
        instruction = f"{instruction}\n\nInput files: {', '.join(files)}"
    return instruction, attachments


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="deal-agent", description=__doc__)
    parser.add_argument("instruction", help="What you want the agent(s) to do.")
    parser.add_argument(
        "--agent",
        choices=sorted(_BUILDERS),
        default="orchestrator",
        help="Which agent to run (default: orchestrator, the full pipeline).",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=[],
        help="Paths to spreadsheets, parcel data, and/or map images/PDFs.",
    )
    args = parser.parse_args(argv)

    agent = _BUILDERS[args.agent]()
    prompt, attachments = _build_prompt(args.instruction, args.files)

    # Only the single-agent map/financial flows pass attachments directly; the
    # orchestrator delegates file paths to its specialists as text.
    direct_attachments = attachments if args.agent in {"land", "financial", "strategist"} else None

    print(f"\n=== Running agent: {agent.name} ===\n", file=sys.stderr)
    result = agent.run(prompt, attachments=direct_attachments)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
