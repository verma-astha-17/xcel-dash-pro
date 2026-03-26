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
import type { PhaseItem } from '../types'

function barColor(index: number, total: number): string {
  const t = 1 - index / Math.max(total - 1, 1)
  const r = Math.round(147 + (29  - 147) * t)
  const g = Math.round(197 + (78  - 197) * t)
  const b = Math.round(253 + (216 - 253) * t)
  return `rgb(${r},${g},${b})`
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow px-3 py-2 text-sm">
      <p className="font-medium text-slate-700">{label}</p>
      <p className="text-blue-600">{payload[0].value} use cases</p>
    </div>
  )
}

export default function PhaseChart({ data }: { data: PhaseItem[] }) {
  const sorted = [...data].sort((a, b) => b.count - a.count)
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <h3 className="font-semibold text-slate-700 mb-1 text-base">Phase Adoption</h3>
      <p className="text-xs text-slate-400 mb-4">Use-case count per SDLC phase (joined with catalogue)</p>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={sorted} layout="vertical" margin={{ left: 10, right: 20, top: 4, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
          <XAxis type="number" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="phase" width={150} tick={{ fontSize: 11, fill: '#475569' }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="count" radius={[0, 5, 5, 0]} maxBarSize={24}>
            {sorted.map((_, i) => (
              <Cell key={i} fill={barColor(i, sorted.length)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
