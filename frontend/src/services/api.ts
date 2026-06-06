import type {
  Member, MemberCreate, MemberListResponse,
  Plan,
  Membership, MembershipWithPlan, MembershipCreate,
  Payment, PaymentCreate, PaymentListResponse,
  DashboardKPI,
  CheckInResult, VoucherStatus,
} from '../types'

const BASE = '/api'

async function req<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    let message = 'Error de servidor'
    if (typeof err.detail === 'string') {
      message = err.detail
    } else if (Array.isArray(err.detail)) {
      message = err.detail.map((e: any) => {
        const rawField = e.loc ? e.loc[e.loc.length - 1] : 'dato'
        const fieldLabels: Record<string, string> = {
          full_name: 'Nombre completo',
          phone: 'Teléfono',
          document: 'Documento',
          age: 'Edad',
          height: 'Altura',
          weight: 'Peso',
          body_weight: 'Peso corporal',
          bicep: 'Bíceps',
          forearm: 'Antebrazo',
          calf: 'Pantorrilla',
          thigh: 'Pierna',
          shoulder: 'Hombro',
          chest: 'Pecho',
          waist: 'Cintura',
          hip: 'Cola'
        }
        const field = fieldLabels[rawField] || rawField
        const msg = e.msg.replace(/^Value error,\s*/i, '')
        return `${field}: ${msg}`
      }).join(', ')
    } else if (err.detail) {
      message = JSON.stringify(err.detail)
    }
    throw new Error(message)
  }
  return res.json()
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
export const getDashboard = (): Promise<DashboardKPI> =>
  req('/dashboard')

// ── Members ───────────────────────────────────────────────────────────────────
export const getMembers = (skip = 0, limit = 50, search = ''): Promise<MemberListResponse> =>
  req(`/members?skip=${skip}&limit=${limit}&search=${encodeURIComponent(search)}`)

export const getMember = (id: number): Promise<Member> =>
  req(`/members/${id}`)

export const createMember = (data: MemberCreate): Promise<Member> =>
  req('/members', { method: 'POST', body: JSON.stringify(data) })

export const updateMember = (id: number, data: Partial<MemberCreate>): Promise<Member> =>
  req(`/members/${id}`, { method: 'PUT', body: JSON.stringify(data) })

export const deleteMember = (id: number, hard = false): Promise<Member> =>
  req(`/members/${id}${hard ? '?hard=true' : ''}`, { method: 'DELETE' })

// ── Plans ─────────────────────────────────────────────────────────────────────
export const getPlans = (): Promise<Plan[]> =>
  req('/plans')

// ── Memberships ───────────────────────────────────────────────────────────────
export const getMemberMemberships = (memberId: number): Promise<{ total: number; items: Membership[] }> =>
  req(`/members/${memberId}/memberships`)

export const getCurrentMembership = (memberId: number): Promise<MembershipWithPlan | null> =>
  req<MembershipWithPlan>(`/members/${memberId}/current-membership`).catch((): null => null)

export const createMembership = (memberId: number, data: MembershipCreate): Promise<Membership> =>
  req(`/members/${memberId}/memberships`, { method: 'POST', body: JSON.stringify(data) })

export const renewMembership = (membershipId: number, planId: number): Promise<Membership> =>
  req(`/members/memberships/${membershipId}/renew`, {
    method: 'POST',
    body: JSON.stringify({ plan_id: planId }),
  })

export const setMembershipActive = (membershipId: number, isActive: boolean): Promise<MembershipWithPlan> =>
  req(`/members/memberships/${membershipId}/active`, {
    method: 'PATCH',
    body: JSON.stringify({ is_active: isActive }),
  })

// ── Payments ──────────────────────────────────────────────────────────────────
export const getMemberPayments = (memberId: number): Promise<PaymentListResponse> =>
  req(`/members/${memberId}/payments`)

export const getAllPayments = (skip = 0, limit = 20): Promise<PaymentListResponse> =>
  req(`/payments?skip=${skip}&limit=${limit}`)

export const createPayment = (memberId: number, data: PaymentCreate): Promise<Payment> =>
  req(`/members/${memberId}/payments`, { method: 'POST', body: JSON.stringify(data) })

export const deletePayment = (paymentId: number): Promise<void> =>
  req(`/payments/${paymentId}`, { method: 'DELETE' })

// ── Attendance / Valeras ───────────────────────────────────────────────────────
export const checkInAttendance = (document: string): Promise<CheckInResult> =>
  req('/attendance/check-in', { method: 'POST', body: JSON.stringify({ document }) })

export const getVoucherStatus = (document: string): Promise<VoucherStatus> =>
  req(`/attendance/voucher-status/${encodeURIComponent(document)}`)

// ── Body Measurements ─────────────────────────────────────────────────────────
export const getMeasurements = (memberId: number) =>
  req<import('../types').BodyMeasurement>(`/members/${memberId}/measurements`).catch((): null => null)

export const upsertMeasurements = (memberId: number, data: import('../types').BodyMeasurementUpsert) =>
  req<import('../types').BodyMeasurement>(`/members/${memberId}/measurements`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
