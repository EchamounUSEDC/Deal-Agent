"""
utils/mock_calls.py — the recorded Logan/Ryan mock-call series.

Three staged calls between Ryan (USEDC rep) and Logan (a financial
advisor on the Cambridge platform), recorded as training material.
The audio ships in assets/mock_calls/; the structured notes below were
reconstructed from offline transcription of the recordings (summaries
and dialogue beats are faithful paraphrases, not verbatim quotes).

Used in two places:
- Sales School curriculum: each call is a case-study listening
  assignment attached to the training week it best illustrates.
- Objection roleplay: "The Logan calls" mode — the AI plays Logan at
  each stage of the sequence so reps can run the same call themselves.
"""

from __future__ import annotations

from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "mock_calls"

MOCK_CALLS = [
    {
        "id": "logan-1",
        "n": 1,
        "title": "Call 1 — the cold open",
        "file": "logan_call_1.m4a",
        "stage": "Cold open & discovery",
        "persona": ("Logan, a financial advisor on the Cambridge platform, "
                    "taking a cold call from a wholesaler he has never heard of"),
        "summary": (
            "Ryan cold-calls Logan: he's been having tax-focused calls with "
            "Cambridge advisors whose clients are writing bigger-than-expected "
            "checks to the IRS, and asks whether Logan feels he has tools to "
            "address that. Logan admits he doesn't get that question much and "
            "has few options. Ryan lays out the three pillars — first-year "
            "income write-off (35–90% of the investment), Roth-conversion tax "
            "bills cut roughly in half, and the same for recent capital "
            "gains — fields Logan's active-vs-passive income question, and "
            "books a 15–30 minute screen-share for the next afternoon."
        ),
        "listen_for": [
            "The hook is a problem question, not a pitch: “your clients are "
            "writing bigger-than-expected checks to the IRS — do you have the "
            "tools to address that?” (SPIN: problem → implication).",
            "The first fifteen seconds carry name, firm, and reason for "
            "calling in one breath — the thin-slicing window where "
            "credibility forms (Ambady & Rosenthal).",
            "Ryan differentiates through the platform (a small shop among "
            "~4,000 Cambridge advisors vs. the wirehouse giants) before any "
            "product mechanics — relevance before features.",
            "When Logan raises active-vs-passive income, Ryan answers the "
            "technical point directly — an ability signal (trust research), "
            "not a deflection.",
            "The close is a calendared, specific next step (“tomorrow "
            "afternoon”), never “call me back”.",
        ],
        "advisor_script": [
            "Logan speaking.",
            "Honestly, I don't get that question much. Clients complain about "
            "taxes every April, but I don't really have many options to hand "
            "them. What exactly do you guys do?",
            "Hm — is that write-off active or passive? Most of the "
            "flow-through deals I've seen only offset passive income, which "
            "doesn't help my W-2-heavy clients.",
        ],
        "areas": ["discovery", "delivery"],
    },
    {
        "id": "logan-2",
        "n": 2,
        "title": "Call 2 — the re-connect",
        "file": "logan_call_2.m4a",
        "stage": "Follow-up & credibility",
        "persona": ("Logan, a busy advisor who only vaguely remembers Ryan "
                    "from one earlier call and takes a lot of wholesaler calls"),
        "summary": (
            "Ryan calls back and Logan barely remembers him. Instead of "
            "re-pitching from zero, Ryan re-anchors with credibility — USEDC "
            "does everything related to tax mitigation and has been an "
            "approved Cambridge partner for four or five years — then walks "
            "the three-pillar menu again (first-year write-off on the 1099 as "
            "non-passive income, Roth conversions with the tax bill "
            "discounted ~50%, capital gains realized in the past 180 days cut "
            "in half) and ends with a choice question: which of the three "
            "fits your book? He offers case studies and white papers and asks "
            "for 15–30 minutes early the next week."
        ),
        "listen_for": [
            "The recovery: Logan doesn't remember him. Ryan re-anchors with "
            "verifiable credibility (approved partner, ten years, first "
            "sponsors on the platform) instead of restarting the pitch — "
            "integrity and ability signals (Mayer-Davis-Schoorman).",
            "The three-pillar menu ends with “which of the three speaks to "
            "you?” — the advisor names the need himself (SPIN need-payoff; "
            "OARS change-talk).",
            "Social proof stays factual — case studies, white papers, tenure "
            "on the platform — no hype adjectives, which keeps it inside "
            "FINRA 2210's fair-and-balanced lane.",
            "The ask stays small: 15–30 minutes with visuals. A priming dose "
            "that opens the information gap without dumping everything "
            "(Loewenstein).",
        ],
        "advisor_script": [
            "Logan speaking… sorry, Ryan from where? US Energy? Remind me — "
            "I take a lot of these calls.",
            "Right, the tax thing. Look, I've got maybe two clients writing "
            "six-figure checks to the IRS every year. Which of those three "
            "pillars actually fits a normal advisory book?",
            "The Roth conversion piece sounds too good to be true — how "
            "exactly are you cutting a conversion tax bill in half? And is "
            "Cambridge actually signed off on all of this?",
        ],
        "areas": ["objection handling", "relationship building"],
    },
    {
        "id": "logan-3",
        "n": 3,
        "title": "Call 3 — program selection & the deadline",
        "file": "logan_call_3.m4a",
        "stage": "Deepening interest & next step",
        "persona": ("Logan, now genuinely interested — he has read the "
                    "material Ryan sent and has a specific client in mind, "
                    "but is wary of being rushed"),
        "summary": (
            "Logan has read what Ryan sent and is excited. Ryan asks which of "
            "USEDC's program types interests him rather than assuming; Logan "
            "points to the 1031 angle for clients who sold property. Ryan "
            "teaches the QBI-threshold idea with a concrete persona — the "
            "dentist whose income sits just above the threshold, where an "
            "85–90% first-year deduction pulls them back under it — and "
            "discloses a real early-investor deadline at the end of July "
            "(better rate, flexibility to add on later) while explicitly "
            "removing pressure: convincing a client to six figures in two "
            "weeks is tough, so let's get time on the books tomorrow and talk "
            "it through over screens."
        ),
        "listen_for": [
            "Logan arrives pre-sold — and Ryan still asks which program "
            "interests him instead of assuming. Discovery never stops.",
            "The QBI-threshold explanation is tied to a concrete client "
            "persona (the over-threshold dentist) — problem-centered adult "
            "learning (Knowles), not an abstract tax lecture.",
            "The compliance masterclass: the July deadline is a real, "
            "disclosed program fact, and Ryan pairs it with explicit "
            "pressure-removal (“I'm not pressing you… six figures in two "
            "weeks is tough”). That's the research line between a factual "
            "deadline and manufactured urgency (FINRA 2210).",
            "Every call in the series ends the same way: a booked, specific "
            "next step with screens and visuals.",
        ],
        "advisor_script": [
            "Hey Ryan — good timing, actually. I read the piece you sent "
            "over. The 1031 angle caught my eye; I've got a client who just "
            "sold a rental portfolio.",
            "Before we go further — what's this end-of-July deadline about? "
            "I'm not rushing a client into a six-figure decision in two "
            "weeks.",
            "Walk me through the QBI threshold piece once more — the dentist "
            "example. If the deduction pulls them back under the threshold, "
            "what does the real after-tax math look like?",
        ],
        "areas": ["closing", "product knowledge"],
    },
]

_AREA_TO_CALL = {area: call for call in MOCK_CALLS for area in call["areas"]}


def call_for_area(area: str) -> dict | None:
    """The case-study call that best illustrates a curriculum area."""
    return _AREA_TO_CALL.get(area)


def audio_path(call: dict) -> Path:
    return ASSETS / call["file"]
