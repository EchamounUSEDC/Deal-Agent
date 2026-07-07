"""
pages/team_trends.py — 📊 Trends

Individual-first trends: pick a rep and every view — headline findings,
conversion heatmap, product/objection trend lines, breakdowns, duration
distribution — is computed from that one person's calls, phrased in
second person, with team comparisons where they add context. Selecting
"Whole team" runs the identical analytics across everyone and adds the
leaderboard. No AI needed — every finding here is arithmetic, so the
tab is identical in demo and live mode.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils import charts
from utils.database import calls_df, rep_names

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
             "Saturday", "Sunday"]
TEAM = "🌐 Whole team"

# One rep has ~an eighth of the team's calls, so individual mode uses
# coarser time buckets and smaller (but still guarded) sample minimums.
PARTS_OF_DAY = [(9, 12, "Morning"), (12, 15, "Midday"), (15, 18, "Afternoon")]


def _conv(s: pd.Series) -> float:
    return round(100 * (s == "converted").mean(), 1) if len(s) else 0.0


def _part_of_day(hour: int) -> str:
    for lo, hi, label in PARTS_OF_DAY:
        if lo <= hour < hi:
            return label
    return "Afternoon"


# ---------------------------------------------------------------------------
# Headline findings — plain sentences, each one computed
# ---------------------------------------------------------------------------

def _headlines(df: pd.DataFrame, team_df: pd.DataFrame, individual: bool) -> list[str]:
    """`df` is the focus (one rep, or everyone); `team_df` is always everyone."""
    you = "You" if individual else "The team"
    your = "your" if individual else "the team's"
    rate = _conv(df["outcome"])
    min_n = 8 if individual else 24
    finds: list[str] = []

    # Individual only: where do they stand vs the team?
    if individual:
        team_rate = _conv(team_df["outcome"])
        gap = round(rate - team_rate, 1)
        if abs(gap) >= 1:
            finds.append(
                f"**You convert {rate}% vs the {team_rate}% team average** — "
                + (f"{gap} pts ahead. Keep doing what's working."
                   if gap > 0 else f"{abs(gap)} pts of upside to close.")
            )

    # Best converting window: day × morning/afternoon
    windows = df.groupby(
        [df["call_time"].dt.weekday, df["call_time"].dt.hour >= 13]
    )["outcome"]
    best_rate, best_label = 0.0, None
    for (day, is_pm), s in windows:
        if len(s) >= min_n and _conv(s) > best_rate:
            best_rate = _conv(s)
            best_label = f"{DAY_NAMES[day]} {'afternoons' if is_pm else 'mornings'}"
    if best_label:
        finds.append(
            f"**{'Your' if individual else 'Team'} {best_label} convert best** — "
            f"{best_rate}% vs {your} {rate}% overall."
        )

    # Best product for the focus
    by_prod = df.groupby("product_interest")["outcome"].agg(rate=_conv, n="size")
    by_prod = by_prod[by_prod["n"] >= min_n]
    if not by_prod.empty:
        top_p = by_prod["rate"].idxmax()
        finds.append(
            f"**{your.capitalize()} strongest product is the {top_p}** — "
            f"{by_prod.loc[top_p, 'rate']}% of those calls convert."
        )

    # Team only: territory spread (meaningless for one rep's single territory)
    if not individual:
        by_terr = df.groupby("territory")["outcome"].agg(_conv).sort_values(ascending=False)
        if len(by_terr) >= 2:
            finds.append(
                f"**{by_terr.index[0]} leads on conversion** at {by_terr.iloc[0]}%; "
                f"{by_terr.index[-1]} trails at {by_terr.iloc[-1]}%."
            )

    # Fastest-moving objection: share in the 2nd half vs the 1st half
    mid = df["call_time"].min() + (df["call_time"].max() - df["call_time"].min()) / 2
    exploded = df.explode("objections").dropna(subset=["objections"])
    if not exploded.empty:
        early = exploded[exploded["call_time"] < mid]["objections"].value_counts(normalize=True)
        late = exploded[exploded["call_time"] >= mid]["objections"].value_counts(normalize=True)
        delta = (late.reindex(early.index.union(late.index), fill_value=0)
                 - early.reindex(early.index.union(late.index), fill_value=0)) * 100
        mover = delta.abs().idxmax()
        pts = delta[mover]
        if abs(pts) >= 1:
            finds.append(
                f"**'{mover}' objections are {'up' if pts > 0 else 'down'} "
                f"{abs(pts):.1f} pts** on {your} calls in the second half of the period."
            )

    # Duration sweet spot
    bins = pd.cut(df["duration_min"], [0, 10, 20, 30, 999],
                  labels=["under 10", "10–20", "20–30", "over 30"])
    by_bin = df.groupby(bins, observed=True)["outcome"].agg(rate=_conv, n="size")
    by_bin = by_bin[by_bin["n"] >= min_n]
    if not by_bin.empty:
        top = by_bin["rate"].idxmax()
        tail = {
            "under 10": "quick qualification is beating long pitches right now",
            "10–20": "tight, focused calls are winning",
            "20–30": "long enough for discovery, short enough to stay sharp",
            "over 30": "thorough discovery is paying off — don't rush investors off the phone",
        }[str(top)]
        finds.append(
            f"**{your.capitalize()} calls of {top} minutes convert best** "
            f"({by_bin.loc[top, 'rate']}%) — {tail}."
        )

    # Team only: who sets the pace
    if not individual:
        by_rep = df.groupby("rep_name")["outcome"].agg(rate=_conv, n="size")
        by_rep = by_rep[by_rep["n"] >= min_n]
        if not by_rep.empty:
            top_rep = by_rep["rate"].idxmax()
            finds.append(
                f"**{top_rep} sets the pace** — {by_rep.loc[top_rep, 'rate']}% conversion "
                f"across {int(by_rep.loc[top_rep, 'n'])} calls."
            )
    return finds


# ---------------------------------------------------------------------------
# Chart data
# ---------------------------------------------------------------------------

def _heatmap_data(df: pd.DataFrame, individual: bool):
    """Team: day × hour. Individual: day × part-of-day, so each cell keeps
    a workable sample size for one person's call volume."""
    min_cell = 4 if individual else 8
    d = df.assign(day=df["call_time"].dt.weekday)
    if individual:
        d = d.assign(slot=d["call_time"].dt.hour.map(_part_of_day))
        slots = [label for _, _, label in PARTS_OF_DAY]
    else:
        d = d.assign(slot=d["call_time"].dt.hour)
        slots = sorted(d["slot"].unique())
    days = sorted(d["day"].unique())
    grouped = d.groupby(["day", "slot"])["outcome"].agg(rate=_conv, n="size")
    z, counts = [], []
    for day in days:
        z_row, n_row = [], []
        for slot in slots:
            if (day, slot) in grouped.index and grouped.loc[(day, slot), "n"] >= min_cell:
                z_row.append(float(grouped.loc[(day, slot), "rate"]))
                n_row.append(int(grouped.loc[(day, slot), "n"]))
            else:
                z_row.append(None)
                n_row.append(0)
        z.append(z_row)
        counts.append(n_row)
    if individual:
        x_labels = slots
    else:
        x_labels = [f"{h % 12 or 12}{'am' if h < 12 else 'pm'}" for h in slots]
    y_labels = [DAY_NAMES[d_] for d_ in days]
    return z, x_labels, y_labels, counts, min_cell


