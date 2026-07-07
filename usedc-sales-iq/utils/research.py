"""
utils/research.py — the research library the AI trains on.

Encodes the USEDC Sales School source library (thin-slicing, honest
signals, SPIN, OARS, trust theory, curiosity/information-gap theory,
speech-rate research, interruption science, FINRA rules, and the
advisor pain-point playbooks) as machine-readable data, plus the
Phase-3 scoring architecture built on it:

- score_call(row):   react to a single call — 0-5 category scores,
                     a confidence-weighted composite, and a FINRA-style
                     compliance flag layer that overrides the score.
- score_response(s): react to a single utterance (roleplay/live coach),
                     with every judgment citing its research anchor.
- principles_digest(): compact digest injected into every live AI
                     prompt, so generated coaching is grounded in the
                     same sources as the deterministic engine.

Confidence discipline (per the library's Phase 3): a category's weight
in the composite reflects the strength of its research base, not how
important the behavior is. High = 1.0, Medium = 0.7, Low = 0.3.
Compliance is a GATE, not an input — a hard flag forces human review
regardless of the numeric score.
"""

from __future__ import annotations

import re

TIER_WEIGHT = {"high": 1.0, "medium": 0.7, "low": 0.3}

# ---------------------------------------------------------------------------
# Sources (id -> citation). Tier 1 = peer-reviewed/regulatory/primary,
# Tier 2 = credible industry research, Tier 3 = practitioner content.
# ---------------------------------------------------------------------------

SOURCES = {
    "thin-slice": ("Thin slices of expressive behavior — Ambady & Rosenthal, "
                   "Harvard / J. Personality & Social Psychology, 1993", 1),
    "honest-signals": ("Thin Slices of Negotiation (nonverbal dynamics predict ~30% "
                       "of outcome variance) — Curhan & Pentland, MIT / "
                       "J. Applied Psychology, 2007", 1),
    "speech-rate": ("Speed of Speech and Persuasion (120–180 wpm normal band; "
                    "inverted-U vs credibility) — Miller, Maruyama, Beaber & "
                    "Valone, NIMH-funded, 1976", 1),
    "fluency": ("Interruptions and silences: a single disrupted-fluency moment "
                "produces felt rejection — peer-reviewed conversation research, 2018", 1),
    "turn-taking": ("Perceived conversation quality: turn-taking equality predicts "
                    "quality; unsuccessful interruptions predict the opposite — "
                    "HCI research", 1),
    "spin": ("SPIN Selling field study (implication & need-payoff questions "
             "correlate with success in complex sales) — Rackham", 2),
    "oars": ("Motivational interviewing / OARS: reflect-then-respond around "
             "resistance beats direct confrontation", 1),
    "trust": ("Integrative model of trust: Ability + Benevolence + Integrity — "
              "Mayer, Davis & Schoorman, 1995", 1),
    "curiosity": ("Information-gap theory of curiosity ('priming dose'; an opened "
                  "but abandoned gap converts to frustration) — Loewenstein, 1994", 1),
    "andragogy": ("Adult learning is problem-centered, not content-centered — "
                  "Knowles' andragogy", 1),
    "finra-2210": ("FINRA Rule 2210 — communications must be fair and balanced; "
                   "no false, exaggerated, or misleading claims", 1),
    "finra-2111": ("FINRA Rule 2111 (Suitability) & 2090 (Know Your Customer)", 1),
    "gong-vm": ("Voicemail dataset, 300M+ calls: voicemails prime the next touch "
                "(email replies ~2x) but 3+ per prospect backfires — Gong Labs", 2),
    "cerulli": ("The Great Wealth Transfer: $124T through 2048; family meetings are "
                "the top retention strategy (81% of HNW practices) — Cerulli, 2024", 1),
    "pwc-fbs": ("US Family Business Survey: only ~34% of family businesses have a "
                "documented succession plan — PwC", 1),
    "bengen-swr": ("4% initial withdrawal rate research — Bengen, J. Financial "
                   "Planning, 1994; Morningstar's forward-looking updates put fixed "
                   "at ~3.9%, flexible guardrails up to ~5.7%", 1),
    "guardrails": ("Guardrails withdrawal decision rules — Guyton & Klinger, "
                   "J. Financial Planning, 2004/2006", 1),
    "roth": ("Roth conversion bracket-optimization (McQuarrie & DiLellio) AND the "
             "'long-horizon wager' caveat (McQuarrie, FPA 2024) — present both sides", 1),
    "concentration": ("The 'concentration paradox': concentrated stock is the "
                      "client's identity/success story, not just a risk statistic — "
                      "Envestnet", 2),
    "daf": ("National Study on Donor-Advised Funds — DAF Research Collaborative / "
            "DePaul, 2024; appreciated-asset giving mechanics", 1),
    "qoz": ("QOZ community-impact research is negative-to-mixed (Brookings, Tax "
            "Policy Center, GAO); investor tax mechanics are real — never conflate "
            "the two", 1),
    "alts": ("Institutions allocate ~25% to alternatives vs ~5% for advisors "
             "(Fidelity); but 'Harmful diversification' (peer-reviewed) shows the "
             "benefit is strategy- and period-specific, never universal", 2),
}


