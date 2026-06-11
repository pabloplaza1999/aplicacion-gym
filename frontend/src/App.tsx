import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Members from './pages/Members'
import Payments from './pages/Payments'
import Attendance from './pages/Attendance'
import Store from './pages/Store'
import Settings from './pages/Settings'

const NAV = [
  { to: '/',         label: 'Dashboard', icon: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
      <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
      <rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>
    </svg>
  )},
  { to: '/members',  label: 'Clientes', icon: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
      <circle cx="9" cy="7" r="4"/>
      <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
    </svg>
  )},
  { to: '/payments', label: 'Pagos', icon: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
      <rect x="1" y="4" width="22" height="16" rx="2"/>
      <line x1="1" y1="10" x2="23" y2="10"/>
    </svg>
  )},
  { to: '/attendance', label: 'Asistencia', icon: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
      <path d="M9 11l3 3L22 4"/>
      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
    </svg>
  )},
  { to: '/tienda', label: 'Tienda', icon: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
      <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
      <line x1="3" y1="6" x2="21" y2="6"/>
      <path d="M16 10a4 4 0 0 1-8 0"/>
    </svg>
  )},
]

const NAV_BOTTOM = [
  { to: '/configuracion', label: 'Configuración', icon: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
      <circle cx="12" cy="12" r="3"/>
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
    </svg>
  )},
]

export default function App() {
  const location = useLocation()
  return (
    <div className="min-h-screen flex">
      <aside className="w-60 shrink-0 flex flex-col border-r border-surface-border bg-surface-card">
        <div className="px-5 py-5 border-b border-surface-border">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded bg-brand-500/10 border border-brand-500/30 flex items-center justify-center shadow-brand-sm">
              <svg viewBox="0 0 32 32" fill="none" className="w-5 h-5" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 20 C6 18 5 15 6 12 C7 9 9 8 11 8 L13 6 L15 8 C18 7 21 9 22 13 C23 17 21 20 18 22 L17 26 L14 26 L13 22 C11 22 9 21 8 20Z" fill="#4A4A55" stroke="#6B6B78" strokeWidth="0.5"/>
                <path d="M13 6 L14 3 L15 6" fill="#E8E8E8" stroke="#ccc" strokeWidth="0.3"/>
                <circle cx="11.5" cy="13" r="1.2" fill="#E02020"/>
              </svg>
            </div>
            <div>
              <p className="font-display text-lg leading-none tracking-widest text-white">RHINO</p>
              <p className="text-xs font-semibold text-brand-500 tracking-[0.2em] uppercase leading-none mt-0.5">Power</p>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-0.5">
          {NAV.map(({ to, label, icon }) => {
            const active = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)
            return (
              <NavLink key={to} to={to}
                className={`group flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium
                  transition-all duration-200 relative overflow-hidden border
                  ${active
                    ? 'bg-gradient-to-r from-brand-500/20 to-transparent text-white border-brand-500/25'
                    : 'text-gray-500 hover:text-gray-200 hover:bg-surface-raised/80 border-transparent'}`}>
                {active && <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-brand-500 rounded-r shadow-brand-sm transition-all duration-200" />}
                <span className={active ? 'text-brand-400' : 'text-gray-600 group-hover:text-gray-400 transition-colors'}>{icon}</span>
                <span className="tracking-wide">{label}</span>
              </NavLink>
            )
          })}
        </nav>
        <div className="p-3 border-t border-surface-border space-y-0.5">
          {NAV_BOTTOM.map(({ to, label, icon }) => {
            const active = location.pathname.startsWith(to)
            return (
              <NavLink key={to} to={to}
                className={`group flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium
                  transition-all duration-200 relative overflow-hidden border
                  ${active
                    ? 'bg-gradient-to-r from-brand-500/20 to-transparent text-white border-brand-500/25'
                    : 'text-gray-500 hover:text-gray-200 hover:bg-surface-raised/80 border-transparent'}`}>
                {active && <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-brand-500 rounded-r shadow-brand-sm transition-all duration-200" />}
                <span className={active ? 'text-brand-400' : 'text-gray-600 group-hover:text-gray-400 transition-colors'}>{icon}</span>
                <span className="tracking-wide">{label}</span>
              </NavLink>
            )
          })}
          <div className="px-3 pt-2">
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-brand-500 animate-pulse" />
              <p className="text-xs text-gray-600 font-mono">v0.1.0 · Fase 2</p>
            </div>
          </div>
        </div>
      </aside>
      <main className="flex-1 overflow-auto bg-surface">
        <Routes>
          <Route path="/"              element={<Dashboard />} />
          <Route path="/members"       element={<Members />} />
          <Route path="/payments"      element={<Payments />} />
          <Route path="/attendance"    element={<Attendance />} />
          <Route path="/tienda"        element={<Store />} />
          <Route path="/configuracion" element={<Settings />} />
        </Routes>
      </main>
    </div>
  )
}
