export default function Empty({ message = 'Sin registros' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3">
      <div className="w-12 h-12 rounded border border-surface-muted flex items-center justify-center">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5 text-gray-700">
          <circle cx="12" cy="12" r="10"/><line x1="8" y1="12" x2="16" y2="12"/>
        </svg>
      </div>
      <p className="text-xs font-semibold text-gray-600 uppercase tracking-widest">{message}</p>
    </div>
  )
}
