import { useEffect, useState } from 'react'
import Modal from './Modal'
import Spinner from './Spinner'
import { getNotificationHistory } from '../services/api'
import type { NotificationHistoryResponse, NotificationLogRead } from '../types'

const THRESHOLD_LABEL: Record<number, string> = { 7: '7d', 3: '3d', 1: '1d', 0: 'Hoy' }

function fmtDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString('es-CO', {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit',
    })
  } catch { return iso }
}

function LogRow({ item }: { item: NotificationLogRead }) {
  return (
    <tr className="border-b border-surface-border hover:bg-surface-raised/30 transition-colors">
      <td className="py-2.5 pr-3 text-sm text-gray-200 font-medium">{item.member_name ?? '—'}</td>
      <td className="py-2.5 pr-3 text-xs text-gray-500 font-mono">{item.plan_name ?? '—'}</td>
      <td className="py-2.5 pr-3 text-center">
        <span className="text-xs font-mono px-1.5 py-0.5 rounded bg-surface-raised text-gray-400">
          {THRESHOLD_LABEL[item.threshold_days] ?? `${item.threshold_days}d`}
        </span>
      </td>
      <td className="py-2.5 pr-3 text-center">
        <span className={`text-xs font-mono px-1.5 py-0.5 rounded border ${
          item.status === 'sent'
            ? 'bg-success-400/10 text-success-400 border-success-400/30'
            : 'bg-red-500/10 text-red-400 border-red-500/30'
        }`}>
          {item.status === 'sent' ? 'Enviado' : 'Fallido'}
        </span>
      </td>
      <td className="py-2.5 text-xs text-gray-600 font-mono">{fmtDate(item.sent_at)}</td>
    </tr>
  )
}

export default function NotificationHistoryModal({ onClose }: { onClose: () => void }) {
  const [data, setData] = useState<NotificationHistoryResponse | null>(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getNotificationHistory(page, 20)
      .then(setData)
      .finally(() => setLoading(false))
  }, [page])

  return (
    <Modal title="Historial de notificaciones" onClose={onClose}>
      <div className="min-w-[560px]">
        {loading ? (
          <Spinner />
        ) : !data || data.total === 0 ? (
          <p className="text-gray-500 text-sm font-mono text-center py-6">Sin notificaciones registradas.</p>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-gray-600 text-xs uppercase tracking-wider border-b border-surface-border">
                    <th className="text-left py-2 pr-3 font-semibold">Cliente</th>
                    <th className="text-left py-2 pr-3 font-semibold">Plan</th>
                    <th className="text-center py-2 pr-3 font-semibold">Umbral</th>
                    <th className="text-center py-2 pr-3 font-semibold">Estado</th>
                    <th className="text-left py-2 font-semibold">Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map(item => <LogRow key={item.id} item={item} />)}
                </tbody>
              </table>
            </div>

            {data.pages > 1 && (
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-surface-border">
                <span className="text-xs text-gray-600 font-mono">
                  {data.total} registros · página {data.page} de {data.pages}
                </span>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-3 py-1 text-xs font-mono border border-surface-border rounded hover:border-brand-500/50 disabled:opacity-40 text-gray-300 transition-colors"
                  >
                    ← Anterior
                  </button>
                  <button
                    onClick={() => setPage(p => Math.min(data.pages, p + 1))}
                    disabled={page === data.pages}
                    className="px-3 py-1 text-xs font-mono border border-surface-border rounded hover:border-brand-500/50 disabled:opacity-40 text-gray-300 transition-colors"
                  >
                    Siguiente →
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </Modal>
  )
}
