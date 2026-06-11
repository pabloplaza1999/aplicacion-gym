import { useEffect, useState, useCallback } from 'react'
import type {
  ProductCategory, Product, Sale, InventoryMovement,
  ProductCreate, ProductUpdate, SaleCreate, SaleItemCreate,
  Customer, CustomerCreate, CreditPaymentCreate, CarteraKPI,
  StoreReport,
} from '../types'
import {
  getCategories, createCategory, updateCategory, toggleCategory, deleteCategory,
  getProducts, createProduct, updateProduct, toggleProduct, bulkDeleteProducts,
  registerEntry, registerAdjustment, getMovements,
  createSale, getSales, cancelSale, purgeOrphanedSales,
  searchCustomers, createCustomer, deleteCustomer,
  registerCreditPayment, getSalePayments,
  getCartera, getCustomers,
  getStoreReport,
} from '../services/api'
import Spinner from '../components/Spinner'
import StatCard from '../components/StatCard'

// ── helpers ───────────────────────────────────────────────────────────────────
function fmt(n: number) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n)
}

function daysSince(dateStr: string) {
  return Math.floor((Date.now() - new Date(dateStr).getTime()) / 86400000)
}

type Tab = 'products' | 'sales' | 'categories' | 'cartera' | 'customers' | 'reports'

// ── StatusBadge ────────────────────────────────────────────────────────────────
function StatusBadge({ status }: { status: string }) {
  const cfg: Record<string, { label: string; cls: string }> = {
    PAID:      { label: 'Pagada',    cls: 'text-green-400 bg-green-500/10 border-green-500/20' },
    PENDING:   { label: 'Pendiente', cls: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20' },
    PARTIAL:   { label: 'Parcial',   cls: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
    CANCELLED: { label: 'Anulada',   cls: 'text-red-400 bg-red-500/10 border-red-500/20' },
  }
  const c = cfg[status] ?? { label: status, cls: 'text-gray-400 bg-gray-500/10 border-gray-500/20' }
  return <span className={`text-xs border px-1.5 py-0.5 rounded font-mono ${c.cls}`}>{c.label}</span>
}

// ── ProductForm ────────────────────────────────────────────────────────────────
function ProductForm({
  categories, initial, onSave, onCancel,
}: {
  categories: ProductCategory[]
  initial?: Product | null
  onSave: () => void
  onCancel: () => void
}) {
  const [form, setForm] = useState({
    category_id: initial?.category_id ?? (categories[0]?.id ?? 0),
    name: initial?.name ?? '',
    description: initial?.description ?? '',
    price: initial?.price ?? 0,
    cost: initial?.cost ?? 0,
    stock: initial?.stock ?? 0,
    min_stock: initial?.min_stock ?? 0,
  })
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true); setErr('')
    try {
      if (initial) {
        await updateProduct(initial.id, {
          category_id: form.category_id, name: form.name,
          description: form.description || undefined, price: form.price,
          cost: form.cost || undefined, min_stock: form.min_stock,
        } as ProductUpdate)
        const diff = form.stock - initial.stock
        if (diff !== 0) {
          await registerAdjustment(initial.id, { quantity: diff, note: 'Ajuste manual desde edición de producto' })
        }
      } else {
        await createProduct({
          category_id: form.category_id, name: form.name,
          description: form.description || undefined, price: form.price,
          cost: form.cost || undefined, stock: form.stock, min_stock: form.min_stock,
        } as ProductCreate)
      }
      onSave()
    } catch (e: any) { setErr(e.message) }
    finally { setSaving(false) }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {err && <p className="text-xs text-brand-400 font-mono bg-brand-500/10 px-3 py-2 rounded">{err}</p>}
      <div className="grid grid-cols-2 gap-3">
        <div className="col-span-2">
          <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Categoría</label>
          <select value={form.category_id} onChange={e => setForm(f => ({ ...f, category_id: +e.target.value }))} className="input w-full">
            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div className="col-span-2">
          <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Nombre *</label>
          <input required value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} className="input w-full" placeholder="Proteína whey 1 kg" />
        </div>
        <div className="col-span-2">
          <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Descripción</label>
          <input value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} className="input w-full" placeholder="Opcional" />
        </div>
        <div>
          <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Precio venta *</label>
          <input type="number" min="0" step="100" required value={form.price || ''} onChange={e => setForm(f => ({ ...f, price: +e.target.value }))} className="input w-full" placeholder="0" />
        </div>
        <div>
          <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Costo</label>
          <input type="number" min="0" step="100" value={form.cost || ''} onChange={e => setForm(f => ({ ...f, cost: +e.target.value }))} className="input w-full" placeholder="0" />
        </div>
        <div>
          <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">{initial ? 'Stock actual' : 'Stock inicial'}</label>
          <input type="number" min="0" value={form.stock || ''} onChange={e => setForm(f => ({ ...f, stock: +e.target.value }))} className="input w-full" placeholder="0" />
        </div>
        <div>
          <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Stock mínimo</label>
          <input type="number" min="0" value={form.min_stock || ''} onChange={e => setForm(f => ({ ...f, min_stock: +e.target.value }))} className="input w-full" placeholder="0" />
          <p className="text-xs text-gray-600 mt-1">Alerta cuando el stock llegue a este nivel</p>
        </div>
      </div>
      <div className="flex gap-2 pt-1">
        <button type="submit" disabled={saving} className="btn-primary flex-1">{saving ? 'Guardando…' : initial ? 'Actualizar' : 'Crear producto'}</button>
        <button type="button" onClick={onCancel} className="btn-ghost flex-1">Cancelar</button>
      </div>
    </form>
  )
}

