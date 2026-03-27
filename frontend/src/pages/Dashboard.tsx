import {
  useSummaryKPIs,
  useStatusDistribution,
  useImplementationsByAccountPhase,
  useImplementationsByAccountTechnology,
} from '../api/hooks'
import KPICards from '../components/KPICards'
import StatusChart from '../components/StatusChart'
import AccountPhaseChart from '../components/AccountPhaseChart'
import AccountTechnologyChart from '../components/AccountTechnologyChart'
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
  const kpis     = useSummaryKPIs()
  const status   = useStatusDistribution()
  const accPhase = useImplementationsByAccountPhase()
  const accTech  = useImplementationsByAccountTechnology()

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Usecase Dashboard</h1>
        <p className="text-sm text-slate-400 mt-1">
          GenAI use cases portfolio — live data via DuckDB, no manual ETL
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

      {/* Priority Chart 1 — Implementations by Account & SDLC Phase */}
      <section className="space-y-3">
        <SectionHeader
          title="Implementations by Account & SDLC Phase"
          subtitle="How many use cases each account runs, broken down by SDLC phase"
        />
        {accPhase.isLoading ? (
          <Loader />
        ) : accPhase.error ? (
          <ApiError message="Failed to load phase data" />
        ) : accPhase.data ? (
          <AccountPhaseChart data={accPhase.data} />
        ) : null}
      </section>

      {/* Priority Chart 2 — Implementations by Account & Technology */}
      <section className="space-y-3">
        <SectionHeader
          title="Implementations by Account & Technology"
          subtitle="GenAI technology stack per account"
        />
        {accTech.isLoading ? (
          <Loader />
        ) : accTech.error ? (
          <ApiError message="Failed to load technology data" />
        ) : accTech.data ? (
          <AccountTechnologyChart data={accTech.data} />
        ) : null}
      </section>

      {/* Priority Chart 3 — Use Cases by Status */}
      <section className="space-y-3">
        <SectionHeader
          title="Use Cases by Status"
          subtitle="Current development status across all implementations"
        />
        {status.isLoading ? (
          <Loader />
        ) : status.error ? (
          <ApiError message="Failed to load status data" />
        ) : status.data ? (
          <StatusChart data={status.data} />
        ) : null}
      </section>
    </div>
  )
}

