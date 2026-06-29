# Co-Gen CUP Presentation

Consolidated Investment-Committee presentation for the **Central Utility Plant (CUP)
Co-Generation project** (Mammoth Hill · Central City, CO), built from the two source
memos and styled to match the firm's IC deck template.

## Deliverable

- **`CoGen_CUP_Presentation.pptx`** — 18-slide deck on the IC template (navy / cream /
  red, Calibri). 16:9.

### Slide map

| # | Slide | Image |
|---|-------|-------|
| 1 | Title | — |
| 2 | **Project Overview** (the memo's first paragraph) | — |
| 3 | Divider — Advantages | — |
| 4 | Primary Focus | — |
| 5 | Application Timeline (IMEG phases → Xcel submittal) | — |
| 6 | CUP Location | site context map |
| 7 | Alternate Delivery Sources | — |
| 8 | Utility Cost Control | — |
| 9 | Long-Term Economic Payback | combined-cycle schematic |
| 10 | Central City Mini-District Constraints | — |
| 11 | Divider — Disadvantage | — |
| 12 | Time Value of Money | — |
| 13 | Proposed Equipment — Caterpillar CG170-16 ($599,000) | Caterpillar gen-set |
| 14 | Emissions Control & Exhaust Dilution | plume-dilution chart |
| 15 | Project Update & Status to Date | — |
| 16 | RFP & Consultant Selection | — |
| 17 | Recommendation | — |
| 18 | **Internal Comparison Agent** | scoring table |

Each memo bullet point is on its own slide; the memo's opening paragraph is the first
content slide; images are placed on the slides whose bullet they illustrate.

## Embedded comparison agent

The deck **embeds a runnable agent** at `agent/cogen_comparison_agent.py` *inside the
.pptx package itself* (the `.pptx` is a zip — the part travels with the file). It is a
dependency-free copy of [`deal_agent/agents/cogen_comparison_agent.py`](../deal_agent/agents/cogen_comparison_agent.py),
which scores the three CUP delivery options against weighted criteria for internal
comparison:

```bash
# extract and run the agent that ships inside the deck
unzip -p CoGen_CUP_Presentation.pptx agent/cogen_comparison_agent.py > agent.py
python agent.py            # weighted scoring matrix + recommendation
python agent.py --json     # machine-readable matrix
```

| Option | Weighted score (1–5) |
|--------|----------------------|
| USGPD self-develop & operate the CUP | **4.55** |
| Central City third-party mini-district | 2.60 |
| Xcel grid-only / independent developer | 1.95 |

Criteria & weights: Control 20, Timeline 20, Reliability 20, Cost Control 15,
Capital/Time-Value 15, Thermal Payback 10. Slide 18 renders this matrix; speaker notes
explain how to run it.

## Rebuilding

```bash
pip install python-pptx matplotlib Pillow
python gen_diagrams.py     # regenerates assets/{site_map,combined_cycle,plume}.png
python build_deck.py       # rebuilds CoGen_CUP_Presentation.pptx + re-embeds the agent
```

- `template.pptx` — the firm IC template the deck is built on (theme/master/layouts).
- `assets/` — images used in the deck. The combined-cycle, plume and site-context
  graphics are original diagrams drawn in the template palette; the Caterpillar image is
  from the Aaron Equipment quote.

> Source `.docx` memos are intentionally **not** committed (they are gitignored as they
> may contain confidential client data).
