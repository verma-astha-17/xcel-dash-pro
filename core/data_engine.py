"""Data loading, normalization, enrichment, and filtering helpers."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import streamlit as st


DEFAULT_ACCOUNT_CSV = "data/Account GenAI Use Cases.csv"
DEFAULT_CATALOGUE_CSV = "data/GenAI Use Cases Catalogue.csv"
DEFAULT_DATA_DIR = "data"

# SDLC phases derived from real dataset phase values
SDLC_PHASES = [
    "Analysis Requirements",
    "Design",
    "Coding",
    "Test",
    "Deploy",
    "Incident/Problem Management",
    "Operate",
    "Governance",
    "Transition",
]

# Development statuses mapped from Spanish source values
STATUS_OPTIONS = [
    "In Production",
    "In Development",
    "Validation",
    "Deployment",
    "Design",
    "Ideation",
    "Blocked",
]

PRIORITY_OPTIONS = ["Low", "Medium", "High", "Critical"]

ROI_MAPPING: Dict[str, int] = {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}

_STATUS_MAPPING: Dict[str, str] = {
    "producción": "In Production",
    "produccion": "In Production",
    "bloqueado": "Blocked",
    "validación": "Validation",
    "validacion": "Validation",
    "desarrollo": "In Development",
    "despliegue": "Deployment",
    "diseño": "Design",
    "diseno": "Design",
    "ideación": "Ideation",
    "ideacion": "Ideation",
}

_READINESS_BY_STATUS: Dict[str, float] = {
    "In Production": 1.0,
    "Validation": 0.75,
    "Deployment": 0.65,
    "In Development": 0.5,
    "Design": 0.3,
    "Ideation": 0.15,
    "Blocked": 0.1,
}

_ACTIVE_STATUSES = {"In Production", "Validation", "Deployment", "In Development"}


def _normalize_status(value: str) -> str:
    text = str(value).strip().lower()
    return _STATUS_MAPPING.get(text, "In Development")


def _parse_pct(value) -> float:
    """Parse '10%' or '10' to float (returns 0.0 on failure)."""
    text = str(value).strip().replace("%", "").replace(",", ".")
    try:
        return float(text)
    except (ValueError, TypeError):
        return 0.0


def _parse_json_array(value) -> list[str]:
    """Parse JSON array strings like '["ADM","C&CA"]' into plain Python lists."""
    text = str(value).strip()
    if not text or text in ("nan", "[]", ""):
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
    except (json.JSONDecodeError, ValueError):
        pass
    return [x.strip() for x in re.split(r"[;,]", text) if x.strip()]


def _compute_effort_days(start, end) -> int:
    """Estimate project duration in days from start/end date strings."""
    try:
        s = pd.to_datetime(str(start), errors="raise")
        e = pd.to_datetime(str(end), errors="raise")
        return max(1, min(int((e - s).days), 365))
    except Exception:
        return 30


def _pct_to_roi_label(pct: float) -> str:
    if pct >= 15:
        return "Very High"
    if pct >= 7:
        return "High"
    if pct >= 3:
        return "Medium"
    return "Low"


@st.cache_data
def load_data(filepath: str = DEFAULT_ACCOUNT_CSV) -> pd.DataFrame:
    """Load raw CSV data from disk."""
    return pd.read_csv(filepath)


def discover_csv_file(data_dir: str = DEFAULT_DATA_DIR) -> str:
    """Return the Account GenAI Use Cases CSV path (primary data file)."""
    primary = Path(DEFAULT_ACCOUNT_CSV)
    if primary.exists():
        return str(primary)
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


def _load_account_csv(filepath: str) -> pd.DataFrame:
    """Load and rename columns for the Account GenAI Use Cases CSV."""
    df = pd.read_csv(filepath)
    rename_map = {
        "Use Case Name": "Use_Case_Name",
        "Account": "Account",
        "Engagement Code": "Engagement_Code",
        "Description": "Use_Case_Description",
        "Use Case linked": "Use_Case_Linked",
        "Use Case linked:Phase View": "SDLC_Phase",
        "GenAI Technology": "Technology",
        "Development Status": "Status",
        "Principal SME": "SME",
        "Stakeholders": "Stakeholders",
        "Start Date": "Start_Date",
        "End Date": "End_Date",
        "%Productivity Estimated": "Productivity_Estimated",
        "%Productivity Achieved": "Productivity_Achieved",
        "Lessons learnt": "Lessons_Learnt",
        "Comments": "Comments",
    }
    return df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})


def _load_catalogue_csv(filepath: str) -> pd.DataFrame:
    """Load and rename columns for the GenAI Use Cases Catalogue CSV."""
    df = pd.read_csv(filepath)
    rename_map = {
        "Phase": "Cat_Phase",
        "Process": "Process",
        "Title": "Use_Case_Linked",
        "Role": "Role",
        "Technology": "Cat_Technology",
        "Practice applicability": "Practice_Applicability",
        "Use Case SPOC": "SPOC",
        "Use Case Page": "Use_Case_Page",
        "Use Case Maturity": "Maturity",
    }
    return df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})


def normalize_schema(account_df: pd.DataFrame, catalogue_df: pd.DataFrame) -> pd.DataFrame:
    """Merge account deployments with catalogue master data and normalize columns."""
    cat_cols = [c for c in ["Use_Case_Linked", "Role", "Practice_Applicability", "Cat_Phase", "Maturity", "Process"] if c in catalogue_df.columns]
    cat_sub = catalogue_df[cat_cols].drop_duplicates(subset=["Use_Case_Linked"])

    merged = account_df.merge(cat_sub, on="Use_Case_Linked", how="left")
    merged["Use_Case_ID"] = [f"UC-{i:03d}" for i in range(1, len(merged) + 1)]

    # Fill SDLC_Phase from catalogue Cat_Phase when account phase is missing
    if "Cat_Phase" in merged.columns:
        merged["SDLC_Phase"] = merged["SDLC_Phase"].fillna(merged["Cat_Phase"])
    merged["SDLC_Phase"] = merged["SDLC_Phase"].fillna("").astype(str).str.strip()

    merged["Status"] = merged["Status"].apply(_normalize_status)
    merged["Technology"] = merged["Technology"].fillna("Unknown").astype(str).str.strip()
    merged["Account"] = merged["Account"].fillna("Unknown").astype(str).str.strip()
    merged["Use_Case_Name"] = merged["Use_Case_Name"].fillna("").astype(str).str.strip()
    merged["Use_Case_Description"] = merged["Use_Case_Description"].fillna("").astype(str) if "Use_Case_Description" in merged.columns else ""
    merged["Maturity"] = merged["Maturity"].fillna("Unknown").astype(str) if "Maturity" in merged.columns else "Unknown"
    merged["Role"] = merged["Role"].fillna("[]").astype(str)
    merged["Practice_Applicability"] = merged["Practice_Applicability"].fillna("[]").astype(str)

    merged["Productivity_Estimated_Pct"] = merged["Productivity_Estimated"].apply(_parse_pct) if "Productivity_Estimated" in merged.columns else 0.0
    merged["Productivity_Achieved_Pct"] = merged["Productivity_Achieved"].apply(_parse_pct) if "Productivity_Achieved" in merged.columns else 0.0

    merged["Effort_Days"] = merged.apply(
        lambda r: _compute_effort_days(r.get("Start_Date", ""), r.get("End_Date", "")), axis=1
    )
    merged["ROI_Potential"] = merged["Productivity_Estimated_Pct"].apply(_pct_to_roi_label)
    merged["ROI_Score"] = merged["ROI_Potential"].map(ROI_MAPPING).fillna(2).astype(float)
    merged["Priority"] = "Medium"
    merged["Complexity"] = "Medium"
    merged["Complexity_Score"] = 2

    return merged


def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Add Readiness_Score derived from status and productivity."""
    out = df.copy()
    status_score = out["Status"].map(_READINESS_BY_STATUS).fillna(0.0)
    prod_score = (out["Productivity_Achieved_Pct"] / 20.0).clip(0, 1)
    out["Readiness_Score"] = (status_score * 60 + prod_score * 40).clip(0, 100)
    return out


