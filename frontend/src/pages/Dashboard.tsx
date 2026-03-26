import {
  useSummaryKPIs,
  useStatusDistribution,
  usePhaseAdoption,
  useProductivityByAccount,
  useTechnologyDistribution,
} from '../api/hooks'
import KPICards from '../components/KPICards'
import StatusChart from '../components/StatusChart'
import PhaseChart from '../components/PhaseChart'
import ProductivityChart from '../components/ProductivityChart'
import TechnologyChart from '../components/TechnologyChart'
import Loader, { CardSkeleton } from '../components/Loader'

function SectionHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div>
      <h2 className="text-lg font-semibold text-slate-800">{title}</h2>
      <p className="text-sm text-slate-400">{subtitle}</p>
    </div>
  )
}

function ApiError({ message }: { message: string }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
      ⚠️ {message} — make sure the backend is running on{' '}
      <code className="font-mono bg-red-100 px-1 rounded">http://localhost:8000</code>
    </div>
  )
}

export default function Dashboard() {
  const kpis         = useSummaryKPIs()
  const status       = useStatusDistribution()
  const phase        = usePhaseAdoption()
  const productivity = useProductivityByAccount()
  const technology   = useTechnologyDistribution()

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">GenAI Portfolio Overview</h1>
        <p className="text-sm text-slate-400 mt-1">
          Live data from CSV files via DuckDB — no manual ETL required
        </p>
      </div>

      {/* KPI Cards */}
      <section>
        {kpis.isLoading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {Array.from({ length: 5 }).map((_, i) => <CardSkeleton key={i} />)}
          </div>
        ) : kpis.error ? (
          <ApiError message="Failed to load KPIs" />
        ) : kpis.data ? (
          <KPICards data={kpis.data} />
        ) : null}
      </section>

      {/* Status + Phase */}
      <section className="space-y-3">
        <SectionHeader title="Status & Phase Breakdown" subtitle="Execution health and SDLC coverage" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {status.isLoading ? <Loader /> : status.data ? <StatusChart data={status.data} /> : null}
          {phase.isLoading  ? <Loader /> : phase.data  ? <PhaseChart  data={phase.data}  /> : null}
        </div>
      </section>

      {/* Productivity */}
      <section className="space-y-3">
        <SectionHeader
          title="Productivity by Account"
          subtitle="Average estimated vs achieved productivity gain (%)"
        />
        {productivity.isLoading ? (
          <Loader />
        ) : productivity.data ? (
          <ProductivityChart data={productivity.data} />
        ) : null}
      </section>

      {/* Technology */}
      <section className="space-y-3">
        <SectionHeader
          title="Technology Distribution"
          subtitle="GenAI technologies in use across the portfolio"
        />
        {technology.isLoading ? (
          <Loader />
        ) : technology.data ? (
          <TechnologyChart data={technology.data} />
        ) : null}
      </section>
    </div>
  )
}
