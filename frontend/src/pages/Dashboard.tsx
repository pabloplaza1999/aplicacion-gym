import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getDashboard, getBackupStatus, getNotificationStatus, runNotificationsNow } from '../services/api'
import type { DashboardKPI, AlertsSummary, MembershipAlert, DebtorAlert, LowStockAlertItem, MembersByPlan, BackupStatus, NotificationStatusPanel } from '../types'
import StatCard from '../components/StatCard'
import Spinner from '../components/Spinner'
import BackupModal from '../components/BackupModal'
import NotificationHistoryModal from '../components/NotificationHistoryModal'
import { fmtBogotaDate } from '../utils/validators'

function fmt(n: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n)
}

// ── Members by plan table ──────────────────────────────────────────────────────

function MembersByPlanTable({ rows }: { rows: MembersByPlan[] }) {
  if (rows.length === 0) return null
  return (
    <div className="card space-y-4">
      <div className="flex items-center gap-3">
        <div className="w-1 h-5 bg-brand-500 rounded-full shadow-brand-sm" />
        <h2 className="font-display text-lg tracking-widest text-white uppercase">Membresías por plan</h2>
        <span className="text-xs font-mono text-gray-600 ml-1">un cliente puede aparecer en varios planes</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm font-mono">
          <thead>
            <tr className="text-gray-600 text-xs uppercase tracking-wider border-b border-surface-border">
              <th className="text-left py-2 pr-4 font-semibold">Plan</th>
              <th className="text-right py-2 px-3 font-semibold">Activos</th>
              <th className="text-right py-2 px-3 font-semibold">Agotados</th>
              <th className="text-right py-2 px-3 font-semibold">Vencidos</th>
              <th className="text-right py-2 px-3 font-semibold">Congelados</th>
              <th className="text-right py-2 pl-3 font-semibold">Total</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border">
            {rows.map(p => (
              <tr key={p.plan_id} className="hover:bg-surface-raised/30 transition-colors duration-100">
                <td className="py-3 pr-4 text-gray-200 font-medium">{p.plan_name}</td>
                <td className="text-right py-3 px-3">
                  <span className={p.active_count > 0 ? 'text-success-400 font-semibold' : 'text-gray-600'}>
                    {p.active_count > 0 ? p.active_count : '—'}
                  </span>
                </td>
                <td className="text-right py-3 px-3">
                  {p.plan_type === 'voucher' ? (
                    <span className={p.exhausted_count > 0 ? 'text-energy-400 font-semibold' : 'text-gray-600'}>
                      {p.exhausted_count > 0 ? p.exhausted_count : '0'}
                    </span>
                  ) : (
                    <span className="text-gray-700">—</span>
                  )}
                </td>
                <td className="text-right py-3 px-3">
                  <span className={p.expired_count > 0 ? 'text-red-400 font-semibold' : 'text-gray-600'}>
                    {p.expired_count > 0 ? p.expired_count : '—'}
                  </span>
                </td>
                <td className="text-right py-3 px-3">
                  <span className={p.frozen_count > 0 ? 'text-blue-400 font-semibold' : 'text-gray-600'}>
                    {p.frozen_count > 0 ? p.frozen_count : '—'}
                  </span>
                </td>
                <td className="text-right py-3 pl-3 text-white font-bold">{p.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// ── Alerts panel ──────────────────────────────────────────────────────────────

type AlertTab = 'expired' | 'today' | 'three_days' | 'seven_days' | 'cartera' | 'low_stock'
type OverdueFilter = 'all' | '1-7' | '8-30' | '30+'

const TAB_CONFIG: { key: AlertTab; label: string; color: string; chipColor: string }[] = [
  { key: 'expired',    label: 'Vencidas',    color: 'text-red-400',     chipColor: 'bg-red-500/15 text-red-400 border-red-500/30' },
  { key: 'today',      label: 'Hoy',         color: 'text-orange-400',  chipColor: 'bg-orange-500/15 text-orange-400 border-orange-500/30' },
  { key: 'three_days', label: '3 días',      color: 'text-yellow-400',  chipColor: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30' },
  { key: 'seven_days', label: '7 días',      color: 'text-blue-400',    chipColor: 'bg-blue-500/15 text-blue-400 border-blue-500/30' },
  { key: 'cartera',    label: 'Cartera',     color: 'text-amber-400',   chipColor: 'bg-amber-500/15 text-amber-400 border-amber-500/30' },
  { key: 'low_stock',  label: 'Bajo stock',  color: 'text-emerald-400', chipColor: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' },
]

const OVERDUE_FILTERS: { key: OverdueFilter; label: string }[] = [
  { key: 'all',  label: 'Todos' },
  { key: '1-7',  label: '1 – 7 días' },
  { key: '8-30', label: '8 – 30 días' },
  { key: '30+',  label: '+ 30 días' },
]

function matchesOverdue(item: MembershipAlert, filter: OverdueFilter): boolean {
  const d = item.days_overdue ?? 0
  if (filter === 'all')  return true
  if (filter === '1-7')  return d >= 1 && d <= 7
  if (filter === '8-30') return d >= 8 && d <= 30
  if (filter === '30+')  return d > 30
  return true
}

function countFor(alerts: AlertsSummary, key: AlertTab): number {
  if (key === 'cartera')   return alerts.debtors_count   ?? 0
  if (key === 'low_stock') return alerts.low_stock_count ?? 0
  return alerts[`${key}_count` as keyof AlertsSummary] as number
}

function membershipItems(alerts: AlertsSummary, key: AlertTab): MembershipAlert[] {
  return alerts[`${key}_items` as keyof AlertsSummary] as MembershipAlert[]
}

function defaultTab(alerts: AlertsSummary): AlertTab {
  for (const t of TAB_CONFIG) {
    if (countFor(alerts, t.key) > 0) return t.key
  }
  return 'expired'
}

function AlertsPanel({ alerts }: { alerts: AlertsSummary }) {
  const [activeTab, setActiveTab] = useState<AlertTab>(() => defaultTab(alerts))
  const [query, setQuery] = useState('')
  const [overdueFilter, setOverdueFilter] = useState<OverdueFilter>('all')

  const total = TAB_CONFIG.reduce((s, t) => s + countFor(alerts, t.key), 0)
  const cfg = TAB_CONFIG.find(t => t.key === activeTab)!

  const isMembership = ['expired', 'today', 'three_days', 'seven_days'].includes(activeTab)
  const isExpiredTab = activeTab === 'expired'

  const rawMemberItems = isMembership ? membershipItems(alerts, activeTab) : []
  const memberItems = rawMemberItems.filter(item => {
    const q = query.trim().toLowerCase()
    const matchesQuery = !q || item.member_name.toLowerCase().includes(q) || (item.document ?? '').toLowerCase().includes(q)
    const matchesFilter = isExpiredTab ? matchesOverdue(item, overdueFilter) : true
    return matchesQuery && matchesFilter
  })

  const debtorItems  = activeTab === 'cartera'    ? (alerts.top_debtors    ?? []) : []
  const stockItems   = activeTab === 'low_stock'  ? (alerts.low_stock_items ?? []) : []

  return (
    <div className="card space-y-4">
      <div className="flex items-center gap-3">
        <div className="w-1 h-5 bg-brand-500 rounded-full shadow-brand-sm" />
        <h2 className="font-display text-lg tracking-widest text-white uppercase">Alertas operativas</h2>
        <span className="text-xs font-mono text-gray-600">{total} total</span>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2">
        {TAB_CONFIG.map(t => {
          const count = countFor(alerts, t.key)
          const active = activeTab === t.key
          return (
            <button
              key={t.key}
              onClick={() => { setActiveTab(t.key); setQuery(''); setOverdueFilter('all') }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-mono border transition-all
                ${active ? `${t.chipColor} border` : 'border-surface-border text-gray-600 hover:text-gray-400 hover:border-gray-600'}`}
            >
              {t.label}
              {count > 0 && <span className={`font-bold ${active ? '' : t.color}`}>{count}</span>}
            </button>
          )
        })}
      </div>

      {/* Search */}
      {isMembership && (
        <div className="flex flex-wrap items-center gap-3">
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Buscar por nombre o cédula…"
            className="flex-1 min-w-[180px] bg-surface-raised border border-surface-border rounded px-3 py-1.5 text-xs text-white font-mono placeholder-gray-600 focus:outline-none focus:border-brand-500"
          />
          {isExpiredTab && (
            <div className="flex gap-1">
              {OVERDUE_FILTERS.map(f => (
                <button
                  key={f.key}
                  onClick={() => setOverdueFilter(f.key)}
                  className={`px-2.5 py-1 rounded text-xs font-mono border transition-all
                    ${overdueFilter === f.key
                      ? 'bg-brand-500/15 text-brand-400 border-brand-500/30'
                      : 'border-surface-border text-gray-600 hover:text-gray-400'}`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Content */}
      {isMembership && (
        memberItems.length === 0
          ? <p className="text-gray-600 text-xs font-mono py-2">Sin resultados.</p>
          : <div className="divide-y divide-surface-border">
              {memberItems.map((item, i) => (
                <div key={i} className="py-3 flex items-center justify-between group hover:bg-surface-raised/40 hover:px-2 hover:-mx-2 rounded transition-all duration-150 cursor-default">
                  <div>
                    <p className="text-sm font-semibold text-white group-hover:text-brand-400 transition-colors">{item.member_name}</p>
                    <p className="text-xs text-gray-600 font-mono mt-0.5">
                      {item.plan_name}
                      {item.document && <> · {item.document}</>}
                      {isExpiredTab && item.days_overdue != null && item.days_overdue > 0 && (
                        <span className="text-red-400"> · {item.days_overdue}d vencida</span>
                      )}
                    </p>
                  </div>
                  <span className={`text-xs font-mono shrink-0 ml-4 ${cfg.color}`}>{fmtBogotaDate(item.end_date)}</span>
                </div>
              ))}
            </div>
      )}

      {activeTab === 'cartera' && (
        debtorItems.length === 0
          ? <p className="text-gray-600 text-xs font-mono py-2">Sin deudores.</p>
          : <div className="divide-y divide-surface-border">
              {debtorItems.map((d: DebtorAlert, i) => (
                <div key={i} className="py-3 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-white">{d.customer_name}</p>
                    <p className="text-xs text-gray-600 font-mono mt-0.5">
                      {d.days_overdue > 0 && <>{d.days_overdue}d · </>}
                      {d.oldest_sale_date}
                    </p>
                  </div>
                  <span className="text-amber-400 text-sm font-mono font-semibold ml-4">{fmt(d.outstanding_balance)}</span>
                </div>
              ))}
            </div>
      )}

      {activeTab === 'low_stock' && (
        stockItems.length === 0
          ? <p className="text-gray-600 text-xs font-mono py-2">Sin productos bajo stock.</p>
          : <div className="divide-y divide-surface-border">
              {stockItems.map((item: LowStockAlertItem, i) => (
                <div key={i} className="py-3 flex items-center justify-between group hover:bg-surface-raised/40 hover:px-2 hover:-mx-2 rounded transition-all duration-150 cursor-default">
                  <div>
                    <p className="text-sm font-semibold text-emerald-400">{item.product_name}</p>
                    <p className="text-xs text-gray-600 font-mono mt-0.5">mínimo {item.min_stock} uds</p>
                  </div>
                  <span className="text-xs font-mono text-gray-400 shrink-0 ml-4">
                    {item.stock} / {item.min_stock}
                  </span>
                </div>
              ))}
            </div>
      )}
    </div>
  )
}

// ── Main Dashboard ─────────────────────────────────────────────────────────────

export default function Dashboard() {
  const [kpi, setKpi] = useState<DashboardKPI | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [backupStatus, setBackupStatus] = useState<BackupStatus | null>(null)
  const [showBackupModal, setShowBackupModal] = useState(false)
  const [notifStatus, setNotifStatus] = useState<NotificationStatusPanel | null>(null)
  const [showNotifModal, setShowNotifModal] = useState(false)
  const [runningNotif, setRunningNotif] = useState(false)
  const [runResult, setRunResult] = useState<string | null>(null)

  useEffect(() => {
    Promise.allSettled([
      getDashboard(),
      getBackupStatus(),
      getNotificationStatus(),
    ]).then(([kpiRes, backupRes, notifRes]) => {
      if (kpiRes.status === 'fulfilled') setKpi(kpiRes.value)
      else setError((kpiRes.reason as Error).message)
      if (backupRes.status === 'fulfilled') setBackupStatus(backupRes.value)
      if (notifRes.status === 'fulfilled') setNotifStatus(notifRes.value)
    }).finally(() => setLoading(false))
  }, [])

  async function handleRunNotif() {
    setRunningNotif(true)
    setRunResult(null)
    try {
      const res = await runNotificationsNow()
      setRunResult(res.message)
      const updated = await getNotificationStatus()
      setNotifStatus(updated)
    } catch (e: any) {
      setRunResult(e.message || 'Error al ejecutar.')
    } finally {
      setRunningNotif(false)
    }
  }

  if (loading) return <Spinner />
  if (error) return <div className="p-8 text-brand-400 text-sm font-mono">{error}</div>
  if (!kpi) return null

  const now = new Date()
  const monthName = now.toLocaleString('es-CO', { month: 'long', year: 'numeric' })
  const monthShort = now.toLocaleString('es-CO', { month: 'short' })
  const hasStoreKpis = kpi.store_revenue != null

  return (
    <div className="p-8 space-y-8 animate-fade-up">
      <div className="flex items-end justify-between border-b border-surface-border pb-6">
        <div>
          <p className="text-xs font-semibold text-brand-500 uppercase tracking-[0.3em] mb-1">Panel de control</p>
          <h1 className="font-display text-4xl tracking-widest text-white uppercase">Dashboard</h1>
        </div>
        <p className="text-xs font-mono text-gray-600 capitalize pb-1">{monthName}</p>
      </div>

      {/* Membresías */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard label="Clientes activos"   value={kpi.total_active_members}  sub="cuentas habilitadas" accent="green" />
        <StatCard label="Membresías activas" value={kpi.memberships.active}     sub={`${kpi.memberships.expiring} por vencer · ${kpi.memberships.expired} vencidas`} accent="blue" />
        <StatCard label="Por vencer"         value={kpi.memberships.expiring}   sub="próximos 5 días" accent="yellow" />
        <StatCard label="Congeladas"         value={kpi.memberships.frozen}     sub="pausadas temporalmente" accent="blue" />
        <StatCard label="Valeras agotadas"   value={kpi.memberships.exhausted}  sub="sin ingresos restantes" accent="yellow" />
        <StatCard label={`Ingresos membresías ${monthShort}`} value={fmt(kpi.monthly_revenue)} sub="mes actual" accent="green" />
      </div>

      {/* Distribución por plan */}
      {kpi.members_by_plan && kpi.members_by_plan.length > 0 && (
        <MembersByPlanTable rows={kpi.members_by_plan} />
      )}

      {/* Ingresos consolidados del mes */}
      {hasStoreKpis && (
        <>
          <div>
            <p className="text-xs font-semibold text-brand-500 uppercase tracking-[0.3em] mb-4">Ingresos del mes</p>
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
              <StatCard label="Membresías"     value={fmt(kpi.membership_revenue!)} sub="pagos recibidos" accent="green" />
              <StatCard label="Tienda"         value={fmt(kpi.store_revenue!)}      sub="contado + abonos cobrados" accent="blue" />
              <StatCard label="Total ingresos" value={fmt(kpi.total_revenue!)}      sub="membresías + tienda" accent="green" />
            </div>
          </div>

          <div>
            <p className="text-xs font-semibold text-brand-500 uppercase tracking-[0.3em] mb-4">Tienda</p>
            <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
              <StatCard label={`Ventas ${monthShort}`}   value={kpi.store_sales_count!}       sub="transacciones no canceladas" accent="blue" />
              <StatCard label="Cartera pendiente" value={fmt(kpi.cartera_balance!)} sub="saldo por cobrar" accent="yellow" />
            </div>
          </div>
        </>
      )}

      {kpi.alerts && <AlertsPanel alerts={kpi.alerts} />}

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
                    <div className="h-2 bg-surface-raised rounded-full overflow-hidden">
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
                <div key={i} className="py-3.5 flex items-center justify-between group hover:bg-surface-raised/40 hover:px-2 hover:-mx-2 rounded transition-all duration-150 cursor-default">
                  <div>
                    <p className="text-sm font-semibold text-white group-hover:text-brand-400 transition-colors">{r.member_name}</p>
                    <p className="text-xs text-gray-600 font-mono mt-0.5">{r.plan_name} · hasta {fmtBogotaDate(r.end_date)}</p>
                  </div>
                  {r.amount_paid && <span className="text-brand-400 text-sm font-mono font-semibold">{fmt(r.amount_paid)}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Respaldos */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-1 h-5 bg-brand-500 rounded-full shadow-brand-sm" />
            <h2 className="font-display text-lg tracking-widest text-white uppercase">Respaldos</h2>
            {backupStatus && (
              <span className={`w-2 h-2 rounded-full ${
                backupStatus.indicator === 'green'  ? 'bg-success-400' :
                backupStatus.indicator === 'orange' ? 'bg-energy-400' : 'bg-red-500'
              }`} />
            )}
          </div>
          <button
            onClick={() => setShowBackupModal(true)}
            className="text-xs text-brand-400 hover:text-brand-300 font-mono underline underline-offset-2 transition-colors"
          >
            Ver respaldos
          </button>
        </div>
        <p className="text-sm text-gray-500 font-mono mt-3">
          {backupStatus?.last_backup
            ? <>Último respaldo: <span className="text-gray-300">{backupStatus.last_backup.filename}</span> · hace {backupStatus.hours_ago}h</>
            : backupStatus
              ? <span className="text-red-400">Sin respaldos registrados</span>
              : <span className="text-gray-600">Cargando estado del respaldo...</span>
          }
        </p>
      </div>

      {/* Notificaciones */}
      <div className="card space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-1 h-5 bg-brand-500 rounded-full shadow-brand-sm" />
            <h2 className="font-display text-lg tracking-widest text-white uppercase">Notificaciones</h2>
            {notifStatus && (
              <span className={`w-2 h-2 rounded-full ${
                !notifStatus.is_configured ? 'bg-red-500' :
                !notifStatus.enabled       ? 'bg-gray-500' : 'bg-success-400'
              }`} />
            )}
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={handleRunNotif}
              disabled={runningNotif}
              className="text-xs text-brand-400 hover:text-brand-300 font-mono underline underline-offset-2 transition-colors disabled:opacity-40"
            >
              {runningNotif ? 'Ejecutando...' : 'Ejecutar ahora'}
            </button>
            <button
              onClick={() => setShowNotifModal(true)}
              className="text-xs text-brand-400 hover:text-brand-300 font-mono underline underline-offset-2 transition-colors"
            >
              Ver historial
            </button>
            <Link
              to="/configuracion"
              className="text-xs text-gray-500 hover:text-gray-300 font-mono underline underline-offset-2 transition-colors"
            >
              Configurar
            </Link>
          </div>
        </div>

        {notifStatus && !notifStatus.is_configured && (
          <p className="text-xs text-energy-400 font-mono">
            ⚠ SMTP no configurado — las notificaciones están desactivadas.
            <Link to="/configuracion" className="ml-2 text-brand-400 hover:text-brand-300 underline underline-offset-2">Configurar ahora</Link>
          </p>
        )}

        {notifStatus && notifStatus.is_configured && (
          <div className="grid grid-cols-3 gap-4 pt-1">
            <div>
              <p className="text-xs text-gray-600 font-mono">Enviados hoy</p>
              <p className={`text-xl font-bold font-mono ${notifStatus.sent_today > 0 ? 'text-success-400' : 'text-gray-600'}`}>
                {notifStatus.sent_today}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-600 font-mono">Fallidos hoy</p>
              <p className={`text-xl font-bold font-mono ${notifStatus.failed_today > 0 ? 'text-red-400' : 'text-gray-600'}`}>
                {notifStatus.failed_today}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-600 font-mono">Sin email</p>
              <p className={`text-xl font-bold font-mono ${notifStatus.pending_count > 0 ? 'text-energy-400' : 'text-gray-600'}`}>
                {notifStatus.pending_count}
              </p>
            </div>
          </div>
        )}

        {notifStatus?.last_run_at && (
          <p className="text-xs text-gray-600 font-mono">
            Último envío: <span className="text-gray-400">
              {new Date(notifStatus.last_run_at).toLocaleString('es-CO')}
            </span>
          </p>
        )}

        {runResult && (
          <p className="text-xs text-gray-400 font-mono border-t border-surface-border pt-2">{runResult}</p>
        )}
      </div>

      {showBackupModal && <BackupModal onClose={() => setShowBackupModal(false)} />}
      {showNotifModal  && <NotificationHistoryModal onClose={() => setShowNotifModal(false)} />}
    </div>
  )
}