def _weekly_counts(df: pd.DataFrame, col: str, top_n: int) -> tuple[pd.DataFrame, list[str]]:
    """Weekly call counts per category, keeping the top_n categories by volume."""
    top = df[col].value_counts().head(top_n).index.tolist()
    d = df[df[col].isin(top)]
    weekly = (
        d.groupby([pd.Grouper(key="call_time", freq="W-MON"), col])
        .size().unstack(fill_value=0).reset_index()
        .rename(columns={"call_time": "week"})
    )
    return weekly, top


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

def render_team_trends() -> None:
    reps = rep_names()
    left, mid, right = st.columns([3, 2, 1])
    with mid:
        focus = st.selectbox("Focus", reps + [TEAM] if reps else [TEAM],
                             label_visibility="collapsed")
    with right:
        days = st.selectbox("Period", [30, 60, 90], index=2,
                            format_func=lambda d: f"Last {d} days",
                            label_visibility="collapsed")
    individual = focus != TEAM
    with left:
        st.title(f"📊 {focus}'s Trends" if individual else "📊 Team Trends")

    st.caption(
        ("Your patterns, computed from your calls alone — no AI, just arithmetic."
         if individual else
         "Team-wide patterns computed from every call — no AI, just arithmetic.")
    )

    team_df = calls_df(days=days)
    if team_df.empty:
        st.info("No calls in the database yet. Analyze a call or reload to seed demo data.")
        return
    df = team_df[team_df["rep_name"] == focus] if individual else team_df
    if df.empty:
        st.warning(f"No calls for {focus} in the last {days} days.")
        return

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Calls", len(df))
    if individual:
        m2.metric("Conversion", f"{_conv(df['outcome'])}%",
                  delta=f"{round(_conv(df['outcome']) - _conv(team_df['outcome']), 1)}% vs team")
        m3.metric("Avg score", round(df["score"].mean(), 1),
                  delta=f"{round(df['score'].mean() - team_df['score'].mean(), 1)} vs team")
        best_day = df.groupby(df["call_time"].dt.weekday)["outcome"].agg(_conv).idxmax()
        m4.metric("Best day", DAY_NAMES[best_day])
    else:
        m2.metric("Team conversion", f"{_conv(df['outcome'])}%")
        m3.metric("Avg call score", round(df["score"].mean(), 1))
        m4.metric("Active reps", df["rep_name"].nunique())

    finds = _headlines(df, team_df, individual)
    if finds:
        st.subheader("📣 This period's findings")
        cols = st.columns(2)
        for i, f in enumerate(finds):
            with cols[i % 2], st.container(border=True):
                st.markdown(f)

    z, x_labels, y_labels, counts, min_cell = _heatmap_data(df, individual)
    st.plotly_chart(
        charts.conversion_heatmap(
            z, x_labels, y_labels, counts,
            ("Your conversion rate by day and time" if individual
             else "Conversion rate by day and hour"),
        ),
        width="stretch",
    )
    st.caption(f"Cells with fewer than {min_cell} calls are left blank.")

    t1, t2 = st.columns(2)
    with t1:
        weekly_p, prods = _weekly_counts(df, "product_interest", top_n=5)
        st.plotly_chart(
            charts.multi_line(weekly_p, "week", prods,
                              "Product interest by week", "Calls"),
            width="stretch",
        )
    with t2:
        exploded = df.explode("objections").dropna(subset=["objections"])
        if not exploded.empty:
            weekly_o, objs = _weekly_counts(exploded, "objections", top_n=5)
            st.plotly_chart(
                charts.multi_line(weekly_o, "week", objs,
                                  "Objections raised by week", "Mentions"),
                width="stretch",
            )

    b1, b2 = st.columns(2)
    if individual:
        with b1:
            by_prod_calls = df["product_interest"].value_counts()
            st.plotly_chart(
                charts.hbar(by_prod_calls.index.tolist(), by_prod_calls.tolist(),
                            "Your calls by product", " calls"),
                width="stretch",
            )
        with b2:
            by_prod = df.groupby("product_interest")["outcome"].agg(_conv)
            st.plotly_chart(
                charts.hbar(by_prod.index.tolist(), by_prod.tolist(),
                            "Your conversion by product", "%"),
                width="stretch",
            )
    else:
        with b1:
            by_rep_calls = df["rep_name"].value_counts()
            st.plotly_chart(
                charts.hbar(by_rep_calls.index.tolist(), by_rep_calls.tolist(),
                            "Calls per rep", " calls"),
                width="stretch",
            )
        with b2:
            by_terr = df.groupby("territory")["outcome"].agg(_conv)
            st.plotly_chart(
                charts.hbar(by_terr.index.tolist(), by_terr.tolist(),
                            "Conversion by territory", "%"),
                width="stretch",
            )

    st.plotly_chart(
        charts.duration_histogram(
            df["duration_min"],
            "Your call duration distribution" if individual else "Call duration distribution",
        ),
        width="stretch",
    )

    if individual:
        st.subheader("📦 Your product performance")
        board = (
            df.groupby("product_interest")
            .agg(
                calls=("id", "size"),
                won=("outcome", lambda s: int((s == "converted").sum())),
                conversion=("outcome", _conv),
                avg_score=("score", lambda s: round(s.mean(), 1)),
                avg_duration=("duration_min", lambda s: round(s.mean(), 1)),
            )
            .sort_values("conversion", ascending=False)
            .reset_index()
            .rename(columns={"product_interest": "product"})
        )
        first_col = ("product", "Product")
    else:
        st.subheader("🏆 Leaderboard")
        board = (
            df.groupby("rep_name")
            .agg(
                calls=("id", "size"),
                won=("outcome", lambda s: int((s == "converted").sum())),
                conversion=("outcome", _conv),
                avg_score=("score", lambda s: round(s.mean(), 1)),
                avg_duration=("duration_min", lambda s: round(s.mean(), 1)),
            )
            .sort_values("conversion", ascending=False)
            .reset_index()
            .rename(columns={"rep_name": "rep"})
        )
        first_col = ("rep", "Rep")
    board.insert(0, "rank", [f"{i + 1}" for i in range(len(board))])
    st.dataframe(
        board,
        width="stretch",
        hide_index=True,
        column_config={
            "rank": st.column_config.TextColumn("#", width="small"),
            first_col[0]: first_col[1],
            "calls": "Calls",
            "won": "Won",
            "conversion": st.column_config.ProgressColumn(
                "Conversion", format="%.1f%%", min_value=0,
                max_value=float(board["conversion"].max() or 1),
            ),
            "avg_score": "Avg score",
            "avg_duration": "Avg min",
        },
    )
