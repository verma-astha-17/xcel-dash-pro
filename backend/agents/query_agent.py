"""QueryAgent — named SQL intents over DuckDB views.

All methods return JSON-serialisable Python objects (list[dict] or dict).
Parameterised queries are used wherever user-supplied filter values are
passed to avoid SQL injection.
"""
from __future__ import annotations

from typing import Optional

from .data_layer import DataLayerAgent

# ---------------------------------------------------------------------------
# Re-usable SQL fragments
# ---------------------------------------------------------------------------

# Normalise Spanish development-status values → English labels.
# Using LOWER(TRIM(...)) so accentuation variants are handled.
_STATUS_EXPR = """CASE LOWER(TRIM(a."Development Status"))
    WHEN 'producción'    THEN 'In Production'
    WHEN 'produccion'    THEN 'In Production'
    WHEN 'en producción' THEN 'In Production'
    WHEN 'en produccion' THEN 'In Production'
    WHEN 'bloqueado'     THEN 'Blocked'
    WHEN 'validación'    THEN 'Validation'
    WHEN 'validacion'    THEN 'Validation'
    WHEN 'desarrollo'    THEN 'In Development'
    WHEN 'despliegue'    THEN 'Deployment'
    WHEN 'diseño'        THEN 'Design'
    WHEN 'diseno'        THEN 'Design'
    WHEN 'ideación'      THEN 'Ideation'
    WHEN 'ideacion'      THEN 'Ideation'
    WHEN 'identificado'  THEN 'Ideation'
    ELSE COALESCE(TRIM(a."Development Status"), 'In Development')
END"""

# Parse a "12.5%" or "12,5" column to DOUBLE (returns NULL on failure).
def _pct_col(col: str) -> str:
    return f"""TRY_CAST(REPLACE(REPLACE(a."{col}", '%', ''), ',', '.') AS DOUBLE)"""


