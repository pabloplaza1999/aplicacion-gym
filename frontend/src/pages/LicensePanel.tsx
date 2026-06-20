import { useEffect, useState } from 'react'
import type { GymLicensePanel, GymInfo, LicenseInfo, ModuleStatus } from '../types'
import {
  getSuperAdminPanel, updateGymInfo, changeGymPlan,
  updateLicenseValidity, toggleModule,
} from '../services/api'

// ── Helpers ───────────────────────────────────────────────────────────────────

function PlanBadge({ plan }: { plan: string }) {
  const colors: Record<string, string> = {
    starter:      'bg-gray-700 text-gray-200',
    professional: 'bg-blue-900/60 text-blue-300',
    premium:      'bg-amber-900/60 text-amber-300',
  }
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded uppercase tracking-wide ${colors[plan] ?? 'bg-gray-700 text-gray-200'}`}>
      {plan}
    </span>
  )
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    active:    'bg-emerald-900/50 text-emerald-400',
    expired:   'bg-red-900/50 text-red-400',
    suspended: 'bg-yellow-900/50 text-yellow-400',
  }
  const labels: Record<string, string> = {
    active: 'Activa', expired: 'Vencida', suspended: 'Suspendida',
  }
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded ${colors[status] ?? 'bg-gray-700 text-gray-400'}`}>
      {labels[status] ?? status}
    </span>
  )
}

function SourceBadge({ source }: { source: string }) {
  return source === 'plan'
    ? <span className="text-xs px-1.5 py-0.5 rounded bg-brand-500/15 text-brand-400 font-medium">Plan</span>
    : <span className="text-xs px-1.5 py-0.5 rounded bg-gray-700 text-gray-400 font-medium">Addon</span>
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-surface-card border border-surface-border rounded-lg overflow-hidden">
      <div className="px-5 py-3 border-b border-surface-border">
        <h2 className="text-sm font-semibold text-white tracking-wide">{title}</h2>
      </div>
      <div className="p-5">{children}</div>
    </div>
  )
}

// ── Gym Info Section ───────────────────────────────────────────────────────────

