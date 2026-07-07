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
    )
    # Style the title only if one exists — a font-only title renders as
    # a literal "undefined" in plotly.js.
    if fig.layout.title.text:
        fig.update_layout(title_font=dict(color=INK, size=15))
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


def conversion_heatmap(z: list[list], x_labels: list[str], y_labels: list[str],
                       counts: list[list], title: str) -> go.Figure:
    """Day×hour conversion-rate heatmap. Sequential single hue (magnitude);
    cells with too little data arrive as None and render as gaps."""
    fig = go.Figure(go.Heatmap(
        z=z,
        x=x_labels,
        y=y_labels,
        customdata=counts,
        colorscale=[[i / (len(BLUE_RAMP) - 1), c] for i, c in enumerate(BLUE_RAMP)],
        zmin=0,
        hoverongaps=False,
        xgap=2,
        ygap=2,
        colorbar=dict(title="Conv %", ticksuffix="%", outlinewidth=0,
                      tickfont=dict(color=MUTED)),
        hovertemplate="%{y} %{x} — %{z:.0f}% conversion (%{customdata} calls)<extra></extra>",
    ))
    fig.update_layout(title=title)
    fig.update_yaxes(autorange="reversed")  # Monday on top
    fig.update_xaxes(side="bottom")
    return apply_theme(fig, height=340)


def multi_line(df, x_col: str, series_cols: list[str], title: str,
               y_title: str = "") -> go.Figure:
    """Weekly trend lines for up to 8 series. Colors are assigned by the
    caller's column order (fixed, never cycled into new hues)."""
    fig = go.Figure()
    for i, col in enumerate(series_cols[: len(SERIES)]):
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[col],
            name=col,
            mode="lines",
            line=dict(color=SERIES[i], width=2),
            hovertemplate="Week of %{x|%b %d}<br>" + col + ": %{y}<extra></extra>",
        ))
    fig.update_layout(
        title=title,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color=INK_2)),
    )
    fig.update_yaxes(title=y_title or None, rangemode="tozero")
    return apply_theme(fig, height=340)


def duration_histogram(durations, title: str) -> go.Figure:
    fig = go.Figure(go.Histogram(
        x=durations,
        xbins=dict(size=5),
        marker=dict(color=BLUE, line=dict(color=SURFACE, width=2)),
        hovertemplate="%{x} min: %{y} calls<extra></extra>",
    ))
    fig.update_layout(title=title, bargap=0.02, showlegend=False)
    fig.update_xaxes(title="Duration (min)")
    fig.update_yaxes(title=None)
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
