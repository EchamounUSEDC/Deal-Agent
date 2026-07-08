"""
pages/sales_school.py — 🎓 Sales School

Personalized training built from each rep's real call data: a 4-week
curriculum targeting their weakest areas, a weekly lesson and daily tip,
an interactive objection roleplay (the AI plays a skeptical investor and
coaches every response), scored quizzes, a best-practices playbook, and
TED-Talk summaries. Demo mode is fully playable offline; live mode
upgrades the lesson text, roleplay, and quiz generation.
"""

from __future__ import annotations

from collections import Counter
from datetime import date

import pandas as pd
import streamlit as st

from pages.sales_coach import CLOSING_TECHNIQUES, DISCOVERY_QUESTIONS, REBUTTALS
from utils import research
from utils.ai import generate_json, is_live
from utils.database import calls_df, rep_names
from utils.mock_calls import MOCK_CALLS, audio_path, call_for_area
from utils.sample_data import SKILL_AREAS

# ---------------------------------------------------------------------------
# Static content library
# ---------------------------------------------------------------------------

DAILY_TIPS = [
    "Say the investor's name in the first 30 seconds — and mean it.",
    "Ask one more question before you pitch. Then ask another.",
    "Silence after your close is your friend. Whoever speaks first concedes.",
    "Write down the exact words of every objection you hear today.",
    "Slow down 10%. Confidence sounds unhurried.",
    "End every call with a calendared next step, never 'call me back'.",
    "Mirror the investor's last three words as a question — instant depth.",
    "Lead with the problem you solve, not the product you sell.",
    "One story beats five statistics. Have yours ready.",
    "Before dialing, decide the single thing this call must achieve.",
]

TED_TALKS = [
    {
        "title": "How great leaders inspire action — Simon Sinek",
        "length": "18 min",
        "summary": "People don't buy what you do, they buy why you do it. Sinek's "
                   "'golden circle' says to lead with purpose, then how, then what.",
        "apply": "Open investor calls with why USEDC exists — American energy "
                 "independence and investor income — before any fund mechanics.",
    },
    {
        "title": "How to speak so that people want to listen — Julian Treasure",
        "length": "10 min",
        "summary": "Vocal toolbox: register, timbre, prosody, pace, pitch, volume — "
                   "and the four leaks that make people tune out (gossip, judging, "
                   "negativity, exaggeration).",
        "apply": "Directly targets pace and monologue-length flags from your Sales "
                 "Coach delivery signals.",
    },
    {
        "title": "What I learned from 100 days of rejection — Jia Jiang",
        "length": "15 min",
        "summary": "Jiang deliberately sought rejection daily and found a 'no' is "
                   "often the start of a negotiation — ask 'why?' and stay in the room.",
        "apply": "When an investor passes, ask one curious follow-up question "
                 "instead of hanging up. That question is where deals reopen.",
    },
    {
        "title": "The puzzle of motivation — Dan Pink",
        "length": "18 min",
        "summary": "Autonomy, mastery, and purpose beat carrots and sticks for any "
                   "task requiring judgment.",
        "apply": "Give investors autonomy: offer two good options (allocation "
                 "sizes, funds) instead of pushing one — people commit to choices "
                 "they made themselves.",
    },
    {
        "title": "Your body language may shape who you are — Amy Cuddy",
        "length": "21 min",
        "summary": "Posture changes hormones and confidence. Two minutes of "
                   "expansive posture before a high-stakes moment measurably helps.",
        "apply": "Stand up for your toughest calls. Investors can hear posture.",
    },
]

