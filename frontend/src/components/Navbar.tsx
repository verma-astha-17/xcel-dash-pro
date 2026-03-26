import { Link, useLocation } from 'react-router-dom'

const NAV = [
  { to: '/dashboard', label: '📊 Overview' },
  { to: '/drilldown', label: '🔍 Drill-down' },
]

export default function Navbar() {
  const { pathname } = useLocation()

  return (
    <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center gap-8 shadow-sm sticky top-0 z-10">
      <div className="flex items-center gap-2 mr-4">
        <span className="text-2xl">🤖</span>
        <span className="font-bold text-slate-800 text-lg tracking-tight">
          GenAI Portfolio
        </span>
        <span className="ml-2 px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs font-medium">
          DuckDB
        </span>
      </div>

      <nav className="flex gap-1">
        {NAV.map(({ to, label }) => (
          <Link
            key={to}
            to={to}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              pathname === to
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            {label}
          </Link>
        ))}
      </nav>

      <div className="ml-auto text-xs text-slate-400">
        Powered by FastAPI · DuckDB · Recharts
      </div>
    </header>
  )
}
