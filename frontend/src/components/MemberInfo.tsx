import { useEffect, useState } from 'react'
import { updateMember, getMeasurements, upsertMeasurements } from '../services/api'
import type { Member, BodyMeasurement, BodyMeasurementUpsert } from '../types'
import Badge from './Badge'

// ── helpers ───────────────────────────────────────────────────────────────────
const toNum  = (v: string) => { const n = parseFloat(v);  return isNaN(n) ? null : n }
const toInt  = (v: string) => { const n = parseInt(v, 10); return isNaN(n) ? null : n }
const str    = (v?: number | null) => (v != null ? String(v) : '')
const isPos  = (v: string) => { const n = parseFloat(v); return !isNaN(n) && n > 0 }
const isNonNeg = (v: string) => { const n = parseFloat(v); return !isNaN(n) && n >= 0 }
const onlyDigits = (v: string) => /^\d*$/.test(v)

// ── Field ─────────────────────────────────────────────────────────────────────
function Field({
  label, value, onChange, type = 'text', unit, error,
}: {
  label: string; value: string; onChange: (v: string) => void
  type?: string; unit?: string; error?: boolean
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="label flex items-center justify-between">
        <span>{label}</span>
        {unit && <span className="text-gray-600 font-normal text-xs">{unit}</span>}
      </label>
      <input
        className={`input ${error ? 'ring-2 ring-red-500/50 border-red-500/50' : ''}`}
        type={type}
        inputMode={type === 'number' ? 'decimal' : undefined}
        value={value}
        step={type === 'number' ? 'any' : undefined}
        onChange={e => onChange(e.target.value)}
        placeholder="—"
      />
    </div>
  )
}

// ── Section ───────────────────────────────────────────────────────────────────
function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest whitespace-nowrap">
          {title}
        </p>
        <div className="h-px flex-1 bg-surface-border" />
      </div>
      {children}
    </div>
  )
}

// ── MemberInfo ────────────────────────────────────────────────────────────────
interface Props {
  member:    Member
  onUpdated: () => void   // simple refresh signal — no payload passed up
}

type MFields = Record<string, string>

const emptyM = (): MFields => ({
  age: '', height: '', shoulder: '', chest: '', waist: '',
  hip: '', bicep: '', forearm: '', calf: '', thigh: '', body_weight: '',
})

