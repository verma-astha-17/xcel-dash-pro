import { Link, useLocation } from 'react-router-dom'

const NAV = [
  { to: '/dashboard',    label: 'Overview',     icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { to: '/master-table', label: 'Master Table', icon: 'M3 10h18M3 14h18M3 6h18M9 10v8M15 10v8' },
  { to: '/drilldown',    label: 'Explore',      icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' },
]

export default function Navbar() {
  const { pathname } = useLocation()

  return (
    <header className="bg-slate-900 sticky top-0 z-20 shadow-2xl">
      <div className="max-w-screen-2xl mx-auto px-6 flex items-stretch h-14">

        {/* Brand */}
        <div className="flex items-center gap-3 pr-8 mr-2 border-r border-slate-700/60 flex-shrink-0">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-900/40">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div>
            <div className="text-white font-semibold text-sm tracking-wide leading-tight">Usecase Dashboard</div>
            <div className="text-slate-400 text-[10px] leading-tight tracking-wider uppercase">GenAI Portfolio</div>
          </div>
        </div>

        {/* Nav links */}
        <nav className="flex items-stretch gap-1 px-4">
          {NAV.map(({ to, label, icon }) => {
            const active = pathname === to || (to !== '/dashboard' && pathname.startsWith(to))
            return (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-2 px-4 text-sm font-medium transition-all duration-150 border-b-2 ${
                  active
                    ? 'text-white border-blue-500 bg-white/5'
                    : 'text-slate-400 border-transparent hover:text-slate-200 hover:border-slate-600 hover:bg-white/5'
                }`}
              >
                <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                  <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
                </svg>
                {label}
              </Link>
            )
          })}
        </nav>

        {/* Right section */}
        <div className="ml-auto flex items-center gap-4">
          <span className="flex items-center gap-1.5 text-xs text-slate-400">
            <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse shadow-sm shadow-emerald-400/60" />
            Live
          </span>
          <div className="h-5 w-px bg-slate-700" />
          <span className="text-[11px] text-slate-500 hidden sm:block">FastAPI · DuckDB · Chart.js</span>
        </div>

      </div>
    </header>
  )
}

