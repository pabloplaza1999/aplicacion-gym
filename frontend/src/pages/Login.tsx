import { useState, type FormEvent } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { loginUser } from '../services/api'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as any)?.from?.pathname || '/'
  const sessionExpired = new URLSearchParams(window.location.search).get('expired') === '1'

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!username.trim() || !password) return
    setLoading(true)
    setError('')
    try {
      const res = await loginUser({ username: username.trim(), password })
      login(res.access_token, username.trim(), res.is_temporary)
      navigate(res.is_temporary ? '/change-password' : from, { replace: true })
    } catch (err: any) {
      setError(err.message || 'Error de servidor')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface">
      <div className="w-full max-w-sm px-4">
        <div className="card p-8 space-y-6">
          {/* Logo */}
          <div className="flex flex-col items-center gap-2 mb-2">
            <div className="w-12 h-12 rounded-lg bg-brand-500/10 border border-brand-500/30 flex items-center justify-center">
              <svg viewBox="0 0 32 32" fill="none" className="w-7 h-7" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 20 C6 18 5 15 6 12 C7 9 9 8 11 8 L13 6 L15 8 C18 7 21 9 22 13 C23 17 21 20 18 22 L17 26 L14 26 L13 22 C11 22 9 21 8 20Z" fill="#4A4A55" stroke="#6B6B78" strokeWidth="0.5"/>
                <path d="M13 6 L14 3 L15 6" fill="#E8E8E8" stroke="#ccc" strokeWidth="0.3"/>
                <circle cx="11.5" cy="13" r="1.2" fill="#E02020"/>
              </svg>
            </div>
            <div className="text-center">
              <p className="font-display text-xl tracking-widest text-white">RHINO</p>
              <p className="text-xs font-semibold text-brand-500 tracking-[0.2em] uppercase">Power</p>
            </div>
          </div>

          {sessionExpired && (
            <div className="bg-amber-500/10 border border-amber-500/30 rounded-md px-3 py-2 text-sm text-amber-400 text-center">
              Tu sesión ha expirado. Inicia sesión nuevamente.
            </div>
          )}

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-md px-3 py-2 text-sm text-red-400 text-center">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">Usuario</label>
              <input
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                className="w-full bg-surface-raised border border-surface-border rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500 transition-colors"
                autoComplete="username"
                autoFocus
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">Contraseña</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="w-full bg-surface-raised border border-surface-border rounded-md px-3 py-2 pr-9 text-sm text-white focus:outline-none focus:border-brand-500 transition-colors"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(v => !v)}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  )}
                </button>
              </div>
            </div>
            <button
              type="submit"
              disabled={loading || !username.trim() || !password}
              className="w-full bg-brand-500 hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2 rounded-md text-sm transition-colors mt-2"
            >
              {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
            </button>
          </form>
        </div>
        <p className="text-center text-xs text-gray-600 mt-4">Rhino Power · Sistema de Gestión</p>
      </div>
    </div>
  )
}
