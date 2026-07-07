"""
pages/sales_coach.py — 🎯 Sales Coach

Per-rep AI coaching report grounded in real call stats. Everything the
AI says is anchored to numbers computed here from the calls table; in
demo mode a deterministic report is built from the same numbers, so the
tab is fully functional offline.
"""

from __future__ import annotations

from collections import Counter

import pandas as pd
import streamlit as st

from utils import charts
from utils.ai import generate_json, is_live
from utils.database import calls_df, coach_notes, rep_names, save_coach_note

# ---------------------------------------------------------------------------
# Coaching content library (used by the demo fallback; the live model is
# free to improve on it but is prompted with the same grounding stats).
# ---------------------------------------------------------------------------

REBUTTALS = {
    "Fees feel high": (
        "Fair question — let's look at net returns instead of fees in isolation. "
        "After fees, the fund's distribution history is X%. Would it help to see "
        "that side by side with what you're earning now?",
        "Reframes cost as net outcome and moves to evidence instead of apologizing.",
    ),
    "Market volatility": (
        "That's exactly why clients like this structure — distributions come from "
        "production, not from timing the market. What part of the volatility "
        "worries you most: income or principal?",
        "Turns the objection into a discovery question and positions the product as the answer.",
    ),
    "Liquidity concerns": (
        "Let's size this so liquidity never becomes a problem — what portion of "
        "your portfolio do you truly not need to touch for 5 years?",
        "Solves the concern with allocation sizing instead of dismissing it.",
    ),
    "Needs spouse/advisor sign-off": (
        "Great — they should be part of this. Can we get 15 minutes on the "
        "calendar this week with them on the line, so I can answer their "
        "questions directly?",
        "Keeps control of the next step instead of waiting for a callback that rarely comes.",
    ),
    "Timing — next quarter": (
        "Totally understand. So the timing works for you, what would need to be "
        "in place by then? Let's set the follow-up now — how's the first Tuesday "
        "of the quarter?",
        "Books a concrete next step and surfaces the real blocker behind 'timing'.",
    ),
    "Already invested elsewhere": (
        "That tells me you already believe in the asset class — how has that "
        "investment performed, and what would you want the next one to do "
        "differently?",
        "Treats existing investments as qualification, not disqualification.",
    ),
    "Risk tolerance": (
        "Let's put numbers on it — of the amount we discussed, what's the most "
        "you'd be comfortable seeing fluctuate in a bad year?",
        "Quantifies risk instead of leaving it as a vague feeling.",
    ),
}

DISCOVERY_QUESTIONS = [
    "What prompted you to take this call today?",
    "How are you generating income from your portfolio right now?",
    "What's your experience with energy or alternative investments so far?",
    "Twelve months from now, what would make this a great decision in hindsight?",
    "Who else weighs in on investment decisions of this size?",
    "What would need to be true for this to be an easy yes?",
]

CLOSING_TECHNIQUES = [
    ("Calendar close", "Never end on 'call me back' — end on a booked date: "
     "'I have Tuesday 2pm or Thursday 10am, which works?'"),
    ("Summary close", "Replay their own words: 'You said you want monthly income "
     "and a tax offset — this checks both. What's holding us back?'"),
    ("Advisor-inclusion close", "When a spouse or advisor is the gatekeeper, sell "
     "the three-way call, not the product."),
    ("Takeaway close", "For stalled follow-ups: 'This tranche closes on the 30th. "
     "If the timing's wrong I'd rather you skip it — should we?'"),
]


# ---------------------------------------------------------------------------
# Stats — the grounding layer
# ---------------------------------------------------------------------------

def _pct(numer: int, denom: int) -> float:
    return round(100 * numer / denom, 1) if denom else 0.0


