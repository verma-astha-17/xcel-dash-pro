import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { ProductivityItem } from '../types'

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow px-3 py-2 text-sm max-w-[200px]">
      <p className="font-medium text-slate-700 mb-1 truncate">{label}</p>
      {payload.map((p: any) => (
        <p key={p.dataKey} style={{ color: p.fill }}>
          {p.name}: {p.value != null ? `${p.value}%` : '-'}
        </p>
      ))}
    </div>
  )
}

export default function ProductivityChart({ data }: { data: ProductivityItem[] }) {
  const clean = data.filter(d => d.estimated != null || d.achieved != null)
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <h3 className="font-semibold text-slate-700 mb-1 text-base">Productivity: Estimated vs Achieved</h3>
      <p className="text-xs text-slate-400 mb-4">Average % productivity gain per account (grouped bar)</p>
      <ResponsiveContainer width="100%" height={320}>
        <ComposedChart data={clean} margin={{ left: 10, right: 10, top: 4, bottom: 80 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
          <XAxis dataKey="account" tick={{ fontSize: 11, fill: '#475569' }} angle={-40} textAnchor="end" interval={0} axisLine={false} tickLine={false} />
          <YAxis unit="%" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ paddingTop: 16, fontSize: 12 }} iconType="circle" iconSize={10} />
          <Bar dataKey="estimated" name="Estimated" fill="#93c5fd" radius={[4, 4, 0, 0]} maxBarSize={24} />
          <Bar dataKey="achieved" name="Achieved" fill="#2563eb" radius={[4, 4, 0, 0]} maxBarSize={24} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
