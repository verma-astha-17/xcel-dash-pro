import { useState, useCallback } from 'react'
import { useUseCases, useFilterOptions } from '../api/hooks'
import UseCasesTable from '../components/UseCasesTable'
import Loader from '../components/Loader'
import type { Filters } from '../types'

const PAGE_SIZE = 100
const EMPTY_FILTERS: Filters = { account: '', status: '', phase: '', search: '' }

export default function Drilldown() {
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
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Drill-down</h1>
        <p className="text-sm text-slate-400 mt-1">
          Explore, filter, and sort all GenAI use cases (joined with catalogue master data)
        </p>
      </div>

      {/* Filter bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4">
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
        <div className="flex items-center gap-3">
          <p className="text-sm text-slate-500">
            {isFetching ? 'Loading…' : `${data.total} use cases found`}
            {data.total > PAGE_SIZE && ` · Page ${page + 1} of ${totalPages}`}
          </p>
          <DownloadButton filters={filters} total={data.total} />
        </div>
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

function FilterInput({
  label, value, placeholder, onChange,
}: {
  label: string; value: string; placeholder: string; onChange: (v: string) => void
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-slate-500">{label}</label>
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
      <label className="text-xs font-medium text-slate-500">{label}</label>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        className="border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[160px]"
      >
        <option value="">All</option>
        {options.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  )
}

function DownloadButton({ filters, total }: { filters: Filters; total: number }) {
  if (total === 0) return null

  const handleDownload = async () => {
    const qs = new URLSearchParams()
    if (filters.account) qs.set('account', filters.account)
    if (filters.status)  qs.set('status',  filters.status)
    if (filters.phase)   qs.set('phase',   filters.phase)
    if (filters.search)  qs.set('search',  filters.search)
    qs.set('limit', '500')
    qs.set('offset', '0')

    const res = await fetch(`/api/use-cases?${qs}`)
    if (!res.ok) return
    const json = await res.json()
    const rows: Record<string, unknown>[] = json.data ?? []
    if (!rows.length) return

    const headers = Object.keys(rows[0])
    const csv = [
      headers.join(','),
      ...rows.map(r =>
        headers.map(h => {
          const v = r[h] ?? ''
          return String(v).includes(',') ? `"${v}"` : v
        }).join(',')
      ),
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'genai_use_cases.csv'
    a.click()
    URL.revokeObjectURL(a.href)
  }

  return (
    <button
      onClick={handleDownload}
      className="text-sm text-blue-600 hover:text-blue-800 hover:underline ml-auto"
    >
      ⬇ Download CSV
    </button>
  )
}