def _compute_stats(rep_df: pd.DataFrame, team_df: pd.DataFrame) -> dict:
    conv = int((rep_df["outcome"] == "converted").sum())
    stats = {
        "rep": rep_df["rep_name"].iloc[0],
        "territory": rep_df["territory"].iloc[0],
        "total_calls": len(rep_df),
        "conversions": conv,
        "conversion_rate": _pct(conv, len(rep_df)),
        "team_conversion_rate": _pct(
            int((team_df["outcome"] == "converted").sum()), len(team_df)
        ),
        "avg_score": round(rep_df["score"].mean(), 1),
        "team_avg_score": round(team_df["score"].mean(), 1),
        "avg_duration": round(rep_df["duration_min"].mean(), 1),
        "team_avg_duration": round(team_df["duration_min"].mean(), 1),
        "follow_up_share": _pct(int((rep_df["outcome"] == "follow_up").sum()), len(rep_df)),
    }

    obj_counts = Counter(o for objs in rep_df["objections"] for o in objs)
    stats["top_objections"] = obj_counts.most_common(4)

    by_product = rep_df.groupby("product_interest")["outcome"].agg(
        lambda s: _pct(int((s == "converted").sum()), len(s))
    )
    if not by_product.empty:
        stats["best_product"] = (by_product.idxmax(), float(by_product.max()))
        stats["worst_product"] = (by_product.idxmin(), float(by_product.min()))

    weekly = (
        rep_df.set_index("call_time")["score"]
        .resample("W-MON").mean().dropna().reset_index()
        .rename(columns={"call_time": "week", "score": "value"})
    )
    stats["weekly_scores"] = weekly

    # Real lines from the rep's weakest calls — grounding for the rewrites.
    weak = rep_df[(rep_df["score"] < 62) & (rep_df["objections"].str.len() > 0)]
    weak = weak.nsmallest(3, "score")
    stats["weak_calls"] = [
        {"said": r.transcript_snippet, "objection": r.objections[0],
         "score": int(r.score), "customer": r.customer_name}
        for r in weak.itertuples()
    ]

    stalled = rep_df[rep_df["outcome"] == "follow_up"]
    stats["stalled_no_next_step"] = int(
        stalled["objections"].apply(
            lambda o: "Needs spouse/advisor sign-off" in o or "Timing — next quarter" in o
        ).sum()
    )
    stats["short_calls"] = int((rep_df["duration_min"] < 8).sum())
    return stats


# ---------------------------------------------------------------------------
# Coaching report — demo fallback + live prompt, same shape
# ---------------------------------------------------------------------------

