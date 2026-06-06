interface Props {
  label: string; value: string | number; sub?: string
  accent?: 'green' | 'yellow' | 'red' | 'blue'
}
const accents = {
  green:  { value: 'text-brand-400', bar: 'bg-brand-500' },
  yellow: { value: 'text-orange-400', bar: 'bg-orange-500' },
  red:    { value: 'text-red-400',    bar: 'bg-red-500' },
  blue:   { value: 'text-sky-400',    bar: 'bg-sky-500' },
}
export default function StatCard({ label, value, sub, accent = 'green' }: Props) {
  const a = accents[accent]
  return (
    <div className="card flex flex-col gap-1 hover:border-surface-muted transition-colors duration-300">
      <div className={`w-6 h-0.5 rounded-full ${a.bar} mb-2`} />
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest">{label}</p>
      <p className={`font-display text-4xl leading-none ${a.value}`}>{value}</p>
      {sub && <p className="text-xs text-gray-600 mt-1 font-mono">{sub}</p>}
    </div>
  )
}
