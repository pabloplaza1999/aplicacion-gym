import { NavLink } from 'react-router-dom'

const links = [
  { to: '/',           label: 'Dashboard'  },
  { to: '/members',    label: 'Clientes'   },
  { to: '/payments',   label: 'Pagos'      },
  { to: '/attendance', label: 'Asistencia' },
]

export function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 h-14 bg-surface-0/80 backdrop-blur border-b border-zinc-800 flex items-center px-6 gap-8">
      {/* Logo */}
      <span className="font-display font-700 text-lg tracking-tight text-brand-400 mr-4">
        GymOS
      </span>

      {links.map(({ to, label }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className={({ isActive }) =>
            isActive
              ? 'text-sm font-medium text-zinc-100'
              : 'text-sm text-zinc-500 hover:text-zinc-300 transition-colors'
          }
        >
          {label}
        </NavLink>
      ))}
    </nav>
  )
}