def _demo_report(s: dict) -> dict:
    strengths, weaknesses = [], []

    if s["conversion_rate"] >= s["team_conversion_rate"]:
        strengths.append(
            f"Converts above the team — {s['conversion_rate']}% vs the team's "
            f"{s['team_conversion_rate']}% across {s['total_calls']} calls."
        )
    else:
        weaknesses.append(
            f"Conversion sits at {s['conversion_rate']}% vs the team's "
            f"{s['team_conversion_rate']}% — the gap is the coaching priority."
        )

    if s["avg_score"] >= s["team_avg_score"]:
        strengths.append(
            f"Call quality is a weapon: {s['avg_score']} average score vs "
            f"{s['team_avg_score']} team average."
        )
    else:
        weaknesses.append(
            f"Average call score of {s['avg_score']} trails the team's "
            f"{s['team_avg_score']} — focus on structure: agenda, discovery, next step."
        )

    if s.get("best_product"):
        name, rate = s["best_product"]
        strengths.append(f"Strongest on the {name} — {rate}% of those calls convert.")

    if s["top_objections"]:
        top, n = s["top_objections"][0]
        weaknesses.append(
            f"'{top}' comes up on {n} calls and is the most common stall — "
            "drill the rebuttal until it's automatic."
        )
    if s["avg_duration"] < s["team_avg_duration"] - 2:
        weaknesses.append(
            f"Calls average {s['avg_duration']} min vs {s['team_avg_duration']} for the "
            "team — short calls usually mean discovery is getting skipped."
        )

    missed = []
    if s["stalled_no_next_step"]:
        missed.append(
            f"{s['stalled_no_next_step']} follow-ups stalled on sign-off or timing with no "
            "concrete next step — every one should end with a calendared three-way call."
        )
    if s["short_calls"]:
        missed.append(
            f"{s['short_calls']} calls ran under 8 minutes — too short to complete "
            "discovery; these prospects were qualified out prematurely."
        )
    if s.get("worst_product"):
        name, rate = s["worst_product"]
        missed.append(
            f"Only {rate}% of {name} conversations convert — either stop leading "
            "with it or get a product refresher this week."
        )

    rewrites = []
    for wc in s["weak_calls"]:
        better, why = REBUTTALS.get(wc["objection"], REBUTTALS["Timing — next quarter"])
        rewrites.append({
            "said": wc["said"],
            "context": f"{wc['objection']} (call scored {wc['score']})",
            "try_instead": better,
            "why": why,
        })

    goals = [
        f"Lift conversion from {s['conversion_rate']}% to "
        f"{round(s['conversion_rate'] + 3, 1)}% — one extra close a week.",
        "End every follow-up with a calendared date — zero 'call me back whenever' endings.",
    ]
    if s["top_objections"]:
        goals.append(
            f"Run the '{s['top_objections'][0][0]}' rebuttal in roleplay twice this "
            "week (Sales School tab) until it scores 80+."
        )
    goals.append("Ask at least 3 discovery questions before presenting any product.")

    return {
        "summary": (
            f"{s['rep']} logged {s['total_calls']} calls with a {s['conversion_rate']}% "
            f"conversion rate ({s['team_conversion_rate']}% team) and an average call "
            f"score of {s['avg_score']} ({s['team_avg_score']} team). The fastest path "
            "to improvement is below."
        ),
        "strengths": strengths[:3],
        "weaknesses": weaknesses[:3],
        "missed_opportunities": missed[:3],
        "rewrites": rewrites,
        "discovery_questions": DISCOVERY_QUESTIONS,
        "closing_techniques": [{"name": n, "how": h} for n, h in CLOSING_TECHNIQUES],
        "weekly_goals": goals[:4],
    }


def _coaching_report(s: dict) -> dict:
    fallback = _demo_report(s)
    grounding = {k: v for k, v in s.items() if k != "weekly_scores"}
    prompt = f"""
Write a coaching report for sales rep {s['rep']} using ONLY these call statistics:

{grounding}

Return JSON with exactly these keys:
- "summary": 2-3 sentence overview citing the numbers above
- "strengths": list of 3 short strings, each citing a stat
- "weaknesses": list of 3 short strings, each citing a stat
- "missed_opportunities": list of up to 3 short strings
- "rewrites": list of objects with "said" (quote from weak_calls above verbatim),
  "context", "try_instead" (a stronger line), "why"
- "discovery_questions": list of 6 strings tailored to this rep's weaknesses
- "closing_techniques": list of 4 objects with "name" and "how"
- "weekly_goals": list of 4 short, measurable goal strings
"""
    report = generate_json(prompt, fallback=fallback)
    # Never render a half-empty report if the model skips keys.
    return {**fallback, **{k: v for k, v in report.items() if v}}


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

