import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { changePassword } from '../services/api'

export default function ChangePassword() {
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { username, login } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (newPassword.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres')
      return
    }
    if (newPassword !== confirmPassword) {
      setError('Las contraseñas no coinciden')
      return
    }
    setLoading(true)
    setError('')
    try {
      const res = await changePassword({ new_password: newPassword, confirm_password: confirmPassword })
      // Backend returns a fresh token with is_temporary=false — update context and proceed
      login(res.access_token, username!, false)
      navigate('/', { replace: true })
    } catch (err: any) {
      setError(err.message || 'Error al cambiar contraseña')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface">
      <div className="w-full max-w-sm px-4">
        <div className="card p-8 space-y-6">
          <div className="text-center space-y-1">
            <h1 className="text-lg font-semibold text-white">Cambia tu contraseña</h1>
            <p className="text-sm text-gray-400">
              Es tu primer acceso. Debes establecer una contraseña personal antes de continuar.
            </p>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-md px-3 py-2 text-sm text-red-400 text-center">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">Nueva contraseña</label>
              <input
                type="password"
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                className="w-full bg-surface-raised border border-surface-border rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500 transition-colors"
                autoComplete="new-password"
                autoFocus
              />
              <p className="text-xs text-gray-600 mt-1">Mínimo 8 caracteres</p>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1.5">Confirmar contraseña</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                className="w-full bg-surface-raised border border-surface-border rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500 transition-colors"
                autoComplete="new-password"
              />
            </div>
            <button
              type="submit"
              disabled={loading || newPassword.length < 8 || !confirmPassword}
              className="w-full bg-brand-500 hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2 rounded-md text-sm transition-colors mt-2"
            >
              {loading ? 'Guardando...' : 'Guardar contraseña'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
