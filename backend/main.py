"""FastAPI application — GenAI Use Cases Portfolio API.

Run from the project root:
    uvicorn backend.main:app --reload --port 8000

Endpoints:
    GET  /api/health
    GET  /api/schema
    GET  /api/summary-kpis
    GET  /api/status-distribution
    GET  /api/phase-adoption
    GET  /api/productivity-by-account
    GET  /api/technology-distribution
    GET  /api/maturity-by-phase
    GET  /api/filters/options
    GET  /api/use-cases          ?account=&status=&phase=&search=&limit=&offset=
    POST /api/admin/reload
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# Ensure `backend/` is on sys.path so `from agents.X import Y` resolves
# whether uvicorn is launched from the root or from backend/.
sys.path.insert(0, str(Path(__file__).parent))

from agents.data_layer import DataLayerAgent   # noqa: E402
from agents.schema_agent import SchemaAgent    # noqa: E402
from agents.query_agent import QueryAgent      # noqa: E402

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="GenAI Use Cases Portfolio API",
    version="1.0.0",
    description=(
        "Agentic data layer (DuckDB) + REST API for the GenAI portfolio dashboard. "
        "CSV files are registered as virtual SQL tables; no ETL pipeline required."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Agent singletons (one DuckDB connection per process) ─────────────────────

_datalayer = DataLayerAgent()
_schema    = SchemaAgent(_datalayer)
_query     = QueryAgent(_datalayer)


def _wrap(data) -> dict:
    return {
        "data": data,
        "meta": {"generated_at": datetime.now(timezone.utc).isoformat()},
    }


# ── Health & Schema ───────────────────────────────────────────────────────────

@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok", "registered_tables": list(_datalayer.tables.keys())}


@app.get("/api/schema", tags=["system"])
def schema():
    """Return discovered table schemas and join hints."""
    return _wrap(_schema.get_schema_manifest())


# ── Aggregated chart data ─────────────────────────────────────────────────────

@app.get("/api/summary-kpis", tags=["charts"])
def summary_kpis():
    """Total use cases, in-production count, accounts, avg productivity."""
    return _wrap(_query.summary_kpis())


@app.get("/api/status-distribution", tags=["charts"])
def status_distribution():
    """Count of use cases per normalised development status."""
    return _wrap(_query.status_distribution())


@app.get("/api/phase-adoption", tags=["charts"])
def phase_adoption():
    """Count of use cases per SDLC phase (joined with catalogue)."""
    return _wrap(_query.phase_adoption())


@app.get("/api/productivity-by-account", tags=["charts"])
def productivity_by_account():
    """Average estimated vs achieved productivity grouped by account."""
    return _wrap(_query.productivity_by_account())


@app.get("/api/technology-distribution", tags=["charts"])
def technology_distribution():
    """Count of use cases per GenAI technology."""
    return _wrap(_query.technology_distribution())


@app.get("/api/maturity-by-phase", tags=["charts"])
def maturity_by_phase():
    """Use case count broken down by SDLC phase and maturity level."""
    return _wrap(_query.maturity_by_phase())


# ── Filter helpers ────────────────────────────────────────────────────────────

@app.get("/api/filters/options", tags=["filters"])
def filter_options():
    """Distinct values for all filterable dimensions."""
    return _wrap(_query.filter_options())


# ── Paginated drill-down ──────────────────────────────────────────────────────

@app.get("/api/use-cases", tags=["data"])
def use_cases(
    account: Optional[str] = Query(None, description="Filter by account name"),
    status:  Optional[str] = Query(None, description="Filter by normalised status (English)"),
    phase:   Optional[str] = Query(None, description="Filter by SDLC phase"),
    search:  Optional[str] = Query(None, description="Free-text search on name / account / use-case"),
    limit:   int = Query(100, ge=1, le=500, description="Page size"),
    offset:  int = Query(0,   ge=0,         description="Page offset"),
):
    """Paginated, filterable list of enriched use cases (joined with catalogue)."""
    return _wrap(_query.use_cases(account, status, phase, search, limit, offset))


# ── Admin ─────────────────────────────────────────────────────────────────────

@app.post("/api/admin/reload", tags=["system"])
def reload_data():
    """Re-register CSV views — call after dropping a new file into data/."""
    _datalayer.refresh()
    return {"status": "reloaded", "registered_tables": list(_datalayer.tables.keys())}
