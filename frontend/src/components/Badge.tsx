type Status = 'active' | 'expiring' | 'expired' | 'inactive' | 'frozen' | 'exhausted'
const labels: Record<Status, string> = {
  active: 'Activo', expiring: 'Por vencer', expired: 'Vencido',
  inactive: 'Inactivo', frozen: 'Congelada', exhausted: 'Agotada',
}
export default function Badge({ status }: { status: Status }) {
  return (
    <span className={`badge-${status}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {labels[status]}
    </span>
  )
}
