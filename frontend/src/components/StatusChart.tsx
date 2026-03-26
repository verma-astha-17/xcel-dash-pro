import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { StatusItem } from '../types'

const PALETTE: Record<string, string> = {
  'In Production':  '#22c55e',
  'In Development': '#f59e0b',
  'Validation':     '#a855f7',
  'Deployment':     '#06b6d4',
  'Design':         '#f97316',
  'Ideation':       '#94a3b8',
  'Blocked':        '#ef4444',
}

const FALLBACK = [
  '#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#84cc16', '#f97316', '#ec4899',
]

export default function StatusChart({ data }: { data: StatusItem[] }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <h3 className="font-semibold text-slate-700 mb-1 text-base">
        Status Distribution
      </h3>
      <p className="text-xs text-slate-400 mb-4">
        Current development status across all use cases
      </p>

      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            dataKey="count"
            nameKey="status"
            cx="50%"
            cy="48%"
            innerRadius={70}
            outerRadius={110}
            paddingAngle={3}
            label={({ percent }) =>
              percent > 0.04 ? `${(percent * 100).toFixed(0)}%` : ''
            }
            labelLine={false}
          >
            {data.map((entry, i) => (
              <Cell
                key={entry.status}
                fill={PALETTE[entry.status] ?? FALLBACK[i % FALLBACK.length]}
              />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number, name: string) => [
              `${value} use cases`,
              name,
            ]}
          />
          <Legend
            iconType="circle"
            iconSize={10}
            formatter={(value) => (
              <span className="text-xs text-slate-600">{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
