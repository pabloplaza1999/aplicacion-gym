"""
Pruebas de integracion - Modulo Tienda Fase A
Requiere el servidor corriendo en http://localhost:8000
"""
import requests
import time

BASE = "http://localhost:8000/api"

PASS = "[PASS]"
FAIL = "[FAIL]"
results = []


def check(label, ok, detail=""):
    tag = PASS if ok else FAIL
    msg = f"{tag} {label}" + (f" - {detail}" if detail else "")
    print(msg)
    results.append(ok)


def post(path, body=None):
    return requests.post(f"{BASE}{path}", json=body or {})


def get(path):
    return requests.get(f"{BASE}{path}")


def put(path, body=None):
    return requests.put(f"{BASE}{path}", json=body or {})


def patch(path, params=None):
    url = f"{BASE}{path}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    return requests.patch(url)


def delete(path):
    return requests.delete(f"{BASE}{path}")


def ts():
    """Sufijo unico para nombres."""
    return str(int(time.time()))[-6:]


print("=" * 60)
print("TEST: Tienda Fase A - Categorias, Productos, Inventario, Ventas")
print("=" * 60)

# __ 1. Categorias _____________________________________________________________
print("\n--- Categorias ---")

suffix = ts()
cat_name = f"Suplementos_{suffix}"

r = post("/store/categories", {"name": cat_name})
check("Crear categoria", r.status_code == 201, r.text[:80])
cat_id = r.json().get("id") if r.status_code == 201 else None

r2 = post("/store/categories", {"name": cat_name})
check("Crear categoria duplicada -> 400", r2.status_code == 400)

r3 = get("/store/categories")
check("Listar categorias", r3.status_code == 200 and isinstance(r3.json(), list))

r4 = put(f"/store/categories/{cat_id}", {"name": f"Suplementos_v2_{suffix}"})
check("Actualizar nombre categoria", r4.status_code == 200 and r4.json().get("name") == f"Suplementos_v2_{suffix}")
cat_name = f"Suplementos_v2_{suffix}"

r5 = patch(f"/store/categories/{cat_id}/active", {"is_active": "false"})
check("Desactivar categoria", r5.status_code == 200 and r5.json().get("is_active") == False)

r6 = patch(f"/store/categories/{cat_id}/active", {"is_active": "true"})
check("Activar categoria", r6.status_code == 200 and r6.json().get("is_active") == True)

# __ 2. Productos ______________________________________________________________
print("\n--- Productos ---")

prod_name = f"Proteina Whey 1kg_{suffix}"
r = post("/store/products", {
    "category_id": cat_id,
    "name": prod_name,
    "price": 120000,
    "cost": 80000,
    "stock": 10,
    "min_stock": 2,
})
check("Crear producto con stock inicial", r.status_code == 201, r.text[:80])
prod_id = r.json().get("id") if r.status_code == 201 else None
check("Producto tiene stock=10", r.status_code == 201 and r.json().get("stock") == 10)
check("is_low_stock=False con stock 10 y min 2", r.status_code == 201 and r.json().get("is_low_stock") == False)
check("category_name presente", r.status_code == 201 and r.json().get("category_name") == cat_name)

r2 = post("/store/products", {"category_id": cat_id, "name": prod_name, "price": 50000})
check("Crear producto duplicado -> 400", r2.status_code == 400)

r3 = post("/store/products", {"category_id": 99999, "name": f"X_{suffix}", "price": 10000})
check("Crear producto categoria inexistente -> 400", r3.status_code == 400)

r4 = get("/store/products")
check("Listar productos", r4.status_code == 200 and "items" in r4.json())

r5 = get(f"/store/products/{prod_id}")
check("Obtener producto por ID", r5.status_code == 200 and r5.json().get("id") == prod_id)

r6 = put(f"/store/products/{prod_id}", {"price": 130000})
check("Actualizar precio producto", r6.status_code == 200 and r6.json().get("price") == 130000)

# Producto low-stock
prod_low_name = f"Creatina_{suffix}"
r7 = post("/store/products", {
    "category_id": cat_id,
    "name": prod_low_name,
    "price": 80000,
    "stock": 1,
    "min_stock": 3,
})
check("Crear producto con stock bajo", r7.status_code == 201)
prod_low_id = r7.json().get("id") if r7.status_code == 201 else None
check("is_low_stock=True (stock 1 <= min 3)", r7.status_code == 201 and r7.json().get("is_low_stock") == True)

r8 = get("/store/inventory/low-stock")
check("Low-stock endpoint retorna lista", r8.status_code == 200 and isinstance(r8.json(), list))
low_ids = [p["id"] for p in r8.json()]
check("Producto low-stock aparece en /inventory/low-stock", prod_low_id in low_ids)

# Desactivar producto
r9 = patch(f"/store/products/{prod_id}/active", {"is_active": "false"})
check("Desactivar producto", r9.status_code == 200 and r9.json().get("is_active") == False)
r10 = patch(f"/store/products/{prod_id}/active", {"is_active": "true"})
check("Activar producto", r10.status_code == 200 and r10.json().get("is_active") == True)

# __ 3. Inventario _____________________________________________________________
print("\n--- Inventario ---")

r = post(f"/store/products/{prod_id}/inventory/entry", {"quantity": 5, "note": "Reposicion prueba"})
check("Registrar entrada inventario", r.status_code == 200 or r.status_code == 201, r.text[:80])
mov_id = r.json().get("id") if r.status_code in (200, 201) else None
check("stock_before + 5 = stock_after", r.status_code in (200, 201) and r.json().get("stock_after") == r.json().get("stock_before") + 5)

