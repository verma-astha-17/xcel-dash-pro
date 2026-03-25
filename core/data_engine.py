"""Data loading, normalization, enrichment, and filtering helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import streamlit as st


DELIMITER = ";#"
DEFAULT_DATA_PATH = "data/ai_use_cases.csv"
DEFAULT_DATA_DIR = "data"

SDLC_PHASES = [
    "Requirements",
    "Architecture",
    "Design",
    "Development",
    "Testing",
    "Deployment",
    "Maintenance",
    "Operations",
    "Optimization",
    "Retirement",
    "Support",
]

STATUS_OPTIONS = ["Not Started", "In Progress", "Completed", "On Hold", "Cancelled"]
PRIORITY_OPTIONS = ["Low", "Medium", "High", "Critical"]

EFFORT_MAPPING: Dict[str, int] = {"XS": 1, "S": 3, "M": 10, "L": 25, "XL": 45}
ROI_MAPPING: Dict[str, int] = {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}
COMPLEXITY_MAPPING: Dict[str, int] = {"Low": 1, "Medium": 2, "High": 3}


def _normalize_effort(value: str) -> str:
    text = str(value).upper()
    for key in ["XS", "XL", "S", "M", "L"]:
        if key in text:
            return key
    return "M"


def _normalize_roi(value: str) -> str:
    text = str(value).strip().lower().replace("veryhigh", "very high")
    if "very high" in text:
        return "Very High"
    if "high" in text:
        return "High"
    if "medium" in text:
        return "Medium"
    if "low" in text:
        return "Low"
    return "Medium"


def _normalize_complexity(value: str) -> str:
    text = str(value).strip().lower()
    if "high" in text:
        return "High"
    if "medium" in text:
        return "Medium"
    if "low" in text:
        return "Low"
    return "Medium"


def _normalize_status(value: str) -> str:
    text = str(value).strip().lower()
    lookup = {
        "not started": "Not Started",
        "in progress": "In Progress",
        "completed": "Completed",
        "on hold": "On Hold",
        "cancelled": "Cancelled",
        "canceled": "Cancelled",
    }
    return lookup.get(text, "Not Started")


def _normalize_priority(value: str) -> str:
    text = str(value).strip().lower()
    lookup = {"low": "Low", "medium": "Medium", "high": "High", "critical": "Critical"}
    return lookup.get(text, "Medium")


def _split_values(value: str) -> list[str]:
    return [v.strip() for v in str(value).split(DELIMITER) if str(v).strip()]


@st.cache_data
def load_data(filepath: str = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load raw CSV data from disk."""
    return pd.read_csv(filepath)