function GymSection({ gym, onUpdated }: { gym: GymInfo; onUpdated: () => void }) {
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({ name: gym.name, contact_name: gym.contact_name ?? '', contact_email: gym.contact_email ?? '' })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleSave() {
    setSaving(true)
    setError('')
    try {
      await updateGymInfo({
        name: form.name || undefined,
        contact_name: form.contact_name || null,
        contact_email: form.contact_email || null,
      })
      setEditing(false)
      onUpdated()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  if (editing) {
    return (
      <SectionCard title="Gimnasio">
        <div className="space-y-3">
          <div>
            <label className="block text-xs text-gray-400 mb-1">Nombre</label>
            <input
              className="w-full bg-surface-raised border border-surface-border rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500"
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Contacto</label>
            <input
              className="w-full bg-surface-raised border border-surface-border rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500"
              placeholder="Nombre del contacto"
              value={form.contact_name}
              onChange={e => setForm(f => ({ ...f, contact_name: e.target.value }))}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Email</label>
            <input
              type="email"
              className="w-full bg-surface-raised border border-surface-border rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500"
              placeholder="email@gimnasio.com"
              value={form.contact_email}
              onChange={e => setForm(f => ({ ...f, contact_email: e.target.value }))}
            />
          </div>
          {error && <p className="text-xs text-red-400">{error}</p>}
          <div className="flex gap-2 pt-1">
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-4 py-1.5 text-sm bg-brand-500 hover:bg-brand-600 text-white rounded disabled:opacity-50 transition-colors"
            >
              {saving ? 'Guardando…' : 'Guardar'}
            </button>
            <button
              onClick={() => setEditing(false)}
              className="px-4 py-1.5 text-sm border border-surface-border text-gray-400 hover:text-white rounded transition-colors"
            >
              Cancelar
            </button>
          </div>
        </div>
      </SectionCard>
    )
  }

  return (
    <SectionCard title="Gimnasio">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-white font-medium">{gym.name}</p>
          <p className="text-xs text-gray-500">slug: {gym.slug}</p>
          {gym.contact_name && <p className="text-sm text-gray-400">{gym.contact_name}</p>}
          {gym.contact_email && <p className="text-sm text-gray-500">{gym.contact_email}</p>}
          <span className={`inline-block text-xs px-2 py-0.5 rounded mt-1 ${gym.active ? 'bg-emerald-900/50 text-emerald-400' : 'bg-gray-700 text-gray-400'}`}>
            {gym.active ? 'Activo' : 'Inactivo'}
          </span>
        </div>
        <button
          onClick={() => { setForm({ name: gym.name, contact_name: gym.contact_name ?? '', contact_email: gym.contact_email ?? '' }); setEditing(true) }}
          className="text-xs text-gray-500 hover:text-brand-400 transition-colors"
        >
          Editar
        </button>
      </div>
    </SectionCard>
  )
}

// ── License Section ────────────────────────────────────────────────────────────

const PLANS = ['starter', 'professional', 'premium'] as const

function LicenseSection({ license, onUpdated }: { license: LicenseInfo | null; onUpdated: () => void }) {
  const [editingPlan, setEditingPlan] = useState(false)
  const [editingValidity, setEditingValidity] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState(license?.plan_name ?? 'professional')
  const [validFrom, setValidFrom] = useState(license?.valid_from ?? '')
  const [validUntil, setValidUntil] = useState(license?.valid_until ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function handlePlanSave() {
    setSaving(true); setError('')
    try {
      await changeGymPlan({ plan_name: selectedPlan })
      setEditingPlan(false)
      onUpdated()
    } catch (e: any) { setError(e.message) } finally { setSaving(false) }
  }

  async function handleValiditySave() {
    setSaving(true); setError('')
    try {
      await updateLicenseValidity({
        valid_from: validFrom || null,
        valid_until: validUntil || null,
      })
      setEditingValidity(false)
      onUpdated()
    } catch (e: any) { setError(e.message) } finally { setSaving(false) }
  }

  if (!license) {
    return (
      <SectionCard title="Licencia">
        <p className="text-sm text-gray-500">Sin licencia activa para este gimnasio.</p>
      </SectionCard>
    )
  }

  return (
    <SectionCard title="Licencia">
      <div className="space-y-4">
        {/* Plan row */}
        <div className="flex items-center justify-between">
          {editingPlan ? (
            <div className="flex items-center gap-2 flex-wrap">
              {PLANS.map(p => (
                <button
                  key={p}
                  onClick={() => setSelectedPlan(p)}
                  className={`px-3 py-1.5 text-sm rounded border transition-colors ${
                    selectedPlan === p
                      ? 'border-brand-500 bg-brand-500/10 text-white'
                      : 'border-surface-border text-gray-400 hover:border-gray-500'
                  }`}
                >
                  {p}
                </button>
              ))}
              <button onClick={handlePlanSave} disabled={saving}
                className="px-3 py-1.5 text-sm bg-brand-500 text-white rounded disabled:opacity-50">
                {saving ? '…' : 'Guardar'}
              </button>
              <button onClick={() => setEditingPlan(false)} className="text-xs text-gray-500 hover:text-white">Cancelar</button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-400">Plan</span>
              <PlanBadge plan={license.plan_name} />
            </div>
          )}
          {!editingPlan && (
            <button onClick={() => { setSelectedPlan(license.plan_name); setEditingPlan(true) }}
              className="text-xs text-gray-500 hover:text-brand-400 transition-colors">Cambiar</button>
          )}
        </div>

        {/* Status + validity row */}
        <div className="flex items-center justify-between">
          {editingValidity ? (
            <div className="flex items-center gap-3 flex-wrap">
              <div>
                <label className="block text-xs text-gray-400 mb-1">Desde</label>
                <input type="date" value={validFrom}
                  onChange={e => setValidFrom(e.target.value)}
                  className="bg-surface-raised border border-surface-border rounded px-2 py-1 text-sm text-white focus:outline-none focus:border-brand-500" />
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Hasta (vacío = sin vencimiento)</label>
                <input type="date" value={validUntil}
                  onChange={e => setValidUntil(e.target.value)}
                  className="bg-surface-raised border border-surface-border rounded px-2 py-1 text-sm text-white focus:outline-none focus:border-brand-500" />
              </div>
              <div className="flex gap-2 items-end">
                <button onClick={handleValiditySave} disabled={saving}
                  className="px-3 py-1.5 text-sm bg-brand-500 text-white rounded disabled:opacity-50">
                  {saving ? '…' : 'Guardar'}
                </button>
                <button onClick={() => setEditingValidity(false)} className="text-xs text-gray-500 hover:text-white">Cancelar</button>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <StatusBadge status={license.status} />
              <span className="text-sm text-gray-500">
                {license.valid_from ?? '—'}
                {license.valid_until ? ` → ${license.valid_until}` : ' · Sin vencimiento'}
              </span>
            </div>
          )}
          {!editingValidity && (
            <button onClick={() => {
              setValidFrom(license.valid_from ?? '')
              setValidUntil(license.valid_until ?? '')
              setEditingValidity(true)
            }} className="text-xs text-gray-500 hover:text-brand-400 transition-colors">Fechas</button>
          )}
        </div>

        {error && <p className="text-xs text-red-400">{error}</p>}
        {license.notes && <p className="text-xs text-gray-600 border-t border-surface-border pt-3">{license.notes}</p>}
      </div>
    </SectionCard>
  )
}

// ── Modules Section ────────────────────────────────────────────────────────────

function ModuleRow({ mod, onToggle }: { mod: ModuleStatus; onToggle: (key: string, active: boolean) => Promise<void> }) {
  const [toggling, setToggling] = useState(false)

  async function handleToggle() {
    setToggling(true)
    try { await onToggle(mod.module_key, !mod.active) } finally { setToggling(false) }
  }

  return (
    <div className="flex items-center justify-between py-3 border-b border-surface-border last:border-0">
      <div className="flex items-center gap-3">
        <div className={`w-2 h-2 rounded-full ${mod.active ? 'bg-emerald-400' : 'bg-gray-600'}`} />
        <span className="text-sm text-white">{mod.name}</span>
        <SourceBadge source={mod.source} />
        <span className="text-xs text-gray-600 font-mono">{mod.module_key}</span>
      </div>
      <button
        onClick={handleToggle}
        disabled={toggling}
        className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors disabled:opacity-50 ${
          mod.active ? 'bg-brand-500' : 'bg-gray-700'
        }`}
      >
        <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
          mod.active ? 'translate-x-4' : 'translate-x-0.5'
        }`} />
      </button>
    </div>
  )
}

function ModulesSection({ modules, onUpdated }: { modules: ModuleStatus[]; onUpdated: () => void }) {
  const [error, setError] = useState('')

  async function handleToggle(key: string, active: boolean) {
    setError('')
    try {
      await toggleModule(key, { active })
      onUpdated()
    } catch (e: any) { setError(e.message) }
  }

  const active = modules.filter(m => m.active)
  const inactive = modules.filter(m => !m.active)

  return (
    <SectionCard title={`Módulos (${active.length}/${modules.length} activos)`}>
      {error && <p className="text-xs text-red-400 mb-3">{error}</p>}
      {modules.length === 0 ? (
        <p className="text-sm text-gray-500">Sin módulos registrados.</p>
      ) : (
        <div>
          {[...active, ...inactive].map(mod => (
            <ModuleRow key={mod.module_key} mod={mod} onToggle={handleToggle} />
          ))}
        </div>
      )}
    </SectionCard>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function LicensePanel() {
  const [panel, setPanel] = useState<GymLicensePanel | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function loadPanel() {
    setError('')
    try {
      const data = await getSuperAdminPanel()
      setPanel(data)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadPanel() }, [])

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-white">Panel de Licenciamiento</h1>
        <p className="text-sm text-gray-500 mt-1">Gestión de gimnasio, plan comercial y módulos activos.</p>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-gray-500">
          <div className="w-4 h-4 rounded-full border-2 border-brand-500 border-t-transparent animate-spin" />
          <span className="text-sm">Cargando…</span>
        </div>
      )}

      {error && (
        <div className="bg-red-900/20 border border-red-800/40 rounded-lg p-4">
          <p className="text-sm text-red-400">{error}</p>
          <button onClick={loadPanel} className="mt-2 text-xs text-red-400 hover:text-red-300 underline">
            Reintentar
          </button>
        </div>
      )}

      {panel && !loading && (
        <div className="space-y-4">
          <GymSection gym={panel.gym} onUpdated={loadPanel} />
          <LicenseSection license={panel.license} onUpdated={loadPanel} />
          <ModulesSection modules={panel.modules} onUpdated={loadPanel} />
        </div>
      )}
    </div>
  )
}
