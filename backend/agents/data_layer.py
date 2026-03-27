"""DataLayerAgent — scans the data/ folder and registers every CSV as a DuckDB view.

Table names are derived from file stems:
  'Account GenAI Use Cases.csv'   → account_genai_use_cases
  'GenAI Use Cases Catalogue.csv' → genai_use_cases_catalogue

Adding a new CSV file to data/ and calling .refresh() is all that is needed to
make it queryable — no code changes required.
"""
from __future__ import annotations

import math
import re
import threading
from pathlib import Path
from typing import Any

import duckdb


def _sanitize(filename: str) -> str:
    """Convert a CSV filename stem to a safe SQL identifier."""
    stem = Path(filename).stem
    name = re.sub(r"[^a-zA-Z0-9]", "_", stem).lower()
    name = re.sub(r"_+", "_", name).strip("_")
    return name


class DataLayerAgent:
    """Registers CSV files as DuckDB virtual views (no data is copied)."""

    def __init__(self, data_dir: str | Path | None = None) -> None:
        if data_dir is None:
            # backend/agents/ → backend/ → project root → data/
            data_dir = Path(__file__).parent.parent.parent / "data"
        self.data_dir = Path(data_dir)
        self._lock = threading.Lock()
        self.conn: duckdb.DuckDBPyConnection = duckdb.connect()
        self.tables: dict[str, str] = {}   # table_name → csv path
        self._register_all()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _register_all(self) -> None:
        for csv_path in sorted(self.data_dir.glob("*.csv")):
            table_name = _sanitize(csv_path.name)
            safe = str(csv_path.resolve()).replace("\\", "/")
            with self._lock:
                self.conn.execute(
                    f"CREATE OR REPLACE VIEW {table_name} AS "
                    f"SELECT * FROM read_csv_auto('{safe}', header=true, all_varchar=false)"
                )
            self.tables[table_name] = str(csv_path)

    # ── Public API ────────────────────────────────────────────────────────────

    def get_columns(self, table_name: str) -> list[str]:
        with self._lock:
            rows = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
        return [row[0] for row in rows]

    def query(self, sql: str, params: list[Any] | None = None) -> list[dict]:
        """Execute SQL and return a list of dicts (NaN/Inf → None for clean JSON)."""
        with self._lock:
            df = self.conn.execute(sql, params or []).df()
        records = df.to_dict(orient="records")
        return [
            {k: (None if isinstance(v, float) and not math.isfinite(v) else v) for k, v in row.items()}
            for row in records
        ]

    def refresh(self) -> None:
        """Re-scan data/ — picks up any new CSV files dropped in at runtime."""
        self._register_all()
