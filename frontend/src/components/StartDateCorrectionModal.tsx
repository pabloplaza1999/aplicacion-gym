import { useState } from 'react'
import Modal from './Modal'
import type { MembershipWithPlan, MembershipStartDateCorrectionCreate } from '../types'
import { correctMembershipStartDate } from '../services/api'
import { fmtBogotaDate } from '../utils/validators'

interface Props {
  membership: MembershipWithPlan
  onUpdated: () => void
  onClose: () => void
}

function todayBogota(): string {
  return new Date().toLocaleDateString('en-CA', { timeZone: 'America/Bogota' })
}

export default function StartDateCorrectionModal({ membership, onUpdated, onClose }: Props) {
  const [newDate, setNewDate] = useState('')
  const [reason, setReason]   = useState('')
  const [saving, setSaving]   = useState(false)
  const [err, setErr]         = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!newDate) { setErr('Selecciona una nueva fecha de inicio.'); return }
    if (reason.trim().length < 10) { setErr('El motivo debe tener al menos 10 caracteres.'); return }
    setSaving(true); setErr('')
    try {
      const payload: MembershipStartDateCorrectionCreate = {
        new_start_date: newDate,
        reason: reason.trim(),
      }
      await correctMembershipStartDate(membership.id, payload)
      onUpdated()
      onClose()
    } catch (e: any) {
      setErr(e.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title="Corregir fecha de inicio" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="bg-surface-raised rounded p-3 space-y-1">
          <p className="label">Fecha de inicio actual</p>
          <p className="text-sm text-gray-200 font-mono">{fmtBogotaDate(membership.start_date)}</p>
          <p className="text-xs text-gray-600 uppercase tracking-widest">{membership.plan_name}</p>
        </div>

        {err && (
          <div className="flex items-center gap-2 bg-brand-500/10 border border-brand-500/25 rounded px-3 py-2">
            <span className="w-1 h-4 bg-brand-500 rounded-full shrink-0" />
            <p className="text-brand-400 text-xs font-mono">{err}</p>
          </div>
        )}

        <div>
          <label className="label">Nueva fecha de inicio *</label>
          <input
            className="input"
            type="date"
            max={todayBogota()}
            value={newDate}
            onChange={e => setNewDate(e.target.value)}
          />
        </div>

        <div>
          <label className="label">Motivo de la corrección *</label>
          <textarea
            className="input resize-none"
            rows={3}
            placeholder="Describe el motivo (mínimo 10 caracteres)..."
            value={reason}
            onChange={e => setReason(e.target.value)}
          />
          <p className="text-xs text-gray-600 mt-1 font-mono">{reason.trim().length} / 10 mín.</p>
        </div>

        <div className="flex gap-2 pt-1">
          <button type="submit" disabled={saving} className="btn-primary flex-1">
            {saving ? 'Guardando...' : 'Confirmar corrección'}
          </button>
          <button type="button" onClick={onClose} className="btn-ghost">Cancelar</button>
        </div>
      </form>
    </Modal>
  )
}
