import { useEffect, useState, useCallback } from 'react'
import { getAllPayments, deletePayment } from '../services/api'
import type { Payment, PaymentMethod } from '../types'
import Spinner from '../components/Spinner'
import Empty from '../components/Empty'

function fmt(n: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n)
}
const METHOD_LABELS: Record<PaymentMethod, string> = { cash:'Efectivo', transfer:'Transferencia', qr:'QR', nequi:'Nequi' }
const METHOD_STYLES: Record<PaymentMethod, string> = {
  cash:     'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
  transfer: 'bg-sky-500/10     text-sky-400     border border-sky-500/20',
  qr:       'bg-violet-500/10  text-violet-400  border border-violet-500/20',
  nequi:    'bg-pink-500/10    text-pink-400    border border-pink-500/20',
}

export default function Payments() {
  const [payments, setPayments]       = useState<Payment[]>([])
  const [total, setTotal]             = useState(0)
  const [totalAmount, setTotalAmount] = useState(0)
  const [page, setPage]               = useState(0)
  const [loading, setLoading]         = useState(true)
  const LIMIT = 20

  const load = useCallback(async (p = page) => {
    setLoading(true)
    try {
      const res = await getAllPayments(p * LIMIT, LIMIT)
      setPayments(res.items); setTotal(res.total); setTotalAmount(res.total_amount)
    } finally { setLoading(false) }
  }, [page])

  useEffect(() => { load() }, [page])

  async function handleDelete(id: number) {
    if (!confirm('¿Eliminar este pago?')) return
    try { await deletePayment(id); load(page) } catch (e: any) { console.error(e) }
  }

  const totalPages = Math.ceil(total / LIMIT)

  return (
    <div className="p-8 space-y-6 animate-fade-up">
      <div className="flex items-end justify-between border-b border-surface-border pb-6">
        <div>
          <p className="text-xs font-semibold text-brand-500 uppercase tracking-[0.3em] mb-1">Historial</p>
          <h1 className="font-display text-4xl tracking-widest text-white uppercase">Pagos</h1>
        </div>
        <div className="text-right pb-1">
          <p className="text-xs font-mono text-gray-600">{total} registros</p>
          <p className="text-brand-400 font-mono font-semibold">{fmt(totalAmount)}</p>
        </div>
      </div>

      <div className="card p-0 overflow-hidden">
        {loading ? <Spinner /> : payments.length === 0 ? <Empty /> : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border bg-surface-raised">
                {['#','Cliente','Método','Monto','Fecha',''].map((h,i) => (
                  <th key={i} className={`px-5 py-3 text-xs font-semibold text-gray-600 uppercase tracking-widest
                    ${i===3?'text-right':'text-left'} ${i===5?'w-10':''}`}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {payments.map((p, idx) => (
                <tr key={p.id}
                  className={`border-b border-surface-border/40 transition-colors group hover:bg-surface-raised
                    ${idx % 2 === 0 ? '' : 'bg-surface-card/50'}`}>
                  <td className="px-5 py-3.5 font-mono text-xs text-gray-700">#{p.id}</td>
                  <td className="px-5 py-3.5">
                    <p className="text-gray-200 font-medium">{p.member_name ?? `Cliente #${p.member_id}`}</p>
                    {p.membership_id && <p className="text-xs text-gray-700 font-mono mt-0.5">mem #{p.membership_id}</p>}
                  </td>
                  <td className="px-5 py-3.5">
                    <span className={`inline-flex px-2.5 py-0.5 rounded text-xs font-semibold uppercase tracking-wide ${METHOD_STYLES[p.payment_method as PaymentMethod]}`}>
                      {METHOD_LABELS[p.payment_method as PaymentMethod] ?? p.payment_method}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-right font-mono font-semibold text-brand-400">{fmt(p.amount)}</td>
                  <td className="px-5 py-3.5 font-mono text-xs text-gray-600">{p.payment_date.slice(0,10)}</td>
                  <td className="px-5 py-3.5">
                    <button onClick={() => handleDelete(p.id)}
                      className="opacity-0 group-hover:opacity-100 w-6 h-6 flex items-center justify-center rounded text-gray-600 hover:text-brand-400 hover:bg-brand-500/10 transition-all text-xs"
                      title="Eliminar">✕</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-xs font-mono text-gray-600">Página {page+1} / {totalPages}</p>
          <div className="flex gap-2">
            <button onClick={() => setPage(p => Math.max(0,p-1))} disabled={page===0} className="btn-ghost disabled:opacity-30 text-xs">← Anterior</button>
            <button onClick={() => setPage(p => Math.min(totalPages-1,p+1))} disabled={page>=totalPages-1} className="btn-ghost disabled:opacity-30 text-xs">Siguiente →</button>
          </div>
        </div>
      )}
    </div>
  )
}