QUESTION_BANK = [
    {
        "topic": "objection handling",
        "q": "An investor says 'the fees feel high.' What's the strongest first move?",
        "options": [
            "Apologize and mention a discount may be possible",
            "Reframe to net returns and offer the distribution history",
            "Explain that all funds have fees",
            "Change the subject to tax benefits",
        ],
        "answer": 1,
        "why": "Reframe cost as net outcome, then move to evidence. Apologizing "
               "validates the frame that fees are the problem.",
    },
    {
        "topic": "objection handling",
        "q": "'I need to talk to my spouse first.' Best response?",
        "options": [
            "'No problem, call me back when you've talked.'",
            "'What do you think they'll say?'",
            "'They should be part of this — can we book 15 minutes this week with them on the line?'",
            "'Most of my clients decide on their own.'",
        ],
        "answer": 2,
        "why": "Keep control of the next step and sell the three-way call. "
               "Waiting for a callback loses the deal to inertia.",
    },
    {
        "topic": "discovery",
        "q": "How many open-ended questions should you ask before presenting a product?",
        "options": ["None — lead with the pitch", "One", "At least three", "Ten or more"],
        "answer": 2,
        "why": "Three open questions is the working minimum to earn the right to "
               "pitch: motivation, current portfolio, decision process.",
    },
    {
        "topic": "discovery",
        "q": "Which is an open-ended discovery question?",
        "options": [
            "'Are you an accredited investor?'",
            "'Do you like monthly income?'",
            "'What would make this a great decision twelve months from now?'",
            "'Can I send you the brochure?'",
        ],
        "answer": 2,
        "why": "It invites a story about their goals — the other three can be "
               "answered in one word.",
    },
    {
        "topic": "closing",
        "q": "The call is going well but time is up. How do you end it?",
        "options": [
            "'Call me whenever you're ready.'",
            "'I'll email you some materials.'",
            "'I have Tuesday 2pm or Thursday 10am for a follow-up — which works?'",
            "'Think it over and I'll try you sometime next week.'",
        ],
        "answer": 2,
        "why": "The calendar close: a concrete either/or next step. Every other "
               "option hands momentum to chance.",
    },
    {
        "topic": "closing",
        "q": "After you ask for the commitment, the line goes quiet. You should…",
        "options": [
            "Fill the silence by adding more benefits",
            "Lower the suggested amount",
            "Wait — let the silence work",
            "Apologize for being pushy",
        ],
        "answer": 2,
        "why": "Silence after a close is decision time. Interrupting it restarts "
               "the sale and signals doubt.",
    },
    {
        "topic": "delivery",
        "q": "What talking pace lands best on investor calls?",
        "options": ["As fast as possible to fit more in", "Around 150 words per minute",
                    "Under 100 wpm so nothing is missed", "Pace doesn't matter"],
        "answer": 1,
        "why": "~150 wpm reads as confident and clear. Much faster sounds like "
               "pressure; much slower loses attention.",
    },
    {
        "topic": "delivery",
        "q": "The investor starts talking while you're explaining. What do you do?",
        "options": [
            "Finish your sentence — your point matters",
            "Talk slightly louder",
            "Stop immediately and listen",
            "Ask them to hold their thought",
        ],
        "answer": 2,
        "why": "An interrupting investor is giving you signal. Every talk-over "
               "costs trust; investors buy when they feel heard.",
    },
    {
        "topic": "relationship building",
        "q": "Best way to open a first call with a referred investor?",
        "options": [
            "Straight into the fund's returns",
            "Mention the referrer and ask what prompted them to take the call",
            "Read the compliance disclosure",
            "Ask how much they have to invest",
        ],
        "answer": 1,
        "why": "Borrowed trust plus an open question — rapport and discovery in "
               "one move.",
    },
    {
        "topic": "product knowledge",
        "q": "An investor asks a technical question you can't answer. You should…",
        "options": [
            "Give your best guess confidently",
            "Say it's not important",
            "Say you'll get the exact answer and book the follow-up call now",
            "Redirect to a different product",
        ],
        "answer": 2,
        "why": "Guessing risks compliance and trust. The honest answer plus a "
               "calendared follow-up turns a gap into a next step.",
    },
]