def cite(source_id: str) -> str:
    return SOURCES[source_id][0]


# ---------------------------------------------------------------------------
# The 20-category scoring architecture (Phase 3).
# status: 'active'  = scorable from the delivery metrics on the calls table
#         'partial' = scorable as a proxy from a transcript line / skills
#         'pending' = needs full transcript/audio from the Call Analyzer
# ---------------------------------------------------------------------------

CATEGORIES = [
    {"name": "Active Listening", "confidence": "high", "status": "active",
     "reads": "interruptions per call (turn violations)", "anchor": ["fluency", "oars"]},
    {"name": "Discovery & Questioning", "confidence": "medium", "status": "active",
     "reads": "open-question count (SPIN classification pending transcripts)",
     "anchor": ["spin", "oars"]},
    {"name": "Cold Call Openings", "confidence": "high", "status": "pending",
     "reads": "first 10–15s: pace stability, filler words, clear intro (needs audio)",
     "anchor": ["thin-slice"]},
    {"name": "Advisor Psychology", "confidence": "medium", "status": "pending",
     "reads": "bias-aware framing (anchoring, loss/gain frames) — needs transcript",
     "anchor": ["concentration", "roth"]},
    {"name": "Trust Building", "confidence": "high", "status": "partial",
     "reads": "ability/benevolence/integrity signals (skills proxy today)",
     "anchor": ["trust"]},
    {"name": "Behavioral Finance", "confidence": "high", "status": "pending",
     "reads": "claims consistent with established bias research — needs transcript",
     "anchor": ["roth", "concentration"]},
    {"name": "Tax-Planning Discussions", "confidence": "medium", "status": "pending",
     "reads": "two-sided framing on contested topics; accuracy vs current law",
     "anchor": ["roth", "daf", "qoz"]},
    {"name": "Executive Presence", "confidence": "high", "status": "pending",
     "reads": "activity balance, vocal mirroring, engagement consistency (needs audio)",
     "anchor": ["honest-signals"]},
    {"name": "Voice & Speech", "confidence": "high", "status": "active",
     "reads": "words per minute vs the 120–180 research band", "anchor": ["speech-rate"]},
    {"name": "Communication Clarity", "confidence": "medium", "status": "pending",
     "reads": "jargon paired with plain-language restatement — needs transcript",
     "anchor": ["andragogy"]},
    {"name": "Objection Handling", "confidence": "medium", "status": "partial",
     "reads": "reflect-then-respond vs immediate counter (snippet proxy today)",
     "anchor": ["oars", "finra-2210"]},
    {"name": "Financial Education & Simplification", "confidence": "high", "status": "active",
     "reads": "average uninterrupted explanation length (priming dose)",
     "anchor": ["curiosity", "andragogy"]},
    {"name": "Relationship Management", "confidence": "medium", "status": "pending",
     "reads": "multi-generational and planning-led framing — needs transcript",
     "anchor": ["cerulli"]},
    {"name": "Compliance & Ethics", "confidence": "high", "status": "active",
     "reads": "absolute claims, urgency/scarcity pressure, missing balance — A GATE, NOT A SCORE",
     "anchor": ["finra-2210", "finra-2111"]},
    {"name": "Gatekeeper Conversations", "confidence": "low", "status": "pending",
     "reads": "name use, respect language (thin evidence — coaching only, minimal weight)",
     "anchor": ["thin-slice"]},
    {"name": "Voicemail Effectiveness", "confidence": "medium", "status": "pending",
     "reads": "length <30s, personalized reason, references next touch",
     "anchor": ["gong-vm"]},
    {"name": "Curiosity Creation", "confidence": "high", "status": "pending",
     "reads": "gap specificity, priming ratio, gap-closure latency — needs transcript",
     "anchor": ["curiosity"]},
    {"name": "Planning Opportunity Identification", "confidence": "high", "status": "pending",
     "reads": "pain-point surfaced as a need-payoff question — needs transcript",
     "anchor": ["spin", "cerulli", "pwc-fbs"]},
    {"name": "Conversation Structure", "confidence": "high", "status": "active",
     "reads": "talk-time balance (turn-taking equality)", "anchor": ["turn-taking", "spin"]},
    {"name": "Follow-up Conversion / Overall Experience", "confidence": "high", "status": "partial",
     "reads": "concrete next step vs vague ending; composite of all categories",
     "anchor": ["curiosity"]},
]


