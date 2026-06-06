import { useEffect, useState, useCallback } from 'react'
import {
  getMembers, createMember, updateMember, deleteMember,
  getCurrentMembership, getMemberPayments, createMembership,
  renewMembership, setMembershipActive, getPlans, createPayment, deletePayment,
} from '../services/api'
import type { Member, MemberCreate, MembershipWithPlan, Plan, Payment, PaymentMethod } from '../types'
import Modal from '../components/Modal'
import Badge from '../components/Badge'
import Spinner from '../components/Spinner'
import Empty from '../components/Empty'
import MemberInfo from '../components/MemberInfo'

function fmt(n: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n)
}
const onlyLetters = (v: string) => /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]*$/.test(v)
const onlyDigits  = (v: string) => /^\d*$/.test(v)

// ── MemberForm ────────────────────────────────────────────────────────────────
function MemberForm({ initial, onSave, onCancel }: {
  initial?: Partial<MemberCreate>; onSave: (d: MemberCreate) => Promise<void>; onCancel: () => void
}) {
  const [form, setForm] = useState<MemberCreate>({
    full_name: initial?.full_name ?? '', phone: initial?.phone ?? '',
    document: initial?.document ?? '', notes: initial?.notes ?? '',
  })
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.full_name.trim()) { setErr('El nombre completo es requerido'); return }
    if (!form.phone.trim()) { setErr('El teléfono es requerido'); return }
    if (/\d/.test(form.full_name)) { setErr('El nombre no debe contener números'); return }
    if (!/^\d+$/.test(form.phone)) { setErr('El teléfono debe contener solo números'); return }
    if (form.document && !/^\d+$/.test(form.document)) { setErr('El documento debe contener solo números'); return }
    setSaving(true); setErr('')
    try { await onSave(form) } catch (e: any) { setErr(e.message) } finally { setSaving(false) }
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      {err && (
        <div className="flex items-center gap-2 bg-brand-500/10 border border-brand-500/25 rounded px-3 py-2">
          <span className="w-1 h-4 bg-brand-500 rounded-full shrink-0" />
          <p className="text-brand-400 text-xs font-mono">{err}</p>
        </div>
      )}
      <div>
        <label className="label">Nombre completo *</label>
        <input className="input" value={form.full_name} placeholder="Ej: Ana García"
          onChange={e => onlyLetters(e.target.value) && setForm(f => ({ ...f, full_name: e.target.value }))} />
      </div>
      <div>
        <label className="label">Teléfono *</label>
        <input className="input" value={form.phone} placeholder="3001234567"
          onChange={e => onlyDigits(e.target.value) && setForm(f => ({ ...f, phone: e.target.value }))} />
      </div>
      <div>
        <label className="label">Documento</label>
        <input className="input" value={form.document} placeholder="CC / TI"
          onChange={e => onlyDigits(e.target.value) && setForm(f => ({ ...f, document: e.target.value }))} />
      </div>
      <div>
        <label className="label">Notas</label>
        <textarea className="input resize-none" rows={2} value={form.notes} placeholder="Observaciones..."
          onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} />
      </div>
      <div className="flex gap-2 pt-2">
        <button type="submit" disabled={saving} className="btn-primary flex-1">
          {saving ? 'Guardando...' : 'Guardar'}
        </button>
        <button type="button" onClick={onCancel} className="btn-ghost">Cancelar</button>
      </div>
    </form>
  )
}

