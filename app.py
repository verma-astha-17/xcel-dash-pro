"""AI Use Case Portfolio Dashboard - rebuilt SaaS edition."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from core.data_engine import (
    DEFAULT_ACCOUNT_CSV,
    DEFAULT_CATALOGUE_CSV,
    PRIORITY_OPTIONS,
    SDLC_PHASES,
    STATUS_OPTIONS,
    calculate_ai_readiness_score,
    calculate_phase_saturation,
    discover_csv_file,
    list_csv_files,
    load_and_clean_data,
)
from core.ui_components import COLORS, create_card, create_navigation, inject_saas_css, section_header
from core.visuals import (
    create_cross_functional_matrix,
    create_implementation_quadrant,
    create_priority_complexity_heatmap,
    create_pulse_plot,
    create_status_pie_chart,
    create_strategic_heatmap,
)


def configure_page() -> None:
    st.set_page_config(page_title="AI Use Case Catalogue", page_icon="📊", layout="wide")
    inject_saas_css()


def initialize_app_state() -> None:
    """Initialize settings and filter state once."""
    if "settings_page_size" not in st.session_state:
        st.session_state.settings_page_size = 50
    if "settings_compact_table" not in st.session_state:
        st.session_state.settings_compact_table = False
    if "settings_default_sort" not in st.session_state:
        st.session_state.settings_default_sort = "Readiness_Score"
    if "settings_default_desc" not in st.session_state:
        st.session_state.settings_default_desc = True

    if "filter_roles" not in st.session_state:
        st.session_state.filter_roles = []
    if "filter_technology" not in st.session_state:
        st.session_state.filter_technology = []
    if "filter_practices" not in st.session_state:
        st.session_state.filter_practices = []
    if "filter_phases" not in st.session_state:
        st.session_state.filter_phases = []
    if "filter_accounts" not in st.session_state:
        st.session_state.filter_accounts = []
    if "filter_status" not in st.session_state:
        st.session_state.filter_status = []


def create_filters(df_exploded: pd.DataFrame) -> dict:
    st.sidebar.markdown("### Filters")
    st.sidebar.caption("Tip: leave a filter empty to include all values.")

    quick_a, quick_b = st.sidebar.columns(2)
    if quick_a.button("Reset", use_container_width=True):
        st.session_state.filter_roles = []
        st.session_state.filter_technology = []
        st.session_state.filter_practices = []
        st.session_state.filter_phases = []
        st.session_state.filter_accounts = []
        st.session_state.filter_status = []
        st.rerun()
    if quick_b.button("In Production", use_container_width=True):
        st.session_state.filter_status = ["In Production"]
        st.rerun()

    roles = sorted(df_exploded["Role"].dropna().unique().tolist())
    tech = sorted(df_exploded["Technology"].dropna().unique().tolist())
    practices = sorted(df_exploded["Practice_Applicability"].dropna().unique().tolist())
    accounts = sorted(df_exploded["Account"].dropna().unique().tolist())

    return {
        "roles": st.sidebar.multiselect("Role", roles, key="filter_roles"),
        "technology": st.sidebar.multiselect("Technology", tech, key="filter_technology"),
        "practices": st.sidebar.multiselect("Practice", practices, key="filter_practices"),
        "phases": st.sidebar.multiselect("SDLC Phase", SDLC_PHASES, key="filter_phases"),
        "accounts": st.sidebar.multiselect("Account", accounts, key="filter_accounts"),
        "status": st.sidebar.multiselect("Status", STATUS_OPTIONS, key="filter_status"),
    }


def apply_filters(df_exploded: pd.DataFrame, df_enriched: pd.DataFrame, filters: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    filtered = df_exploded.copy()

    if filters["roles"]:
        filtered = filtered[filtered["Role"].isin(filters["roles"])]
    if filters["technology"]:
        filtered = filtered[filtered["Technology"].isin(filters["technology"])]
    if filters["practices"]:
        filtered = filtered[filtered["Practice_Applicability"].isin(filters["practices"])]
    if filters["phases"]:
        filtered = filtered[filtered["SDLC_Phase"].isin(filters["phases"])]
    if filters["accounts"]:
        filtered = filtered[filtered["Account"].isin(filters["accounts"])]
    if filters["status"]:
        filtered = filtered[filtered["Status"].isin(filters["status"])]

    ids = set(filtered["Use_Case_ID"].unique())
    return filtered, df_enriched[df_enriched["Use_Case_ID"].isin(ids)].copy()


def show_overview(df: pd.DataFrame, df_exploded: pd.DataFrame) -> None:
    section_header("Overview", "Executive summary of GenAI use cases across accounts")

    saturation = calculate_phase_saturation(df)
    readiness = calculate_ai_readiness_score(df)
    in_production = int((df["Status"] == "In Production").sum())
    blocked = int((df["Status"] == "Blocked").sum())
    avg_prod_achieved = float(df["Productivity_Achieved_Pct"].mean()) if not df.empty else 0.0
    unique_accounts = df["Account"].nunique() if not df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        create_card("Total Use Cases", str(len(df)))
    with c2:
        create_card("In Production", str(in_production))
    with c3:
        create_card("Avg Productivity Achieved", f"{avg_prod_achieved:.1f}%")
    with c4:
        create_card("Accounts", str(unique_accounts))

    left, right = st.columns([2, 1])
    with left:
        section_header("Portfolio Saturation", "Adoption by SDLC phase")
        st.plotly_chart(create_pulse_plot(saturation), width="stretch")
    with right:
        section_header("Status Mix", "Current execution health")
        st.plotly_chart(create_status_pie_chart(df), width="stretch")

    section_header("Productivity: Estimated vs Achieved", "Which use cases overperformed or underperformed")
    st.plotly_chart(create_implementation_quadrant(df), width="stretch")


def show_roadmap(df: pd.DataFrame, df_exploded: pd.DataFrame) -> None:
    section_header("Roadmap", "Strategic prioritization view")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_strategic_heatmap(df_exploded), width="stretch")
    with col2:
        st.plotly_chart(create_priority_complexity_heatmap(df), width="stretch")

    st.plotly_chart(create_cross_functional_matrix(df_exploded), width="stretch")


def show_drilldown(df: pd.DataFrame) -> None:
    section_header("Drill-down", "Explore and export the detailed catalogue")

    query = st.text_input("Search by name, account, or ID")
    view = df.copy()
    if query:
        q = query.strip()
        view = view[
            view["Use_Case_Name"].str.contains(q, case=False, na=False)
            | view["Use_Case_ID"].str.contains(q, case=False, na=False)
            | view["Account"].str.contains(q, case=False, na=False)
        ]

    sort_options = ["Readiness_Score", "Productivity_Achieved_Pct", "Use_Case_Name", "Status", "Account", "SDLC_Phase"]
    default_sort = st.session_state.settings_default_sort
    default_idx = sort_options.index(default_sort) if default_sort in sort_options else 0
    sort_col = st.selectbox("Sort by", sort_options, index=default_idx)

    desc_default = st.session_state.settings_default_desc
    sort_desc = st.toggle("Descending", value=desc_default)
    view = view.sort_values(sort_col, ascending=not sort_desc)

    page_size = int(st.session_state.settings_page_size)
    compact = bool(st.session_state.settings_compact_table)
    view_page = view.head(page_size)
    st.caption(f"Showing {len(view_page)} of {len(view)} records")

    display_cols = [c for c in [
        "Use_Case_ID", "Use_Case_Name", "Account", "SDLC_Phase", "Status",
        "Technology", "Productivity_Estimated", "Productivity_Achieved", "Readiness_Score",
    ] if c in view_page.columns]

    st.dataframe(
        view_page[display_cols],
        use_container_width=True,
        hide_index=True,
        height=420 if compact else 620,
    )
    st.download_button("Download CSV", data=view.to_csv(index=False), file_name="genai_use_cases_filtered.csv", mime="text/csv")


def show_settings(data_path: str) -> None:
    section_header("Settings", "Data sources and table behavior")

    st.subheader("Data Sources")
    st.info(f"**Account Use Cases:** `{DEFAULT_ACCOUNT_CSV}`")
    st.info(f"**GenAI Catalogue:** `{DEFAULT_CATALOGUE_CSV}`")

    col_a, col_b = st.columns(2)
    if col_a.button("Reload Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.subheader("Drill-down Table")
    st.session_state.settings_page_size = st.slider(
        "Rows shown in table",
        min_value=10,
        max_value=200,
        step=10,
        value=int(st.session_state.settings_page_size),
    )
    st.session_state.settings_compact_table = st.toggle(
        "Compact table height",
        value=bool(st.session_state.settings_compact_table),
    )
    st.session_state.settings_default_sort = st.selectbox(
        "Default sort column",
        ["Readiness_Score", "Productivity_Achieved_Pct", "Use_Case_Name", "Status", "Account", "SDLC_Phase"],
        index=["Readiness_Score", "Productivity_Achieved_Pct", "Use_Case_Name", "Status", "Account", "SDLC_Phase"].index(
            st.session_state.settings_default_sort
            if st.session_state.settings_default_sort in ["Readiness_Score", "Productivity_Achieved_Pct", "Use_Case_Name", "Status", "Account", "SDLC_Phase"]
            else "Readiness_Score"
        ),
    )
    st.session_state.settings_default_desc = st.toggle(
        "Default sort descending",
        value=bool(st.session_state.settings_default_desc),
    )

    st.subheader("Build Information")
    st.write(f"Account CSV: {DEFAULT_ACCOUNT_CSV}")
    st.write(f"Catalogue CSV: {DEFAULT_CATALOGUE_CSV}")
    st.write(f"Theme primary color: {COLORS['primary']}")
    st.success("Dashboard is loaded from real org data (Account GenAI Use Cases + GenAI Use Cases Catalogue).")


def main() -> None:
    configure_page()
    initialize_app_state()
    selected = create_navigation()

    try:
        df_enriched, df_exploded = load_and_clean_data()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()
    filters = create_filters(df_exploded) if selected != "⚙️ Settings" else None

    if filters:
        filtered_exploded, filtered_enriched = apply_filters(df_exploded, df_enriched, filters)
    else:
        filtered_exploded, filtered_enriched = df_exploded, df_enriched

    if selected == "📊 Overview":
        show_overview(filtered_enriched, filtered_exploded)
    elif selected == "🗺️ Roadmap":
        show_roadmap(filtered_enriched, filtered_exploded)
    elif selected == "🔍 Drill-down":
        show_drilldown(filtered_enriched)
    else:
        show_settings(DEFAULT_ACCOUNT_CSV)


if __name__ == "__main__":
    main()
