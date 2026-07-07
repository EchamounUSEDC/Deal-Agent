"""
pages/team_trends.py — 📊 Team Trends

Team-wide patterns computed straight from the calls table: headline
findings in plain sentences, a day×hour conversion heatmap, product and
objection trend lines, per-rep and per-territory breakdowns, duration
distribution, and a leaderboard. No AI needed — every finding here is
arithmetic, so the tab is identical in demo and live mode.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils import charts
from utils.database import calls_df

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
             "Saturday", "Sunday"]
MIN_CELL = 8    # calls needed before a heatmap cell / finding is trusted


def _conv(s: pd.Series) -> float:
    return round(100 * (s == "converted").mean(), 1) if len(s) else 0.0


# ---------------------------------------------------------------------------
# Headline findings — plain sentences, each one computed
# ---------------------------------------------------------------------------

def _headlines(df: pd.DataFrame) -> list[str]:
    team_rate = _conv(df["outcome"])
    finds: list[str] = []

    # Best converting window: day × morning/afternoon
    windows = df.groupby(
        [df["call_time"].dt.weekday, df["call_time"].dt.hour >= 13]
    )["outcome"]
    best_rate, best_label = 0.0, None
    for (day, is_pm), s in windows:
        if len(s) >= MIN_CELL * 3 and _conv(s) > best_rate:
            best_rate = _conv(s)
            best_label = f"{DAY_NAMES[day]} {'afternoons' if is_pm else 'mornings'}"
    if best_label:
        finds.append(
            f"**{best_label} convert best** — {best_rate}% vs the "
            f"{team_rate}% team average."
        )

    # Best territory
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
                f"{abs(pts):.1f} pts** in the second half of the period."
            )

    # Duration sweet spot
    bins = pd.cut(df["duration_min"], [0, 10, 20, 30, 999],
                  labels=["under 10", "10–20", "20–30", "over 30"])
    by_bin = df.groupby(bins, observed=True)["outcome"].agg(
        rate=_conv, n="size")
    by_bin = by_bin[by_bin["n"] >= MIN_CELL * 3]
    if not by_bin.empty:
        top = by_bin["rate"].idxmax()
        tail = {
            "under 10": "quick qualification is beating long pitches right now",
            "10–20": "tight, focused calls are winning",
            "20–30": "long enough for discovery, short enough to stay sharp",
            "over 30": "thorough discovery is paying off — don't rush investors off the phone",
        }[str(top)]
        finds.append(
            f"**Calls of {top} minutes convert best** ({by_bin.loc[top, 'rate']}%) — {tail}."
        )

    # Top rep
    by_rep = df.groupby("rep_name")["outcome"].agg(rate=_conv, n="size")
    by_rep = by_rep[by_rep["n"] >= MIN_CELL * 2]
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

def _heatmap_data(df: pd.DataFrame):
    d = df.assign(day=df["call_time"].dt.weekday, hour=df["call_time"].dt.hour)
    days = sorted(d["day"].unique())
    hours = sorted(d["hour"].unique())
    grouped = d.groupby(["day", "hour"])["outcome"].agg(rate=_conv, n="size")
    z, counts = [], []
    for day in days:
        z_row, n_row = [], []
        for hour in hours:
            if (day, hour) in grouped.index and grouped.loc[(day, hour), "n"] >= MIN_CELL:
                z_row.append(float(grouped.loc[(day, hour), "rate"]))
                n_row.append(int(grouped.loc[(day, hour), "n"]))
            else:
                z_row.append(None)
                n_row.append(0)
        z.append(z_row)
        counts.append(n_row)
    x_labels = [f"{h % 12 or 12}{'am' if h < 12 else 'pm'}" for h in hours]
    y_labels = [DAY_NAMES[d_] for d_ in days]
    return z, x_labels, y_labels, counts


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
    st.title("📊 Team Trends")
    st.caption("Team-wide patterns computed from every call — no AI, just arithmetic.")

    _, right = st.columns([4, 1])
    with right:
        days = st.selectbox("Period", [30, 60, 90], index=2,
                            format_func=lambda d: f"Last {d} days",
                            label_visibility="collapsed")

    df = calls_df(days=days)
    if df.empty:
        st.info("No calls in the database yet. Analyze a call or reload to seed demo data.")
        return

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total calls", len(df))
    m2.metric("Team conversion", f"{_conv(df['outcome'])}%")
    m3.metric("Avg call score", round(df["score"].mean(), 1))
    m4.metric("Active reps", df["rep_name"].nunique())

    finds = _headlines(df)
    if finds:
        st.subheader("📣 This period's findings")
        cols = st.columns(2)
        for i, f in enumerate(finds):
            with cols[i % 2], st.container(border=True):
                st.markdown(f)

    z, x_labels, y_labels, counts = _heatmap_data(df)
    st.plotly_chart(
        charts.conversion_heatmap(z, x_labels, y_labels, counts,
                                  "Conversion rate by day and hour"),
        width="stretch",
    )
    st.caption(f"Cells with fewer than {MIN_CELL} calls are left blank.")

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
        charts.duration_histogram(df["duration_min"], "Call duration distribution"),
        width="stretch",
    )

    st.subheader("🏆 Leaderboard")
    board = (
        df.groupby("rep_name")
        .agg(
            calls=("id", "size"),
            conversions=("outcome", lambda s: int((s == "converted").sum())),
            conversion=("outcome", _conv),
            avg_score=("score", lambda s: round(s.mean(), 1)),
            avg_duration=("duration_min", lambda s: round(s.mean(), 1)),
        )
        .sort_values("conversion", ascending=False)
        .reset_index()
    )
    board.insert(0, "rank", [f"{i + 1}" for i in range(len(board))])
    st.dataframe(
        board,
        width="stretch",
        hide_index=True,
        column_config={
            "rank": st.column_config.TextColumn("#", width="small"),
            "rep_name": "Rep",
            "calls": "Calls",
            "conversions": "Won",
            "conversion": st.column_config.ProgressColumn(
                "Conversion", format="%.1f%%", min_value=0,
                max_value=float(board["conversion"].max() or 1),
            ),
            "avg_score": "Avg score",
            "avg_duration": "Avg min",
        },
    )
