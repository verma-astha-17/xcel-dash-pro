import type { SummaryKPIs } from '../types'

interface CardDef {
  key: keyof SummaryKPIs
  label: string
  icon: string
  colorCls: string
  suffix?: string
}

const CARDS: CardDef[] = [
  {
    key: 'total_use_cases',
    label: 'Total Use Cases',
    icon: '📋',
    colorCls: 'bg-blue-50 border-blue-200 text-blue-800',
  },
  {
    key: 'in_production',
    label: 'In Production',
    icon: '✅',
    colorCls: 'bg-green-50 border-green-200 text-green-800',
  },
  {
    key: 'blocked',
    label: 'Blocked',
    icon: '🚫',
    colorCls: 'bg-red-50 border-red-200 text-red-800',
  },
  {
    key: 'unique_accounts',
    label: 'Accounts',
    icon: '🏢',
    colorCls: 'bg-purple-50 border-purple-200 text-purple-800',
  },
  {
    key: 'avg_productivity_achieved',
    label: 'Avg Productivity Achieved',
    icon: '📈',
    colorCls: 'bg-amber-50 border-amber-200 text-amber-800',
    suffix: '%',
  },
]

export default function KPICards({ data }: { data: SummaryKPIs }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
      {CARDS.map(({ key, label, icon, colorCls, suffix }) => {
        const val = data[key]
        const display =
          val == null ? '—' : `${val}${suffix ?? ''}`

        return (
          <div
            key={key}
            className={`rounded-xl border p-5 flex flex-col gap-1 ${colorCls}`}
          >
            <span className="text-2xl">{icon}</span>
            <span className="text-3xl font-bold leading-tight">{display}</span>
            <span className="text-xs font-medium opacity-70 leading-snug">
              {label}
            </span>
          </div>
        )
      })}
    </div>
  )
}
