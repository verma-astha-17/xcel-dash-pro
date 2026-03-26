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

const STATUS_BADGE: Record<string, string> = {
  'In Production':  'bg-green-100 text-green-800',
  'In Development': 'bg-yellow-100 text-yellow-800',
  'Validation':     'bg-purple-100 text-purple-800',
  'Deployment':     'bg-cyan-100 text-cyan-800',
  'Design':         'bg-orange-100 text-orange-800',
  'Ideation':       'bg-slate-100 text-slate-700',
  'Blocked':        'bg-red-100 text-red-800',
}

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
    header: 'Phase',
    cell: info => <span className="text-slate-600 whitespace-nowrap">{info.getValue() || '—'}</span>,
  }),
  col.accessor('status', {
    header: 'Status',
    cell: info => (
      <span
        className={`px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap ${
          STATUS_BADGE[info.getValue()] ?? 'bg-slate-100 text-slate-700'
        }`}
      >
        {info.getValue() || '—'}
      </span>
    ),
  }),
  col.accessor('technology', {
    header: 'Technology',
    cell: info => <span className="text-slate-600">{info.getValue() || '—'}</span>,
  }),
  col.accessor('maturity', {
    header: 'Maturity',
    cell: info => <span className="text-slate-500 text-xs">{info.getValue() || '—'}</span>,
  }),
  col.accessor('productivity_estimated', {
    header: 'Est. %',
    cell: info => (
      <span className="text-slate-600">
        {info.getValue() != null ? `${info.getValue()}%` : '—'}
      </span>
    ),
  }),
  col.accessor('productivity_achieved', {
    header: 'Ach. %',
    cell: info => {
      const v = info.getValue()
      if (v == null) return <span className="text-slate-400">—</span>
      const cls = v >= 10 ? 'text-green-700 font-medium' : v <= 0 ? 'text-red-600' : 'text-slate-600'
      return <span className={cls}>{v}%</span>
    },
  }),
  col.accessor('role', {
    header: 'Role',
    cell: info => <span className="text-slate-500 text-xs">{info.getValue() || '—'}</span>,
  }),
]

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
          {table.getRowModel().rows.map((row, i) => (
            <tr
              key={row.id}
              className={`border-b border-slate-100 hover:bg-blue-50/30 transition-colors ${
                i % 2 === 0 ? '' : 'bg-slate-50/50'
              }`}
            >
              {row.getVisibleCells().map(cell => (
                <td key={cell.id} className="px-4 py-3">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