def discover_csv_file(data_dir: str = DEFAULT_DATA_DIR) -> str:
    """Discover the CSV file to use from the data directory.

    Selection order:
    1. Use DEFAULT_DATA_PATH if it exists.
    2. Otherwise pick the most recently modified CSV in data_dir.
    """
    default_path = Path(DEFAULT_DATA_PATH)
    if default_path.exists():
        return str(default_path)

    directory = Path(data_dir)
    csv_files = sorted(directory.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in '{data_dir}'.")

    return str(csv_files[0])


def list_csv_files(data_dir: str = DEFAULT_DATA_DIR) -> list[str]:
    """Return CSV files from data_dir sorted by most recently modified first."""
    directory = Path(data_dir)
    if not directory.exists():
        return []
    csv_files = sorted(directory.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [str(p) for p in csv_files]


def normalize_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Map incoming CSV schema to dashboard canonical columns."""
    canonical = {
        "Use_Case_ID": "Use_Case_ID",
        "Use_Case_Name": "Use_Case_Name",
        "SDLC_Phase": "SDLC_Phase",
        "Priority": "Priority",
        "Status": "Status",
        "Effort_Estimate": "Effort_Estimate",
        "ROI_Potential": "ROI_Potential",
        "Complexity": "Complexity",
        "Role": "Role",
        "Technology": "Technology",
        "Practice_Applicability": "Practice_Applicability",
        "Use_Case_Description": "Use_Case_Description",
        "Expected_Benefits": "Expected_Benefits",
        "Implementation_Timeline": "Implementation_Timeline",
    }

    aliases = {
        "Sr No": "_sr_no",
        "Use Case": "Use_Case_Name",
        "Phase": "SDLC_Phase",
        "Use Case Description": "Use_Case_Description",
        "Expected Benefits": "Expected_Benefits",
        "Practice Applicability": "Practice_Applicability",
        "Effort Estimate": "Effort_Estimate",
        "ROI Potential": "ROI_Potential",
        "Implementation Timeline": "Implementation_Timeline",
    }

    working = df.rename(columns=aliases).copy()

    if "Use_Case_ID" not in working.columns:
        if "_sr_no" in working.columns:
            working["Use_Case_ID"] = working["_sr_no"].apply(lambda x: f"UC-{int(x):03d}")
        else:
            working["Use_Case_ID"] = [f"UC-{i:03d}" for i in range(1, len(working) + 1)]

    for col in canonical:
        if col not in working.columns:
            working[col] = ""

    working = working[list(canonical.keys())]

    working["SDLC_Phase"] = working["SDLC_Phase"].astype(str).str.strip().str.title()
    working["Priority"] = working["Priority"].apply(_normalize_priority)
    working["Status"] = working["Status"].apply(_normalize_status)
    working["Effort_Estimate"] = working["Effort_Estimate"].apply(_normalize_effort)
    working["ROI_Potential"] = working["ROI_Potential"].apply(_normalize_roi)
    working["Complexity"] = working["Complexity"].apply(_normalize_complexity)

    for col in ["Role", "Technology", "Practice_Applicability"]:
        working[col] = working[col].astype(str).str.replace(";", DELIMITER, regex=False)
        working[col] = working[col].astype(str).str.replace(f"{DELIMITER}{DELIMITER}", DELIMITER, regex=False)

    return working


def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Add numeric columns used by charts and KPIs."""
    out = df.copy()
    out["Effort_Days"] = out["Effort_Estimate"].map(EFFORT_MAPPING).fillna(10)
    out["ROI_Score"] = out["ROI_Potential"].map(ROI_MAPPING).fillna(2)
    out["Complexity_Score"] = out["Complexity"].map(COMPLEXITY_MAPPING).fillna(2)

    out["Readiness_Score"] = (
        (out["ROI_Score"] / 4 * 40)
        + ((4 - out["Complexity_Score"]) / 3 * 25)
        + ((45 - out["Effort_Days"]) / 45 * 20)
        + (out["Status"].map({"Completed": 1.0, "In Progress": 0.6}).fillna(0) * 15)
    ).clip(0, 100)

    return out


def explode_multivalued_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Create exploded rows for multi-valued filtering columns."""
    exploded = df.copy()
    for col in ["Role", "Technology", "Practice_Applicability"]:
        exploded[col] = exploded[col].apply(_split_values)
    exploded = exploded.explode("Role").explode("Technology").explode("Practice_Applicability")
    exploded = exploded.dropna(subset=["Role", "Technology", "Practice_Applicability"])
    return exploded


def calculate_phase_saturation(df: pd.DataFrame) -> pd.DataFrame:
    """Compute active saturation for each SDLC phase."""
    rows = []
    for phase in SDLC_PHASES:
        phase_df = df[df["SDLC_Phase"] == phase]
        total = len(phase_df)
        active = len(phase_df[phase_df["Status"].isin(["In Progress", "Completed"])])
        saturation = (active / total * 100) if total else 0
        rows.append({"Phase": phase, "Total": total, "Active": active, "Saturation": saturation})
    return pd.DataFrame(rows)


def calculate_ai_readiness_score(df: pd.DataFrame) -> float:
    """Compute overall readiness score (0-100)."""
    if df.empty:
        return 0.0
    return float(df["Readiness_Score"].mean())


@st.cache_data
def load_and_clean_data(filepath: str | None = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load CSV and return both enriched and exploded dataframes."""
    resolved_path = filepath or discover_csv_file()
    raw = load_data(resolved_path)
    normalized = normalize_schema(raw)
    enriched = enrich_dataframe(normalized)
    exploded = explode_multivalued_columns(enriched)
    return enriched, exploded