# ---------------------------------------------------------------------------
# Compliance gate (FINRA 2210-style language screens)
# ---------------------------------------------------------------------------

ABSOLUTE_CLAIMS = [
    "guarantee", "guaranteed", "can't lose", "cannot lose", "no risk",
    "risk-free", "risk free", "never fails", "always goes up", "sure thing",
    "certain to", "promise you",
]
URGENCY_PRESSURE = [
    "act now", "last chance", "only today", "today only", "before it's too late",
    "spots left", "closing soon", "won't last", "everyone is buying",
    "don't miss out", "once in a lifetime",
]
UNSUPPORTED_IMPACT = [
    "transforms communities", "revitalizes the neighborhood", "guaranteed community",
]


def _matches(text: str, phrases: list[str]) -> list[str]:
    """Longest-match-wins so 'guaranteed' doesn't also flag 'guarantee'."""
    hits = [p for p in phrases if p in text]
    return [p for p in hits
            if not any(p != other and p in other for other in hits)]


def compliance_flags(text: str) -> list[str]:
    """FINRA-style screen. Any hit is a hard flag for human review — a gate,
    not a coaching-score input."""
    t = (text or "").lower()
    flags = []
    for phrase in _matches(t, ABSOLUTE_CLAIMS):
        flags.append(f"Absolute/exaggerated claim: “{phrase}” — {cite('finra-2210')}.")
    for phrase in _matches(t, URGENCY_PRESSURE):
        flags.append(f"Manufactured urgency/scarcity: “{phrase}” — flagged per "
                     f"{cite('finra-2210')} and the ethical-persuasion boundary research.")
    for phrase in _matches(t, UNSUPPORTED_IMPACT):
        flags.append(f"Unsupported community-impact claim: “{phrase}” — {cite('qoz')}.")
    return flags


# ---------------------------------------------------------------------------
# Reacting to a call — the scoring engine over the delivery metrics
# ---------------------------------------------------------------------------

def _band_score(value: float, ideal_lo: float, ideal_hi: float,
                ok_lo: float, ok_hi: float) -> float:
    """5 inside the ideal band, 4 inside the ok band, decaying outside —
    band scoring per the speech-rate research (never a single target)."""
    if ideal_lo <= value <= ideal_hi:
        return 5.0
    if ok_lo <= value <= ok_hi:
        return 4.0
    dist = (ok_lo - value) if value < ok_lo else (value - ok_hi)
    return max(1.0, 4.0 - dist / 10.0)


