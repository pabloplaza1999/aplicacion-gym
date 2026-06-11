import { useState, useEffect } from 'react'
import Modal from './Modal'
import Spinner from './Spinner'
import { listBackups, createManualBackup } from '../services/api'
import type { BackupFile, BackupListResponse } from '../types'

interface Props {
  onClose: () => void
}

function fmtDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString('es-CO', {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit',
    })
  } catch {
    return iso
  }
}

function BackupRow({ file }: { file: BackupFile }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-surface-border last:border-0">
      <div>
        <p className="text-sm text-gray-200 font-mono">{file.filename}</p>
        <p className="text-xs text-gray-500">{fmtDate(file.created_at)} · {file.size_kb} KB</p>
      </div>
    </div>
  )
}

export default function BackupModal({ onClose }: Props) {
  const [data, setData] = useState<BackupListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [created, setCreated] = useState<BackupFile | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listBackups()
      .then(setData)
      .catch(() => setError('No se pudo cargar la lista de respaldos.'))
      .finally(() => setLoading(false))
  }, [])

  async function handleCreate() {
    setCreating(true)
    setError(null)
    setCreated(null)
    try {
      const file = await createManualBackup()
      setCreated(file)
      const updated = await listBackups()
      setData(updated)
    } catch (e: any) {
      setError(e.message || 'Error al crear el respaldo.')
    } finally {
      setCreating(false)
    }
  }

  return (
    <Modal title="Gestión de respaldos" onClose={onClose}>
      <div className="space-y-5">
        {/* Acción manual */}
        <div className="flex flex-col gap-2">
          <button
            onClick={handleCreate}
            disabled={creating}
            className="w-full py-2 rounded bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white text-sm font-semibold transition-colors flex items-center justify-center gap-2"
          >
            {creating ? <><Spinner /><span>Creando respaldo...</span></> : 'Crear respaldo ahora'}
          </button>
          {created && (
            <p className="text-xs text-success-400 text-center">
              ✓ Respaldo creado: <span className="font-mono">{created.filename}</span>
            </p>
          )}
          {error && <p className="text-xs text-red-400 text-center">{error}</p>}
        </div>

        {loading && <div className="flex justify-center py-4"><Spinner /></div>}

        {/* Automáticos */}
        {data && (
          <div className="space-y-1">
            <p className="text-xs font-semibold uppercase tracking-widest text-gray-500">
              Automáticos ({data.automatic.length}/30)
            </p>
            {data.automatic.length === 0
              ? <p className="text-xs text-gray-600 py-2">Sin respaldos automáticos aún.</p>
              : <div className="max-h-40 overflow-y-auto pr-1">
                  {data.automatic.map(f => <BackupRow key={f.filename} file={f} />)}
                </div>
            }
          </div>
        )}

        {/* Manuales */}
        {data && (
          <div className="space-y-1">
            <p className="text-xs font-semibold uppercase tracking-widest text-gray-500">
              Manuales ({data.manual.length}/10)
            </p>
            {data.manual.length === 0
              ? <p className="text-xs text-gray-600 py-2">Sin respaldos manuales.</p>
              : <div className="max-h-32 overflow-y-auto pr-1">
                  {data.manual.map(f => <BackupRow key={f.filename} file={f} />)}
                </div>
            }
          </div>
        )}
      </div>
    </Modal>
  )
}