// ── MemberDetail ──────────────────────────────────────────────────────────────
function MemberDetail({ member, plans, onClose, onUpdated }: {
  member: Member; plans: Plan[]; onClose: () => void; onUpdated: () => void
}) {
  const [membership, setMembership]       = useState<MembershipWithPlan | null>(null)
  const [payments, setPayments]           = useState<Payment[]>([])
  const [loadingDetail, setLoadingDetail] = useState(true)
  const [tab, setTab]                     = useState<'info' | 'membership' | 'payments'>('info')
  const [selectedPlan, setSelectedPlan]   = useState<number>(0)
  const [showPayment, setShowPayment]     = useState(false)
  const [payAmount, setPayAmount]         = useState('')
  const [payMethod, setPayMethod]         = useState<PaymentMethod>('cash')
  const [saving, setSaving]               = useState(false)
  const [err, setErr]                     = useState('')

  const load = useCallback(async () => {
    setLoadingDetail(true)
    const [m, p] = await Promise.all([getCurrentMembership(member.id), getMemberPayments(member.id)])
    setMembership(m); setPayments(p.items); setLoadingDetail(false)
  }, [member.id])

  useEffect(() => { load() }, [load])
  useEffect(() => { if (plans.length > 0 && selectedPlan === 0) setSelectedPlan(plans[0].id) }, [plans, selectedPlan])

  async function handleNewMembership() {
    setSaving(true); setErr('')
    try { await createMembership(member.id, { member_id: member.id, plan_id: selectedPlan }); await load(); onUpdated() }
    catch (e: any) { setErr(e.message) } finally { setSaving(false) }
  }
  async function handleRenew() {
    if (!membership) return
    setSaving(true); setErr('')
    try { await renewMembership(membership.id, selectedPlan); await load(); onUpdated() }
    catch (e: any) { setErr(e.message) } finally { setSaving(false) }
  }
  async function handleToggleMembership() {
    if (!membership) return
    setSaving(true); setErr('')
    try { await setMembershipActive(membership.id, !membership.is_active); await load(); onUpdated() }
    catch (e: any) { setErr(e.message) } finally { setSaving(false) }
  }
  async function handlePayment() {
    const amount = parseFloat(payAmount)
    if (!amount || amount <= 0) { setErr('Monto inválido'); return }
    setSaving(true); setErr('')
    try {
      await createPayment(member.id, { member_id: member.id, membership_id: membership?.id, amount, payment_method: payMethod })
      await load(); setShowPayment(false); setPayAmount('')
    } catch (e: any) { setErr(e.message) } finally { setSaving(false) }
  }

  const METHODS: PaymentMethod[] = ['cash', 'transfer', 'qr', 'nequi']
  const METHOD_LABELS: Record<PaymentMethod, string> = { cash: 'Efectivo', transfer: 'Transferencia', qr: 'QR', nequi: 'Nequi' }

  return (
    <div className="h-full flex flex-col">
      {/* Tabs */}
      <div className="flex border-b border-surface-border mb-5">
        {(['info', 'membership', 'payments'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`flex-1 py-2.5 text-xs font-semibold uppercase tracking-widest transition-all border-b-2 -mb-px
              ${tab === t ? 'border-brand-500 text-white' : 'border-transparent text-gray-600 hover:text-gray-300'}`}>
            {{ info: 'Info', membership: 'Membresía', payments: 'Pagos' }[t]}
          </button>
        ))}
      </div>

      {err && (
        <div className="flex items-center gap-2 bg-brand-500/10 border border-brand-500/25 rounded px-3 py-2 mb-4">
          <span className="w-1 h-4 bg-brand-500 rounded-full shrink-0" />
          <p className="text-brand-400 text-xs font-mono">{err}</p>
        </div>
      )}

      {loadingDetail ? <Spinner /> : (
        <>
          {tab === 'info' && <MemberInfo member={member} onUpdated={() => onUpdated()} />}

          {tab === 'membership' && (
            <div className="space-y-4">
              {membership ? (
                <div className="card space-y-3">
                  <div className="flex items-center justify-between">
                    <p className="font-display text-lg tracking-wider text-white uppercase">{membership.plan_name}</p>
                    <Badge status={membership.status} />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { label: 'Inicio',  value: membership.start_date.slice(0,10) },
                      { label: 'Vence',   value: membership.end_date.slice(0,10) },
                      { label: 'Días restantes', value: <span className="text-brand-400 font-mono font-bold">{membership.days_remaining}</span> },
                      { label: 'Precio',  value: <span className="font-mono">{fmt(membership.plan_price)}</span> },
                    ].map(({ label, value }) => (
                      <div key={label} className="bg-surface-raised rounded p-2.5">
                        <p className="label mb-1">{label}</p>
                        <p className="text-sm text-gray-200">{value}</p>
                      </div>
                    ))}
                  </div>
                  <button onClick={handleToggleMembership} disabled={saving}
                    className={`btn-ghost w-full text-xs uppercase tracking-widest ${
                      membership.is_active ? 'text-yellow-500 hover:text-yellow-400' : 'text-brand-400 hover:text-brand-300'}`}>
                    {saving ? 'Procesando...' : membership.is_active ? 'Desactivar membresía' : 'Activar membresía'}
                  </button>
                </div>
              ) : (
                <div className="bg-surface-raised border border-surface-border rounded p-4">
                  <p className="text-gray-600 text-sm font-mono">Sin membresía activa</p>
                </div>
              )}
              <div>
                <label className="label">Seleccionar plan</label>
                <select className="input" value={selectedPlan} onChange={e => setSelectedPlan(Number(e.target.value))}>
                  {plans.map(p => <option key={p.id} value={p.id}>{p.name} — {fmt(p.price)}</option>)}
                </select>
              </div>
              {membership ? (
                <button onClick={handleRenew} disabled={saving} className="btn-primary w-full">
                  {saving ? 'Procesando...' : 'Renovar membresía'}
                </button>
              ) : (
                <button onClick={handleNewMembership} disabled={saving} className="btn-primary w-full">
                  {saving ? 'Procesando...' : 'Crear membresía'}
                </button>
              )}
            </div>
          )}

          {tab === 'payments' && (
            <div className="space-y-4">
              {showPayment ? (
                <div className="card space-y-4">
                  <p className="font-display text-base tracking-widest text-white uppercase">Registrar pago</p>
                  <div>
                    <label className="label">Monto (COP)</label>
                    <input className="input font-mono" type="number" value={payAmount}
                      onChange={e => setPayAmount(e.target.value)} placeholder="60000" />
                  </div>
                  <div>
                    <label className="label">Método de pago</label>
                    <div className="grid grid-cols-2 gap-2">
                      {METHODS.map(m => (
                        <button key={m} onClick={() => setPayMethod(m)}
                          className={`py-2.5 rounded text-xs font-semibold uppercase tracking-wider border transition-all
                            ${payMethod === m
                              ? 'bg-brand-500/15 border-brand-500/40 text-brand-400 shadow-brand-sm'
                              : 'border-surface-border text-gray-600 hover:text-gray-300 hover:border-surface-muted'}`}>
                          {METHOD_LABELS[m]}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={handlePayment} disabled={saving} className="btn-primary flex-1">
                      {saving ? 'Guardando...' : 'Confirmar pago'}
                    </button>
                    <button onClick={() => setShowPayment(false)} className="btn-ghost">Cancelar</button>
                  </div>
                </div>
              ) : (
                <button onClick={() => setShowPayment(true)} className="btn-primary w-full">+ Registrar pago</button>
              )}

              {payments.length === 0 ? <Empty message="Sin pagos registrados" /> : (
                <div className="divide-y divide-surface-border">
                  {payments.map(p => (
                    <div key={p.id} className="py-3 flex items-center justify-between group">
                      <div>
                        <p className="text-sm text-white font-mono font-semibold">{fmt(p.amount)}</p>
                        <p className="text-xs text-gray-600 mt-0.5 uppercase tracking-wide">
                          {METHOD_LABELS[p.payment_method as PaymentMethod]} · {p.payment_date.slice(0,10)}
                        </p>
                      </div>
                      <button
                        onClick={() => confirm('¿Eliminar este pago?') && deletePayment(p.id).then(() => load()).catch(e => setErr(e.message))}
                        className="opacity-0 group-hover:opacity-100 w-7 h-7 flex items-center justify-center rounded text-gray-600 hover:text-brand-400 hover:bg-brand-500/10 transition-all text-xs"
                        title="Eliminar pago">✕
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}

      <div className="mt-auto pt-4 border-t border-surface-border">
        <button onClick={onClose} className="btn-ghost w-full text-xs uppercase tracking-widest">Cerrar panel</button>
      </div>
    </div>
  )
}

// ── Members Page ──────────────────────────────────────────────────────────────
export default function Members() {
  const [members, setMembers]       = useState<Member[]>([])
  const [total, setTotal]           = useState(0)
  const [plans, setPlans]           = useState<Plan[]>([])
  const [search, setSearch]         = useState('')
  const [loading, setLoading]       = useState(true)
  const [selected, setSelected]     = useState<Member | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [editMember, setEditMember] = useState<Member | null>(null)

  const load = useCallback(async (q = search) => {
    setLoading(true)
    const res = await getMembers(0, 50, q)
    setMembers(res.items); setTotal(res.total); setLoading(false)
  }, [search])

  useEffect(() => { load(); getPlans().then(setPlans).catch(() => {}) }, [])
  useEffect(() => { const t = setTimeout(() => load(search), 300); return () => clearTimeout(t) }, [search])

  async function handleCreate(data: MemberCreate) {
    await createMember(data); setShowCreate(false); load()
  }
  async function handleUpdate(data: MemberCreate) {
    if (!editMember) return
    await updateMember(editMember.id, data); setEditMember(null); load()
  }

  // ── Activar / Desactivar (soft toggle) ────────────────────────────────────
  async function handleToggleActive(m: Member) {
    const action = m.is_active ? 'desactivar' : 'activar'
    if (!confirm(`¿Desea ${action} a ${m.full_name}?`)) return
    try {
      const updated = await updateMember(m.id, { is_active: !m.is_active } as any)
      setSelected(updated)
      load()
    } catch (e: any) { alert(e.message) }
  }

  // ── Eliminar permanente ───────────────────────────────────────────────────
  async function handleHardDelete(m: Member) {
    if (!confirm(`¿Eliminar PERMANENTEMENTE a ${m.full_name}? Esta acción no se puede deshacer y borrará todo su historial (pagos, membresías y medidas).`)) return
    try {
      await deleteMember(m.id, true)
      setSelected(null)
      load()
    } catch (e: any) { alert(e.message) }
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* List panel */}
      <div className={`flex flex-col border-r border-surface-border transition-all duration-300 ${selected ? 'w-80' : 'flex-1'}`}>
        <div className="px-6 py-5 border-b border-surface-border flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold text-brand-500 uppercase tracking-[0.3em] mb-0.5">Gestión</p>
            <h1 className="font-display text-3xl tracking-widest text-white uppercase">Clientes</h1>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-gray-600">{total}</span>
            <button onClick={() => setShowCreate(true)} className="btn-primary shrink-0">+ Nuevo</button>
          </div>
        </div>

        <div className="px-4 py-3 border-b border-surface-border">
          <div className="relative">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
              className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-600 pointer-events-none">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input className="input pl-9" placeholder="Buscar nombre o teléfono..."
              value={search} onChange={e => setSearch(e.target.value)} />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {loading ? <Spinner /> : members.length === 0 ? <Empty message="Sin clientes" /> : (
            members.map(m => (
              <div key={m.id} onClick={() => setSelected(m)}
                className={`px-4 py-3.5 cursor-pointer border-b border-surface-border/40 transition-all group
                  ${selected?.id === m.id
                    ? 'bg-brand-500/10 border-l-2 border-l-brand-500'
                    : 'hover:bg-surface-raised'}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-semibold transition-colors ${selected?.id === m.id ? 'text-white' : 'text-gray-300 group-hover:text-white'}`}>
                      {m.full_name}
                    </p>
                    <p className="text-xs text-gray-600 font-mono mt-0.5">{m.phone}</p>
                  </div>
                  <Badge status={m.is_active ? 'active' : 'inactive'} />
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Detail panel */}
      {selected && (
        <div className="flex-1 overflow-y-auto">
          <div className="px-6 py-5 border-b border-surface-border flex items-start justify-between sticky top-0 bg-surface z-10">
            <div>
              <p className="text-xs font-mono text-gray-600">ID #{selected.id}</p>
              <h2 className="font-display text-2xl tracking-widest text-white uppercase mt-0.5">{selected.full_name}</h2>
            </div>
            {/* ── Botones: Editar / Activar-Desactivar / Eliminar ── */}
            <div className="flex gap-2 mt-1 flex-wrap justify-end">
              <button onClick={() => setEditMember(selected)} className="btn-ghost text-xs">
                Editar
              </button>
              {selected.is_active ? (
                <button
                  onClick={() => handleToggleActive(selected)}
                  className="btn-ghost text-xs text-yellow-500 hover:text-yellow-400">
                  Desactivar
                </button>
              ) : (
                <button
                  onClick={() => handleToggleActive(selected)}
                  className="btn-ghost text-xs text-brand-400 hover:text-brand-300">
                  Activar
                </button>
              )}
              <button onClick={() => handleHardDelete(selected)} className="btn-danger text-xs">
                Eliminar
              </button>
            </div>
          </div>
          <div className="p-6">
            <MemberDetail member={selected} plans={plans}
              onClose={() => setSelected(null)} onUpdated={() => load()} />
          </div>
        </div>
      )}

      {showCreate && (
        <Modal title="Nuevo cliente" onClose={() => setShowCreate(false)}>
          <MemberForm onSave={handleCreate} onCancel={() => setShowCreate(false)} />
        </Modal>
      )}
      {editMember && (
        <Modal title="Editar cliente" onClose={() => setEditMember(null)}>
          <MemberForm initial={editMember} onSave={handleUpdate} onCancel={() => setEditMember(null)} />
        </Modal>
      )}
    </div>
  )
}
