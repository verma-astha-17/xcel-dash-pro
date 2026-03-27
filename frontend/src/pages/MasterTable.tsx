import { useState, useCallback } from 'react'
import { useUseCases, useFilterOptions } from '../api/hooks'
import UseCasesTable, { CoverageLegend } from '../components/UseCasesTable'
import Loader from '../components/Loader'
import type { Filters } from '../types'

const PAGE_SIZE = 100
const EMPTY_FILTERS: Filters = { account: '', status: '', phase: '', search: '' }

export default function MasterTable() {
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS)
  const [page, setPage] = useState(0)

  const { data: options } = useFilterOptions()

  const { data, isLoading, isFetching } = useUseCases({
    account: filters.account || undefined,
    status:  filters.status  || undefined,
    phase:   filters.phase   || undefined,
    search:  filters.search  || undefined,
    limit:   PAGE_SIZE,
    offset:  page * PAGE_SIZE,
  })

  const update = useCallback((key: keyof Filters, value: string) => {
    setFilters(f => ({ ...f, [key]: value }))
    setPage(0)
  }, [])

  const reset = useCallback(() => {
    setFilters(EMPTY_FILTERS)
    setPage(0)
  }, [])

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 1

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Master Use Cases Table</h1>
        <p className="text-sm text-slate-400 mt-1">
          All GenAI use case implementations — joined with the catalogue, colour-coded by coverage level
        </p>
      </div>

      {/* Coverage legend */}
      <CoverageLegend />

      {/* Filter bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
        <div className="flex flex-wrap gap-3 items-end">
          <FilterInput
            label="Search"
            value={filters.search}
            placeholder="Name, account, use case…"
            onChange={v => update('search', v)}
          />
          <FilterSelect
            label="Account"
            value={filters.account}
            options={options?.accounts ?? []}
            onChange={v => update('account', v)}
          />
          <FilterSelect
            label="Status"
            value={filters.status}
            options={options?.statuses ?? []}
            onChange={v => update('status', v)}
          />
          <FilterSelect
            label="SDLC Phase"
            value={filters.phase}
            options={options?.phases ?? []}
            onChange={v => update('phase', v)}
          />
          <button
            onClick={reset}
            className="px-4 py-2 text-sm bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 font-medium transition-colors self-end"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Results count */}
      {data && (
        <p className="text-sm text-slate-500">
          {isFetching ? 'Loading…' : `${data.total} use cases found`}
          {data.total > PAGE_SIZE && ` · Page ${page + 1} of ${totalPages}`}
        </p>
      )}

      {/* Table */}
      {isLoading ? <Loader /> : data ? <UseCasesTable data={data.data} /> : null}

      {/* Pagination */}
      {data && data.total > PAGE_SIZE && (
        <div className="flex items-center justify-center gap-3 pt-2">
          <button
            disabled={page === 0}
            onClick={() => setPage(p => p - 1)}
            className="px-4 py-2 rounded-lg border border-slate-200 text-sm text-slate-700 disabled:opacity-40 hover:bg-slate-50 transition-colors"
          >
            ← Prev
          </button>
          <span className="text-sm text-slate-500 min-w-[90px] text-center">
            Page {page + 1} / {totalPages}
          </span>
          <button
            disabled={page + 1 >= totalPages}
            onClick={() => setPage(p => p + 1)}
            className="px-4 py-2 rounded-lg border border-slate-200 text-sm text-slate-700 disabled:opacity-40 hover:bg-slate-50 transition-colors"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}

// ── Filter helpers ────────────────────────────────────────────────────────────

function FilterInput({
  label, value, placeholder, onChange,
}: {
  label: string; value: string; placeholder: string; onChange: (v: string) => void
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">{label}</label>
      <input
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={e => onChange(e.target.value)}
        className="border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 w-52 bg-white"
      />
    </div>
  )
}

function FilterSelect({
  label, value, options, onChange,
}: {
  label: string; value: string; options: string[]; onChange: (v: string) => void
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">{label}</label>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        className="border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white w-44"
      >
        <option value="">All</option>
        {options.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  )
}
