import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import type { TechnologyItem } from '../types'

const TECH_COLORS = [
  '#7c3aed', '#6d28d9', '#5b21b6', '#4c1d95',
  '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe',
]

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow px-3 py-2 text-sm">
      <p className="font-medium text-slate-700">{label}</p>
      <p className="text-violet-600">{payload[0].value} use cases</p>
    </div>
  )
}

export default function TechnologyChart({ data }: { data: TechnologyItem[] }) {
  const top12 = data.slice(0, 12)

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <h3 className="font-semibold text-slate-700 mb-1 text-base">
        Technology Distribution
      </h3>
      <p className="text-xs text-slate-400 mb-4">
        Top GenAI technologies used across use cases
      </p>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={top12}
          margin={{ left: 10, right: 10, top: 4, bottom: 80 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
          <XAxis
            dataKey="technology"
            tick={{ fontSize: 11, fill: '#475569' }}
            angle={-40}
            textAnchor="end"
            interval={0}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#64748b' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="count" radius={[5, 5, 0, 0]} maxBarSize={32}>
            {top12.map((_, i) => (
              <Cell key={i} fill={TECH_COLORS[i % TECH_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
