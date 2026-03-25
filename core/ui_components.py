"""Reusable UI primitives for the SaaS-style Streamlit dashboard."""

from __future__ import annotations

import streamlit as st


COLORS = {
    "background": "#f8fafc",
    "card": "#ffffff",
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "text": "#0f172a",
    "muted": "#64748b",
    "border": "#e2e8f0",
}


def inject_saas_css() -> None:
    """Inject SaaS UI styles and remove Streamlit default chrome."""
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {{
  --bg: {COLORS['background']};
  --card: {COLORS['card']};
  --primary: {COLORS['primary']};
  --primary-hover: {COLORS['primary_hover']};
  --text: {COLORS['text']};
  --muted: {COLORS['muted']};
  --border: {COLORS['border']};
  --success: {COLORS['success']};
  --warning: {COLORS['warning']};
  --danger: {COLORS['danger']};
}}

html, body {{
  font-family: 'Inter', sans-serif;
  color: var(--text);
}}

p, label, span, div {{
  color: var(--text);
}}

.stApp {{
  background: var(--bg);
}}

div[data-testid="stAppViewContainer"] {{
  background: var(--bg);
}}

header[data-testid="stHeader"] {{
  display: none;
}}

#MainMenu {{
  visibility: hidden;
}}

footer {{
  visibility: hidden;
}}

.viewerBadge_container__1QSob {{
  display: none;
}}

section[data-testid="stSidebar"] {{
  background: var(--card);
  border-right: 1px solid var(--border);
  min-width: 330px;
}}

section[data-testid="stSidebar"] * {{
  color: var(--text);
}}

div[role="radiogroup"] label p,
div[role="radiogroup"] span {{
  color: var(--text) !important;
  font-weight: 500;
}}

div[role="radiogroup"] label {{
  border-radius: 8px;
  padding: 0.25rem 0.35rem;
}}

div[role="radiogroup"] label:hover {{
  background: #eff6ff;
}}

div[role="radiogroup"] label[data-checked="true"],
div[role="radiogroup"] [aria-checked="true"] {{
  background: #dbeafe !important;
  border: 1px solid #bfdbfe;
}}

div[role="radiogroup"] label[data-checked="true"] p,
div[role="radiogroup"] [aria-checked="true"] p {{
  color: var(--primary) !important;
  font-weight: 700;
}}

.block-container {{
  padding-top: 1.2rem;
  padding-bottom: 1.2rem;
}}

div[data-testid="stMetric"] {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.10);
  padding: 0.9rem 1rem;
}}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] p,
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
  color: var(--text) !important;
}}

div[data-testid="stMetric"] [data-testid="stMetricLabel"] {{
  color: var(--muted) !important;
}}

.saas-section {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.10);
  padding: 0.85rem 1rem 0.65rem;
  margin-bottom: 0.9rem;
}}

.saas-title {{
  margin: 0;
  font-size: 1.02rem;
  font-weight: 700;
  color: var(--text);
}}

.saas-subtitle {{
  margin: 0.2rem 0 0;
  color: var(--muted);
  font-size: 0.86rem;
}}

.stButton > button {{
  background: var(--primary);
  color: white;
  border: 0;
  border-radius: 10px;
  font-weight: 600;
}}

.stButton > button:hover {{
  background: var(--primary-hover);
}}

.stSelectbox label,
.stTextInput label,
.stMultiSelect label {{
  color: var(--text) !important;
  font-weight: 600;
  font-size: 0.88rem;
}}

div[data-baseweb="select"] > div {{
  background: #ffffff !important;
  border-color: var(--border) !important;
  border-radius: 10px !important;
  min-height: 42px;
}}

div[data-baseweb="select"] input,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {{
  color: var(--text) !important;
}}

div[data-baseweb="select"] input::placeholder {{
  color: var(--muted) !important;
  opacity: 1;
}}

div[data-baseweb="tag"] {{
  background: #dbeafe !important;
  color: var(--text) !important;
  border-radius: 6px !important;
  border: 1px solid #bfdbfe !important;
  font-size: 0.78rem !important;
}}

section[data-testid="stSidebar"] .stButton > button {{
  min-height: 40px;
}}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {{
  margin-bottom: 0.15rem;
}}

div[data-testid="stDataFrame"] * {{
  color: var(--text) !important;
}}

div[data-testid="stDataFrame"] [role="grid"] {{
  background: #ffffff !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px;
}}

div[data-testid="stDataFrame"] [role="columnheader"] {{
  background: #f1f5f9 !important;
  color: var(--text) !important;
  font-weight: 700;
}}

div[data-testid="stDataFrame"] [role="gridcell"] {{
  background: #ffffff !important;
  color: var(--text) !important;
}}

.js-plotly-plot .modebar {{
  background: rgba(255, 255, 255, 0.95) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px;
}}

.js-plotly-plot .modebar-btn svg path {{
  fill: #334155 !important;
}}

div[data-testid="stMarkdownContainer"] p {{
  color: var(--text);
}}

.nav-label {{
  font-size: 0.84rem;
  color: var(--muted);
  margin-bottom: 0.35rem;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def create_navigation() -> str:
    """Render sidebar navigation and return the selected section."""
    st.sidebar.markdown("## AI Portfolio")
    st.sidebar.markdown('<div class="nav-label">Navigation</div>', unsafe_allow_html=True)
    return st.sidebar.radio(
        "Navigation",
        ["📊 Overview", "🗺️ Roadmap", "🔍 Drill-down", "⚙️ Settings"],
        label_visibility="collapsed",
    )


def create_card(title: str, value: str, delta: str | None = None) -> None:
    """Render a KPI using Streamlit metric with card styling via CSS."""
    st.metric(label=title, value=value, delta=delta)


def section_header(title: str, subtitle: str = "") -> None:
    """Render a consistent section header."""
    st.markdown(
        (
            f'<div class="saas-section"><p class="saas-title">{title}</p>'
            f'<p class="saas-subtitle">{subtitle}</p></div>'
        ),
        unsafe_allow_html=True,
    )