# Scripted investor for offline roleplay: opening line + two escalations.
INVESTOR_SCRIPTS = {
    "Fees feel high": [
        "I looked at the paperwork and honestly, the fees seem steep compared to my index funds.",
        "I hear you, but my advisor says anything over 1% is a red flag. Why should this be different?",
        "Okay… if the net numbers really hold up, maybe. What would you suggest as a next step?",
    ],
    "Market volatility": [
        "With everything going on with oil prices, this feels like a really risky time to get in.",
        "But what happens to my income if prices drop 30% like they did a few years back?",
        "That's a fairer picture than I expected. What would you do in my position?",
    ],
    "Liquidity concerns": [
        "My money would be locked up for years, right? I don't love that.",
        "What if something happens and I need that cash in year two?",
        "Sizing it that way makes some sense. How do we figure out the right amount?",
    ],
    "Needs spouse/advisor sign-off": [
        "This sounds interesting but I never move without my wife signing off.",
        "She's pretty skeptical of anything that isn't a mutual fund, honestly.",
        "A call with all three of us could work. When were you thinking?",
    ],
    "Timing — next quarter": [
        "I like it, but the timing's bad — check back with me next quarter.",
        "It's just a busy stretch. Nothing specific, I'd rather wait.",
        "Fine, you got me — there's no real blocker. What would starting small look like?",
    ],
    "Already invested elsewhere": [
        "I already have money in an energy fund with another firm.",
        "It's done okay, I guess. Distributions have been a little inconsistent.",
        "No one's ever actually compared them side by side for me. Could you?",
    ],
    "Risk tolerance": [
        "I'm retired. I can't afford to gamble at this point in my life.",
        "Even 'moderate' risk makes me nervous — I watched my neighbor lose big in 2008.",
        "Framing it as a small slice of the portfolio helps. What number were you thinking?",
    ],
}


WEEK_THEMES = {
    "discovery": (
        "Discovery that earns the right to pitch",
        "You can't prescribe before you diagnose. This week is about asking "
        "before telling: what prompted the call, what their portfolio does today, "
        "what a win looks like in twelve months.",
        ["Ask 3+ open questions on every call before mentioning any product",
         "Steal one question a day from the discovery list and make it yours",
         "After each call, write down the investor's goal in their own words"],
    ),
    "objection handling": (
        "Turning objections into conversations",
        "An objection is engagement — a question wearing armor. This week you'll "
        "meet your most common objection with curiosity instead of a monologue: "
        "acknowledge, ask, then answer with evidence.",
        ["Run the roleplay on your top objection until you score 80+",
         "Write out your rebuttal word-for-word, then cut it in half",
         "On live calls: pause two seconds before answering any objection"],
    ),
    "delivery": (
        "Delivery: pace, listening, and letting silence work",
        "What you say is half the call; how you sound is the other half. This "
        "week targets your delivery signals: pace near 150 wpm, zero talk-overs, "
        "explanations under 60 seconds, and more open questions.",
        ["Record yourself for one minute; count your wpm and cut 10%",
         "Track interruptions per call on paper — the goal is zero",
         "After every explanation, hand the turn back with a question"],
    ),
    "closing": (
        "Closing with a calendar, not a hope",
        "Deals die in the follow-up gap. This week, every call ends with a "
        "concrete, calendared next step — an either/or time offer, a three-way "
        "call with the spouse or advisor, or a decision.",
        ["End every call this week with an either/or calendar offer",
         "For each stalled follow-up, book the three-way call",
         "Practice the summary close: replay their words, then ask"],
    ),
    "relationship building": (
        "Trust before transactions",
        "Investors move money with people they trust. This week is rapport with "
        "a purpose: referrals, names, stories, and following up on the personal "
        "details that make the second call feel like a conversation.",
        ["Open each call with something you remember about them",
         "Ask one non-money question per call and write down the answer",
         "Send one useful, no-ask follow-up note per day"],
    ),
    "product knowledge": (
        "Knowing the product cold",
        "Confidence leaks when the details get fuzzy. This week is fluency: "
        "distributions, tax treatment, timelines, and the honest answer to the "
        "three hardest questions investors ask.",
        ["Write the three questions you dread and script exact answers",
         "Shadow one call from the team's product specialist or top rep",
         "Explain each fund to a friend in 60 seconds — no jargon"],
    ),
}