# Verificar que el stock del producto subio
rp = get(f"/store/products/{prod_id}")
check("Stock producto actualizado tras entrada (+5)", rp.json().get("stock") == 15)

r2 = post(f"/store/products/{prod_id}/inventory/adjustment", {"quantity": -3, "note": "Ajuste merma"})
check("Ajuste negativo inventario", r2.status_code in (200, 201))
check("stock_after = stock_before - 3", r2.status_code in (200, 201) and r2.json().get("stock_after") == r2.json().get("stock_before") - 3)

rp2 = get(f"/store/products/{prod_id}")
check("Stock producto actualizado tras ajuste -3", rp2.json().get("stock") == 12)

r3 = post(f"/store/products/{prod_id}/inventory/adjustment", {"quantity": -9999, "note": "Ajuste excesivo"})
check("Ajuste que dejaria stock negativo -> 400", r3.status_code == 400)

r4 = get(f"/store/products/{prod_id}/inventory/movements")
check("Listar movimientos producto", r4.status_code == 200 and isinstance(r4.json(), list))
check("Al menos 3 movimientos (inicial, entrada, ajuste)", len(r4.json()) >= 3)

# __ 4. Ventas _________________________________________________________________
print("\n--- Ventas ---")

stock_before_sale = get(f"/store/products/{prod_id}").json().get("stock")

r = post("/store/sales", {
    "items": [{"product_id": prod_id, "quantity": 2}],
    "discount": 5000,
    "notes": "Venta prueba",
})
check("Crear venta exitosa", r.status_code == 201, r.text[:80])
sale_id = r.json().get("id") if r.status_code == 201 else None
sale = r.json() if r.status_code == 201 else {}

check("Venta tiene items", len(sale.get("items", [])) == 1)
check("subtotal = precio x cantidad", sale.get("subtotal") == 130000 * 2)
check("total = subtotal - descuento", sale.get("total") == sale.get("subtotal", 0) - 5000)
check("status = completed", sale.get("status") == "completed")
check("product_name en item de venta", sale.get("items", [{}])[0].get("product_name") is not None)

rp3 = get(f"/store/products/{prod_id}")
check("Stock descontado tras venta (-2)", rp3.json().get("stock") == stock_before_sale - 2)

# Movimiento tipo 'sale' registrado
r_mov = get(f"/store/products/{prod_id}/inventory/movements")
types = [m["type"] for m in r_mov.json()]
check("Movimiento tipo 'sale' registrado", "sale" in types)

# Venta con stock insuficiente
r2 = post("/store/sales", {"items": [{"product_id": prod_id, "quantity": 99999}]})
check("Venta con stock insuficiente -> 409", r2.status_code == 409)

# Venta con producto inexistente
r3 = post("/store/sales", {"items": [{"product_id": 99999, "quantity": 1}]})
check("Venta con producto inexistente -> 400", r3.status_code == 400)

# Venta sin items
r4 = post("/store/sales", {"items": []})
check("Venta sin items -> 422", r4.status_code == 422)

# Obtener venta por ID
r5 = get(f"/store/sales/{sale_id}")
check("Obtener venta por ID", r5.status_code == 200 and r5.json().get("id") == sale_id)

# Listar ventas
r6 = get("/store/sales")
check("Listar ventas", r6.status_code == 200 and "items" in r6.json())
check("total_amount > 0", r6.json().get("total_amount", 0) > 0)

# __ 5. Anulacion de venta _____________________________________________________
print("\n--- Anulacion ---")

stock_before_cancel = get(f"/store/products/{prod_id}").json().get("stock")

r = post(f"/store/sales/{sale_id}/cancel", None)
check("Anular venta", r.status_code == 200 and r.json().get("status") == "cancelled")

rp4 = get(f"/store/products/{prod_id}")
check("Stock repuesto tras anulacion (+2)", rp4.json().get("stock") == stock_before_cancel + 2)

r2 = post(f"/store/sales/{sale_id}/cancel", None)
check("Anular venta ya anulada -> 400", r2.status_code == 400)

# __ 6. Eliminacion con restricciones _________________________________________
print("\n--- Restricciones eliminacion ---")

r = delete(f"/store/products/{prod_id}")
check("Eliminar producto con movimientos -> 400", r.status_code == 400)

r2 = delete(f"/store/categories/{cat_id}")
check("Eliminar categoria con productos -> 400", r2.status_code == 400)

# Producto sin movimientos (usando low_id)
r3 = delete(f"/store/products/{prod_low_id}")
# prod_low no tiene ventas pero si tiene movimiento inicial si stock>0
# puede ser 400 o 204 segun si se registro movimiento inicial
status_msg = "204 o 400" if r3.status_code in (204, 400) else f"inesperado {r3.status_code}"
check(f"Eliminar producto low-stock ({status_msg})", r3.status_code in (204, 400))

# __ 7. Impacto en modulos existentes __________________________________________
print("\n--- Regresiones modulos existentes ---")

r = get("/dashboard")
check("Dashboard aun responde", r.status_code == 200)
check("Dashboard tiene frozen en memberships", "frozen" in r.json().get("memberships", {}))

r2 = get("/members?limit=5")
check("Modulo miembros sin regresion", r2.status_code == 200)

r3 = get("/payments?limit=5")
check("Modulo pagos sin regresion", r3.status_code == 200)

# __ Resultado final ___________________________________________________________
print("\n" + "=" * 60)
total = len(results)
passed = sum(results)
failed = total - passed
print(f"RESULTADO: {passed}/{total} pruebas PASS - {failed} FAIL")
if failed == 0:
    print("STATUS: PASS")
elif failed <= 2:
    print("STATUS: PASS CON RIESGOS")
else:
    print("STATUS: FAIL")
print("=" * 60)