def score_call(row: dict) -> dict:
    """React to one call. `row` is a calls-table row (dict-like).
    Returns {"categories": [...], "composite": float|None,
             "flags": [...], "review_required": bool}."""
    cats: list[dict] = []

    def add(name: str, score: float, note: str, source_id: str, proxy: bool = False):
        conf = next(c["confidence"] for c in CATEGORIES if c["name"] == name)
        cats.append({
            "name": name, "score": round(min(5.0, max(0.0, score)), 1),
            "confidence": conf, "weight": TIER_WEIGHT[conf],
            "note": note + (" (proxy — full transcript will refine this)" if proxy else ""),
            "source": cite(source_id),
        })

    ints = row.get("interruptions")
    if ints is not None:
        score = {0: 5.0, 1: 3.8, 2: 2.5}.get(int(ints), 1.0)
        add("Active Listening", score,
            f"{int(ints)} interruption(s). Even one disrupted-fluency moment "
            "produces felt rejection — and it compounds.", "fluency")

    oq = row.get("open_questions")
    if oq is not None:
        score = min(5.0, 1.0 + float(oq) * 1.1)
        add("Discovery & Questioning", score,
            f"{int(oq)} open question(s). Implication and need-payoff questions "
            "are what correlate with success — volume is the floor, not the goal.",
            "spin")

    wpm = row.get("words_per_minute")
    if wpm is not None:
        score = _band_score(float(wpm), 130, 170, 120, 180)
        add("Voice & Speech", score,
            f"{float(wpm):.0f} wpm vs the 120–180 research band (credibility follows "
            "an inverted-U — both extremes hurt).", "speech-rate")

    tr = row.get("talk_ratio")
    if tr is not None:
        imbalance = abs(float(tr) - 0.5)
        score = 5.0 if imbalance <= 0.08 else 4.0 if imbalance <= 0.15 \
            else 2.5 if imbalance <= 0.25 else 1.5
        add("Conversation Structure", score,
            f"Rep spoke {float(tr) * 100:.0f}% of the call. Turn-taking equality "
            "predicts perceived conversation quality.", "turn-taking")

    mono = row.get("avg_monologue_sec")
    if mono is not None:
        m = float(mono)
        score = 5.0 if m <= 45 else 4.0 if m <= 60 else 2.5 if m <= 80 else 1.0
        add("Financial Education & Simplification", score,
            f"Average explanation ran {m:.0f}s. The 'priming dose' finding: partial "
            "information sustains curiosity; complete dumps collapse it.", "curiosity")

    skills = row.get("skills") or {}
    if isinstance(skills, dict) and skills.get("relationship building") is not None:
        add("Trust Building", float(skills["relationship building"]) / 20.0,
            "Benevolence/ability/integrity balance, proxied from the call's "
            "relationship-building sub-score.", "trust", proxy=True)

    snippet = row.get("transcript_snippet") or ""
    if snippet:
        s_score, s_notes, _ = score_response(snippet)
        add("Objection Handling", s_score / 20.0,
            "Scored from the call's key line: " + " ".join(n for n in s_notes[:2]),
            "oars", proxy=True)

    outcome = row.get("outcome")
    if outcome is not None:
        score = {"converted": 5.0, "follow_up": 3.5, "no_sale": 2.0}.get(outcome, 2.5)
        add("Follow-up Conversion / Overall Experience", score,
            f"Outcome: {outcome}. A concrete, scheduled next step is the difference "
            "between an open gap and an abandoned one.", "curiosity", proxy=True)

    flags = compliance_flags(f"{snippet} {row.get('summary', '')}")

    weighted = [(c["score"], c["weight"]) for c in cats]
    composite = (round(sum(s * w for s, w in weighted) / sum(w for _, w in weighted), 2)
                 if weighted else None)
    return {
        "categories": cats,
        "composite": composite,
        "flags": flags,
        "review_required": bool(flags),
    }


# ---------------------------------------------------------------------------
# Reacting to a single utterance — used by the roleplay coach
# ---------------------------------------------------------------------------

_ACK_WORDS = ("understand", "fair", "hear you", "makes sense", "appreciate",
              "great question", "i get", "good point", "that's real")
_NEXT_STEP = ("calendar", "schedule", "tuesday", "thursday", "book", "next step",
              "follow-up", "follow up", "15 minutes", "put time")
_OPEN_STARTERS = ("what", "how", "why", "walk me through", "tell me", "help me understand")


