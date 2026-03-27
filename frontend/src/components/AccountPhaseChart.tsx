import { useMemo } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'
import type { AccountPhaseItem } from '../types'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const PHASE_COLORS: Record<string, string> = {
  'Design':                      '#93c5fd',
  'Coding':                      '#6ee7b7',
  'Incident/Problem Management': '#fca5a5',
  'Analysis Requirements':       '#c4b5fd',
  'Governance':                  '#67e8f9',
  'Operate':                     '#86efac',
  'Transition':                  '#fde68a',
  'Deploy':                      '#bbf7d0',
  'Test':                        '#f9a8d4',
  'All':                         '#cbd5e1',
  'Unknown':                     '#e2e8f0',
}

const FALLBACK = [
  '#93c5fd', '#6ee7b7', '#fde68a', '#fca5a5', '#c4b5fd',
  '#67e8f9', '#bbf7d0', '#fed7aa', '#f9a8d4', '#cbd5e1',
]

export default function AccountPhaseChart({ data }: { data: AccountPhaseItem[] }) {
  const { chartData, options, height } = useMemo(() => {
    const phases   = Array.from(new Set(data.map(d => d.phase))).sort()
    const accounts = Array.from(new Set(data.map(d => d.account))).sort()
    const lookup   = new Map(data.map(d => [`${d.account}||${d.phase}`, d.count]))

    // Only include phases that have at least one non-zero value
    const activePhases = phases.filter(ph =>
      accounts.some(acc => (lookup.get(`${acc}||${ph}`) ?? 0) > 0)
    )

    const chartData = {
      labels: accounts,
      datasets: activePhases.map((phase, i) => ({
        label: phase,
        data: accounts.map(acc => lookup.get(`${acc}||${phase}`) ?? 0),
        backgroundColor: PHASE_COLORS[phase] ?? FALLBACK[i % FALLBACK.length],
        hoverBackgroundColor: PHASE_COLORS[phase] ?? FALLBACK[i % FALLBACK.length],
        borderRadius: 0,
        borderSkipped: false,
        stack: 'stack',
        barPercentage: 0.6,
        categoryPercentage: 0.7,
      })),
    }

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 600, easing: 'easeInOutQuart' as const },
      plugins: {
        legend: {
          position: 'bottom' as const,
          labels: {
            usePointStyle: true,
            pointStyle: 'rectRounded' as const,
            padding: 18,
            font: { size: 11, family: 'Inter, system-ui, sans-serif' },
            color: '#475569',
            boxWidth: 12,
            boxHeight: 12,
          },
          onClick: (_e: any, legendItem: any, legend: any) => {
            const chart = legend.chart
            const idx = legendItem.datasetIndex
            // If every other dataset is already hidden, this is a second click → restore all
            const alreadySolo = chart.data.datasets.every((_: any, i: number) =>
              i === idx ? true : !chart.isDatasetVisible(i)
            )
            chart.data.datasets.forEach((_: any, i: number) => {
              chart.setDatasetVisibility(i, alreadySolo ? true : i === idx)
            })
            chart.update()
          },
        },
        tooltip: {
          backgroundColor: '#1e293b',
          titleColor: '#f8fafc',
          bodyColor: '#cbd5e1',
          footerColor: '#94a3b8',
          padding: 12,
          cornerRadius: 8,
          mode: 'index' as const,
          intersect: false,
          callbacks: {
            title: (items: any[]) => items[0]?.label ?? '',
            label: (ctx: any) =>
              ctx.parsed.y > 0 ? `  ${ctx.dataset.label}: ${ctx.parsed.y}` : undefined,
            footer: (items: any[]) => {
              const total = items.reduce((s, i) => s + (i.parsed.y ?? 0), 0)
              return total > 0 ? `  Total: ${total}` : ''
            },
          },
        },
      },
      scales: {
        x: {
          stacked: true,
          grid: { display: false },
          ticks: {
            font: { size: 11, family: 'Inter, system-ui, sans-serif', weight: 600 },
            color: '#334155',
            maxRotation: 35,
            minRotation: 20,
          },
          border: { display: false },
        },
        y: {
          stacked: true,
          beginAtZero: true,
          grid: { color: '#f1f5f9', lineWidth: 1 },
          ticks: {
            font: { size: 11, family: 'Inter, system-ui, sans-serif' },
            color: '#94a3b8',
            precision: 0,
            stepSize: 1,
          },
          border: { display: false },
        },
      },
    }

    const height = 380
    return { chartData, options, height }
  }, [data])

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
      <div className="flex items-center justify-between mb-1">
        <p className="text-xs text-slate-400">Use case count per account · stacked by SDLC phase</p>
        <span className="text-[10px] text-slate-300 italic">Click legend to isolate · click again to restore</span>
      </div>
      <div style={{ height }}>
        <Bar data={chartData} options={options} />
      </div>
    </div>
  )
}
