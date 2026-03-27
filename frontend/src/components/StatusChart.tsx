import { useMemo } from 'react'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, type Plugin } from 'chart.js'
import { Doughnut } from 'react-chartjs-2'
import type { StatusItem } from '../types'

ChartJS.register(ArcElement, Tooltip, Legend)

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
  const total = data.reduce((s, d) => s + d.count, 0)

  // Inline Chart.js plugin that draws the total in the doughnut hole
  const centerTextPlugin: Plugin<'doughnut'> = useMemo(() => ({
    id: 'centerText',
    afterDraw(chart) {
      const { ctx, chartArea } = chart
      if (!chartArea) return
      const cx = (chartArea.left + chartArea.right) / 2
      const cy = (chartArea.top + chartArea.bottom) / 2
      ctx.save()
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.font = 'bold 32px Inter, system-ui, sans-serif'
      ctx.fillStyle = '#1e293b'
      ctx.fillText(String(total), cx, cy - 10)
      ctx.font = '12px Inter, system-ui, sans-serif'
      ctx.fillStyle = '#94a3b8'
      ctx.fillText('total', cx, cy + 16)
      ctx.restore()
    },
  }), [total])

  const { chartData, options } = useMemo(() => {
    const chartData = {
      labels: data.map(d => d.status),
      datasets: [{
        data: data.map(d => d.count),
        backgroundColor: data.map((d, i) => PALETTE[d.status] ?? FALLBACK[i % FALLBACK.length]),
        borderColor: '#fff',
        borderWidth: 3,
        hoverOffset: 10,
      }],
    }

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '64%',
      plugins: {
        legend: {
          position: 'right' as const,
          align: 'center' as const,
          labels: {
            usePointStyle: true,
            pointStyle: 'circle' as const,
            padding: 16,
            font: { size: 12 },
            color: '#475569',
            generateLabels: (chart: any) => {
              const dataset = chart.data.datasets[0]
              return chart.data.labels.map((label: string, i: number) => ({
                text: `${label}  (${dataset.data[i]})`,
                fillStyle: dataset.backgroundColor[i],
                strokeStyle: dataset.backgroundColor[i],
                lineWidth: 0,
                hidden: !chart.getDataVisibility(i),
                index: i,
              }))
            },
          },
        },
        tooltip: {
          backgroundColor: '#1e293b',
          titleColor: '#f8fafc',
          bodyColor: '#cbd5e1',
          padding: 12,
          cornerRadius: 8,
          callbacks: {
            label: (ctx: any) => {
              const t = ctx.dataset.data.reduce((a: number, b: number) => a + b, 0)
              const pct = ((ctx.parsed / t) * 100).toFixed(1)
              return `  ${ctx.parsed} use cases  (${pct}%)`
            },
          },
        },
      },
      layout: {
        padding: { top: 8, bottom: 8 },
      },
    }

    return { chartData, options }
  }, [data])

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <p className="text-xs text-slate-400">Current development status across all use cases</p>
        <span className="text-[10px] text-slate-300 italic">Click legend to toggle</span>
      </div>
      <div style={{ height: 320 }}>
        <Doughnut data={chartData} options={options} plugins={[centerTextPlugin]} />
      </div>
    </div>
  )
}

