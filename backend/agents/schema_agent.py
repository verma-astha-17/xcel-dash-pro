"""SchemaAgent — discovers join keys between registered DuckDB views.

Strategy:
1. Known joins (hardcoded high-confidence hints for the current dataset).
2. Generic fuzzy column-name matching across tables (threshold 0.80).

When new CSVs are added the generic path finds candidate joins automatically.
"""
from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from .data_layer import DataLayerAgent

# Known joins for this dataset — confidence 1.0
_KNOWN_JOINS: list[tuple[str, str, str, str]] = [
    (
        "account_genai_use_cases",
        "Use Case linked",
        "genai_use_cases_catalogue",
        "Title",
    ),
]


@dataclass
class JoinHint:
    left_table: str
    left_column: str
    right_table: str
    right_column: str
    confidence: float


class SchemaAgent:
    """Auto-discovers relationships between CSV-backed DuckDB views."""

    SIMILARITY_THRESHOLD = 0.80

    def __init__(self, datalayer: DataLayerAgent) -> None:
        self.dl = datalayer

    def discover_joins(self) -> list[JoinHint]:
        schemas: dict[str, list[str]] = {
            t: self.dl.get_columns(t) for t in self.dl.tables
        }
        hints: list[JoinHint] = []

        # 1. High-confidence known joins
        for lt, lc, rt, rc in _KNOWN_JOINS:
            if (
                lt in schemas
                and lc in schemas[lt]
                and rt in schemas
                and rc in schemas[rt]
            ):
                hints.append(JoinHint(lt, lc, rt, rc, confidence=1.0))

        already = {(h.left_table, h.left_column) for h in hints}

        # 2. Generic fuzzy matching for any additional tables
        tables = list(schemas.keys())
        for i, t1 in enumerate(tables):
            for t2 in tables[i + 1:]:
                for c1 in schemas[t1]:
                    if (t1, c1) in already:
                        continue
                    for c2 in schemas[t2]:
                        score = SequenceMatcher(
                            None, c1.lower(), c2.lower()
                        ).ratio()
                        if score >= self.SIMILARITY_THRESHOLD:
                            hints.append(JoinHint(t1, c1, t2, c2, round(score, 3)))
                            already.add((t1, c1))
                            break

        return hints

    def get_schema_manifest(self) -> dict:
        hints = self.discover_joins()
        return {
            "tables": {
                name: self.dl.get_columns(name) for name in self.dl.tables
            },
            "joins": [
                {
                    "from": f"{h.left_table}.{h.left_column}",
                    "to": f"{h.right_table}.{h.right_column}",
                    "confidence": h.confidence,
                }
                for h in hints
            ],
        }
