"""
utils/charts.py — shared Plotly theme + chart builders.

One place for color and chrome so every tab's charts read as one system.
Categorical hues are assigned in the fixed SERIES order (never cycled into
new hues); sequential encodings use the single-hue BLUE_RAMP; chrome (grid,
axes, labels) stays recessive so the data carries the chart.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

# Fixed categorical order — assign by slot, never generate extra hues.
SERIES = ["#2a78d6", "#1baf7a", "#eda100", "#008300",
          "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"]
BLUE = SERIES[0]

# Single-hue sequential ramp (light -> dark) for magnitude encodings.
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
             "#256abf", "#1c5cab", "#104281", "#0d366b"]

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'


def apply_theme(fig: go.Figure, height: int = 320) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family=FONT, color=INK_2, size=13),
        margin=dict(l=8, r=8, t=36, b=8),
        hoverlabel=dict(bgcolor="#ffffff", font=dict(family=FONT, color=INK)),
        title=dict(font=dict(color=INK, size=15)),
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=AXIS, tickfont=dict(color=MUTED), zeroline=False)
    fig.update_yaxes(gridcolor=GRID, linecolor=AXIS, tickfont=dict(color=MUTED), zeroline=False)
    return fig


def score_gauge(score: float, team_avg: float | None = None, title: str = "Coaching score") -> go.Figure:
    """0-100 gauge; the threshold needle marks the team average for context."""
    gauge: dict = {
        "axis": {"range": [0, 100], "tickcolor": AXIS, "tickfont": {"color": MUTED}},
        "bar": {"color": BLUE, "thickness": 0.35},
        "bgcolor": SURFACE,
        "borderwidth": 0,
        "steps": [
            {"range": [0, 40], "color": "#f0efec"},
            {"range": [40, 70], "color": "#f7f6f3"},
            {"range": [70, 100], "color": "#fcfcfb"},
        ],
    }
    if team_avg is not None:
        gauge["threshold"] = {
            "line": {"color": INK_2, "width": 2},
            "thickness": 0.8,
            "value": team_avg,
        }
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(score, 1),
        number={"font": {"color": INK, "family": FONT}},
        title={"text": title, "font": {"color": INK_2, "size": 14}},
        gauge=gauge,
    ))
    return apply_theme(fig, height=260)


def weekly_trend(weekly: pd.DataFrame, y_title: str = "Avg score") -> go.Figure:
    """Line of a weekly aggregate. Expects columns: week (datetime), value."""
    fig = go.Figure(go.Scatter(
        x=weekly["week"],
        y=weekly["value"],
        mode="lines+markers",
        line=dict(color=BLUE, width=2),
        marker=dict(size=8, color=BLUE, line=dict(color=SURFACE, width=2)),
        hovertemplate="Week of %{x|%b %d}<br>" + y_title + ": %{y:.1f}<extra></extra>",
    ))
    fig.update_layout(title=f"{y_title} by week", showlegend=False)
    fig.update_yaxes(title=None)
    fig.update_xaxes(title=None)
    return apply_theme(fig)


def hbar(labels: list[str], values: list[float], title: str,
         hover_suffix: str = "") -> go.Figure:
    """Sorted single-hue horizontal bar — magnitude by category."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    fig = go.Figure(go.Bar(
        x=[values[i] for i in order],
        y=[labels[i] for i in order],
        orientation="h",
        marker=dict(color=BLUE, cornerradius=4),
        width=0.55,
        hovertemplate="%{y}: %{x}" + hover_suffix + "<extra></extra>",
    ))
    fig.update_layout(title=title, showlegend=False, bargap=0.35)
    return apply_theme(fig, height=max(220, 40 * len(labels) + 90))
