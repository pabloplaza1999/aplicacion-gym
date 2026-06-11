import { Users, CalendarCheck, AlertCircle, CreditCard } from 'lucide-react'

// Rediseño UI Pro Max (aprobado Paso 1-3).
// Tokens success/energy definidos en tailwind.config.js.
// Iconos: lucide-react (instalado en package.json).

interface Props {
  label: string
  value: string | number
  sub?: string
  accent?: 'green' | 'yellow' | 'red' | 'blue'
}

const accents = {
  green:  { value: 'text-success-400', bar: 'bg-success-500', Icon: Users        },
  yellow: { value: 'text-energy-400',  bar: 'bg-energy-500',  Icon: CalendarCheck },
  red:    { value: 'text-brand-400',   bar: 'bg-brand-500',   Icon: AlertCircle  },
  blue:   { value: 'text-sky-400',     bar: 'bg-sky-500',     Icon: CreditCard   },
}

export default function StatCard({ label, value, sub, accent = 'green' }: Props) {
  const { value: textCls, bar, Icon } = accents[accent]
  return (
    <div className="card flex flex-col gap-1 hover:border-surface-muted hover:-translate-y-0.5 motion-reduce:hover:translate-y-0 transition-all duration-200">
      <div className={`absolute left-0 top-3 bottom-3 w-0.5 rounded-r-full ${bar}`} />
      <div className={`absolute top-4 right-4 ${textCls} opacity-20`}>
        <Icon size={20} aria-hidden="true" />
      </div>
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest">{label}</p>
      <p className={`font-display text-5xl leading-none ${textCls}`}>{value}</p>
      {sub && <p className="text-xs text-gray-600 mt-1.5 font-mono leading-relaxed">{sub}</p>}
    </div>
  )
}