# ---------------------------------------------------------------------------
# Personalization — what does this rep's data say to work on?
# ---------------------------------------------------------------------------

def _rep_profile(rep: str, team_df: pd.DataFrame) -> dict:
    d = team_df[team_df["rep_name"] == rep]
    prof = {
        "rep": rep,
        "calls": len(d),
        "conversion": round(100 * (d["outcome"] == "converted").mean(), 1) if len(d) else 0,
        "team_conversion": round(100 * (team_df["outcome"] == "converted").mean(), 1),
        "top_objection": None,
        "weak_areas": [],
    }
    if d.empty:
        prof["weak_areas"] = ["discovery", "objection handling", "delivery", "closing"]
        return prof

    # Each candidate area gets a weight proportional to the size of THIS
    # rep's gap, so week 1 targets their single biggest problem rather
    # than the same generic theme for everyone.
    weak: list[tuple[float, str]] = []

    obj = Counter(o for objs in d["objections"] for o in objs)
    if obj:
        top_obj, top_n = obj.most_common(1)[0]
        prof["top_objection"] = top_obj
        weak.append((0.8 * top_n / len(d), "objection handling"))  # share of calls

    dd = d.dropna(subset=["interruptions"])
    td = team_df.dropna(subset=["interruptions"])
    if not dd.empty and not td.empty:
        prof["open_q"] = round(dd["open_questions"].mean(), 1)
        prof["team_open_q"] = round(td["open_questions"].mean(), 1)
        prof["interruptions"] = round(dd["interruptions"].mean(), 1)
        prof["team_interruptions"] = round(td["interruptions"].mean(), 1)
        prof["wpm"] = round(dd["words_per_minute"].mean())

        q_gap = prof["team_open_q"] - prof["open_q"]
        if q_gap > 0:
            weak.append((0.6 * q_gap, "discovery"))
        delivery_pressure = (
            max(0.0, prof["interruptions"] - prof["team_interruptions"])
            + max(0.0, (prof["wpm"] - 160) / 25)
        )
        if delivery_pressure > 0:
            weak.append((delivery_pressure, "delivery"))
        skills = pd.DataFrame([s for s in dd["skills"] if s])
        if not skills.empty:
            for rank, area in enumerate(skills.mean().sort_values().index[:2]):
                if area in WEEK_THEMES:
                    weak.append((0.3 - 0.05 * rank, area))

    conv_gap = prof["team_conversion"] - prof["conversion"]
    if conv_gap > 0:
        weak.append((conv_gap / 8, "closing"))

    seen, ordered = set(), []
    for _, area in sorted(weak, reverse=True):
        if area not in seen:
            seen.add(area)
            ordered.append(area)
    for filler in ["discovery", "objection handling", "delivery", "closing"]:
        if filler not in seen:
            ordered.append(filler)
            seen.add(filler)
    prof["weak_areas"] = ordered[:4]
    return prof


