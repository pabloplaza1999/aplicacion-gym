import { useEffect, useState } from 'react'
import Spinner from '../components/Spinner'
import {
  getNotificationSettings,
  saveNotificationSettings,
  testSmtp,
} from '../services/api'
import type { NotificationSettings } from '../types'

const ALL_THRESHOLDS = [7, 3, 1, 0]
const THRESHOLD_LABEL: Record<number, string> = {
  7: '7 días antes',
  3: '3 días antes',
  1: '1 día antes',
  0: 'El día que vence',
}

export default function Settings() {
  const [settings, setSettings] = useState<NotificationSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [showPwd, setShowPwd] = useState(false)
  const [msg, setMsg] = useState<{ text: string; type: 'success' | 'error' } | null>(null)

  // Form state
  const [host, setHost] = useState('')
  const [port, setPort] = useState(587)
  const [user, setUser] = useState('')
  const [password, setPassword] = useState('')
  const [fromName, setFromName] = useState('')
  const [fromEmail, setFromEmail] = useState('')
  const [thresholds, setThresholds] = useState<number[]>([7, 3, 1, 0])
  const [enabled, setEnabled] = useState(true)

  useEffect(() => {
    getNotificationSettings()
      .then(s => {
        setSettings(s)
        setHost(s.smtp_host || '')
        setPort(s.smtp_port || 587)
        setUser(s.smtp_user || '')
        setFromName(s.smtp_from_name || '')
        setFromEmail(s.smtp_from_email || '')
        setThresholds(s.thresholds)
        setEnabled(s.enabled)
      })
      .finally(() => setLoading(false))
  }, [])

  function toggleThreshold(t: number) {
    setThresholds(prev =>
      prev.includes(t) ? prev.filter(x => x !== t) : [...prev, t]
    )
  }

  async function handleSave() {
    setSaving(true)
    setMsg(null)
    try {
      const updated = await saveNotificationSettings({
        smtp_host: host || null,
        smtp_port: port,
        smtp_user: user || null,
        smtp_password: password || null,
        smtp_from_name: fromName || null,
        smtp_from_email: fromEmail || null,
        thresholds,
        enabled,
      })
      setSettings(updated)
      setPassword('')
      setMsg({ text: 'Configuración guardada correctamente.', type: 'success' })
    } catch (e: any) {
      setMsg({ text: e.message || 'Error al guardar.', type: 'error' })
    } finally {
      setSaving(false)
    }
  }

  async function handleTest() {
    setTesting(true)
    setMsg(null)
    try {
      const res = await testSmtp()
      setMsg({ text: res.message, type: 'success' })
    } catch (e: any) {
      setMsg({ text: e.message || 'Error de conexión SMTP.', type: 'error' })
    } finally {
      setTesting(false)
    }
  }

  if (loading) return <Spinner />

  return (
    <div className="p-8 space-y-8 animate-fade-up max-w-2xl">
      <div className="border-b border-surface-border pb-6">
        <p className="text-xs font-semibold text-brand-500 uppercase tracking-[0.3em] mb-1">Sistema</p>
        <h1 className="font-display text-4xl tracking-widest text-white uppercase">Configuración</h1>
      </div>

      {/* SMTP */}
      <div className="card space-y-5">
        <div className="flex items-center gap-3">
          <div className="w-1 h-5 bg-brand-500 rounded-full shadow-brand-sm" />
          <h2 className="font-display text-lg tracking-widest text-white uppercase">Correo SMTP</h2>
          {settings && (
            <span className={`text-xs font-mono px-2 py-0.5 rounded border ${
              settings.is_configured
                ? 'bg-success-400/10 text-success-400 border-success-400/30'
                : 'bg-red-500/10 text-red-400 border-red-500/30'
            }`}>
              {settings.is_configured ? 'Configurado' : 'Sin configurar'}
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2 sm:col-span-1 space-y-1">
            <label className="text-xs text-gray-500 font-mono uppercase tracking-wider">Servidor SMTP</label>
            <input
              value={host}
              onChange={e => setHost(e.target.value)}
              placeholder="smtp.gmail.com"
              className="w-full bg-surface-raised border border-surface-border rounded px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-brand-500"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-gray-500 font-mono uppercase tracking-wider">Puerto</label>
            <input
              type="number"
              value={port}
              onChange={e => setPort(Number(e.target.value))}
              className="w-full bg-surface-raised border border-surface-border rounded px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-brand-500"
            />
          </div>
          <div className="col-span-2 space-y-1">
            <label className="text-xs text-gray-500 font-mono uppercase tracking-wider">Usuario</label>
            <input
              value={user}
              onChange={e => setUser(e.target.value)}
              placeholder="correo@gmail.com"
              className="w-full bg-surface-raised border border-surface-border rounded px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-brand-500"
            />
          </div>
          <div className="col-span-2 space-y-1">
            <label className="text-xs text-gray-500 font-mono uppercase tracking-wider">
              Contraseña {settings?.is_configured && !password && <span className="text-gray-600">(sin cambios si se deja vacía)</span>}
            </label>
            <div className="relative">
              <input
                type={showPwd ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder={settings?.is_configured ? '••••••••' : 'Contraseña de aplicación'}
                className="w-full bg-surface-raised border border-surface-border rounded px-3 py-2 pr-20 text-sm text-white font-mono focus:outline-none focus:border-brand-500"
              />
              <button
                type="button"
                onClick={() => setShowPwd(v => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-500 hover:text-gray-300 font-mono"
              >
                {showPwd ? 'Ocultar' : 'Mostrar'}
              </button>
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-xs text-gray-500 font-mono uppercase tracking-wider">Nombre remitente</label>
            <input
              value={fromName}
              onChange={e => setFromName(e.target.value)}
              placeholder="Rhino Power"
              className="w-full bg-surface-raised border border-surface-border rounded px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-brand-500"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-gray-500 font-mono uppercase tracking-wider">Email remitente</label>
            <input
              value={fromEmail}
              onChange={e => setFromEmail(e.target.value)}
              placeholder="no-reply@gym.com"
              className="w-full bg-surface-raised border border-surface-border rounded px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-brand-500"
            />
          </div>
        </div>
      </div>

      {/* Thresholds */}
      <div className="card space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-1 h-5 bg-brand-500 rounded-full shadow-brand-sm" />
          <h2 className="font-display text-lg tracking-widest text-white uppercase">Umbrales de aviso</h2>
        </div>
        <p className="text-xs text-gray-500 font-mono">Activa los avisos que quieres enviar antes del vencimiento.</p>
        <div className="space-y-2">
          {ALL_THRESHOLDS.map(t => (
            <label key={t} className="flex items-center gap-3 cursor-pointer group">
              <input
                type="checkbox"
                checked={thresholds.includes(t)}
                onChange={() => toggleThreshold(t)}
                className="w-4 h-4 accent-brand-500 cursor-pointer"
              />
              <span className="text-sm text-gray-300 group-hover:text-white transition-colors font-mono">
                {THRESHOLD_LABEL[t]}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Enable / disable */}
      <div className="card">
        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={enabled}
            onChange={e => setEnabled(e.target.checked)}
            className="w-4 h-4 accent-brand-500 cursor-pointer"
          />
          <div>
            <span className="text-sm text-gray-200 font-mono">Notificaciones activas</span>
            <p className="text-xs text-gray-600 font-mono mt-0.5">
              Si se desactiva, el job diario no enviará correos.
            </p>
          </div>
        </label>
      </div>

      {/* Feedback */}
      {msg && (
        <p className={`text-sm font-mono px-4 py-2 rounded border ${
          msg.type === 'success'
            ? 'bg-success-400/10 text-success-400 border-success-400/30'
            : 'bg-red-500/10 text-red-400 border-red-500/30'
        }`}>
          {msg.text}
        </p>
      )}

      {/* Actions */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-5 py-2 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white text-sm font-semibold rounded transition-colors"
        >
          {saving ? 'Guardando...' : 'Guardar configuración'}
        </button>
        <button
          onClick={handleTest}
          disabled={testing || !settings?.is_configured}
          className="px-5 py-2 border border-surface-border hover:border-brand-500/50 disabled:opacity-40 text-gray-300 hover:text-white text-sm font-mono rounded transition-colors"
        >
          {testing ? 'Enviando...' : 'Probar conexión'}
        </button>
      </div>
    </div>
  )
}
