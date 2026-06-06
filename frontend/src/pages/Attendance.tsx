import { useState } from 'react'
import { checkInAttendance, getVoucherStatus } from '../services/api'
import type { CheckInResult, VoucherStatus } from '../types'
import StatCard from '../components/StatCard'
import Spinner from '../components/Spinner'

function fmtDate(iso: string) {
  return new Intl.DateTimeFormat('es-CO', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(iso))
}
function fmtDateTime(iso: string) {
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit',
  }).format(new Date(iso))
}

// Vista unificada de la valera, derivada de un check-in o de una consulta de estado.
interface VoucherView {
  member_name: string
  plan_name: string
  entries_total: number
  entries_used: number
  entries_remaining: number
  end_date: string
  attended_today?: boolean
}

// Estado derivado en cliente (el backend no devuelve un string de estado para la valera).
function voucherEstado(v: VoucherView): { label: string; accent: 'green' | 'yellow' | 'red'; cls: string } {
  const expired = new Date(v.end_date).getTime() < Date.now()
  if (expired)            return { label: 'Vencida', accent: 'red',    cls: 'badge-expired' }
  if (v.entries_remaining <= 0) return { label: 'Agotada', accent: 'yellow', cls: 'badge-expiring' }
  return { label: 'Vigente', accent: 'green', cls: 'badge-active' }
}

export default function Attendance() {
  const [document, setDocument] = useState('')
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState<string | null>(null)
  const [success, setSuccess]   = useState<string | null>(null)
  const [view, setView]         = useState<VoucherView | null>(null)

  function reset() {
    setError(null)
    setSuccess(null)
  }

  async function handleCheckIn(e?: React.FormEvent) {
    e?.preventDefault()
    if (!document.trim()) { setError('Debe ingresar la cédula del cliente'); return }
    reset(); setLoading(true)
    try {
      const r: CheckInResult = await checkInAttendance(document.trim())
      setView({
        member_name: r.member_name,
        plan_name: r.plan_name,
        entries_total: r.entries_total,
        entries_used: r.entries_used,
        entries_remaining: r.entries_remaining,
        end_date: r.end_date,
        attended_today: true,
      })
      setSuccess(
        `Ingreso registrado: ${r.member_name} · ${fmtDateTime(r.check_in_at)} · ` +
        `Quedan ${r.entries_remaining} de ${r.entries_total} ingresos` +
        (r.finished ? ' · Valera finalizada' : '')
      )
    } catch (err: any) {
      setView(null)
      setError(err.message || 'Error al registrar el ingreso')
    } finally {
      setLoading(false)
    }
  }

  async function handleStatus() {
    if (!document.trim()) { setError('Debe ingresar la cédula del cliente'); return }
    reset(); setLoading(true)
    try {
      const s: VoucherStatus = await getVoucherStatus(document.trim())
      setView({
        member_name: s.member_name,
        plan_name: s.plan_name,
        entries_total: s.entries_total,
        entries_used: s.entries_used,
        entries_remaining: s.entries_remaining,
        end_date: s.end_date,
        attended_today: s.attended_today,
      })
    } catch (err: any) {
      setView(null)
      setError(err.message || 'No se pudo consultar la valera')
    } finally {
      setLoading(false)
    }
  }

  const estado = view ? voucherEstado(view) : null

  return (
    <div className="p-8 space-y-6 animate-fade-up">
      <div className="flex items-end justify-between border-b border-surface-border pb-6">
        <div>
          <p className="text-xs font-semibold text-brand-500 uppercase tracking-[0.3em] mb-1">Valeras</p>
          <h1 className="font-display text-4xl tracking-widest text-white uppercase">Asistencia</h1>
        </div>
      </div>

      {/* Formulario de check-in por cédula */}
      <form onSubmit={handleCheckIn} className="card space-y-4">
        <label className="block">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-widest">Cédula del cliente</span>
          <input
            autoFocus
            value={document}
            onChange={(e) => setDocument(e.target.value)}
            placeholder="Ingrese la cédula"
            className="mt-2 w-full bg-surface-raised border border-surface-border rounded-md px-4 py-3
                       text-white font-mono text-lg tracking-wide focus:outline-none focus:border-brand-500
                       transition-colors"
          />
        </label>
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-brand-500 hover:bg-brand-400 disabled:opacity-50 text-white font-semibold
                       rounded-md px-4 py-3 transition-colors uppercase tracking-wide text-sm"
          >
            Registrar ingreso
          </button>
          <button
            type="button"
            onClick={handleStatus}
            disabled={loading}
            className="bg-surface-raised hover:bg-surface-muted disabled:opacity-50 text-gray-300 font-semibold
                       border border-surface-border rounded-md px-4 py-3 transition-colors uppercase tracking-wide text-sm"
          >
            Consultar valera
          </button>
        </div>
      </form>

      {loading && <Spinner />}

      {/* Mensaje de error de la API */}
      {error && !loading && (
        <div className="card border-red-500/40 bg-red-500/5 flex items-start gap-3">
          <span className="mt-0.5 w-2 h-2 rounded-full bg-red-500 shrink-0" />
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      {/* Mensaje de check-in exitoso */}
      {success && !loading && (
        <div className="card border-brand-500/40 bg-brand-500/5 flex items-start gap-3">
          <span className="mt-0.5 w-2 h-2 rounded-full bg-brand-500 shrink-0 animate-pulse" />
          <p className="text-brand-300 text-sm">{success}</p>
        </div>
      )}

      {/* Visualización de la valera (solo membresías tipo voucher) */}
      {view && estado && !loading && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-display text-2xl text-white">{view.member_name}</p>
              <p className="text-sm text-gray-500 font-mono">{view.plan_name}</p>
            </div>
            <span className={estado.cls}>
              <span className="w-1.5 h-1.5 rounded-full bg-current" />
              {estado.label}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <StatCard label="Ingresos totales" value={view.entries_total} accent="blue" />
            <StatCard label="Consumidos" value={view.entries_used} accent="yellow" />
            <StatCard
              label="Restantes"
              value={view.entries_remaining}
              accent={view.entries_remaining > 0 ? 'green' : 'red'}
            />
          </div>

          <div className="card flex flex-wrap gap-x-10 gap-y-3 text-sm">
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest">Vencimiento</p>
              <p className="text-gray-200 font-mono mt-1">{fmtDate(view.end_date)}</p>
            </div>
            {view.attended_today !== undefined && (
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest">Asistió hoy</p>
                <p className="text-gray-200 font-mono mt-1">{view.attended_today ? 'Sí' : 'No'}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
