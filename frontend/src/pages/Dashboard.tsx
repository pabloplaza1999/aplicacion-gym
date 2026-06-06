import { useEffect, useState } from 'react'
import { getDashboard } from '../services/api'
import type { DashboardKPI } from '../types'
import StatCard from '../components/StatCard'
import Spinner from '../components/Spinner'

function fmt(n: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n)
}

export default function Dashboard() {
  const [kpi, setKpi] = useState<DashboardKPI | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getDashboard().then(setKpi).catch(e => setError(e.message)).finally(() => setLoading(false))
  }, [])

  if (loading) return <Spinner />
  if (error) return <div className="p-8 text-brand-400 text-sm font-mono">{error}</div>
  if (!kpi) return null

  const now = new Date()
  const monthName = now.toLocaleString('es-CO', { month: 'long', year: 'numeric' })

  return (
    <div className="p-8 space-y-8 animate-fade-up">
      <div className="flex items-end justify-between border-b border-surface-border pb-6">
        <div>
          <p className="text-xs font-semibold text-brand-500 uppercase tracking-[0.3em] mb-1">Panel de control</p>
          <h1 className="font-display text-4xl tracking-widest text-white uppercase">Dashboard</h1>
        </div>
        <p className="text-xs font-mono text-gray-600 capitalize pb-1">{monthName}</p>
      </div>

      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard label="Clientes activos"   value={kpi.total_active_members}  sub="cuentas habilitadas" accent="green" />
        <StatCard label="Membresías activas" value={kpi.memberships.active}     sub={`${kpi.memberships.expiring} por vencer · ${kpi.memberships.expired} vencidas`} accent="blue" />
        <StatCard label="Por vencer"         value={kpi.memberships.expiring}   sub="próximos 5 días" accent="yellow" />
        <StatCard label={`Ingresos ${now.toLocaleString('es-CO',{month:'short'})}`} value={fmt(kpi.monthly_revenue)} sub="mes actual" accent="green" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="card space-y-5">
          <div className="flex items-center gap-3">
            <div className="w-1 h-5 bg-brand-500 rounded-full shadow-brand-sm" />
            <h2 className="font-display text-lg tracking-widest text-white uppercase">Ingresos por plan</h2>
          </div>
          {kpi.revenue_by_plan.length === 0 ? (
            <p className="text-gray-600 text-sm font-mono">Sin pagos este mes</p>
          ) : (
            <div className="space-y-4">
              {kpi.revenue_by_plan.map(p => {
                const pct = kpi.monthly_revenue > 0 ? Math.round((p.total_amount / kpi.monthly_revenue) * 100) : 0
                return (
                  <div key={p.plan_id}>
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="text-gray-300 font-medium">{p.plan_name}</span>
                      <span className="text-brand-400 font-mono font-semibold">{fmt(p.total_amount)}</span>
                    </div>
                    <div className="h-1 bg-surface-raised rounded-full overflow-hidden">
                      <div className="h-full rounded-full transition-all duration-700"
                        style={{ width:`${pct}%`, background:'linear-gradient(90deg,#a01515,#E02020)' }} />
                    </div>
                    <p className="text-xs text-gray-600 font-mono mt-1">{p.count} pagos · {pct}%</p>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        <div className="card space-y-5">
          <div className="flex items-center gap-3">
            <div className="w-1 h-5 bg-brand-500 rounded-full shadow-brand-sm" />
            <h2 className="font-display text-lg tracking-widest text-white uppercase">Renovaciones recientes</h2>
          </div>
          {kpi.recent_renewals.length === 0 ? (
            <p className="text-gray-600 text-sm font-mono">Sin renovaciones</p>
          ) : (
            <div className="divide-y divide-surface-border">
              {kpi.recent_renewals.map((r, i) => (
                <div key={i} className="py-3 flex items-center justify-between group">
                  <div>
                    <p className="text-sm font-semibold text-white group-hover:text-brand-400 transition-colors">{r.member_name}</p>
                    <p className="text-xs text-gray-600 font-mono mt-0.5">{r.plan_name} · hasta {r.end_date}</p>
                  </div>
                  {r.amount_paid && <span className="text-brand-400 text-sm font-mono font-semibold">{fmt(r.amount_paid)}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