def _curriculum(prof: dict) -> list[dict]:
    fallback = []
    for i, area in enumerate(prof["weak_areas"]):
        theme, lesson, drills = WEEK_THEMES[area]
        why = f"Chosen because your call data flags {area} as a growth area."
        if area == "discovery" and prof.get("open_q") is not None:
            why = (f"You ask {prof['open_q']} open questions per call vs "
                   f"{prof['team_open_q']} for the team — discovery is the gap.")
        elif area == "delivery" and prof.get("interruptions") is not None:
            why = (f"You average {prof['interruptions']} interruptions per call "
                   f"(team: {prof['team_interruptions']}) at {prof.get('wpm', '—')} wpm — "
                   "delivery is where the data points.")
        elif area == "objection handling" and prof["top_objection"]:
            why = (f"'{prof['top_objection']}' is the most common objection on "
                   "your calls — this week is built around beating it.")
            lesson += (f" Your target this week: '{prof['top_objection']}'. "
                       f"Model rebuttal: {REBUTTALS.get(prof['top_objection'], ('', ''))[0]}")
        elif area == "closing" and prof["conversion"] < prof["team_conversion"]:
            why = (f"You convert {prof['conversion']}% vs the team's "
                   f"{prof['team_conversion']}% — tighter closes are the fastest fix.")
        fallback.append({
            "week": i + 1, "area": area, "theme": theme,
            "why": why, "lesson": lesson, "drills": drills,
        })

    prompt = f"""
Build a 4-week sales curriculum for rep {prof['rep']} based on this profile:
{ {k: v for k, v in prof.items()} }
Return JSON: {{"weeks": [{{"week": 1, "area": "...", "theme": "...", "why": "...",
"lesson": "...", "drills": ["...", "...", "..."]}} , ... 4 items]}}.
Each "why" must cite the profile. Keep lessons under 120 words.
"""
    result = generate_json(prompt, fallback={"weeks": fallback})
    weeks = result.get("weeks") or fallback
    return weeks if len(weeks) == 4 else fallback


# ---------------------------------------------------------------------------
# Roleplay engine
# ---------------------------------------------------------------------------

def _roleplay_turn(persona: str, script: list[str], history: list[dict],
                   user_msg: str, turn: int) -> dict:
    # The research engine reacts to the utterance — every note cites its source.
    score, notes, flags = research.score_response(user_msg)
    demo = {
        "score": score,
        "feedback": "  \n".join(notes),
        "flags": flags,
        "investor_reply": script[turn] if turn < len(script) else "",
        "done": turn >= len(script),
    }
    if not is_live():
        return demo
    transcript = "\n".join(f"{m['role']}: {m['text']}" for m in history)
    prompt = f"""
You are running a sales roleplay. You play {persona}.
The rep just said: "{user_msg}"

Conversation so far:
{transcript}

The deterministic research engine scored this response {score}/100 with these
notes:
{chr(10).join(notes)}

Return JSON: {{"score": 0-100 (stay within 15 points of the engine score unless
you see something it missed), "feedback": "2-3 sentences of coaching that keep
the engine's research citations", "investor_reply": "your next in-character
line (empty string if the conversation has reached a natural close)",
"done": true/false}}. Stay in character and escalate realistically. React the
way the research library in your instructions says to.
"""
    result = generate_json(prompt, fallback=demo)
    result.setdefault("flags", flags)
    return result


