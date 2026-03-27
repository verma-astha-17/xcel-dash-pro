import { useQuery } from '@tanstack/react-query'
import { apiFetch } from './client'
import type {
  SummaryKPIs,
  StatusItem,
  PhaseItem,
  ProductivityItem,
  TechnologyItem,
  MaturityItem,
  AccountPhaseItem,
  AccountTechnologyItem,
  UseCasesResponse,
  FilterOptions,
} from '../types'

// ── Chart queries ─────────────────────────────────────────────────────────────

export const useSummaryKPIs = () =>
  useQuery({
    queryKey: ['summary-kpis'],
    queryFn: () => apiFetch<SummaryKPIs>('/api/summary-kpis'),
  })

export const useStatusDistribution = () =>
  useQuery({
    queryKey: ['status-distribution'],
    queryFn: () => apiFetch<StatusItem[]>('/api/status-distribution'),
  })

export const usePhaseAdoption = () =>
  useQuery({
    queryKey: ['phase-adoption'],
    queryFn: () => apiFetch<PhaseItem[]>('/api/phase-adoption'),
  })

export const useProductivityByAccount = () =>
  useQuery({
    queryKey: ['productivity-by-account'],
    queryFn: () => apiFetch<ProductivityItem[]>('/api/productivity-by-account'),
  })

export const useTechnologyDistribution = () =>
  useQuery({
    queryKey: ['technology-distribution'],
    queryFn: () => apiFetch<TechnologyItem[]>('/api/technology-distribution'),
  })

export const useMaturityByPhase = () =>
  useQuery({
    queryKey: ['maturity-by-phase'],
    queryFn: () => apiFetch<MaturityItem[]>('/api/maturity-by-phase'),
  })

export const useImplementationsByAccountPhase = () =>
  useQuery({
    queryKey: ['implementations-by-account-phase'],
    queryFn: () => apiFetch<AccountPhaseItem[]>('/api/implementations-by-account-phase'),
  })

export const useImplementationsByAccountTechnology = () =>
  useQuery({
    queryKey: ['implementations-by-account-technology'],
    queryFn: () => apiFetch<AccountTechnologyItem[]>('/api/implementations-by-account-technology'),
  })

// ── Filter options ────────────────────────────────────────────────────────────

export const useFilterOptions = () =>
  useQuery({
    queryKey: ['filter-options'],
    queryFn: () => apiFetch<FilterOptions>('/api/filters/options'),
    staleTime: 10 * 60 * 1000,
  })

// ── Paginated use-cases ───────────────────────────────────────────────────────

interface UseCaseParams {
  account?: string
  status?: string
  phase?: string
  search?: string
  limit?: number
  offset?: number
}

export const useUseCases = (params: UseCaseParams) =>
  useQuery({
    queryKey: ['use-cases', params],
    queryFn: () => {
      const qs = new URLSearchParams()
      if (params.account) qs.set('account', params.account)
      if (params.status)  qs.set('status',  params.status)
      if (params.phase)   qs.set('phase',   params.phase)
      if (params.search)  qs.set('search',  params.search)
      qs.set('limit',  String(params.limit  ?? 100))
      qs.set('offset', String(params.offset ?? 0))
      return apiFetch<UseCasesResponse>(`/api/use-cases?${qs}`)
    },
  })
