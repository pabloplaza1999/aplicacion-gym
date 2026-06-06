// ── Members ──────────────────────────────────────────────────────────────────
export interface Member {
  id: number
  full_name: string
  phone: string
  document?: string
  notes?: string
  registration_date: string
  is_active: boolean
}

export interface MemberCreate {
  full_name: string
  phone: string
  document?: string
  notes?: string
}

export interface MemberListResponse {
  total: number
  items: Member[]
}

// ── Plans ─────────────────────────────────────────────────────────────────────
export interface Plan {
  id: number
  name: string
  price: number
  duration_days: number
  plan_type: string
}

// ── Memberships ───────────────────────────────────────────────────────────────
export interface Membership {
  id: number
  member_id: number
  plan_id: number
  start_date: string
  end_date: string
  status: 'active' | 'expiring' | 'expired' | 'inactive'
  freeze_days: number
  is_active: boolean
}

export interface MembershipWithPlan extends Membership {
  days_remaining: number
  plan_name: string
  plan_price: number
  plan_duration_days: number
}

export interface MembershipCreate {
  member_id: number
  plan_id: number
}

// ── Payments ──────────────────────────────────────────────────────────────────
export type PaymentMethod = 'cash' | 'transfer' | 'qr' | 'nequi'

export interface Payment {
  id: number
  member_id: number
  membership_id?: number
  amount: number
  payment_method: PaymentMethod
  payment_date: string
  member_name?: string
}

export interface PaymentCreate {
  member_id: number
  membership_id?: number
  amount: number
  payment_method: PaymentMethod
}

export interface PaymentListResponse {
  total: number
  total_amount: number
  items: Payment[]
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
export interface MembershipStatusSummary {
  active: number
  expiring: number
  expired: number
}

export interface RevenueByPlan {
  plan_id: number
  plan_name: string
  count: number
  total_amount: number
}

export interface RecentRenewal {
  member_id: number
  member_name: string
  plan_name: string
  start_date: string
  end_date: string
  amount_paid?: number
}

export interface DashboardKPI {
  total_active_members: number
  memberships: MembershipStatusSummary
  monthly_revenue: number
  revenue_by_plan: RevenueByPlan[]
  recent_renewals: RecentRenewal[]
}

// ── Body Measurements ─────────────────────────────────────────────────────────
export interface BodyMeasurementUpsert {
  age?: number | null
  height?: number | null
  shoulder?: number | null
  chest?: number | null
  waist?: number | null
  hip?: number | null
  bicep?: number | null
  forearm?: number | null
  calf?: number | null
  thigh?: number | null
  body_weight?: number | null
}

export interface BodyMeasurement extends BodyMeasurementUpsert {
  id?: number
  member_id?: number
  updated_at?: string
}