def render_sales_coach() -> None:
    st.title("🎯 Sales Coach")
    st.caption(
        "Per-rep coaching grounded in real call data — "
        + ("**live AI** mode" if is_live() else "**demo** mode (set OPENAI_API_KEY for live AI)")
    )

    reps = rep_names()
    if not reps:
        st.info("No calls in the database yet. Analyze a call or reload to seed demo data.")
        return

    top_left, top_right = st.columns([3, 1])
    with top_left:
        rep = st.selectbox("Rep", reps, label_visibility="collapsed")
    with top_right:
        days = st.selectbox("Period", [30, 60, 90], index=2,
                            format_func=lambda d: f"Last {d} days",
                            label_visibility="collapsed")

    team_df = calls_df(days=days)
    rep_df = team_df[team_df["rep_name"] == rep]
    if rep_df.empty:
        st.warning(f"No calls for {rep} in the last {days} days.")
        return

    s = _compute_stats(rep_df, team_df)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Calls", s["total_calls"])
    m2.metric("Conversion", f"{s['conversion_rate']}%",
              delta=f"{round(s['conversion_rate'] - s['team_conversion_rate'], 1)}% vs team")
    m3.metric("Avg score", s["avg_score"],
              delta=f"{round(s['avg_score'] - s['team_avg_score'], 1)} vs team")
    m4.metric("Avg duration", f"{s['avg_duration']} min",
              delta=f"{round(s['avg_duration'] - s['team_avg_duration'], 1)} vs team")

    c1, c2 = st.columns([1, 2])
    with c1:
        st.plotly_chart(
            charts.score_gauge(s["avg_score"], team_avg=s["team_avg_score"]),
            width="stretch",
        )
        st.caption("Needle marks the team average.")
    with c2:
        if len(s["weekly_scores"]) >= 2:
            st.plotly_chart(charts.weekly_trend(s["weekly_scores"]), width="stretch")
        else:
            st.info("Not enough history yet for a weekly trend.")

    with st.spinner("Generating coaching report…" if is_live() else ""):
        report = _coaching_report(s)

    st.markdown(f"> {report['summary']}")

    col_s, col_w = st.columns(2)
    with col_s:
        st.subheader("💪 Strengths")
        for item in report["strengths"]:
            st.markdown(f"- {item}")
    with col_w:
        st.subheader("🎯 Work on")
        for item in report["weaknesses"]:
            st.markdown(f"- {item}")
        if s["top_objections"]:
            labels = [o for o, _ in s["top_objections"]]
            values = [n for _, n in s["top_objections"]]
            st.plotly_chart(
                charts.hbar(labels, values, "Most common objections", " calls"),
                width="stretch",
            )

    if report["missed_opportunities"]:
        st.subheader("🚪 Missed opportunities")
        for item in report["missed_opportunities"]:
            st.markdown(f"- {item}")

    if report["rewrites"]:
        st.subheader("🗣️ Said vs. try instead")
        st.caption("Real lines from this rep's lowest-scoring calls, rewritten.")
        for rw in report["rewrites"]:
            with st.container(border=True):
                st.markdown(f"**Context:** {rw['context']}")
                st.markdown(f"❌ *“{rw['said']}”*")
                st.markdown(f"✅ *“{rw['try_instead']}”*")
                st.caption(rw["why"])

    col_d, col_c = st.columns(2)
    with col_d:
        with st.expander("🔍 Discovery questions to use this week", expanded=False):
            for q in report["discovery_questions"]:
                st.markdown(f"- {q}")
    with col_c:
        with st.expander("🤝 Closing techniques", expanded=False):
            for t in report["closing_techniques"]:
                st.markdown(f"**{t['name']}** — {t['how']}")

    st.subheader("📅 Goals for this week")
    for i, goal in enumerate(report["weekly_goals"]):
        st.checkbox(goal, key=f"goal_{rep}_{i}")

    st.divider()
    st.subheader("📝 Manager notes")
    with st.form(key=f"note_form_{rep}", clear_on_submit=True):
        note = st.text_area("Add a note", placeholder=f"Coaching note for {rep}…",
                            label_visibility="collapsed")
        if st.form_submit_button("Save note") and note.strip():
            save_coach_note(rep, note)
            st.toast("Note saved.", icon="📝")
    for n in coach_notes(rep):
        with st.container(border=True):
            st.markdown(n["note"])
            st.caption(f"{n['author']} · {n['created_at']}")