// ── QuickCustomerModal ─────────────────────────────────────────────────────────
function QuickCustomerModal({
  initialName, onCreated, onClose,
}: {
  initialName?: string
  onCreated: (c: Customer) => void
  onClose: () => void
}) {
  const [form, setForm] = useState<CustomerCreate>({ name: initialName ?? '', document: '', phone: '' })
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true); setErr('')
    try {
      const c = await createCustomer({
        name: form.name,
        document: form.document || undefined,
        phone: form.phone || undefined,
      })
      onCreated(c)
    } catch (e: any) { setErr(e.message) }
    finally { setSaving(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-surface-card border border-surface-border rounded-xl w-full max-w-sm">
        <div className="flex items-center justify-between px-5 py-4 border-b border-surface-border">
          <h3 className="text-white font-medium">Nuevo cliente</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors">✕</button>
        </div>
        <form onSubmit={handleSubmit} className="p-5 space-y-3">
          {err && <p className="text-xs text-brand-400 font-mono bg-brand-500/10 px-3 py-2 rounded">{err}</p>}
          <div>
            <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Nombre *</label>
            <input required value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} className="input w-full" placeholder="Nombre completo" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Documento</label>
            <input value={form.document ?? ''} onChange={e => setForm(f => ({ ...f, document: e.target.value }))} className="input w-full" placeholder="Cédula o NIT (opcional)" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Teléfono</label>
            <input value={form.phone ?? ''} onChange={e => setForm(f => ({ ...f, phone: e.target.value }))} className="input w-full" placeholder="Opcional" />
          </div>
          <div className="flex gap-2 pt-1">
            <button type="submit" disabled={saving} className="btn-primary flex-1">{saving ? 'Creando…' : 'Crear cliente'}</button>
            <button type="button" onClick={onClose} className="btn-ghost flex-1">Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ── CustomerPicker ─────────────────────────────────────────────────────────────
function CustomerPicker({
  selected, onSelect,
}: {
  selected: Customer | null
  onSelect: (c: Customer | null) => void
}) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Customer[]>([])
  const [showCreate, setShowCreate] = useState(false)
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    if (!query.trim()) { setResults([]); return }
    const timer = setTimeout(async () => {
      setSearching(true)
      try { setResults(await searchCustomers(query)) }
      catch { setResults([]) }
      finally { setSearching(false) }
    }, 300)
    return () => clearTimeout(timer)
  }, [query])

  if (selected) return (
    <div className="flex items-center justify-between bg-surface-raised border border-surface-border rounded px-3 py-2">
      <div>
        <p className="text-white text-sm font-medium">{selected.name}</p>
        {selected.document && <p className="text-xs text-gray-500 font-mono">{selected.document}</p>}
        {selected.debt_total > 0 && <p className="text-xs text-yellow-400 font-mono">Deuda previa: {fmt(selected.debt_total)}</p>}
      </div>
      <button onClick={() => onSelect(null)} className="text-gray-500 hover:text-white transition-colors text-sm ml-3">✕</button>
    </div>
  )

  return (
    <div className="relative">
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        className="input w-full text-sm"
        placeholder="Buscar por nombre, documento o teléfono…"
      />
      {searching && <p className="text-xs text-gray-500 mt-1">Buscando…</p>}
      {!searching && query.trim() && (
        <div className="absolute z-10 w-full bg-surface-card border border-surface-border rounded-lg shadow-lg mt-1 overflow-hidden">
          {results.map(c => (
            <button key={c.id} onClick={() => { onSelect(c); setQuery(''); setResults([]) }}
              className="w-full px-3 py-2.5 text-left hover:bg-surface-raised transition-colors border-b border-surface-border/50 last:border-0">
              <span className="text-white text-sm">{c.name}</span>
              {c.document && <span className="text-gray-500 font-mono text-xs ml-2">{c.document}</span>}
              {c.debt_total > 0 && <span className="text-yellow-400 text-xs ml-2">· deuda {fmt(c.debt_total)}</span>}
            </button>
          ))}
          {results.length === 0 && <p className="text-gray-600 text-xs px-3 py-2 font-mono">Sin resultados</p>}
          <button onClick={() => setShowCreate(true)}
            className="w-full px-3 py-2 text-left text-xs text-brand-400 hover:bg-surface-raised transition-colors border-t border-surface-border">
            + Crear nuevo cliente
          </button>
        </div>
      )}
      {showCreate && (
        <QuickCustomerModal
          initialName={query}
          onCreated={c => { onSelect(c); setShowCreate(false); setQuery('') }}
          onClose={() => setShowCreate(false)}
        />
      )}
    </div>
  )
}

// ── SaleCart ───────────────────────────────────────────────────────────────────
function SaleCart({ products, onSaved }: { products: Product[]; onSaved: () => void }) {
  const [items, setItems] = useState<(SaleItemCreate & { name: string; price: number })[]>([])
  const [discount, setDiscount] = useState(0)
  const [notes, setNotes] = useState('')
  const [paymentType, setPaymentType] = useState<'cash' | 'credit'>('cash')
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null)
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')
  const [done, setDone] = useState<Sale | null>(null)

  const subtotal = items.reduce((s, i) => s + i.price * i.quantity, 0)
  const total = Math.max(0, subtotal - discount)

  function addProduct(productId: number) {
    const p = products.find(x => x.id === productId)
    if (!p) return
    setItems(prev => {
      const existing = prev.find(x => x.product_id === productId)
      if (existing) return prev.map(x => x.product_id === productId ? { ...x, quantity: x.quantity + 1 } : x)
      return [...prev, { product_id: p.id, quantity: 1, name: p.name, price: p.price }]
    })
  }

  function removeItem(productId: number) { setItems(prev => prev.filter(x => x.product_id !== productId)) }

  function setQty(productId: number, qty: number) {
    if (qty <= 0) return removeItem(productId)
    setItems(prev => prev.map(x => x.product_id === productId ? { ...x, quantity: qty } : x))
  }

  async function handleSale() {
    if (items.length === 0) return
    if (paymentType === 'credit' && !selectedCustomer) { setErr('Selecciona un cliente para la venta a crédito.'); return }
    setSaving(true); setErr('')
    try {
      const payload: SaleCreate = {
        customer_id: selectedCustomer?.id,
        payment_type: paymentType,
        discount,
        notes: notes || undefined,
        items: items.map(i => ({ product_id: i.product_id, quantity: i.quantity })),
      }
      const sale = await createSale(payload)
      setDone(sale)
      onSaved()
    } catch (e: any) { setErr(e.message) }
    finally { setSaving(false) }
  }

  function reset() { setDone(null); setItems([]); setDiscount(0); setNotes(''); setPaymentType('cash'); setSelectedCustomer(null) }

  if (done) return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-full bg-green-500/10 flex items-center justify-center">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5 text-green-400"><polyline points="20 6 9 17 4 12" /></svg>
        </div>
        <div>
          <p className="text-white font-medium">Venta registrada</p>
          <p className="text-xs text-gray-500 font-mono">#{done.id} · {fmt(done.total)} · <StatusBadge status={done.status} /></p>
        </div>
      </div>
      <button className="btn-ghost w-full" onClick={reset}>Nueva venta</button>
    </div>
  )

  return (
    <div className="space-y-4">
      {err && <p className="text-xs text-brand-400 font-mono bg-brand-500/10 px-3 py-2 rounded">{err}</p>}

      <div>
        <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Tipo de pago</label>
        <div className="flex gap-2">
          {(['cash', 'credit'] as const).map(pt => (
            <button key={pt} onClick={() => { setPaymentType(pt); if (pt === 'cash') setSelectedCustomer(null) }}
              className={`flex-1 py-2 text-sm rounded border transition-colors ${paymentType === pt ? 'border-brand-500 text-white bg-brand-500/10' : 'border-surface-border text-gray-500 hover:text-gray-300'}`}>
              {pt === 'cash' ? 'Contado' : 'A crédito'}
            </button>
          ))}
        </div>
      </div>

      {paymentType === 'credit' && (
        <div>
          <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Cliente *</label>
          <CustomerPicker selected={selectedCustomer} onSelect={setSelectedCustomer} />
        </div>
      )}

      <div>
        <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Agregar producto</label>
        <select className="input w-full" defaultValue="" onChange={e => { if (e.target.value) addProduct(+e.target.value); e.target.value = '' }}>
          <option value="">Seleccionar…</option>
          {products.filter(p => p.is_active && p.stock > 0).map(p => (
            <option key={p.id} value={p.id}>{p.name} — {fmt(p.price)} (stock: {p.stock})</option>
          ))}
        </select>
      </div>

      {items.length > 0 && (
        <div className="space-y-2">
          {items.map(item => (
            <div key={item.product_id} className="flex items-center justify-between gap-2 text-sm">
              <span className="text-gray-300 flex-1 truncate">{item.name}</span>
              <div className="flex items-center gap-1">
                <button onClick={() => setQty(item.product_id, item.quantity - 1)} className="w-6 h-6 rounded text-gray-400 hover:text-white hover:bg-surface-raised transition-colors">−</button>
                <span className="w-6 text-center text-white font-mono text-xs">{item.quantity}</span>
                <button onClick={() => setQty(item.product_id, item.quantity + 1)} className="w-6 h-6 rounded text-gray-400 hover:text-white hover:bg-surface-raised transition-colors">+</button>
              </div>
              <span className="text-gray-400 font-mono text-xs w-24 text-right">{fmt(item.price * item.quantity)}</span>
              <button onClick={() => removeItem(item.product_id)} className="text-gray-600 hover:text-brand-400 transition-colors text-xs">✕</button>
            </div>
          ))}
        </div>
      )}

      <div className="border-t border-surface-border pt-3 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Subtotal</span>
          <span className="text-gray-300 font-mono">{fmt(subtotal)}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-500 text-sm">Descuento</span>
          <input type="number" min="0" step="100" value={discount} onChange={e => setDiscount(+e.target.value)} className="input flex-1 text-right text-sm" />
        </div>
        <div className="flex justify-between text-sm font-medium">
          <span className="text-white">Total</span>
          <span className="text-brand-400 font-mono font-bold">{fmt(total)}</span>
        </div>
      </div>

      <input value={notes} onChange={e => setNotes(e.target.value)} className="input w-full text-sm" placeholder="Notas (opcional)" />

      <button onClick={handleSale} disabled={saving || items.length === 0}
        className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed">
        {saving ? 'Registrando…' : `Registrar venta · ${fmt(total)}`}
      </button>
    </div>
  )
}