def score_response(text: str) -> tuple[int, list[str], list[str]]:
    """React to one rep utterance. Returns (score 0-100, coaching notes with
    citations, compliance flags). Deterministic — this is the same engine in
    demo and live mode; live mode adds generated color on top."""
    t = text.lower()
    score, notes = 30, []

    if any(w in t for w in _ACK_WORDS):
        score += 20
        notes.append("✅ Reflect-then-respond: you acknowledged before countering — "
                     f"the pattern the evidence favors ({cite('oars')}).")
    else:
        notes.append("⚠️ You countered without acknowledging first. Reflective "
                     f"listening around resistance beats confrontation ({cite('oars')}).")

    has_q = "?" in text
    is_open = any(t.strip().rstrip("?").endswith(w) or w in t for w in _OPEN_STARTERS)
    if has_q and is_open:
        score += 25
        notes.append("✅ You handed the turn back with an open question — implication/"
                     f"need-payoff questions drive complex sales ({cite('spin')}).")
    elif has_q:
        score += 12
        notes.append("🟡 You asked a question, but a closed one. Open it up — 'what' "
                     f"and 'how' questions let the advisor voice the need ({cite('spin')}).")
    else:
        notes.append("⚠️ No question — you kept the turn. Turn-taking equality predicts "
                     f"conversation quality ({cite('turn-taking')}).")

    words = len(text.split())
    if words <= 60:
        score += 15
        notes.append("✅ Tight. Partial information sustains curiosity — the 'priming "
                     f"dose' ({cite('curiosity')}).")
    else:
        notes.append("⚠️ That's a monologue. Information dumps collapse the curiosity "
                     f"gap ({cite('curiosity')}).")

    if any(w in t for w in _NEXT_STEP):
        score += 10
        notes.append("✅ Concrete next step — an opened gap with scheduled closure, "
                     "not an abandoned one.")

    flags = compliance_flags(text)
    if flags:
        score = min(score, 25)
        notes.insert(0, "🚫 COMPLIANCE FLAG — this response would be routed for human "
                        "review; the score is capped regardless of technique.")
    return min(score, 100), notes, flags


# ---------------------------------------------------------------------------
# Advisor pain-point playbooks (Phase 2/2b, condensed)
# ---------------------------------------------------------------------------

PAIN_POINTS = [
    {
        "name": "Concentrated stock positions",
        "why": "≥30% in a single name creates tax, volatility, and firm-level risk — "
               "but the 'concentration paradox' means the position is the client's "
               "success story, so a purely statistical pitch fails.",
        "questions": ["Do you have clients with 20–25%+ of net worth in one name?",
                      "How did the position build — compensation, a sale, inheritance?",
                      "Has anyone modeled a 30–50% drawdown in that one name against their goals?"],
        "caution": "Lead with identity-aware framing and a menu of options (exchange "
                   "funds, direct indexing, staged sales, charitable) — never one product.",
        "anchor": "concentration",
    },
    {
        "name": "Roth conversion planning",
        "why": "The window between retirement and RMDs is often the most valuable "
               "tax-planning opportunity a client gets; bracket-by-bracket conversion "
               "windows are well researched.",
        "questions": ["Do you have clients in the gap years between retiring and RMDs?",
                      "Modeling conversions bracket-by-bracket, or one-time?",
                      "How is the tax bill funded — from the IRA, or outside assets?"],
        "caution": "Always present BOTH sides: bracket optimization AND the "
                   "'long-horizon wager' caveat. A one-sided 'just convert' pitch is "
                   "factually incomplete.",
        "anchor": "roth",
    },
    {
        "name": "Retirement income & withdrawal strategy",
        "why": "The most rigorously researched area in financial planning — fixed "
               "~3.9% vs flexible guardrails up to ~5.7% is a credibility-building "
               "distinction a rep can teach.",
        "questions": ["Are retiree clients on a fixed percentage or dynamic guardrails?",
                      "How are you handling sequence-of-returns risk for new retirees?"],
        "caution": "Never quote '4%' as a timeless rule — the research itself has "
                   "moved. That's an unrealistic-projection flag.",
        "anchor": "bengen-swr",
    },
    {
        "name": "Charitable planning (DAFs & appreciated assets)",
        "why": "Donating appreciated securities avoids capital gains entirely with a "
               "fair-market-value deduction — and a DAF separates the tax decision "
               "from the giving decision.",
        "questions": ["Any clients giving ad hoc who could formalize it?",
                      "Anyone with an unusually high-income year?",
                      "Anyone sitting on appreciated stock better given than sold?"],
        "caution": "Uncontested mechanics — no need to oversell. Payout-rate policy "
                   "debate exists; keep claims to the client-level mechanics.",
        "anchor": "daf",
    },
    {
        "name": "Qualified Opportunity Zones",
        "why": "Investor-level tax mechanics (deferral, basis step-ups, 10-year "
               "exclusion) are real and documented.",
        "questions": ["Do any clients have large unrealized gains looking for deferral?"],
        "caution": "THE compliance test case: community-impact claims are NOT "
                   "supported by the research (Brookings, TPC, GAO). Tax mechanics "
                   "factual; social benefit contested. Never conflate them.",
        "anchor": "qoz",
    },
    {
        "name": "Business-owner exit & succession",
        "why": "Only ~34% of family businesses have a documented succession plan; the "
               "business is usually the owner's largest asset AND retirement plan.",
        "questions": ["Clients where the business is half their net worth with no exit plan?",
                      "Has anyone run a third-party valuation, or is it a guess?",
                      "Family succession, ESOP, or outside sale — or undecided?"],
        "caution": "Separate succession ('who leads') from exit ('how do I transition') "
                   "before any product talk; respect the identity dimension.",
        "anchor": "pwc-fbs",
    },
    {
        "name": "Estate & wealth transfer",
        "why": "$124T transfers through 2048, heavily concentrated in HNW households; "
               "41% of advisors call it an existential threat because heirs leave.",
        "questions": ["Do you have a relationship with clients' adult children?",
                      "What would your client's spouse do if something happened to them?",
                      "Any clients expecting a significant inheritance themselves?"],
        "caution": "Family meetings beat trust mechanics — the top retention strategy "
                   "at 81% of HNW practices. The '70%/90% wealth lost' stat is industry "
                   "lore, not peer-reviewed — present it as such.",
        "anchor": "cerulli",
    },
    {
        "name": "Alternative investments",
        "why": "Institutions allocate ~25% vs advisors' ~5% — a structural access gap, "
               "not a judgment gap.",
        "questions": ["Are client portfolios closer to institutional norms or traditional?",
                      "What's held them back — access, liquidity, or client comfort?"],
        "caution": "Never say alternatives 'always diversify' — peer-reviewed research "
                   "('Harmful diversification') shows the benefit is strategy- and "
                   "period-specific. State the narrow, defensible claim.",
        "anchor": "alts",
    },
]


