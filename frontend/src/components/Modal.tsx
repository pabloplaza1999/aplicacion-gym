import { useEffect } from 'react'
interface Props { title: string; onClose: () => void; children: React.ReactNode }
export default function Modal({ title, onClose, children }: Props) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm"
      onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="bg-surface-card border border-surface-border rounded-lg w-full max-w-md mx-4 shadow-2xl overflow-hidden animate-fade-up">
        <div className="h-px w-full" style={{background:'linear-gradient(90deg,transparent,#E02020,transparent)'}} />
        <div className="flex items-center justify-between px-6 py-4 border-b border-surface-border">
          <h2 className="font-display text-xl tracking-widest text-white uppercase">{title}</h2>
          <button onClick={onClose} className="w-7 h-7 flex items-center justify-center rounded text-gray-500 hover:text-white hover:bg-surface-muted transition-all text-sm">✕</button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  )
}
