import { useState } from 'react'
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  flexRender,
  createColumnHelper,
  type SortingState,
} from '@tanstack/react-table'
import type { UseCase } from '../types'

// ── Maturity stage classification ─────────────────────────────────────────────

type Stage =
  | 'no-approval'
  | 'not-explored'
  | 'initial-exploration'
  | 'poc'
  | 'pilot'
  | 'adoption'
  | 'industrialized'
  | 'value-generating'
  | 'not-in-scope'

interface StageInfo {
  stage: Stage
  label: string
  rowBorder: string
  badgeBg: string
  badgeText: string
  cellBg: string
}

const STAGE_STYLES: Record<Stage, Omit<StageInfo, 'stage' | 'label'>> = {
  'no-approval':         { rowBorder: 'border-l-red-500',     badgeBg: 'bg-red-100',     badgeText: 'text-red-700',     cellBg: 'bg-red-50/30'     },
  'not-explored':        { rowBorder: 'border-l-slate-400',   badgeBg: 'bg-slate-100',   badgeText: 'text-slate-600',   cellBg: ''                 },
  'initial-exploration': { rowBorder: 'border-l-orange-400',  badgeBg: 'bg-orange-100',  badgeText: 'text-orange-700',  cellBg: 'bg-orange-50/30'  },
  'poc':                 { rowBorder: 'border-l-amber-400',   badgeBg: 'bg-amber-100',   badgeText: 'text-amber-700',   cellBg: 'bg-amber-50/30'   },
  'pilot':               { rowBorder: 'border-l-yellow-400',  badgeBg: 'bg-yellow-100',  badgeText: 'text-yellow-700',  cellBg: 'bg-yellow-50/30'  },
  'adoption':            { rowBorder: 'border-l-blue-400',    badgeBg: 'bg-blue-100',    badgeText: 'text-blue-700',    cellBg: 'bg-blue-50/20'    },
  'industrialized':      { rowBorder: 'border-l-green-500',   badgeBg: 'bg-green-100',   badgeText: 'text-green-700',   cellBg: 'bg-green-50/30'   },
  'value-generating':    { rowBorder: 'border-l-emerald-500', badgeBg: 'bg-emerald-100', badgeText: 'text-emerald-700', cellBg: 'bg-emerald-50/30' },
  'not-in-scope':        { rowBorder: 'border-l-slate-200',   badgeBg: 'bg-slate-50',    badgeText: 'text-slate-400',   cellBg: ''                 },
}

const STAGE_LABELS: Record<Stage, string> = {
  'no-approval':         'No Approval from Client',
  'not-explored':        'Not Yet Explored',
  'initial-exploration': 'Initial Exploration',
  'poc':                 'POC',
  'pilot':               'Pilot',
  'adoption':            'Adoption',
  'industrialized':      'Industrialized',
  'value-generating':    'Value Generating',
  'not-in-scope':        'Not in Scope',
}

function mk(stage: Stage): StageInfo {
  return { stage, label: STAGE_LABELS[stage], ...STAGE_STYLES[stage] }
}

/**
 * Classifies a use case into one of 9 maturity stages using a multi-signal
 * approach: status (deployment health) + maturity (catalogue classification)
 * + productivity ratio (achieved / estimated).
 */
function classifyStage(
  status: string,
  maturity: string,
  est: number | null,
  ach: number | null,
): StageInfo {
  // Signal 1 — explicitly blocked by client
  if (status === 'Blocked') return mk('no-approval')

  // Signal 2 — productivity ratio (only meaningful when est > 0)
  const ratio = est != null && est > 0 && ach != null ? (ach / est) * 100 : null

  // Signal 3 — In Production (highest deployment signal)
  if (status === 'In Production' || maturity === 'Production') {
    if (ratio != null) {
      if (ratio >= 80 || ach! >= 15) return mk('value-generating')
      if (ratio >= 60)               return mk('industrialized')
    }
    // In production but no/low ratio data — at least Adoption
    return mk('adoption')
  }

  // Signal 4 — Deployment (rolled out, not yet measured well)
  if (status === 'Deployment') return mk('adoption')

  // Signal 5 — Validation stage
  if (status === 'Validation') {
    if (ratio != null && ratio >= 60) return mk('adoption')
    return mk('pilot')
  }

  // Signal 6 — In Development
  if (status === 'In Development') {
    if (maturity === 'Pilot') return mk('pilot')
    return mk('poc')
  }

  // Signal 7 — Design / early build
  if (status === 'Design') return mk('initial-exploration')

  // Signal 8 — Ideation
  if (status === 'Ideation') return mk('not-explored')

  // Signal 9 — Maturity-only fallback (no status match above)
  if (maturity === 'Pilot')      return mk('pilot')
  if (maturity === 'Prototype')  return mk('initial-exploration')
  if (maturity === 'Ideation')   return mk('not-explored')

  // No conclusive signals
  return mk('not-in-scope')
}

// ── Maturity Legend ───────────────────────────────────────────────────────────