export default function MemberInfo({ member, onUpdated }: Props) {
  // personal
  const [fullName,  setFullName]  = useState(member.full_name)
  const [phone,     setPhone]     = useState(member.phone)
  const [document,  setDocument]  = useState(member.document ?? '')
  const [notes,     setNotes]     = useState(member.notes ?? '')

  // measurements (all stored as strings while editing)
  const [m,         setM]         = useState<MFields>(emptyM())
  const [loadingM,  setLoadingM]  = useState(true)

  // ui
  const [saving, setSaving] = useState(false)
  const [saved,  setSaved]  = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  // reset on member change
  useEffect(() => {
    setFullName(member.full_name)
    setPhone(member.phone)
    setDocument(member.document ?? '')
    setNotes(member.notes ?? '')
    setErrors({})
  }, [member.id])

  // load measurements
  useEffect(() => {
    setLoadingM(true)
    getMeasurements(member.id)
      .then(data => {
        if (data) {
          setM({
            age:         str((data as BodyMeasurement).age),
            height:      str((data as BodyMeasurement).height),
            shoulder:    str((data as BodyMeasurement).shoulder),
            chest:       str((data as BodyMeasurement).chest),
            waist:       str((data as BodyMeasurement).waist),
            hip:         str((data as BodyMeasurement).hip),
            bicep:       str((data as BodyMeasurement).bicep),
            forearm:     str((data as BodyMeasurement).forearm),
            calf:        str((data as BodyMeasurement).calf),
            thigh:       str((data as BodyMeasurement).thigh),
            body_weight: str((data as BodyMeasurement).body_weight),
          })
        } else {
          setM(emptyM())
        }
      })
      .finally(() => setLoadingM(false))
  }, [member.id])

  const setField = (k: string) => (v: string) => {
    setM(prev => ({ ...prev, [k]: v }))
    // clear field error on change
    setErrors(prev => { const next = { ...prev }; delete next[k]; return next })
  }

  // ── validation ──────────────────────────────────────────────────────────────
  function validate(): boolean {
    const e: Record<string, string> = {}

    if (!fullName.trim())
      e.fullName = 'Requerido'
    else if (/\d/.test(fullName))
      e.fullName = 'Solo texto'

    if (!phone.trim())
      e.phone = 'Requerido'
    else if (!onlyDigits(phone))
      e.phone = 'Solo números'
    else if (parseInt(phone) < 0)
      e.phone = 'Debe ser >= 0'

    if (document && !onlyDigits(document))
      e.document = 'Solo números'
    else if (document && parseInt(document) <= 0)
      e.document = 'Debe ser > 0'

    // measures: if filled, must be > 0
    const measureKeys = ['height','shoulder','chest','waist','hip','bicep','forearm','calf','thigh','body_weight']
    for (const k of measureKeys) {
      if (m[k] !== '' && !isPos(m[k]))
        e[k] = '> 0'
    }
    // age: if filled, must be >= 0 integer
    if (m.age !== '' && !isNonNeg(m.age))
      e.age = '>= 0'

    setErrors(e)
    return Object.keys(e).length === 0
  }

  // ── save ─────────────────────────────────────────────────────────────────────
  async function handleSave() {
    if (!validate()) return
    setSaving(true)
    try {
      await updateMember(member.id, {
        full_name: fullName,
        phone,
        document: document || undefined,
        notes:    notes    || undefined,
      })

      const ageRaw = toInt(m.age)
      const payload: BodyMeasurementUpsert = {
        age:         m.age         !== '' && ageRaw !== null ? Math.round(ageRaw) : null,
        height:      m.height      !== '' ? toNum(m.height)      : null,
        shoulder:    m.shoulder    !== '' ? toNum(m.shoulder)    : null,
        chest:       m.chest       !== '' ? toNum(m.chest)       : null,
        waist:       m.waist       !== '' ? toNum(m.waist)       : null,
        hip:         m.hip         !== '' ? toNum(m.hip)         : null,
        bicep:       m.bicep       !== '' ? toNum(m.bicep)       : null,
        forearm:     m.forearm     !== '' ? toNum(m.forearm)     : null,
        calf:        m.calf        !== '' ? toNum(m.calf)        : null,
        thigh:       m.thigh       !== '' ? toNum(m.thigh)       : null,
        body_weight: m.body_weight !== '' ? toNum(m.body_weight) : null,
      }
      await upsertMeasurements(member.id, payload)

      onUpdated()   // ← void, no payload — avoids [object Object]
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (e: any) {
      setErrors({ _global: e.message ?? 'Error al guardar' })
    } finally {
      setSaving(false)
    }
  }

  // ── render ───────────────────────────────────────────────────────────────────
  return (
    <div className="space-y-6">

      {/* ── 1. Datos del cliente ─────────────────────────────────────── */}
      <Section title="Datos del cliente">
        <div className="grid grid-cols-2 gap-3">

          <div className="col-span-2 space-y-1">
            <label className="label">Nombre completo</label>
            <input
              className={`input ${errors.fullName ? 'ring-2 ring-red-500/50 border-red-500/50' : ''}`}
              type="text"
              value={fullName}
              onChange={e => { setFullName(e.target.value); setErrors(p => { const n={...p}; delete n.fullName; return n }) }}
              placeholder="Nombre completo"
            />
            {errors.fullName && <p className="text-red-400 text-xs">{errors.fullName}</p>}
          </div>

          <div className="space-y-1">
            <Field label="Teléfono" value={phone} onChange={v => { if(onlyDigits(v)) { setPhone(v); setErrors(p => { const n={...p}; delete n.phone; return n }) }}} error={!!errors.phone} />
            {errors.phone && <p className="text-red-400 text-xs">{errors.phone}</p>}
          </div>

          <div className="space-y-1">
            <Field label="Documento" value={document} onChange={v => { if(onlyDigits(v)) setDocument(v) }} error={!!errors.document} />
            {errors.document && <p className="text-red-400 text-xs">{errors.document}</p>}
          </div>

          <div className="flex items-center gap-2 pt-4 col-span-2">
            <span className="label mb-0">Estado</span>
            <Badge status={member.is_active ? 'active' : 'inactive'} />
            <span className="text-xs text-gray-600 ml-1">
              Registrado: {member.registration_date.slice(0, 10)}
            </span>
          </div>

          <div className="col-span-2 space-y-1">
            <label className="label">Notas</label>
            <textarea
              className="input resize-none"
              rows={2}
              value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder="Observaciones..."
            />
          </div>

        </div>
      </Section>

      {/* ── 2. Medidas corporales ────────────────────────────────────── */}
      <Section title="Medidas corporales">
        {loadingM ? (
          <p className="text-xs text-gray-600">Cargando...</p>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            {([
              ['age',         'Edad',         'años', false],
              ['height',      'Altura',        'cm',  true],
              ['body_weight', 'Peso corporal', 'kg',  true],
              ['shoulder',    'Hombro',        'cm',  true],
              ['chest',       'Pecho',         'cm',  true],
              ['waist',       'Cintura',       'cm',  true],
              ['hip',         'Cola',          'cm',  true],
              ['bicep',       'Bíceps',        'cm',  true],
              ['forearm',     'Antebrazo',     'cm',  true],
              ['calf',        'Pantorrilla',   'cm',  true],
              ['thigh',       'Pierna',        'cm',  true],
            ] as [string, string, string, boolean][]).map(([key, label, unit]) => (
              <div key={key} className="space-y-1">
                <Field
                  label={label}
                  value={m[key]}
                  onChange={setField(key)}
                  type="number"
                  unit={unit}
                  error={!!errors[key]}
                />
                {errors[key] && <p className="text-red-400 text-xs">{errors[key]}</p>}
              </div>
            ))}
          </div>
        )}
      </Section>

      {/* ── errors / save ────────────────────────────────────────────── */}
      {errors._global && (
        <p className="text-red-400 text-xs bg-red-500/10 px-3 py-2 rounded-lg">{errors._global}</p>
      )}

      <button
        onClick={handleSave}
        disabled={saving}
        className={`btn-primary w-full transition-all ${saved ? '!bg-brand-600' : ''}`}
      >
        {saving ? 'Guardando...' : saved ? '✓ Guardado' : 'Guardar cambios'}
      </button>

    </div>
  )
}
