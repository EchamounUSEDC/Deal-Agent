"""
app.py — USEDC Sales IQ
-----------------------
Application shell: branding, navigation, and routing only.
All business logic lives in pages/ and utils/ per the development rules.

Every tab routes through the same try/except pattern — drop a module
into pages/ and it activates with no other changes. Sales Coach is live;
Team Trends and Sales School are next; Asa's tabs slot in the same way.
"""

from __future__ import annotations

import streamlit as st

from utils.database import init_db
from utils.sample_data import seed_if_empty

st.set_page_config(
    page_title="USEDC Sales IQ",
    page_icon="⚡",
    layout="wide",
)

# One-time setup
init_db()
if seed_if_empty():
    st.toast("Loaded sample data for demo.", icon="📦")

# Light brand styling
st.markdown(
    """
    <style>
      .block-container { padding-top: 2rem; }
      [data-testid="stSidebar"] { background: #0F2A43; }
      [data-testid="stSidebar"] * { color: #E8ECF1 !important; }
      [data-testid="stMetricValue"] { color: #0F2A43; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## ⚡ USEDC Sales IQ")
    st.caption("AI Sales Intelligence Platform")
    page = st.radio(
        "Navigate",
        [
            "📞 Call Analyzer",
            "📚 Knowledge Base",
            "🧠 AI Insights",
            "🎯 Sales Coach",
            "📊 Team Trends",
            "🎓 Sales School",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Every call makes every rep better.")


def _placeholder(title: str, owner: str) -> None:
    st.title(title)
    st.info(f"This module is being built by {owner}. Drop the file into pages/ to activate it.")


if page == "🎯 Sales Coach":
    from pages.sales_coach import render_sales_coach
    render_sales_coach()
elif page == "📊 Team Trends":
    try:
        from pages.team_trends import render_team_trends
        render_team_trends()
    except ImportError:
        _placeholder("📊 Team Trends", "Ayan (in progress)")
elif page == "🎓 Sales School":
    try:
        from pages.sales_school import render_sales_school
        render_sales_school()
    except ImportError:
        _placeholder("🎓 Sales School", "Ayan (in progress)")
elif page == "📞 Call Analyzer":
    try:
        from pages.call_analyzer import render_call_analyzer
        render_call_analyzer()
    except ImportError:
        _placeholder("📞 Call Analyzer", "Asa")
elif page == "📚 Knowledge Base":
    try:
        from pages.knowledge_base import render_knowledge_base
        render_knowledge_base()
    except ImportError:
        _placeholder("📚 Knowledge Base", "Asa")
elif page == "🧠 AI Insights":
    try:
        from pages.ai_insights import render_ai_insights
        render_ai_insights()
    except ImportError:
        _placeholder("🧠 AI Insights", "Asa")
