// ── Members ──────────────────────────────────────────────────────────────────
export interface Member {
  id: number
  full_name: string
  phone: string
  document?: string
  email?: string
  notes?: string
  registration_date: string
  is_active: boolean
}

export interface MemberCreate {
  full_name: string
  phone: string
  document?: string
  email?: string
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
  status: 'active' | 'expiring' | 'expired' | 'inactive' | 'frozen' | 'exhausted'
  freeze_days: number
  is_active: boolean
  frozen_at: string | null
  frozen_days_remaining: number | null
  last_correction_at: string | null
  last_correction_reason: string | null
}

export interface MembershipStartDateCorrectionCreate {
  new_start_date: string  // "YYYY-MM-DD"
  reason: string
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
  force?: boolean
}

export interface VoucherWarning {
  has_active_voucher: boolean
  membership_id: number | null
  plan_name: string | null
  entries_remaining: number | null
  end_date: string | null
}

// ── Attendance / Valeras ───────────────────────────────────────────────────────
export interface CheckInResult {
  member_id: number
  member_name: string
  membership_id: number
  plan_name: string
  entries_total: number
  entries_used: number
  entries_remaining: number
  end_date: string
  finished: boolean
  check_in_at: string
}

export interface VoucherStatus {
  member_id: number
  member_name: string
  membership_id: number
  plan_name: string
  entries_total: number
  entries_used: number
  entries_remaining: number
  end_date: string
  attended_today: boolean
  finished: boolean
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
  frozen: number
  exhausted: number
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

export interface MembershipAlert {
  membership_id: number
  member_id: number
  member_name: string
  phone?: string
  document?: string
  plan_name: string
  end_date: string
  days_overdue?: number
}

export interface MembersByPlan {
  plan_id: number
  plan_name: string
  plan_type: string
  active_count: number
  exhausted_count: number
  expired_count: number
  frozen_count: number
  total: number
}

export interface DebtorAlert {
  customer_id: number
  customer_name: string
  outstanding_balance: number
  oldest_sale_date?: string | null
  days_overdue: number
}

export interface LowStockAlertItem {
  product_id: number
  product_name: string
  stock: number
  min_stock: number
}

export interface AlertsSummary {
  // Membership alerts
  expired_count: number
  today_count: number
  three_days_count: number
  seven_days_count: number
  expired_items: MembershipAlert[]
  today_items: MembershipAlert[]
  three_days_items: MembershipAlert[]
  seven_days_items: MembershipAlert[]
  // Store alerts (optional — default 0/empty for backward compatibility)
  debtors_count?: number
  low_stock_count?: number
  top_debtors?: DebtorAlert[]
  low_stock_items?: LowStockAlertItem[]
}

export interface DashboardKPI {
  total_active_members: number
  memberships: MembershipStatusSummary
  monthly_revenue: number
  revenue_by_plan: RevenueByPlan[]
  recent_renewals: RecentRenewal[]
  alerts?: AlertsSummary
  // Store KPIs (optional — new in Dashboard Fase B)
  membership_revenue?: number
  store_revenue?: number
  total_revenue?: number
  store_sales_count?: number
  cartera_balance?: number
  // Members by plan distribution
  members_by_plan?: MembersByPlan[]
}

// ── Store — Categories & Products ─────────────────────────────────────────────
export interface ProductCategory {
  id: number
  name: string
  description?: string
  is_active: boolean
  created_at: string
}

export interface ProductCategoryCreate {
  name: string
  description?: string
}

export interface ProductCategoryUpdate {
  name?: string
  description?: string
  is_active?: boolean
}

export interface Product {
  id: number
  category_id: number
  category_name?: string
  name: string
  description?: string
  price: number
  cost?: number
  stock: number
  min_stock: number
  is_active: boolean
  is_low_stock: boolean
  created_at: string
}

export interface ProductCreate {
  category_id: number
  name: string
  description?: string
  price: number
  cost?: number
  stock?: number
  min_stock?: number
}

export interface ProductUpdate {
  category_id?: number
  name?: string
  description?: string
  price?: number
  cost?: number
  min_stock?: number
  is_active?: boolean
}

export interface ProductListResponse {
  total: number
  items: Product[]
}

export interface InventoryMovement {
  id: number
  product_id: number
  product_name?: string
  type: 'entry' | 'sale' | 'adjustment'
  quantity: number
  stock_before: number
  stock_after: number
  note?: string
  sale_id?: number
  created_at: string
}

export interface InventoryEntryCreate {
  quantity: number
  note?: string
}

export interface InventoryAdjustmentCreate {
  quantity: number
  note: string
}

// ── Store — Customers ─────────────────────────────────────────────────────────
export interface Customer {
  id: number
  name: string
  document?: string
  phone?: string
  email?: string
  notes?: string
  member_id?: number
  member_name?: string
  debt_total: number
  created_at: string
}

export interface CustomerCreate {
  name: string
  document?: string
  phone?: string
  email?: string
  notes?: string
}

export interface CustomerUpdate {
  name?: string
  document?: string
  phone?: string
  email?: string
  notes?: string
}

// ── Store — Credit Payments ───────────────────────────────────────────────────
export interface CreditPayment {
  id: number
  sale_id: number
  amount: number
  method: string
  notes?: string
  paid_at: string
  created_at: string
}

export interface CreditPaymentCreate {
  amount: number
  method: string
  notes?: string
}

// ── Store — Sales ─────────────────────────────────────────────────────────────
export type SaleStatus = 'PAID' | 'PARTIAL' | 'PENDING' | 'CANCELLED'
export type PaymentType = 'cash' | 'credit'

export interface SaleItem {
  id: number
  product_id: number
  product_name?: string
  quantity: number
  unit_price: number
  subtotal: number
}

export interface SaleItemCreate {
  product_id: number
  quantity: number
}

export interface Sale {
  id: number
  customer_id?: number
  customer_name?: string
  sale_date: string
  subtotal: number
  discount: number
  total: number
  payment_type: PaymentType
  notes?: string
  status: SaleStatus
  amount_paid: number
  balance: number
  items: SaleItem[]
  created_at: string
}

export interface SaleCreate {
  customer_id?: number
  payment_type?: PaymentType
  discount?: number
  notes?: string
  items: SaleItemCreate[]
}

export interface SaleListResponse {
  total: number
  total_amount: number
  items: Sale[]
}

export interface CarteraKPI {
  total_balance: number
  sale_count: number
  customer_count: number
}

export interface CarteraResponse {
  items: Sale[]
  kpi: CarteraKPI
}

// ── Backup ────────────────────────────────────────────────────────────────────
export interface BackupFile {
  filename: string
  created_at: string
  size_kb: number
  type: 'automatic' | 'manual'
}

export interface BackupListResponse {
  automatic: BackupFile[]
  manual: BackupFile[]
}

export interface BackupStatus {
  last_backup: BackupFile | null
  hours_ago: number | null
  indicator: 'green' | 'orange' | 'red'
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

// ── Store Reports — Fase C ────────────────────────────────────────────────────
export interface TopProductItem {
  product_id: number
  product_name: string
  units_sold: number
  revenue: number
}

export interface LowStockItem {
  product_id: number
  product_name: string
  stock: number
  min_stock: number
  category_name?: string
}

export interface SalesKPI {
  total_sales: number
  total_revenue: number
  cash_sales_count: number
  cash_sales_amount: number
  credit_sales_count: number
  credit_sales_amount: number
  credit_collections_amount: number
  average_ticket: number
}

export interface CarteraReport {
  outstanding_balance: number
  customers_with_debt: number
  pending_sales_count: number
  partial_sales_count: number
  oldest_debt_date?: string | null
}

export interface InventoryReport {
  low_stock_count: number
  low_stock_products: LowStockItem[]
}

export interface StoreReport {
  date_from: string
  date_to: string
  sales: SalesKPI
  top_products: TopProductItem[]
  cartera: CarteraReport
  inventory: InventoryReport
}

// ── Notifications — Fase 2 ────────────────────────────────────────────────────
export interface NotificationSettings {
  smtp_host: string | null
  smtp_port: number
  smtp_user: string | null
  smtp_from_name: string | null
  smtp_from_email: string | null
  thresholds: number[]
  enabled: boolean
  is_configured: boolean
  updated_at: string | null
}

export interface NotificationSettingsUpdate {
  smtp_host?: string | null
  smtp_port?: number
  smtp_user?: string | null
  smtp_password?: string | null
  smtp_from_name?: string | null
  smtp_from_email?: string | null
  thresholds?: number[]
  enabled?: boolean
}

export interface NotificationLogRead {
  id: number
  membership_id: number | null
  member_id: number | null
  member_name: string | null
  plan_name: string | null
  end_date: string | null
  threshold_days: number
  channel: string
  status: 'sent' | 'failed'
  error_message: string | null
  sent_at: string
  recipient: string | null
}

export interface NotificationHistoryResponse {
  items: NotificationLogRead[]
  total: number
  page: number
  pages: number
}

export interface NotificationStatusPanel {
  is_configured: boolean
  enabled: boolean
  last_run_at: string | null
  sent_today: number
  failed_today: number
  pending_count: number
}

export interface NotificationRunResult {
  sent: number
  skipped: number
  failed: number
  message: string
}

// ── Auth — F2 ─────────────────────────────────────────────────────────────────
export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  is_temporary: boolean
}

export interface ChangePasswordRequest {
  new_password: string
  confirm_password: string
}

// ── Platform Features (F4-A/B) ────────────────────────────────────────────────
export interface PremiumFeatures {
  notifications: boolean
  body_tracking: boolean
  store: boolean
}

export interface FeaturesResponse {
  core: Record<string, boolean>
  premium: PremiumFeatures
}

// ── Licensing — F4-C (Super Admin panel) ─────────────────────────────────────
export type UserRole = 'admin' | 'super_admin'

export interface GymInfo {
  id: number
  name: string
  slug: string
  contact_name: string | null
  contact_email: string | null
  active: boolean
}

export interface LicenseInfo {
  id: number
  plan_name: string
  valid_from: string | null
  valid_until: string | null
  status: 'active' | 'expired' | 'suspended'
  notes: string | null
  updated_at: string | null
}

export interface ModuleStatus {
  module_key: string
  name: string
  active: boolean
  source: 'plan' | 'addon'
  activated_at: string | null
  deactivated_at: string | null
}

export interface GymLicensePanel {
  gym: GymInfo
  license: LicenseInfo | null
  modules: ModuleStatus[]
}

export interface GymUpdate {
  name?: string
  contact_name?: string | null
  contact_email?: string | null
}

export interface LicensePlanUpdate {
  plan_name: string
}

export interface LicenseValidityUpdate {
  valid_from?: string | null
  valid_until?: string | null
}

export interface ModuleToggle {
  active: boolean
  notes?: string
}