# ---------------------------------------------------------------------------
# The digest injected into live AI prompts — how the AI "trains itself"
# ---------------------------------------------------------------------------

def principles_digest() -> str:
    return """You coach and score against this research library (cite it when reacting):
- First impressions form in seconds and are hard to reverse (Ambady & Rosenthal
  thin-slicing): weight call openings disproportionately; track recovery separately.
- Speak inside the 120-180 wpm band (Miller et al. 1976). Credibility vs pace is
  an inverted U: score against the band, never a single ideal number.
- Interruptions: even one disrupted-fluency moment creates felt rejection
  (conversation-fluency research); balanced turn-taking predicts perceived
  quality. Distinguish supportive overlap from turn-violating interruption.
- Objections: reflect-then-respond (motivational interviewing/OARS) — acknowledge
  before countering; never confront resistance head-on.
- Questions: implication and need-payoff questions (SPIN, Rackham) beat
  situation questions; the advisor should voice the opportunity themselves.
- Curiosity: give a priming dose that opens a specific information gap, and always
  schedule its closure — an abandoned gap converts to frustration (Loewenstein).
- Trust = Ability + Benevolence + Integrity (Mayer-Davis-Schoorman): specific
  correct statements, client-benefit framing, and consistency across calls.
- Explanations: problem-centered, tied to the advisor's stated client situation
  (Knowles); plain-language restatement after any jargon.
- COMPLIANCE IS A GATE (FINRA 2210/2111): no absolute/exaggerated claims
  ("guaranteed", "risk-free"), no manufactured urgency or scarcity pressure, keep
  claims fair and balanced with risks alongside benefits. Any violation overrides
  every other score and requires human review.
- Two-sided framing on contested topics: Roth conversions are bracket
  optimization AND a long-horizon wager; QOZ tax mechanics are factual but
  community-impact claims are unsupported; alternatives' diversification benefit
  is conditional, never universal; the 4% rule has moved (~3.9% fixed / ~5.7%
  guardrails, Morningstar).
- Confidence discipline: weight feedback by evidence strength (peer-reviewed >
  industry data > practitioner lore) and say which is which."""


def category_table() -> list[dict]:
    """Flat view for UI display."""
    return [
        {
            "Category": c["name"],
            "What the AI reads": c["reads"],
            "Confidence": c["confidence"].capitalize(),
            "Weight": TIER_WEIGHT[c["confidence"]],
            "Status": {"active": "🟢 scoring now", "partial": "🟡 proxy",
                       "pending": "⚪ needs transcript/audio"}[c["status"]],
            "Research anchor": "; ".join(cite(a).split(" — ")[-1] for a in c["anchor"]),
        }
        for c in CATEGORIES
    ]
