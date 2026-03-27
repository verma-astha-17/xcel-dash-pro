// ── API response envelope ─────────────────────────────────────────────────────

export interface ApiResponse<T> {
  data: T
  meta: { generated_at: string }
}

// ── KPI summary ───────────────────────────────────────────────────────────────

export interface SummaryKPIs {
  total_use_cases: number
  in_production: number
  blocked: number
  unique_accounts: number
  avg_productivity_achieved: number | null
  avg_productivity_estimated: number | null
}

// ── Chart data ────────────────────────────────────────────────────────────────

export interface StatusItem {
  status: string
  count: number
}

export interface PhaseItem {
  phase: string
  count: number
}

export interface ProductivityItem {
  account: string
  estimated: number | null
  achieved: number | null
}

export interface TechnologyItem {
  technology: string
  count: number
}

export interface MaturityItem {
  phase: string
  maturity: string
  count: number
}

export interface AccountPhaseItem {
  account: string
  phase: string
  count: number
}

export interface AccountTechnologyItem {
  account: string
  technology: string
  count: number
}

// ── Drill-down ────────────────────────────────────────────────────────────────

export interface UseCase {
  id: number
  use_case_name: string
  account: string
  engagement_code: string
  sdlc_phase: string
  status: string
  technology: string
  use_case_linked: string
  role: string
  practice: string
  maturity: string
  productivity_estimated: number | null
  productivity_achieved: number | null
  start_date: string
  end_date: string
  description: string
}

export interface UseCasesResponse {
  total: number
  data: UseCase[]
}

// ── Filters ───────────────────────────────────────────────────────────────────

export interface FilterOptions {
  accounts: string[]
  phases: string[]
  technologies: string[]
  statuses: string[]
}

export interface Filters {
  account: string
  status: string
  phase: string
  search: string
}