export function CoverageLegend() {
  const stages: Stage[] = [
    'no-approval', 'not-explored', 'initial-exploration', 'poc',
    'pilot', 'adoption', 'industrialized', 'value-generating', 'not-in-scope',
  ]
  return (
    <div className="flex flex-wrap gap-x-5 gap-y-2 px-4 py-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600">
      <span className="font-semibold text-slate-700 w-full">Maturity Stage Legend:</span>
      {stages.map(s => {
        const { badgeBg, badgeText } = STAGE_STYLES[s]
        return (
          <span key={s} className="flex items-center gap-1.5">
            <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${badgeBg} ${badgeText}`}>
              {STAGE_LABELS[s]}
            </span>
          </span>
        )
      })}
    </div>
  )
}

// ── Status badge ──────────────────────────────────────────────────────────────

const STATUS_BADGE: Record<string, string> = {
  'In Production':  'bg-green-100 text-green-800',
  'In Development': 'bg-yellow-100 text-yellow-800',
  'Validation':     'bg-purple-100 text-purple-800',
  'Deployment':     'bg-cyan-100 text-cyan-800',
  'Design':         'bg-orange-100 text-orange-800',
  'Ideation':       'bg-slate-100 text-slate-700',
  'Blocked':        'bg-red-100 text-red-800',
}

// ── Columns ───────────────────────────────────────────────────────────────────

const col = createColumnHelper<UseCase>()

const columns = [
  col.accessor('use_case_name', {
    header: 'Use Case',
    cell: info => (
      <span className="font-medium text-slate-800 max-w-[220px] block truncate" title={info.getValue()}>
        {info.getValue() || '—'}
      </span>
    ),
  }),
  col.accessor('account', {
    header: 'Account',
    cell: info => <span className="text-slate-600">{info.getValue() || '—'}</span>,
  }),
  col.accessor('sdlc_phase', {
    header: 'SDLC Phase',
    cell: info => <span className="text-slate-600 whitespace-nowrap">{info.getValue() || '—'}</span>,
  }),
  col.accessor('status', {
    header: 'Status',
    cell: info => (
      <span className={`px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap ${STATUS_BADGE[info.getValue()] ?? 'bg-slate-100 text-slate-700'}`}>
        {info.getValue() || '—'}
      </span>
    ),
  }),
  col.accessor('technology', {
    header: 'Technology',
    cell: info => <span className="text-slate-600 text-xs">{info.getValue() || '—'}</span>,
  }),
  col.accessor('maturity', {
    header: 'Maturity',
    cell: info => <span className="text-slate-500 text-xs">{info.getValue() || '—'}</span>,
  }),
  col.accessor('productivity_estimated', {
    header: 'Est. %',
    cell: info => (
      <span className="text-slate-500 text-xs">
        {info.getValue() != null ? `${info.getValue()}%` : '—'}
      </span>
    ),
  }),
  col.accessor('productivity_achieved', {
    header: 'Ach. %',
    cell: info => {
      const v = info.getValue()
      if (v == null) return <span className="text-slate-400 text-xs">—</span>
      const cls = v >= 10 ? 'text-green-700 font-medium' : v <= 0 ? 'text-red-600' : 'text-slate-600'
      return <span className={`text-xs ${cls}`}>{v}%</span>
    },
  }),
  col.display({
    id: 'coverage',
    header: 'Maturity Stage',
    cell: ({ row }) => {
      const d = row.original
      const cov = classifyStage(d.status, d.maturity, d.productivity_estimated, d.productivity_achieved)
      if (cov.stage === 'not-in-scope') return <span className="text-slate-300 text-xs">—</span>
      return (
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap ${cov.badgeBg} ${cov.badgeText}`}>
          {cov.label}
        </span>
      )
    },
  }),
]

// ── Component ─────────────────────────────────────────────────────────────────

export default function UseCasesTable({ data }: { data: UseCase[] }) {
  const [sorting, setSorting] = useState<SortingState>([])

  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  })

  if (!data.length) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-400 text-sm">
        No use cases match the current filters.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-sm border-collapse">
        <thead>
          {table.getHeaderGroups().map(hg => (
            <tr key={hg.id} className="bg-slate-50 border-b border-slate-200">
              {hg.headers.map(header => (
                <th
                  key={header.id}
                  onClick={header.column.getToggleSortingHandler()}
                  className="text-left px-4 py-3 font-semibold text-slate-600 text-xs uppercase tracking-wide cursor-pointer select-none hover:text-slate-900 whitespace-nowrap"
                >
                  {flexRender(header.column.columnDef.header, header.getContext())}
                  {
                    {
                      asc:  <span className="ml-1 text-blue-500">↑</span>,
                      desc: <span className="ml-1 text-blue-500">↓</span>,
                    }[header.column.getIsSorted() as string] ?? (
                      <span className="ml-1 text-slate-300">⇅</span>
                    )
                  }
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map(row => {
            const d = row.original
            const cov = classifyStage(d.status, d.maturity, d.productivity_estimated, d.productivity_achieved)
            return (
              <tr
                key={row.id}
                className={`border-b border-slate-100 hover:brightness-95 transition-all border-l-4 ${cov.rowBorder} ${cov.cellBg}`}
              >
                {row.getVisibleCells().map(cell => (
                  <td key={cell.id} className="px-4 py-2.5">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