// ── MovementsModal ─────────────────────────────────────────────────────────────
function MovementsModal({ product, onClose }: { product: Product; onClose: () => void }) {
  const [movements, setMovements] = useState<InventoryMovement[]>([])
  const [loading, setLoading] = useState(true)
  const [mode, setMode] = useState<'entry' | 'adjustment' | null>(null)
  const [qtyStr, setQtyStr] = useState('')
  const [note, setNote] = useState('')
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')

  const load = useCallback(() => {
    setLoading(true)
    getMovements(product.id).then(setMovements).finally(() => setLoading(false))
  }, [product.id])

  useEffect(() => { load() }, [load])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const qty = parseInt(qtyStr, 10)
    if (isNaN(qty) || qty === 0) { setErr('Ingresa una cantidad válida distinta de cero.'); return }
    setSaving(true); setErr('')
    try {
      if (mode === 'entry') await registerEntry(product.id, { quantity: qty, note: note || undefined })
      else if (mode === 'adjustment') await registerAdjustment(product.id, { quantity: qty, note })
      setMode(null); setQtyStr(''); setNote('')
      load()
    } catch (e: any) { setErr(e.message) }
    finally { setSaving(false) }
  }

  const typeLabel = (t: string) => t === 'entry' ? 'Entrada' : t === 'sale' ? 'Venta' : 'Ajuste'
  const typeColor = (t: string) => t === 'entry' ? 'text-green-400' : t === 'sale' ? 'text-blue-400' : 'text-yellow-400'

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-surface-card border border-surface-border rounded-xl w-full max-w-md max-h-[85vh] flex flex-col">
        <div className="flex items-center justify-between px-5 py-4 border-b border-surface-border">
          <div>
            <h3 className="text-white font-medium">{product.name}</h3>
            <p className="text-xs text-gray-500 font-mono">Stock actual: {product.stock}</p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors">✕</button>
        </div>
        <div className="p-4 border-b border-surface-border">
          <div className="flex gap-2">
            <button onClick={() => { setMode('entry'); setQtyStr(''); setNote(''); setErr('') }} className="btn-ghost text-xs flex-1">+ Entrada</button>
            <button onClick={() => { setMode('adjustment'); setQtyStr(''); setNote(''); setErr('') }} className="btn-ghost text-xs flex-1">Ajuste</button>
          </div>
          {mode && (
            <form onSubmit={handleSubmit} className="mt-3 space-y-2">
              {err && <p className="text-xs text-brand-400">{err}</p>}
              <div className="flex gap-2">
                <input type="number" step="1" required value={qtyStr} placeholder={mode === 'entry' ? 'Ej: 10' : 'Ej: -5 o 3'} onChange={e => setQtyStr(e.target.value)} className="input flex-1 text-sm" />
                <input value={note} onChange={e => setNote(e.target.value)} placeholder={mode === 'adjustment' ? 'Motivo *' : 'Nota'} required={mode === 'adjustment'} className="input flex-1 text-sm" />
              </div>
              <div className="flex gap-2">
                <button type="submit" disabled={saving} className="btn-primary flex-1 text-xs">{saving ? '…' : 'Registrar'}</button>
                <button type="button" onClick={() => setMode(null)} className="btn-ghost flex-1 text-xs">Cancelar</button>
              </div>
            </form>
          )}
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? <Spinner /> : movements.length === 0 ? (
            <p className="text-gray-600 text-sm font-mono text-center py-4">Sin movimientos</p>
          ) : (
            <div className="space-y-2">
              {movements.map(m => (
                <div key={m.id} className="flex items-center justify-between text-xs">
                  <div>
                    <span className={`font-medium ${typeColor(m.type)}`}>{typeLabel(m.type)}</span>
                    {m.note && <span className="text-gray-500 ml-2">{m.note}</span>}
                  </div>
                  <div className="text-right">
                    <span className={`font-mono font-bold ${m.quantity > 0 ? 'text-green-400' : 'text-red-400'}`}>{m.quantity > 0 ? '+' : ''}{m.quantity}</span>
                    <span className="text-gray-600 ml-2 font-mono">→ {m.stock_after}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ── AbonoModal ─────────────────────────────────────────────────────────────────
function AbonoModal({ sale, onDone, onClose }: { sale: Sale; onClose: () => void; onDone: () => void }) {
  const [form, setForm] = useState<CreditPaymentCreate>({ amount: sale.balance, method: 'cash', notes: '' })
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true); setErr('')
    try {
      await registerCreditPayment(sale.id, { amount: form.amount, method: form.method, notes: form.notes || undefined })
      onDone()
    } catch (e: any) { setErr(e.message) }
    finally { setSaving(false) }
  }

  const METHODS = [
    { value: 'cash', label: 'Efectivo' },
    { value: 'transfer', label: 'Transferencia' },
    { value: 'qr', label: 'QR' },
    { value: 'nequi', label: 'Nequi' },
  ]

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-surface-card border border-surface-border rounded-xl w-full max-w-sm">
        <div className="flex items-center justify-between px-5 py-4 border-b border-surface-border">
          <div>
            <h3 className="text-white font-medium">Registrar abono</h3>
            <p className="text-xs text-gray-500 font-mono">Venta #{sale.id} · Saldo: {fmt(sale.balance)}</p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors">✕</button>
        </div>
        <form onSubmit={handleSubmit} className="p-5 space-y-3">
          {err && <p className="text-xs text-brand-400 font-mono bg-brand-500/10 px-3 py-2 rounded">{err}</p>}
          {sale.customer_name && (
            <p className="text-sm text-gray-400">Cliente: <span className="text-white">{sale.customer_name}</span></p>
          )}
          <div>
            <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Monto abono *</label>
            <input type="number" required min="1" max={sale.balance} step="any"
              value={form.amount || ''}
              onChange={e => setForm(f => ({ ...f, amount: +e.target.value }))}
              className="input w-full" placeholder="0" />
            <p className="text-xs text-gray-600 mt-1">Máximo: {fmt(sale.balance)}</p>
          </div>
          <div>
            <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Método *</label>
            <select value={form.method} onChange={e => setForm(f => ({ ...f, method: e.target.value }))} className="input w-full">
              {METHODS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 uppercase tracking-wider mb-1">Notas</label>
            <input value={form.notes ?? ''} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} className="input w-full" placeholder="Opcional" />
          </div>
          <div className="flex gap-2 pt-1">
            <button type="submit" disabled={saving} className="btn-primary flex-1">{saving ? 'Registrando…' : 'Registrar abono'}</button>
            <button type="button" onClick={onClose} className="btn-ghost flex-1">Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ── ProductsTab ────────────────────────────────────────────────────────────────
function ProductsTab({ categories, onUpdated }: { categories: ProductCategory[]; onUpdated?: () => void }) {
  const [products, setProducts] = useState<Product[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [catFilter, setCatFilter] = useState(0)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Product | null>(null)
  const [movProduct, setMovProduct] = useState<Product | null>(null)
  const [err, setErr] = useState('')
  const [selected, setSelected] = useState<Set<number>>(new Set())
  const [bulkDeleting, setBulkDeleting] = useState(false)

  const load = useCallback(() => {
    setLoading(true)
    getProducts({ search, categoryId: catFilter || undefined })
      .then(r => { setProducts(r.items); setTotal(r.total) })
      .catch(e => setErr(e.message))
      .finally(() => setLoading(false))
  }, [search, catFilter])

  useEffect(() => { load() }, [load])
  useEffect(() => { setSelected(new Set()) }, [products])

  async function handleToggle(p: Product) {
    try { await toggleProduct(p.id, !p.is_active); load() }
    catch (e: any) { setErr(e.message) }
  }

  function toggleSelect(id: number) {
    setSelected(prev => { const next = new Set(prev); if (next.has(id)) next.delete(id); else next.add(id); return next })
  }

  function toggleAll() {
    setSelected(selected.size === products.length ? new Set() : new Set(products.map(p => p.id)))
  }

  async function handleDeleteOne(p: Product) {
    if (!window.confirm(`¿Eliminar "${p.name}"? Se eliminarán también sus ventas y movimientos.`)) return
    setErr('')
    try { await bulkDeleteProducts([p.id]); load() }
    catch (e: any) { setErr(e.message) }
  }

  async function handleBulkDelete() {
    if (selected.size === 0) return
    if (!window.confirm(`¿Eliminar ${selected.size} producto${selected.size !== 1 ? 's' : ''}? Esta acción no se puede deshacer.`)) return
    setBulkDeleting(true); setErr('')
    try {
      const result = await bulkDeleteProducts(Array.from(selected))
      if (result.blocked.length > 0) {
        const reasons = result.blocked.map(b => b.reason).filter((v, i, a) => a.indexOf(v) === i).join('; ')
        setErr(`${result.deleted.length} eliminados. No se pudo eliminar ${result.blocked.length}: ${reasons}`)
      }
      load()
    } catch (e: any) { setErr(e.message) }
    finally { setBulkDeleting(false) }
  }

  const allSelected = products.length > 0 && selected.size === products.length

  return (
    <div className="space-y-4">
      {err && <p className="text-xs text-brand-400 font-mono bg-brand-500/10 px-3 py-2 rounded">{err}</p>}
      <div className="flex gap-2">
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Buscar producto…" className="input flex-1" />
        <select value={catFilter} onChange={e => setCatFilter(+e.target.value)} className="input w-40">
          <option value={0}>Todas</option>
          {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <button onClick={() => { setEditing(null); setShowForm(true) }} className="btn-primary text-sm">+ Producto</button>
      </div>
      {showForm && (
        <div className="card">
          <ProductForm categories={categories} initial={editing} onSave={() => { setShowForm(false); load(); onUpdated?.() }} onCancel={() => setShowForm(false)} />
        </div>
      )}
      {selected.size > 0 && (
        <div className="flex items-center gap-3 px-3 py-2 bg-brand-500/10 border border-brand-500/20 rounded-lg">
          <span className="text-xs text-brand-400 font-mono flex-1">{selected.size} producto{selected.size !== 1 ? 's' : ''} seleccionado{selected.size !== 1 ? 's' : ''}</span>
          <button onClick={handleBulkDelete} disabled={bulkDeleting} className="text-xs px-3 py-1.5 rounded border border-red-500/30 text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-50">{bulkDeleting ? 'Eliminando…' : 'Eliminar seleccionados'}</button>
          <button onClick={() => setSelected(new Set())} className="text-xs text-gray-500 hover:text-gray-300 transition-colors">Cancelar</button>
        </div>
      )}
      {loading ? <Spinner /> : (
        <div>
          <div className="flex items-center gap-3 mb-3">
            <input type="checkbox" checked={allSelected} onChange={toggleAll} className="w-4 h-4 rounded accent-brand-500 cursor-pointer" title="Seleccionar todos" />
            <p className="text-xs text-gray-600 font-mono">{total} producto{total !== 1 ? 's' : ''}</p>
          </div>
          <div className="space-y-2">
            {products.map(p => (
              <div key={p.id} className={`card flex items-center gap-3 py-3 transition-colors ${!p.is_active ? 'opacity-60' : ''} ${selected.has(p.id) ? 'border-brand-500/30 bg-brand-500/5' : ''}`}>
                <input type="checkbox" checked={selected.has(p.id)} onChange={() => toggleSelect(p.id)} className="w-4 h-4 rounded accent-brand-500 cursor-pointer shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-white text-sm font-medium">{p.name}</span>
                    {p.is_low_stock && <span className="text-xs bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 px-1.5 py-0.5 rounded font-mono">low stock</span>}
                    {!p.is_active && <span className="text-xs text-gray-600">inactivo</span>}
                  </div>
                  <p className="text-xs text-gray-500 font-mono mt-0.5">{p.category_name} · stock: {p.stock}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-brand-400 font-mono font-bold text-sm">{fmt(p.price)}</p>
                  {p.cost ? <p className="text-gray-600 font-mono text-xs">costo: {fmt(p.cost)}</p> : null}
                </div>
                <div className="flex gap-1">
                  <button onClick={() => setMovProduct(p)} title="Inventario" className="btn-ghost text-xs px-2 py-1">📦</button>
                  <button onClick={() => { setEditing(p); setShowForm(true) }} className="btn-ghost text-xs px-2 py-1">Editar</button>
                  <button onClick={() => handleToggle(p)} className={`text-xs px-2 py-1 rounded border transition-colors ${p.is_active ? 'border-brand-500/20 text-brand-400 hover:bg-brand-500/10' : 'border-green-500/20 text-green-400 hover:bg-green-500/10'}`}>{p.is_active ? 'Desactivar' : 'Activar'}</button>
                  <button onClick={() => handleDeleteOne(p)} className="text-xs px-2 py-1 rounded border border-red-500/20 text-red-400 hover:bg-red-500/10 transition-colors">Eliminar</button>
                </div>
              </div>
            ))}
            {products.length === 0 && <p className="text-gray-600 font-mono text-sm text-center py-6">Sin productos</p>}
          </div>
        </div>
      )}
      {movProduct && <MovementsModal product={movProduct} onClose={() => { setMovProduct(null); load() }} />}
    </div>
  )
}

// ── SalesTab ───────────────────────────────────────────────────────────────────
function SalesTab({ products }: { products: Product[] }) {
  const [sales, setSales] = useState<Sale[]>([])
  const [totalAmt, setTotalAmt] = useState(0)
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState('')
  const [cancellingId, setCancellingId] = useState<number | null>(null)
  const [purging, setPurging] = useState(false)

  const load = useCallback(() => {
    setLoading(true)
    getSales({ limit: 50 })
      .then(r => { setSales(r.items); setTotalAmt(r.total_amount) })
      .catch(e => setErr(e.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { load() }, [load])

  async function handleCancel(id: number) {
    if (!window.confirm('¿Anular esta venta? Se repondrá el stock.')) return
    setCancellingId(id)
    try { await cancelSale(id); load() }
    catch (e: any) { setErr(e.message) }
    finally { setCancellingId(null) }
  }

  async function handlePurge() {
    const orphaned = sales.filter(s => s.status === 'CANCELLED' && !s.customer_id)
    if (orphaned.length === 0) { setErr('No hay ventas anuladas sin cliente para limpiar.'); return }
    if (!window.confirm(`¿Eliminar ${orphaned.length} venta${orphaned.length !== 1 ? 's' : ''} anulada${orphaned.length !== 1 ? 's' : ''} sin cliente? Esta acción no se puede deshacer.`)) return
    setPurging(true); setErr('')
    try {
      const result = await purgeOrphanedSales()
      load()
      if (result.deleted === 0) setErr('No se encontraron registros para limpiar.')
    } catch (e: any) { setErr(e.message) }
    finally { setPurging(false) }
  }

  const canCancel = (s: Sale) => s.status === 'PAID' || s.status === 'PENDING'
  const orphanedCount = sales.filter(s => s.status === 'CANCELLED' && !s.customer_id).length

  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <div className="xl:col-span-2 space-y-4">
        {err && <p className="text-xs text-brand-400 font-mono bg-brand-500/10 px-3 py-2 rounded">{err}</p>}
        <div className="flex items-center justify-between gap-3">
          <p className="text-xs text-gray-600 font-mono">{sales.length} ventas · {fmt(totalAmt)} cobrado</p>
          {orphanedCount > 0 && (
            <button onClick={handlePurge} disabled={purging}
              className="text-xs px-3 py-1.5 rounded border border-red-500/20 text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-50">
              {purging ? 'Limpiando…' : `Limpiar ${orphanedCount} anulada${orphanedCount !== 1 ? 's' : ''} sin cliente`}
            </button>
          )}
        </div>
        {loading ? <Spinner /> : (
          <div className="space-y-2">
            {sales.map(sale => (
              <div key={sale.id} className={`card py-3 ${sale.status === 'CANCELLED' ? 'opacity-50' : ''}`}>
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-white text-sm font-mono font-bold">#{sale.id}</span>
                      <StatusBadge status={sale.status} />
                      {sale.customer_name && <span className="text-xs text-gray-400">{sale.customer_name}</span>}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{sale.items.map(i => `${i.product_name} x${i.quantity}`).join(', ')}</p>
                    <p className="text-xs text-gray-600 font-mono mt-0.5">{new Date(sale.sale_date).toLocaleDateString('es-CO')}</p>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-brand-400 font-mono font-bold">{fmt(sale.total)}</p>
                    {sale.discount > 0 && <p className="text-xs text-gray-600 font-mono">desc: {fmt(sale.discount)}</p>}
                    {sale.balance > 0 && <p className="text-xs text-yellow-400 font-mono">saldo: {fmt(sale.balance)}</p>}
                    {canCancel(sale) && (
                      <button onClick={() => handleCancel(sale.id)} disabled={cancellingId === sale.id}
                        className="text-xs text-red-400 hover:text-red-300 transition-colors mt-1">
                        Anular
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {sales.length === 0 && <p className="text-gray-600 font-mono text-sm text-center py-6">Sin ventas</p>}
          </div>
        )}
      </div>
      <div className="card">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-1 h-5 bg-brand-500 rounded-full shadow-brand-sm" />
          <h3 className="font-display text-base tracking-widest text-white uppercase">Nueva venta</h3>
        </div>
        <SaleCart products={products} onSaved={load} />
      </div>
    </div>
  )
}

// ── CarteraTab ─────────────────────────────────────────────────────────────────
function CarteraTab() {
  const [data, setData] = useState<{ items: Sale[]; kpi: CarteraKPI } | null>(null)
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [abonoSale, setAbonoSale] = useState<Sale | null>(null)
  const [detailSale, setDetailSale] = useState<Sale | null>(null)
  const [payments, setPayments] = useState<import('../types').CreditPayment[]>([])
  const [loadingPayments, setLoadingPayments] = useState(false)

  const load = useCallback(() => {
    setLoading(true)
    getCartera({ status: statusFilter || undefined })
      .then(r => setData(r))
      .catch(e => setErr(e.message))
      .finally(() => setLoading(false))
  }, [statusFilter])

  useEffect(() => { load() }, [load])

  async function openDetail(sale: Sale) {
    setDetailSale(sale)
    setLoadingPayments(true)
    try { setPayments(await getSalePayments(sale.id)) }
    catch { setPayments([]) }
    finally { setLoadingPayments(false) }
  }

  const kpi = data?.kpi
  const items = data?.items ?? []

  return (
    <div className="space-y-6">
      {err && <p className="text-xs text-brand-400 font-mono bg-brand-500/10 px-3 py-2 rounded">{err}</p>}

      {kpi && (
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Cartera total', value: fmt(kpi.total_balance), sub: 'saldo pendiente' },
            { label: 'Ventas en deuda', value: String(kpi.sale_count), sub: 'PENDING + PARTIAL' },
            { label: 'Clientes con deuda', value: String(kpi.customer_count), sub: 'clientes únicos' },
          ].map(card => (
            <div key={card.label} className="card">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{card.label}</p>
              <p className="text-2xl font-display text-white font-bold">{card.value}</p>
              <p className="text-xs text-gray-600 font-mono mt-0.5">{card.sub}</p>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-2">
        {(['', 'PENDING', 'PARTIAL'] as const).map(s => (
          <button key={s} onClick={() => setStatusFilter(s)}
            className={`px-3 py-1.5 text-xs rounded border transition-colors ${statusFilter === s ? 'border-brand-500 text-white bg-brand-500/10' : 'border-surface-border text-gray-500 hover:text-gray-300'}`}>
            {s === '' ? 'Todos' : s === 'PENDING' ? 'Pendiente' : 'Parcial'}
          </button>
        ))}
      </div>

      {loading ? <Spinner /> : items.length === 0 ? (
        <p className="text-gray-600 font-mono text-sm text-center py-10">Sin ventas en cartera</p>
      ) : (
        <div className="space-y-2">
          {items.map(sale => (
            <div key={sale.id} className="card py-3">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-white font-mono text-sm font-bold">#{sale.id}</span>
                    <StatusBadge status={sale.status} />
                    {sale.customer_name && <span className="text-gray-300 text-sm">{sale.customer_name}</span>}
                    <span className="text-gray-600 text-xs font-mono">{daysSince(sale.sale_date)}d</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{sale.items.map(i => `${i.product_name} x${i.quantity}`).join(', ')}</p>
                  <p className="text-xs text-gray-600 font-mono mt-0.5">{new Date(sale.sale_date).toLocaleDateString('es-CO')}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-gray-400 font-mono text-xs">Total: {fmt(sale.total)}</p>
                  {sale.amount_paid > 0 && <p className="text-green-400 font-mono text-xs">Abonado: {fmt(sale.amount_paid)}</p>}
                  <p className="text-yellow-400 font-mono font-bold text-sm">Saldo: {fmt(sale.balance)}</p>
                  <div className="flex gap-1 mt-1 justify-end">
                    <button onClick={() => openDetail(sale)} className="btn-ghost text-xs px-2 py-1">Historial</button>
                    <button onClick={() => setAbonoSale(sale)} className="btn-primary text-xs px-2 py-1">Abonar</button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {abonoSale && (
        <AbonoModal sale={abonoSale} onClose={() => setAbonoSale(null)} onDone={() => { setAbonoSale(null); load() }} />
      )}

      {detailSale && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-surface-card border border-surface-border rounded-xl w-full max-w-sm max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between px-5 py-4 border-b border-surface-border">
              <div>
                <h3 className="text-white font-medium">Historial abonos #{detailSale.id}</h3>
                {detailSale.customer_name && <p className="text-xs text-gray-500">{detailSale.customer_name}</p>}
              </div>
              <button onClick={() => setDetailSale(null)} className="text-gray-500 hover:text-white transition-colors">✕</button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {loadingPayments ? <Spinner /> : payments.length === 0 ? (
                <p className="text-gray-600 text-sm font-mono text-center py-4">Sin abonos registrados</p>
              ) : (
                payments.map(p => (
                  <div key={p.id} className="flex items-center justify-between text-sm">
                    <div>
                      <p className="text-white font-mono font-bold">{fmt(p.amount)}</p>
                      <p className="text-xs text-gray-500">{p.method} · {new Date(p.paid_at).toLocaleDateString('es-CO')}</p>
                      {p.notes && <p className="text-xs text-gray-600">{p.notes}</p>}
                    </div>
                  </div>
                ))
              )}
            </div>
            <div className="px-5 py-4 border-t border-surface-border">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-500">Total venta</span>
                <span className="text-white font-mono">{fmt(detailSale.total)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Saldo pendiente</span>
                <span className="text-yellow-400 font-mono font-bold">{fmt(detailSale.balance)}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ── CustomersTab ───────────────────────────────────────────────────────────────
function CustomersTab() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [err, setErr] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const load = useCallback(() => {
    setLoading(true)
    getCustomers(search ? { q: search } : {})
      .then(setCustomers)
      .catch(e => setErr(e.message))
      .finally(() => setLoading(false))
  }, [search])

  useEffect(() => { load() }, [load])

  async function handleDelete(c: Customer) {
    if (!window.confirm(`¿Eliminar a "${c.name}"?`)) return
    setErr(''); setDeletingId(c.id)
    try { await deleteCustomer(c.id); load() }
    catch (e: any) { setErr(e.message) }
    finally { setDeletingId(null) }
  }

  return (
    <div className="space-y-4">
      {err && <p className="text-xs text-brand-400 font-mono bg-brand-500/10 px-3 py-2 rounded">{err}</p>}
      <div className="flex gap-2">
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Buscar por nombre, documento o teléfono…" className="input flex-1" />
        <button onClick={() => setShowCreate(true)} className="btn-primary text-sm">+ Cliente</button>
      </div>
      {loading ? <Spinner /> : (
        <div className="space-y-2">
          {customers.map(c => (
            <div key={c.id} className="card py-3 flex items-center gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-white text-sm font-medium">{c.name}</span>
                  {c.member_name && <span className="text-xs text-brand-400 font-mono">miembro</span>}
                </div>
                <p className="text-xs text-gray-500 font-mono mt-0.5">
                  {[c.document, c.phone].filter(Boolean).join(' · ') || 'Sin documento'}
                </p>
              </div>
              <div className="text-right shrink-0">
                {c.debt_total > 0
                  ? <p className="text-yellow-400 font-mono font-bold text-sm">{fmt(c.debt_total)}</p>
                  : <p className="text-green-400 font-mono text-xs">Sin deuda</p>
                }
              </div>
              <button
                onClick={() => handleDelete(c)}
                disabled={deletingId === c.id}
                className="text-xs px-2 py-1 rounded border border-red-500/20 text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-50 shrink-0"
              >
                {deletingId === c.id ? '…' : 'Eliminar'}
              </button>
            </div>
          ))}
          {customers.length === 0 && <p className="text-gray-600 font-mono text-sm text-center py-6">Sin clientes</p>}
        </div>
      )}
      {showCreate && (
        <QuickCustomerModal
          onCreated={() => { setShowCreate(false); load() }}
          onClose={() => setShowCreate(false)}
        />
      )}
    </div>
  )
}

// ── CategoriesTab ──────────────────────────────────────────────────────────────
function CategoriesTab({ categories, onUpdated }: { categories: ProductCategory[]; onUpdated: () => void }) {
  const [newName, setNewName] = useState('')
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editName, setEditName] = useState('')

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!newName.trim()) return
    setSaving(true); setErr('')
    try { await createCategory({ name: newName.trim() }); setNewName(''); onUpdated() }
    catch (e: any) { setErr(e.message) }
    finally { setSaving(false) }
  }

  function startEdit(c: ProductCategory) { setEditingId(c.id); setEditName(c.name); setErr('') }

  async function handleSaveEdit(e: React.FormEvent) {
    e.preventDefault()
    if (!editName.trim() || editingId === null) return
    setSaving(true); setErr('')
    try { await updateCategory(editingId, { name: editName.trim() }); setEditingId(null); onUpdated() }
    catch (e: any) { setErr(e.message) }
    finally { setSaving(false) }
  }

  async function handleToggle(c: ProductCategory) {
    try { await toggleCategory(c.id, !c.is_active); onUpdated() }
    catch (e: any) { setErr(e.message) }
  }

  async function handleDelete(c: ProductCategory) {
    if (!window.confirm(`¿Eliminar la categoría "${c.name}"?`)) return
    try { await deleteCategory(c.id); onUpdated() }
    catch (e: any) { setErr(e.message) }
  }

  return (
    <div className="max-w-md space-y-4">
      {err && <p className="text-xs text-brand-400 font-mono bg-brand-500/10 px-3 py-2 rounded">{err}</p>}
      <form onSubmit={handleCreate} className="flex gap-2">
        <input value={newName} onChange={e => setNewName(e.target.value)} placeholder="Nueva categoría…" className="input flex-1" />
        <button type="submit" disabled={saving} className="btn-primary text-sm">Crear</button>
      </form>
      <div className="space-y-2">
        {categories.map(c => (
          <div key={c.id} className={`card py-2.5 ${!c.is_active ? 'opacity-60' : ''}`}>
            {editingId === c.id ? (
              <form onSubmit={handleSaveEdit} className="flex items-center gap-2">
                <input autoFocus value={editName} onChange={e => setEditName(e.target.value)} className="input flex-1 text-sm" />
                <button type="submit" disabled={saving} className="btn-primary text-xs px-3">Guardar</button>
                <button type="button" onClick={() => setEditingId(null)} className="btn-ghost text-xs px-3">Cancelar</button>
              </form>
            ) : (
              <div className="flex items-center gap-3">
                <span className="flex-1 text-sm text-gray-300">{c.name}</span>
                <button onClick={() => startEdit(c)} className="text-xs text-gray-400 hover:text-white transition-colors">Editar</button>
                <button onClick={() => handleToggle(c)} className={`text-xs px-2 py-1 rounded border transition-colors ${c.is_active ? 'border-brand-500/20 text-brand-400 hover:bg-brand-500/10' : 'border-green-500/20 text-green-400 hover:bg-green-500/10'}`}>{c.is_active ? 'Desactivar' : 'Activar'}</button>
                <button onClick={() => handleDelete(c)} className="text-xs text-red-500 hover:text-red-300 transition-colors">Eliminar</button>
              </div>
            )}
          </div>
        ))}
        {categories.length === 0 && <p className="text-gray-600 font-mono text-sm">Sin categorías</p>}
      </div>
    </div>
  )
}

// ── ReportsTab ─────────────────────────────────────────────────────────────────
type PeriodPreset = 'today' | 'week' | 'month' | 'custom'

function ReportsTab() {
  const [preset, setPreset] = useState<PeriodPreset>('month')
  const [customFrom, setCustomFrom] = useState('')
  const [customTo, setCustomTo] = useState('')
  const [report, setReport] = useState<StoreReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState('')

  function buildDates(): { dateFrom: string; dateTo: string } {
    const now = new Date()
    if (preset === 'today') {
      const from = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      return { dateFrom: from.toISOString(), dateTo: now.toISOString() }
    }
    if (preset === 'week') {
      const day = now.getDay()
      const diff = now.getDate() - day + (day === 0 ? -6 : 1)
      const from = new Date(now.getFullYear(), now.getMonth(), diff)
      return { dateFrom: from.toISOString(), dateTo: now.toISOString() }
    }
    if (preset === 'month') {
      const from = new Date(now.getFullYear(), now.getMonth(), 1)
      return { dateFrom: from.toISOString(), dateTo: now.toISOString() }
    }
    return {
      dateFrom: customFrom
        ? new Date(customFrom).toISOString()
        : new Date(now.getFullYear(), now.getMonth(), 1).toISOString(),
      dateTo: customTo
        ? new Date(customTo + 'T23:59:59').toISOString()
        : now.toISOString(),
    }
  }

  const load = useCallback(() => {
    setLoading(true); setErr('')
    const { dateFrom, dateTo } = buildDates()
    getStoreReport(dateFrom, dateTo)
      .then(setReport)
      .catch(e => setErr(e.message))
      .finally(() => setLoading(false))
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preset, customFrom, customTo])

  useEffect(() => { load() }, [load])

  const PRESETS: { key: PeriodPreset; label: string }[] = [
    { key: 'today', label: 'Hoy' },
    { key: 'week',  label: 'Esta semana' },
    { key: 'month', label: 'Este mes' },
    { key: 'custom', label: 'Personalizado' },
  ]

  return (
    <div className="space-y-8">
      {err && <p className="text-xs text-brand-400 font-mono bg-brand-500/10 px-3 py-2 rounded">{err}</p>}

      {/* Selector de período */}
      <div className="flex flex-wrap items-center gap-2">
        {PRESETS.map(p => (
          <button key={p.key} onClick={() => setPreset(p.key)}
            className={`px-3 py-1.5 text-xs rounded border transition-colors ${preset === p.key ? 'border-brand-500 text-white bg-brand-500/10' : 'border-surface-border text-gray-500 hover:text-gray-300'}`}>
            {p.label}
          </button>
        ))}
        {preset === 'custom' && (
          <div className="flex items-center gap-2 ml-2">
            <input type="date" value={customFrom} onChange={e => setCustomFrom(e.target.value)} className="input text-xs" />
            <span className="text-gray-600 text-xs">—</span>
            <input type="date" value={customTo} min={customFrom} onChange={e => setCustomTo(e.target.value)} className="input text-xs" />
            <button onClick={load} className="btn-primary text-xs px-3">Aplicar</button>
          </div>
        )}
      </div>

      {loading ? <Spinner /> : report && (
        <>
          {/* Bloque A — Ventas */}
          <section className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-1 h-5 bg-brand-500 rounded-full shadow-brand-sm" />
              <h2 className="font-display text-base tracking-widest text-white uppercase">Ventas</h2>
            </div>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard label="Total ventas" value={report.sales.total_sales} sub="transacciones" accent="blue" />
              <StatCard label="Ingresos" value={fmt(report.sales.total_revenue)} sub="excluye canceladas" accent="green" />
              <StatCard label="Ticket promedio" value={fmt(report.sales.average_ticket)} sub="por venta" accent="blue" />
              <StatCard label="Abonos cobrados" value={fmt(report.sales.credit_collections_amount)} sub="período" accent="yellow" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="card">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Contado</p>
                <p className="text-2xl font-display text-white font-bold">{fmt(report.sales.cash_sales_amount)}</p>
                <p className="text-xs text-gray-600 font-mono mt-1">{report.sales.cash_sales_count} venta{report.sales.cash_sales_count !== 1 ? 's' : ''}</p>
              </div>
              <div className="card">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">A crédito</p>
                <p className="text-2xl font-display text-white font-bold">{fmt(report.sales.credit_sales_amount)}</p>
                <p className="text-xs text-gray-600 font-mono mt-1">{report.sales.credit_sales_count} venta{report.sales.credit_sales_count !== 1 ? 's' : ''}</p>
              </div>
            </div>
            {report.top_products.length > 0 ? (
              <div className="card">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Top productos (período)</p>
                <div className="space-y-2">
                  {report.top_products.map((p, i) => (
                    <div key={p.product_id} className="flex items-center gap-3 text-sm">
                      <span className="text-gray-600 font-mono w-5 text-right shrink-0">{i + 1}</span>
                      <span className="text-gray-300 flex-1">{p.product_name}</span>
                      <span className="text-gray-500 font-mono text-xs">{p.units_sold} uds</span>
                      <span className="text-brand-400 font-mono font-bold">{fmt(p.revenue)}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-gray-600 font-mono text-sm text-center py-4">Sin ventas en el período</p>
            )}
          </section>

          {/* Bloque B — Cartera */}
          <section className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-1 h-5 bg-yellow-500 rounded-full" />
              <h2 className="font-display text-base tracking-widest text-white uppercase">Cartera</h2>
              <span className="text-xs text-gray-600 font-mono">(estado actual)</span>
            </div>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard label="Saldo pendiente" value={fmt(report.cartera.outstanding_balance)} sub="cartera total" accent="red" />
              <StatCard label="Clientes con deuda" value={report.cartera.customers_with_debt} sub="únicos" accent="yellow" />
              <StatCard label="Pendientes" value={report.cartera.pending_sales_count} sub="sin abonos" accent="yellow" />
              <StatCard label="Parciales" value={report.cartera.partial_sales_count} sub="con abonos" accent="blue" />
            </div>
            {report.cartera.oldest_debt_date && (
              <p className="text-xs text-gray-600 font-mono">
                Deuda más antigua: {new Date(report.cartera.oldest_debt_date).toLocaleDateString('es-CO')}
              </p>
            )}
          </section>

          {/* Bloque C — Inventario */}
          <section className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-1 h-5 bg-orange-500 rounded-full" />
              <h2 className="font-display text-base tracking-widest text-white uppercase">Inventario</h2>
              <span className="text-xs text-gray-600 font-mono">(estado actual)</span>
            </div>
            {report.inventory.low_stock_count === 0 ? (
              <p className="text-green-400 font-mono text-sm">Sin productos con bajo stock.</p>
            ) : (
              <div className="card">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-xs text-gray-500 uppercase tracking-wider">Bajo stock</p>
                  <span className="text-xs bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 px-2 py-0.5 rounded font-mono">
                    {report.inventory.low_stock_count} producto{report.inventory.low_stock_count !== 1 ? 's' : ''}
                  </span>
                </div>
                <div className="space-y-2">
                  {report.inventory.low_stock_products.map(p => (
                    <div key={p.product_id} className="flex items-center gap-3 text-sm">
                      <div className="flex-1 min-w-0">
                        <span className="text-gray-300">{p.product_name}</span>
                        {p.category_name && <span className="text-gray-600 text-xs ml-2">{p.category_name}</span>}
                      </div>
                      <div className="text-right shrink-0">
                        <span className="text-yellow-400 font-mono font-bold">{p.stock}</span>
                        <span className="text-gray-600 font-mono text-xs"> / mín {p.min_stock}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  )
}

// ── Store page ─────────────────────────────────────────────────────────────────
export default function Store() {
  const [tab, setTab] = useState<Tab>('products')
  const [categories, setCategories] = useState<ProductCategory[]>([])
  const [products, setProducts] = useState<Product[]>([])

  const loadCategories = useCallback(() => {
    getCategories().then(setCategories).catch(() => {})
  }, [])

  const loadProducts = useCallback(() => {
    getProducts({ activeOnly: false }).then(r => setProducts(r.items)).catch(() => {})
  }, [])

  useEffect(() => { loadCategories(); loadProducts() }, [loadCategories, loadProducts])

  const TABS: { key: Tab; label: string }[] = [
    { key: 'products',   label: 'Productos' },
    { key: 'sales',      label: 'Ventas' },
    { key: 'cartera',    label: 'Cartera' },
    { key: 'customers',  label: 'Clientes' },
    { key: 'categories', label: 'Categorías' },
    { key: 'reports',    label: 'Reportes' },
  ]

  return (
    <div className="p-8 space-y-6 animate-fade-up">
      <div className="flex items-end justify-between border-b border-surface-border pb-6">
        <div>
          <p className="text-xs font-semibold text-brand-500 uppercase tracking-[0.3em] mb-1">Inventario &amp; ventas</p>
          <h1 className="font-display text-4xl tracking-widest text-white uppercase">Tienda</h1>
        </div>
      </div>

      <div className="flex gap-1 border-b border-surface-border">
        {TABS.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px ${
              tab === t.key ? 'border-brand-500 text-white' : 'border-transparent text-gray-500 hover:text-gray-300'
            }`}>
            {t.label}
          </button>
        ))}
      </div>

      <div>
        {tab === 'products'   && <ProductsTab categories={categories} onUpdated={loadProducts} />}
        {tab === 'sales'      && <SalesTab products={products} />}
        {tab === 'cartera'    && <CarteraTab />}
        {tab === 'customers'  && <CustomersTab />}
        {tab === 'categories' && <CategoriesTab categories={categories} onUpdated={loadCategories} />}
        {tab === 'reports'    && <ReportsTab />}
      </div>
    </div>
  )
}
