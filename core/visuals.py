"""Plotly charts for the AI Use Case Portfolio dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from core.data_engine import SDLC_PHASES, STATUS_OPTIONS

COLOR_BG = "#f8fafc"
COLOR_CARD = "#ffffff"
COLOR_PRIMARY = "#2563eb"
COLOR_SUCCESS = "#22c55e"
COLOR_WARNING = "#f59e0b"
COLOR_DANGER = "#ef4444"
COLOR_TEXT_PRIMARY = "#0f172a"
COLOR_TEXT_SECONDARY = "#64748b"

STATUS_COLORS = {
    "In Production": COLOR_SUCCESS,
    "In Development": COLOR_WARNING,
    "Validation": "#a855f7",
    "Deployment": "#06b6d4",
    "Design": "#f97316",
    "Ideation": "#94a3b8",
    "Blocked": COLOR_DANGER,
}


def _layout() -> dict:
    return {
        "template": "plotly_white",
        "paper_bgcolor": COLOR_BG,
        "plot_bgcolor": COLOR_CARD,
        "font": {"family": "Inter, sans-serif", "color": COLOR_TEXT_PRIMARY, "size": 12},
    }


def create_pulse_plot(saturation_df: pd.DataFrame) -> go.Figure:
    ordered = saturation_df.sort_values("Saturation", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=ordered["Saturation"],
            y=ordered["Phase"],
            orientation="h",
            marker={
                "color": ordered["Saturation"],
                "colorscale": [[0, "#cbd5e1"], [0.55, "#93c5fd"], [1, COLOR_PRIMARY]],
                "line": {"color": "#dbeafe", "width": 1},
                "showscale": False,
            },
            text=ordered["Saturation"].map(lambda v: f"{v:.0f}%"),
            textposition="inside",
        )
    )
    fig.update_layout(
        **_layout(),
        title="AI Utilization Across SDLC Phases",
        xaxis_title="Saturation %",
        yaxis_title="SDLC Phase",
        height=420,
        margin={"l": 130, "r": 30, "t": 60, "b": 40},
    )
    fig.update_xaxes(range=[0, 100], gridcolor="#e2e8f0")
    return fig


def create_strategic_heatmap(df_exploded: pd.DataFrame) -> go.Figure:
    col_order = [s for s in STATUS_OPTIONS if s in df_exploded["Status"].unique()]
    heatmap = pd.crosstab(df_exploded["SDLC_Phase"], df_exploded["Status"])
    for s in STATUS_OPTIONS:
        if s not in heatmap.columns:
            heatmap[s] = 0
    heatmap = heatmap[[s for s in STATUS_OPTIONS if s in heatmap.columns]]

    fig = go.Figure(
        go.Heatmap(
            z=heatmap.values,
            x=heatmap.columns.tolist(),
            y=heatmap.index.tolist(),
            colorscale=[[0, "#eff6ff"], [0.5, "#93c5fd"], [1, COLOR_PRIMARY]],
            colorbar={"title": "Use Cases"},
        )
    )
    fig.update_layout(
        **_layout(),
        title="Phase vs Development Status",
        xaxis_title="Development Status",
        yaxis_title="SDLC Phase",
        height=420,
        margin={"l": 200, "r": 40, "t": 60, "b": 40},
    )
    return fig


def create_implementation_quadrant(df: pd.DataFrame) -> go.Figure:
    """Scatter of Productivity Estimated vs Achieved, coloured by status."""
    fig = go.Figure()
    for status in STATUS_OPTIONS:
        subset = df[df["Status"] == status]
        if subset.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=subset["Productivity_Estimated_Pct"],
                y=subset["Productivity_Achieved_Pct"],
                mode="markers",
                name=status,
                marker={
                    "size": 12,
                    "color": STATUS_COLORS.get(status, "#94a3b8"),
                    "line": {"color": "#ffffff", "width": 1},
                    "opacity": 0.85,
                },
                text=subset["Use_Case_Name"],
                customdata=subset[["Account", "SDLC_Phase"]],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Estimated: %{x:.1f}%<br>"
                    "Achieved: %{y:.1f}%<br>"
                    "Account: %{customdata[0]}<br>"
                    "Phase: %{customdata[1]}<extra></extra>"
                ),
            )
        )

    # Diagonal: achieved == estimated target line
    all_pct = pd.concat([df["Productivity_Estimated_Pct"], df["Productivity_Achieved_Pct"]])
    max_val = float(all_pct.max()) if not all_pct.empty else 25
    max_val = max(max_val, 5)
    fig.add_trace(
        go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode="lines",
            line={"dash": "dash", "color": "#94a3b8", "width": 1},
            name="Achieved = Estimated",
            showlegend=True,
        )
    )

    fig.update_layout(
        **_layout(),
        title="Productivity: Estimated vs Achieved (%)",
        height=460,
        margin={"l": 50, "r": 20, "t": 60, "b": 40},
        legend_title_text="Status",
    )
    fig.update_xaxes(title="Productivity Estimated (%)", gridcolor="#e2e8f0")
    fig.update_yaxes(title="Productivity Achieved (%)", gridcolor="#e2e8f0")
    return fig


def create_cross_functional_matrix(df_exploded: pd.DataFrame) -> go.Figure:
    grouped = (
        df_exploded.groupby(["Practice_Applicability", "SDLC_Phase", "Technology"]).size().reset_index(name="Count")
    )
    labels: list[str] = []
    parents: list[str] = []
    values: list[float] = []

    practice_totals = grouped.groupby("Practice_Applicability", as_index=False)["Count"].sum()
    for _, row in practice_totals.iterrows():
        practice = str(row["Practice_Applicability"])
        labels.append(practice)
        parents.append("")
        values.append(float(row["Count"]))

    phase_totals = grouped.groupby(["Practice_Applicability", "SDLC_Phase"], as_index=False)["Count"].sum()
    for _, row in phase_totals.iterrows():
        practice = str(row["Practice_Applicability"])
        phase = str(row["SDLC_Phase"])
        labels.append(f"{practice} | {phase}")
        parents.append(practice)
        values.append(float(row["Count"]))

    for _, row in grouped.iterrows():
        practice = str(row["Practice_Applicability"])
        phase = str(row["SDLC_Phase"])
        tech = str(row["Technology"])
        labels.append(f"{practice} | {phase} | {tech}")
        parents.append(f"{practice} | {phase}")
        values.append(float(row["Count"]))

    fig = go.Figure(
        go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker={"colorscale": [[0, "#dbeafe"], [1, COLOR_PRIMARY]]},
            hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
        )
    )
    fig.update_layout(**_layout(), title="Cross-Functional Matrix", height=500, margin={"l": 20, "r": 20, "t": 60, "b": 20})
    return fig


def create_status_pie_chart(df: pd.DataFrame) -> go.Figure:
    counts = df["Status"].value_counts().reindex(STATUS_OPTIONS, fill_value=0)
    fig = go.Figure(
        go.Pie(
            labels=counts.index.tolist(),
            values=counts.values.tolist(),
            hole=0.52,
            marker={"colors": [STATUS_COLORS.get(s, "#94a3b8") for s in counts.index.tolist()]},
        )
    )
    fig.update_layout(**_layout(), title="Status Distribution", height=360, margin={"l": 10, "r": 10, "t": 60, "b": 10})
    return fig


def create_priority_complexity_heatmap(df: pd.DataFrame) -> go.Figure:
    """Stacked bar: use cases per Account broken down by Development Status."""
    account_status = pd.crosstab(df["Account"], df["Status"])
    for s in STATUS_OPTIONS:
        if s not in account_status.columns:
            account_status[s] = 0
    account_status = account_status[[s for s in STATUS_OPTIONS if s in account_status.columns]]

    fig = go.Figure()
    for status in account_status.columns:
        fig.add_trace(
            go.Bar(
                x=account_status.index.tolist(),
                y=account_status[status].tolist(),
                name=status,
                marker_color=STATUS_COLORS.get(status, "#94a3b8"),
            )
        )
    fig.update_layout(
        **_layout(),
        title="Use Cases per Account by Status",
        barmode="stack",
        xaxis_title="Account",
        yaxis_title="Use Cases",
        height=420,
        margin={"l": 60, "r": 40, "t": 60, "b": 130},
        legend_title_text="Status",
        xaxis_tickangle=-30,
    )
    return fig
