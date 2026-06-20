import type {
  Member, MemberCreate, MemberListResponse,
  Plan,
  Membership, MembershipWithPlan, MembershipCreate, MembershipStartDateCorrectionCreate, VoucherWarning,
  Payment, PaymentCreate, PaymentListResponse,
  DashboardKPI,
  CheckInResult, VoucherStatus,
  ProductCategory, ProductCategoryCreate, ProductCategoryUpdate,
  Product, ProductCreate, ProductUpdate, ProductListResponse,
  InventoryMovement, InventoryEntryCreate, InventoryAdjustmentCreate,
  Sale, SaleCreate, SaleListResponse,
  Customer, CustomerCreate, CustomerUpdate,
  CreditPayment, CreditPaymentCreate,
  CarteraResponse,
  StoreReport,
  LoginRequest, TokenResponse, ChangePasswordRequest,
  GymLicensePanel, GymUpdate, LicensePlanUpdate, LicenseValidityUpdate, ModuleToggle,
  GymInfo, LicenseInfo, ModuleStatus,
} from '../types'

// VITE_API_URL = origen del servidor (ej: http://localhost:8000). El /api se agrega aquí siempre.
const BASE = (import.meta.env.VITE_API_URL || '') + '/api'

const TOKEN_KEY = 'gym_auth_token'

async function req<T>(path: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem(TOKEN_KEY)
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, { headers, ...options })

  // 401 on any route except /auth/login → session expired, redirect to login
  if (res.status === 401 && path !== '/auth/login') {
    localStorage.removeItem(TOKEN_KEY)
    window.location.replace('/login?expired=1')
    return undefined as T
  }

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
          hip: 'Cola',
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
  if (res.status === 204) return undefined as T
  return res.json()
}

// ── Auth — F2 ─────────────────────────────────────────────────────────────────
export const loginUser = (data: LoginRequest): Promise<TokenResponse> =>
  req('/auth/login', { method: 'POST', body: JSON.stringify(data) })

export const changePassword = (data: ChangePasswordRequest): Promise<TokenResponse> =>
  req('/auth/change-password', { method: 'POST', body: JSON.stringify(data) })

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

export const renewMembership = (membershipId: number, planId: number, force = false): Promise<Membership> =>
  req(`/members/memberships/${membershipId}/renew`, {
    method: 'POST',
    body: JSON.stringify({ plan_id: planId, force }),
  })

export const getActiveVoucherWarning = (memberId: number): Promise<VoucherWarning> =>
  req(`/members/${memberId}/active-voucher-warning`)

export const freezeMembership = (membershipId: number): Promise<MembershipWithPlan> =>
  req(`/members/memberships/${membershipId}/freeze`, { method: 'POST' })

export const unfreezeMembership = (membershipId: number): Promise<MembershipWithPlan> =>
  req(`/members/memberships/${membershipId}/unfreeze`, { method: 'POST' })

export const setMembershipActive = (membershipId: number, isActive: boolean): Promise<MembershipWithPlan> =>
  req(`/members/memberships/${membershipId}/active`, {
    method: 'PATCH',
    body: JSON.stringify({ is_active: isActive }),
  })

