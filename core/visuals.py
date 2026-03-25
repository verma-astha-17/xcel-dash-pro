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
    "Not Started": "#94a3b8",
    "In Progress": COLOR_WARNING,
    "Completed": COLOR_SUCCESS,
    "On Hold": COLOR_DANGER,
    "Cancelled": "#64748b",
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
    heatmap = pd.crosstab(df_exploded["SDLC_Phase"], df_exploded["ROI_Potential"]).reindex(SDLC_PHASES, fill_value=0)
    for c in ["Low", "Medium", "High", "Very High"]:
        if c not in heatmap.columns:
            heatmap[c] = 0
    heatmap = heatmap[["Low", "Medium", "High", "Very High"]]

    fig = go.Figure(
        go.Heatmap(
            z=heatmap.values,
            x=heatmap.columns,
            y=heatmap.index,
            colorscale=[[0, "#eff6ff"], [0.5, "#93c5fd"], [1, COLOR_PRIMARY]],
            colorbar={"title": "Use Cases"},
        )
    )
    fig.update_layout(
        **_layout(),
        title="Phase vs ROI Potential",
        xaxis_title="ROI Potential",
        yaxis_title="SDLC Phase",
        height=420,
        margin={"l": 130, "r": 40, "t": 60, "b": 40},
    )
    return fig


def create_implementation_quadrant(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for status in STATUS_OPTIONS:
        subset = df[df["Status"] == status]
        if subset.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=subset["Effort_Days"],
                y=subset["ROI_Score"],
                mode="markers",
                name=status,
                marker={
                    "size": subset["Complexity_Score"] * 14,
                    "color": STATUS_COLORS.get(status, "#94a3b8"),
                    "line": {"color": "#ffffff", "width": 1},
                    "opacity": 0.8,
                },
                text=subset["Use_Case_Name"],
                customdata=subset[["SDLC_Phase", "Priority", "Readiness_Score"]],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Effort: %{x} days<br>"
                    "ROI: %{y}<br>"
                    "Phase: %{customdata[0]}<br>"
                    "Priority: %{customdata[1]}<br>"
                    "Readiness: %{customdata[2]:.1f}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        **_layout(),
        title="Implementation Quadrant (Effort vs ROI vs Complexity)",
        height=460,
        margin={"l": 50, "r": 20, "t": 60, "b": 40},
        legend_title_text="Status",
    )
    fig.update_xaxes(type="log", title="Effort (days, log)", gridcolor="#e2e8f0")
    fig.update_yaxes(title="ROI Score", range=[0.8, 4.2], dtick=1, gridcolor="#e2e8f0")
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
    matrix = pd.crosstab(df["Priority"], df["Complexity_Score"]).reindex(
        ["Low", "Medium", "High", "Critical"], fill_value=0
    )
    for c in [1, 2, 3]:
        if c not in matrix.columns:
            matrix[c] = 0
    matrix = matrix[[1, 2, 3]]

    fig = go.Figure(
        data=go.Heatmap(
            z=matrix.values,
            x=["Low", "Medium", "High"],
            y=matrix.index,
            colorscale=[[0, "#fef3c7"], [0.5, "#fdba74"], [1, COLOR_DANGER]],
            colorbar={"title": "Count"},
        )
    )
    fig.update_layout(
        **_layout(),
        title="Priority vs Complexity",
        xaxis_title="Complexity",
        yaxis_title="Priority",
        height=420,
        margin={"l": 100, "r": 40, "t": 60, "b": 40},
    )
    return fig