def _render_roleplay(prof: dict) -> None:
    st.caption(
        "Respond like you're on a live call — every reply gets scored and "
        "coached against the research library."
    )
    mode = st.radio(
        "Practice mode",
        ["🎭 Objection drills", "🎧 The Logan calls (recorded series)"],
        horizontal=True, label_visibility="collapsed",
    )

    if mode.startswith("🎭"):
        default = prof["top_objection"] if prof["top_objection"] in INVESTOR_SCRIPTS else None
        options = list(INVESTOR_SCRIPTS)
        scenario = st.selectbox(
            "Objection to practice",
            options,
            index=options.index(default) if default else 0,
            help="Defaults to the objection your calls hit most often.",
        )
        script = INVESTOR_SCRIPTS[scenario]
        persona = f'a skeptical investor whose objection is: "{scenario}"'
    else:
        picked = st.selectbox("Which call in the series?",
                              [c["title"] for c in MOCK_CALLS], key="logan_call_pick")
        call = next(c for c in MOCK_CALLS if c["title"] == picked)
        st.caption(f"**{call['stage']}** — listen to how Ryan ran it, then run "
                   "it yourself. The AI plays Logan.")
        st.audio(str(audio_path(call)))
        with st.expander("🎧 What to listen for in the recording"):
            for point in call["listen_for"]:
                st.markdown(f"- {point}")
        script = call["advisor_script"]
        scenario = call["title"]
        persona = call["persona"]

    key = f"rp_{prof['rep']}_{scenario}"
    if key not in st.session_state:
        st.session_state[key] = {
            "messages": [{"role": "investor", "text": script[0]}],
            "scores": [],
            "done": False,
        }
    state = st.session_state[key]

    for m in state["messages"]:
        avatar = {"investor": "🧑‍💼", "rep": "🎧", "coach": "🧑‍🏫"}[m["role"]]
        with st.chat_message("assistant" if m["role"] != "rep" else "user", avatar=avatar):
            if m["role"] == "coach":
                st.markdown(f"**Coach ({m['score']}/100):** {m['text']}")
            else:
                st.markdown(m["text"])

    if state["done"]:
        avg = round(sum(state["scores"]) / len(state["scores"])) if state["scores"] else 0
        st.success(f"Roleplay complete — average response score **{avg}/100**."
                   + (" Strong session. 🏅" if avg >= 80 else
                      " Run it again and push for 80+."))
        if st.button("🔁 Restart roleplay"):
            del st.session_state[key]
            st.rerun()
        return

    user_msg = st.chat_input("Your response to the investor…")
    if user_msg:
        turn = sum(1 for m in state["messages"] if m["role"] == "rep") + 1
        state["messages"].append({"role": "rep", "text": user_msg})
        result = _roleplay_turn(persona, script, state["messages"], user_msg, turn)
        state["scores"].append(int(result.get("score", 50)))
        feedback = result.get("feedback", "")
        for flag in result.get("flags") or []:
            feedback += f"  \n🚫 {flag}"
        state["messages"].append(
            {"role": "coach", "text": feedback,
             "score": int(result.get("score", 50))}
        )
        if result.get("investor_reply"):
            state["messages"].append({"role": "investor", "text": result["investor_reply"]})
        if result.get("done") or turn >= len(script):
            state["done"] = True
        st.rerun()


# ---------------------------------------------------------------------------
# Quiz
# ---------------------------------------------------------------------------

def _pick_questions(prof: dict, n: int = 5) -> list[dict]:
    """Deterministic pick, weak areas first, stable order per rep."""
    ranked = sorted(
        QUESTION_BANK,
        key=lambda q: (q["topic"] not in prof["weak_areas"],
                       prof["weak_areas"].index(q["topic"])
                       if q["topic"] in prof["weak_areas"] else 99),
    )
    return ranked[:n]


def _render_quiz(prof: dict) -> None:
    st.caption("Five questions, weighted toward the areas your call data flags.")
    questions = _pick_questions(prof)
    with st.form(key=f"quiz_{prof['rep']}"):
        answers = []
        for i, q in enumerate(questions):
            st.markdown(f"**{i + 1}. {q['q']}**  \n*({q['topic']})*")
            answers.append(st.radio(
                q["q"], q["options"], index=None,
                key=f"quiz_{prof['rep']}_{i}", label_visibility="collapsed",
            ))
            st.divider()
        submitted = st.form_submit_button("Grade my quiz")

    if submitted:
        if any(a is None for a in answers):
            st.warning("Answer every question before grading.")
            return
        correct = 0
        for q, a in zip(questions, answers):
            if q["options"].index(a) == q["answer"]:
                correct += 1
        pct = round(100 * correct / len(questions))
        st.progress(pct / 100, text=f"Score: {correct}/{len(questions)} ({pct}%)")
        if pct == 100:
            st.success("Perfect score. 🏆")
        elif pct >= 60:
            st.info("Solid — review the misses below and rerun the quiz.")
        else:
            st.warning("Worth a rerun after this week's lesson.")
        for q, a in zip(questions, answers):
            got_it = q["options"].index(a) == q["answer"]
            with st.container(border=True):
                st.markdown(("✅" if got_it else "❌") + f" **{q['q']}**")
                if not got_it:
                    st.markdown(f"Your answer: *{a}*  \nCorrect: *{q['options'][q['answer']]}*")
                st.caption(q["why"])