export const correctMembershipStartDate = (
  membershipId: number,
  payload: MembershipStartDateCorrectionCreate,
): Promise<MembershipWithPlan> =>
  req(`/members/memberships/${membershipId}/start-date`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
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

// ── Store — Categories ────────────────────────────────────────────────────────
export const getCategories = (activeOnly = false): Promise<ProductCategory[]> =>
  req(`/store/categories${activeOnly ? '?active_only=true' : ''}`)

export const createCategory = (data: ProductCategoryCreate): Promise<ProductCategory> =>
  req('/store/categories', { method: 'POST', body: JSON.stringify(data) })

export const updateCategory = (id: number, data: ProductCategoryUpdate): Promise<ProductCategory> =>
  req(`/store/categories/${id}`, { method: 'PUT', body: JSON.stringify(data) })

export const toggleCategory = (id: number, isActive: boolean): Promise<ProductCategory> =>
  req(`/store/categories/${id}/active?is_active=${isActive}`, { method: 'PATCH' })

export const deleteCategory = (id: number): Promise<void> =>
  req(`/store/categories/${id}`, { method: 'DELETE' })

// ── Store — Products ──────────────────────────────────────────────────────────
export const getProducts = (params?: {
  search?: string; categoryId?: number; lowStock?: boolean; activeOnly?: boolean; skip?: number; limit?: number
}): Promise<ProductListResponse> => {
  const q = new URLSearchParams()
  if (params?.search) q.set('search', params.search)
  if (params?.categoryId) q.set('category_id', String(params.categoryId))
  if (params?.lowStock) q.set('low_stock', 'true')
  if (params?.activeOnly) q.set('active_only', 'true')
  if (params?.skip) q.set('skip', String(params.skip))
  if (params?.limit) q.set('limit', String(params.limit))
  const qs = q.toString()
  return req(`/store/products${qs ? `?${qs}` : ''}`)
}

export const createProduct = (data: ProductCreate): Promise<Product> =>
  req('/store/products', { method: 'POST', body: JSON.stringify(data) })

export const updateProduct = (id: number, data: ProductUpdate): Promise<Product> =>
  req(`/store/products/${id}`, { method: 'PUT', body: JSON.stringify(data) })

export const toggleProduct = (id: number, isActive: boolean): Promise<Product> =>
  req(`/store/products/${id}/active?is_active=${isActive}`, { method: 'PATCH' })

export const deleteProduct = (id: number): Promise<void> =>
  req(`/store/products/${id}`, { method: 'DELETE' })

export const bulkDeleteProducts = (
  ids: number[]
): Promise<{ deleted: number[]; blocked: { id: number; reason: string }[] }> =>
  req('/store/products/bulk-delete', { method: 'POST', body: JSON.stringify(ids) })

// ── Store — Inventory ─────────────────────────────────────────────────────────
export const registerEntry = (productId: number, data: InventoryEntryCreate): Promise<InventoryMovement> =>
  req(`/store/products/${productId}/inventory/entry`, { method: 'POST', body: JSON.stringify(data) })

export const registerAdjustment = (productId: number, data: InventoryAdjustmentCreate): Promise<InventoryMovement> =>
  req(`/store/products/${productId}/inventory/adjustment`, { method: 'POST', body: JSON.stringify(data) })

export const getMovements = (productId: number): Promise<InventoryMovement[]> =>
  req(`/store/products/${productId}/inventory/movements`)

export const getLowStock = (): Promise<Product[]> =>
  req('/store/inventory/low-stock')

// ── Store — Customers ─────────────────────────────────────────────────────────
export const getCustomers = (params?: { q?: string; skip?: number; limit?: number }): Promise<Customer[]> => {
  const qs = new URLSearchParams()
  if (params?.q) qs.set('q', params.q)
  if (params?.skip) qs.set('skip', String(params.skip))
  if (params?.limit) qs.set('limit', String(params.limit))
  const s = qs.toString()
  return req(`/store/customers${s ? `?${s}` : ''}`)
}

export const searchCustomers = (q: string): Promise<Customer[]> =>
  req(`/store/customers?q=${encodeURIComponent(q)}&limit=10`)

export const createCustomer = (data: CustomerCreate): Promise<Customer> =>
  req('/store/customers', { method: 'POST', body: JSON.stringify(data) })

export const customerFromMember = (memberId: number): Promise<Customer> =>
  req(`/store/customers/from-member/${memberId}`, { method: 'POST' })

export const getCustomer = (id: number): Promise<Customer> =>
  req(`/store/customers/${id}`)

export const updateCustomer = (id: number, data: CustomerUpdate): Promise<Customer> =>
  req(`/store/customers/${id}`, { method: 'PUT', body: JSON.stringify(data) })

export const deleteCustomer = (id: number): Promise<void> =>
  req(`/store/customers/${id}`, { method: 'DELETE' })

// ── Store — Sales ─────────────────────────────────────────────────────────────
export const purgeOrphanedSales = (): Promise<{ deleted: number }> =>
  req('/store/sales/purge-orphaned', { method: 'POST' })

export const createSale = (data: SaleCreate): Promise<Sale> =>
  req('/store/sales', { method: 'POST', body: JSON.stringify(data) })

export const getSales = (params?: {
  customerId?: number; status?: string; fromDate?: string; toDate?: string; skip?: number; limit?: number
}): Promise<SaleListResponse> => {
  const q = new URLSearchParams()
  if (params?.customerId) q.set('customer_id', String(params.customerId))
  if (params?.status) q.set('status', params.status)
  if (params?.fromDate) q.set('from_date', params.fromDate)
  if (params?.toDate) q.set('to_date', params.toDate)
  if (params?.skip) q.set('skip', String(params.skip))
  if (params?.limit) q.set('limit', String(params.limit))
  const qs = q.toString()
  return req(`/store/sales${qs ? `?${qs}` : ''}`)
}

export const getSale = (id: number): Promise<Sale> =>
  req(`/store/sales/${id}`)

export const cancelSale = (id: number, note?: string): Promise<Sale> =>
  req(`/store/sales/${id}/cancel${note ? `?note=${encodeURIComponent(note)}` : ''}`, { method: 'POST' })

// ── Store — Credit Payments ───────────────────────────────────────────────────
export const registerCreditPayment = (saleId: number, data: CreditPaymentCreate): Promise<CreditPayment> =>
  req(`/store/sales/${saleId}/payments`, { method: 'POST', body: JSON.stringify(data) })

export const getSalePayments = (saleId: number): Promise<CreditPayment[]> =>
  req(`/store/sales/${saleId}/payments`)

// ── Store — Cartera ───────────────────────────────────────────────────────────
export const getCartera = (params?: { status?: string; skip?: number; limit?: number }): Promise<CarteraResponse> => {
  const q = new URLSearchParams()
  if (params?.status) q.set('status', params.status)
  if (params?.skip) q.set('skip', String(params.skip))
  if (params?.limit) q.set('limit', String(params.limit))
  const qs = q.toString()
  return req(`/store/cartera${qs ? `?${qs}` : ''}`)
}

// ── Store — Reports (Fase C) ──────────────────────────────────────────────────
export const getStoreReport = (dateFrom?: string, dateTo?: string): Promise<StoreReport> => {
  const q = new URLSearchParams()
  if (dateFrom) q.set('date_from', dateFrom)
  if (dateTo) q.set('date_to', dateTo)
  const qs = q.toString()
  return req(`/store/reports${qs ? `?${qs}` : ''}`)
}

// ── Backup ────────────────────────────────────────────────────────────────────
export const getBackupStatus = (): Promise<import('../types').BackupStatus> =>
  req('/backup/status')

export const listBackups = (): Promise<import('../types').BackupListResponse> =>
  req('/backup/list')

export const createManualBackup = (): Promise<import('../types').BackupFile> =>
  req('/backup/manual', { method: 'POST' })

// ── Notifications — Fase 2 ────────────────────────────────────────────────────
export const getNotificationSettings = (): Promise<import('../types').NotificationSettings> =>
  req('/notifications/settings')

export const saveNotificationSettings = (
  data: import('../types').NotificationSettingsUpdate
): Promise<import('../types').NotificationSettings> =>
  req('/notifications/settings', { method: 'PUT', body: JSON.stringify(data) })

export const testSmtp = (): Promise<{ message: string }> =>
  req('/notifications/test-smtp', { method: 'POST' })

export const getNotificationStatus = (): Promise<import('../types').NotificationStatusPanel> =>
  req('/notifications/status')

export const getNotificationHistory = (
  page = 1, pageSize = 20
): Promise<import('../types').NotificationHistoryResponse> =>
  req(`/notifications/history?page=${page}&page_size=${pageSize}`)

export const runNotificationsNow = (): Promise<import('../types').NotificationRunResult> =>
  req('/notifications/run', { method: 'POST' })

// ── Body Measurements ─────────────────────────────────────────────────────────
export const getMeasurements = (memberId: number) =>
  req<import('../types').BodyMeasurement>(`/members/${memberId}/measurements`).catch((): null => null)

export const upsertMeasurements = (memberId: number, data: import('../types').BodyMeasurementUpsert) =>
  req<import('../types').BodyMeasurement>(`/members/${memberId}/measurements`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })

export const getFeatures = () =>
  req<import('../types').FeaturesResponse>('/config/features').catch((): null => null)

// ── Super Admin — F4-C (Licensing panel) ─────────────────────────────────────
export const getSuperAdminPanel = (): Promise<GymLicensePanel> =>
  req('/superadmin/panel')

export const updateGymInfo = (data: GymUpdate): Promise<GymInfo> =>
  req('/superadmin/gym', { method: 'PUT', body: JSON.stringify(data) })

export const changeGymPlan = (data: LicensePlanUpdate): Promise<LicenseInfo> =>
  req('/superadmin/license/plan', { method: 'PUT', body: JSON.stringify(data) })

export const updateLicenseValidity = (data: LicenseValidityUpdate): Promise<LicenseInfo> =>
  req('/superadmin/license/validity', { method: 'PUT', body: JSON.stringify(data) })

export const toggleModule = (moduleKey: string, data: ModuleToggle): Promise<ModuleStatus> =>
  req(`/superadmin/modules/${moduleKey}`, { method: 'PATCH', body: JSON.stringify(data) })