class QueryAgent:
    """Executes SQL intents and returns clean JSON-serialisable data."""

    def __init__(self, datalayer: DataLayerAgent) -> None:
        self.dl = datalayer

    # ── Summary KPIs ──────────────────────────────────────────────────────────

    def summary_kpis(self) -> dict:
        sql = f"""
        SELECT
            COUNT(*)                                                                AS total_use_cases,
            SUM(CASE WHEN {_STATUS_EXPR} = 'In Production' THEN 1 ELSE 0 END)      AS in_production,
            SUM(CASE WHEN {_STATUS_EXPR} = 'Blocked'       THEN 1 ELSE 0 END)      AS blocked,
            COUNT(DISTINCT a."Account")                                             AS unique_accounts,
            ROUND(AVG({_pct_col('%Productivity Achieved')}),  1)                   AS avg_productivity_achieved,
            ROUND(AVG({_pct_col('%Productivity Estimated')}), 1)                   AS avg_productivity_estimated
        FROM account_genai_use_cases a
        """
        rows = self.dl.query(sql)
        return rows[0] if rows else {}

    # ── Status Distribution ────────────────────────────────────────────────────

    def status_distribution(self) -> list[dict]:
        sql = f"""
        SELECT {_STATUS_EXPR} AS status, COUNT(*) AS count
        FROM   account_genai_use_cases a
        GROUP  BY 1
        ORDER  BY 2 DESC
        """
        return self.dl.query(sql)

    # ── Phase Adoption (joined) ────────────────────────────────────────────────

    def phase_adoption(self) -> list[dict]:
        sql = """
        SELECT
            COALESCE(
                NULLIF(TRIM(a."Use Case linked:Phase View"), ''),
                NULLIF(TRIM(c."Phase"), ''),
                'Unknown'
            ) AS phase,
            COUNT(*) AS count
        FROM   account_genai_use_cases a
        LEFT JOIN genai_use_cases_catalogue c
               ON TRIM(a."Use Case linked") = TRIM(c."Title")
        GROUP  BY 1
        ORDER  BY 2 DESC
        """
        return self.dl.query(sql)

    # ── Productivity by Account ────────────────────────────────────────────────

    def productivity_by_account(self) -> list[dict]:
        sql = f"""
        SELECT
            COALESCE(TRIM(a."Account"), 'Unknown')              AS account,
            ROUND(AVG({_pct_col('%Productivity Estimated')}), 1) AS estimated,
            ROUND(AVG({_pct_col('%Productivity Achieved')}),  1) AS achieved
        FROM   account_genai_use_cases a
        WHERE  a."Account" IS NOT NULL AND TRIM(a."Account") != ''
        GROUP  BY 1
        ORDER  BY achieved DESC NULLS LAST
        """
        return self.dl.query(sql)

    # ── Technology Distribution ────────────────────────────────────────────────

    def technology_distribution(self) -> list[dict]:
        sql = """
        SELECT
            COALESCE(NULLIF(TRIM(a."GenAI Technology"), ''), 'Unknown') AS technology,
            COUNT(*) AS count
        FROM   account_genai_use_cases a
        GROUP  BY 1
        ORDER  BY 2 DESC
        """
        return self.dl.query(sql)

    # ── Maturity × Phase heatmap ───────────────────────────────────────────────

    def maturity_by_phase(self) -> list[dict]:
        sql = """
        SELECT
            COALESCE(NULLIF(TRIM(c."Phase"), ''),              'Unknown') AS phase,
            COALESCE(NULLIF(TRIM(c."Use Case Maturity"), ''),  'Unknown') AS maturity,
            COUNT(*) AS count
        FROM   account_genai_use_cases a
        LEFT JOIN genai_use_cases_catalogue c
               ON TRIM(a."Use Case linked") = TRIM(c."Title")
        GROUP  BY 1, 2
        ORDER  BY 1, 3 DESC
        """
        return self.dl.query(sql)

    # ── Filter Options ─────────────────────────────────────────────────────────

    def filter_options(self) -> dict:
        def _vals(sql: str) -> list[str]:
            return [r["v"] for r in self.dl.query(sql) if r.get("v")]

        return {
            "accounts": _vals(
                'SELECT DISTINCT TRIM("Account") AS v '
                'FROM account_genai_use_cases '
                'WHERE "Account" IS NOT NULL AND TRIM("Account") != \'\' '
                'ORDER BY v'
            ),
            "phases": _vals(
                'SELECT DISTINCT TRIM("Phase") AS v '
                'FROM genai_use_cases_catalogue '
                'WHERE "Phase" IS NOT NULL AND TRIM("Phase") != \'\' '
                'ORDER BY v'
            ),
            "technologies": _vals(
                'SELECT DISTINCT TRIM("GenAI Technology") AS v '
                'FROM account_genai_use_cases '
                'WHERE "GenAI Technology" IS NOT NULL AND TRIM("GenAI Technology") != \'\' '
                'ORDER BY v'
            ),
            "statuses": [
                "In Production", "In Development", "Validation",
                "Deployment", "Design", "Ideation", "Blocked",
            ],
        }

    # ── Implementations by Account × Phase ──────────────────────────────────────

    def implementations_by_account_phase(self) -> list[dict]:
        sql = """
        SELECT
            COALESCE(TRIM(a."Account"), 'Unknown') AS account,
            COALESCE(
                NULLIF(TRIM(a."Use Case linked:Phase View"), ''),
                NULLIF(TRIM(c."Phase"), ''),
                'Unknown'
            ) AS phase,
            COUNT(*) AS count
        FROM   account_genai_use_cases a
        LEFT JOIN genai_use_cases_catalogue c
               ON TRIM(a."Use Case linked") = TRIM(c."Title")
        WHERE  a."Account" IS NOT NULL AND TRIM(a."Account") != ''
        GROUP  BY 1, 2
        ORDER  BY 1, 3 DESC
        """
        return self.dl.query(sql)

    # ── Implementations by Account × Technology ───────────────────────────────────

    def implementations_by_account_technology(self) -> list[dict]:
        sql = """
        SELECT
            COALESCE(TRIM(a."Account"), 'Unknown')                       AS account,
            COALESCE(NULLIF(TRIM(a."GenAI Technology"), ''), 'Unknown')  AS technology,
            COUNT(*) AS count
        FROM   account_genai_use_cases a
        WHERE  a."Account" IS NOT NULL AND TRIM(a."Account") != ''
        GROUP  BY 1, 2
        ORDER  BY 1, 3 DESC
        """
        return self.dl.query(sql)

    # ── Paginated use-cases (filtered) ─────────────────────────────────────────

    def use_cases(
        self,
        account: Optional[str] = None,
        status:  Optional[str] = None,
        phase:   Optional[str] = None,
        search:  Optional[str] = None,
        limit:   int = 100,
        offset:  int = 0,
    ) -> dict:
        where_parts: list[str] = []
        params: list = []

        if account:
            where_parts.append('TRIM(a."Account") = ?')
            params.append(account)
        if status:
            where_parts.append(f"({_STATUS_EXPR}) = ?")
            params.append(status)
        if phase:
            where_parts.append(
                "COALESCE("
                "  NULLIF(TRIM(a.\"Use Case linked:Phase View\"), ''), "
                "  NULLIF(TRIM(c.\"Phase\"), '')"
                ") = ?"
            )
            params.append(phase)
        if search:
            where_parts.append(
                '(a."Use Case Name" ILIKE ? OR a."Account" ILIKE ? OR a."Use Case linked" ILIKE ?)'
            )
            like = f"%{search}%"
            params.extend([like, like, like])

        where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

        join_sql = """
        FROM   account_genai_use_cases a
        LEFT JOIN genai_use_cases_catalogue c
               ON TRIM(a."Use Case linked") = TRIM(c."Title")
        """

        count_sql = f"SELECT COUNT(*) AS total {join_sql} {where_sql}"
        total = (self.dl.query(count_sql, params) or [{"total": 0}])[0]["total"]

        data_sql = f"""
        SELECT
            ROW_NUMBER() OVER ()                                                   AS id,
            COALESCE(TRIM(a."Use Case Name"),        '')                           AS use_case_name,
            COALESCE(TRIM(a."Account"),              '')                           AS account,
            COALESCE(TRIM(a."Engagement Code"),      '')                           AS engagement_code,
            COALESCE(
                NULLIF(TRIM(a."Use Case linked:Phase View"), ''),
                NULLIF(TRIM(c."Phase"), ''),
                'Unknown'
            )                                                                      AS sdlc_phase,
            ({_STATUS_EXPR})                                                       AS status,
            COALESCE(NULLIF(TRIM(a."GenAI Technology"),     ''), 'Unknown')        AS technology,
            COALESCE(TRIM(a."Use Case linked"),      '')                           AS use_case_linked,
            COALESCE(TRIM(c."Role"),                 '')                           AS role,
            COALESCE(TRIM(c."Practice applicability"),'')                          AS practice,
            COALESCE(NULLIF(TRIM(c."Use Case Maturity"), ''), 'Unknown')           AS maturity,
            ROUND({_pct_col('%Productivity Estimated')}, 1)                        AS productivity_estimated,
            ROUND({_pct_col('%Productivity Achieved')},  1)                        AS productivity_achieved,
            COALESCE(TRIM(a."Start Date"),           '')                           AS start_date,
            COALESCE(TRIM(a."End Date"),             '')                           AS end_date,
            COALESCE(TRIM(a."Description"),          '')                           AS description
        {join_sql}
        {where_sql}
        ORDER BY a."Use Case Name" NULLS LAST
        LIMIT ? OFFSET ?
        """

        rows = self.dl.query(data_sql, params + [limit, offset])
        return {"total": total, "data": rows}