def explode_multivalued_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Parse JSON array columns (Role, Practice_Applicability) and explode rows."""
    exploded = df.copy()
    exploded["Role"] = exploded["Role"].apply(_parse_json_array)
    exploded["Practice_Applicability"] = exploded["Practice_Applicability"].apply(_parse_json_array)
    exploded = exploded.explode("Role").explode("Practice_Applicability")
    for col in ["Role", "Practice_Applicability"]:
        exploded[col] = exploded[col].fillna("Unknown").replace("", "Unknown")
    exploded["Technology"] = exploded["Technology"].fillna("Unknown").astype(str)
    return exploded.dropna(subset=["Use_Case_Name"]).reset_index(drop=True)


def calculate_phase_saturation(df: pd.DataFrame) -> pd.DataFrame:
    """Compute active saturation for each SDLC phase present in data."""
    phases_known = [p for p in SDLC_PHASES if p in df["SDLC_Phase"].values]
    phases_other = [p for p in df["SDLC_Phase"].dropna().unique() if p and p not in SDLC_PHASES]
    rows = []
    for phase in phases_known + phases_other:
        phase_df = df[df["SDLC_Phase"] == phase]
        total = len(phase_df)
        if total == 0:
            continue
        active = len(phase_df[phase_df["Status"].isin(_ACTIVE_STATUSES)])
        rows.append({"Phase": phase, "Total": total, "Active": active, "Saturation": active / total * 100})
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["Phase", "Total", "Active", "Saturation"])


def calculate_ai_readiness_score(df: pd.DataFrame) -> float:
    """Compute overall readiness score (0-100)."""
    if df.empty:
        return 0.0
    return float(df["Readiness_Score"].mean())


@st.cache_data
def load_and_clean_data(
    account_path: str = DEFAULT_ACCOUNT_CSV,
    catalogue_path: str = DEFAULT_CATALOGUE_CSV,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load both CSVs, merge, enrich, and return (enriched, exploded) DataFrames."""
    account_df = _load_account_csv(account_path)
    catalogue_df = _load_catalogue_csv(catalogue_path)
    normalized = normalize_schema(account_df, catalogue_df)
    enriched = enrich_dataframe(normalized)
    exploded = explode_multivalued_columns(enriched)
    return enriched, exploded
