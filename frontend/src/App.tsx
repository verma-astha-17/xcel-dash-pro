import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Drilldown from './pages/Drilldown'
import MasterTable from './pages/MasterTable'

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />
      <div className="flex-1">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/master-table" element={<MasterTable />} />
          <Route path="/drilldown" element={<Drilldown />} />
        </Routes>
      </div>
    </div>
  )
}