# ---------------------------------------------------------------------------
# The AI's brain — the research library it trains on, and the scoring lab
# ---------------------------------------------------------------------------

def _render_brain() -> None:
    st.markdown(
        "The coaching AI doesn't improvise — it **trains itself on a tiered "
        "research library** (peer-reviewed studies, regulatory text, and "
        "industry data) and reacts to calls the way the evidence says to. "
        "The same engine runs everywhere: the roleplay coach, the call scorer, "
        "and every live-AI prompt carries this library as grounding."
    )

    c1, c2, c3 = st.columns(3)
    active = sum(1 for c in research.CATEGORIES if c["status"] == "active")
    partial = sum(1 for c in research.CATEGORIES if c["status"] == "partial")
    c1.metric("Scoring categories", len(research.CATEGORIES))
    c2.metric("Active on today's data", f"{active} + {partial} proxy")
    c3.metric("Research sources", len(research.SOURCES))

    st.markdown("#### The 20-category scoring architecture")
    st.caption(
        "Weights follow evidence strength, not importance: High = 1.0 "
        "(peer-reviewed/regulatory), Medium = 0.7 (credible industry data), "
        "Low = 0.3 (thin evidence — coaching visibility only). Compliance is a "
        "**gate, not a score**: a hard flag forces human review no matter how "
        "well the call scored. Categories marked ⚪ activate as the Call "
        "Analyzer starts writing transcripts and audio features."
    )
    st.dataframe(pd.DataFrame(research.category_table()), width="stretch",
                 hide_index=True)

    st.markdown("#### Source library")
    st.caption("Tier 1 = peer-reviewed, regulatory, or primary research. "
               "Tier 2 = credible industry research, disclosed as such.")
    for sid, (citation, tier) in research.SOURCES.items():
        st.markdown(f"- **T{tier}** · {citation}")


def _render_scoring_lab(rep: str, team_df: pd.DataFrame) -> None:
    st.caption(
        "Pick one of your calls and watch the AI react to it: every category "
        "score cites the research behind it, the composite is confidence-"
        "weighted, and compliance violations override everything."
    )
    d = team_df[team_df["rep_name"] == rep].head(15)
    if d.empty:
        st.info("No calls for this rep yet.")
        return
    options = {
        f"{r.call_time:%b %d, %H:%M} — {r.customer_name} · {r.product_interest} · {r.outcome}": r.Index
        for r in d.itertuples()
    }
    label = st.selectbox("Call to score", list(options))
    row = d.loc[options[label]].to_dict()

    result = research.score_call(row)

    left, right = st.columns([1, 2])
    with left:
        if result["review_required"]:
            st.metric("Composite score", "⚠️ held")
        else:
            st.metric("Composite score", f"{result['composite']}/5"
                      if result["composite"] is not None else "—")
        st.caption("Σ(score × confidence weight) / Σ(weights)")
    with right:
        if result["flags"]:
            for f in result["flags"]:
                st.error(f"🚫 {f}")
            st.caption(
                "Compliance is a gate: flags route the call to human review and "
                "suppress the composite, per FINRA's fair-and-balanced standard."
            )
        else:
            st.success("No compliance flags — fair-and-balanced screens passed "
                       "(FINRA 2210 language checks).")

    st.markdown(f"*Key line from this call:* “{row.get('transcript_snippet', '')}”")

    for cat in result["categories"]:
        with st.container(border=True):
            head, bar = st.columns([2, 3])
            with head:
                st.markdown(f"**{cat['name']}**  ·  {cat['score']}/5")
                st.caption(f"{cat['confidence'].capitalize()} confidence "
                           f"(weight {cat['weight']})")
            with bar:
                st.progress(cat["score"] / 5)
                st.caption(cat["note"])
                st.caption(f"📎 {cat['source']}")


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

def render_sales_school() -> None:
    st.title("🎓 Sales School")

    reps = rep_names()
    if not reps:
        st.info("No calls in the database yet. Analyze a call or reload to seed demo data.")
        return

    left, right = st.columns([3, 1])
    with right:
        rep = st.selectbox("Training for", reps, label_visibility="collapsed")
    team_df = calls_df(days=90)
    prof = _rep_profile(rep, team_df)
    with left:
        st.caption(
            f"Personalized for **{rep}** from {prof['calls']} calls — "
            + ("**live AI** mode" if is_live() else "**demo** mode (set OPENAI_API_KEY for live AI)")
        )

    tip = DAILY_TIPS[date.today().toordinal() % len(DAILY_TIPS)]
    st.info(f"💡 **Today's tip:** {tip}")

    tab_brain, tab_lab, tab_rp, tab_cur, tab_quiz, tab_pb = st.tabs(
        ["🧠 How the AI coaches", "🩺 Score a call", "🎭 Objection roleplay",
         "📚 My curriculum", "📝 Quiz", "📖 Playbook"]
    )

    with tab_brain:
        _render_brain()

    with tab_lab:
        _render_scoring_lab(rep, team_df)

    with tab_cur:
        weeks = _curriculum(prof)
        this_week = date.today().isocalendar().week % 4
        for i, w in enumerate(weeks):
            current = i == this_week
            label = f"Week {w['week']}: {w['theme']}" + ("  ·  ⭐ this week" if current else "")
            with st.expander(label, expanded=current):
                st.caption(w["why"])
                st.markdown(w["lesson"])
                st.markdown("**Drills:**")
                for d in w["drills"]:
                    st.checkbox(d, key=f"drill_{rep}_{w['week']}_{d[:24]}")
                case = call_for_area(w.get("area", ""))
                if case:
                    st.markdown(f"**🎧 Case study: {case['title']}** — "
                                f"{case['stage']} (Ryan & Logan mock-call series)")
                    st.audio(str(audio_path(case)))
                    st.caption("Listen for:")
                    for point in case["listen_for"]:
                        st.markdown(f"- {point}")
                    st.caption("Then run the same call yourself in the "
                               "roleplay tab — the AI plays Logan.")

    with tab_rp:
        _render_roleplay(prof)

    with tab_quiz:
        _render_quiz(prof)

    with tab_pb:
        st.caption("The playbook every USEDC call runs on — each entry tied to "
                   "its research anchor.")
        st.markdown("#### 🧩 Advisor pain-point playbooks")
        st.caption("Where the research says conversations create real planning "
                   "value — with the honest caveats the evidence requires.")
        for pp in research.PAIN_POINTS:
            with st.expander(pp["name"]):
                st.markdown(pp["why"])
                st.markdown("**Discovery questions:**")
                for q in pp["questions"]:
                    st.markdown(f"- {q}")
                st.warning(pp["caution"])
                st.caption(f"📎 {research.cite(pp['anchor'])}")
        st.markdown("#### 🔍 Discovery questions")
        for q in DISCOVERY_QUESTIONS:
            st.markdown(f"- {q}")
        st.markdown("#### 🛡️ Objection rebuttals")
        for objection, (rebuttal, why) in REBUTTALS.items():
            with st.expander(objection):
                st.markdown(f"*“{rebuttal}”*")
                st.caption(why)
        st.markdown("#### 🤝 Closing techniques")
        for name, how in CLOSING_TECHNIQUES:
            st.markdown(f"**{name}** — {how}")
        st.markdown("#### 🎤 Talks worth 18 minutes")
        for talk in TED_TALKS:
            with st.container(border=True):
                st.markdown(f"**{talk['title']}**  ·  {talk['length']}")
                st.markdown(talk["summary"])
                st.caption(f"**Apply it:** {talk['apply']}")
