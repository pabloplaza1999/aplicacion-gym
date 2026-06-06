import requests
import json
from datetime import datetime, timedelta

base_url = "http://localhost:8000/api"

# Generate unique document ID
unique_doc = f"doc_{int(datetime.utcnow().timestamp() * 1000) % 1000000}"

print("=" * 60)
print("TESTING PAYMENTS MODULE")
print("=" * 60)

# Test 1: Create a member for payments
print("\n=== CREATE MEMBER FOR PAYMENTS ===")
member_data = {
    "full_name": "Carlos González",
    "phone": "3105559876",
    "document": unique_doc,
    "notes": "Client for payment testing"
}
response = requests.post(f"{base_url}/members", json=member_data)
print(f"Status: {response.status_code}")
member_id = response.json()["id"]
print(f"Created member ID: {member_id}")

# Test 2: Create a membership
print("\n=== CREATE MEMBERSHIP ===")
membership_data = {
    "member_id": member_id,
    "plan_id": 2,  # Plan Básico
}
response = requests.post(
    f"{base_url}/members/{member_id}/memberships",
    json=membership_data
)
print(f"Status: {response.status_code}")
membership_id = response.json()["id"]
print(f"Created membership ID: {membership_id}")

# Test 3: Register payment (cash)
print("\n=== REGISTER PAYMENT (CASH) ===")
payment_data = {
    "member_id": member_id,
    "membership_id": membership_id,
    "amount": 60000,
    "payment_method": "cash"
}
response = requests.post(
    f"{base_url}/members/{member_id}/payments",
    json=payment_data
)
print(f"Status: {response.status_code}")
payment1_data = response.json()
print(f"Payment created: {payment1_data['id']}")
print(f"Amount: {payment1_data['amount']}, Method: {payment1_data['payment_method']}")

# Test 4: Register payment (transfer)
print("\n=== REGISTER PAYMENT (TRANSFER) ===")
payment_data = {
    "member_id": member_id,
    "membership_id": membership_id,
    "amount": 120000,
    "payment_method": "transfer"
}
response = requests.post(
    f"{base_url}/members/{member_id}/payments",
    json=payment_data
)
print(f"Status: {response.status_code}")
payment2_data = response.json()
print(f"Payment created: {payment2_data['id']}")
print(f"Amount: {payment2_data['amount']}, Method: {payment2_data['payment_method']}")

# Test 5: Register payment (QR)
print("\n=== REGISTER PAYMENT (QR) ===")
payment_data = {
    "member_id": member_id,
    "amount": 30000,
    "payment_method": "qr"
}
response = requests.post(
    f"{base_url}/members/{member_id}/payments",
    json=payment_data
)
print(f"Status: {response.status_code}")
payment3_id = response.json()["id"]
print(f"Payment created: {payment3_id}")

# Test 6: Register payment (Nequi)
print("\n=== REGISTER PAYMENT (NEQUI) ===")
payment_data = {
    "member_id": member_id,
    "amount": 50000,
    "payment_method": "nequi"
}
response = requests.post(
    f"{base_url}/members/{member_id}/payments",
    json=payment_data
)
print(f"Status: {response.status_code}")
print(f"Payment created: {response.json()['id']}")

# Test 7: Get member payment history
print("\n=== GET MEMBER PAYMENT HISTORY ===")
response = requests.get(f"{base_url}/members/{member_id}/payments")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Total payments: {result['total']}")
print(f"Total amount: {result['amount_total']}")
print(f"Items count: {len(result['items'])}")
for i, p in enumerate(result['items'], 1):
    print(f"  {i}. Amount: {p['amount']}, Method: {p['payment_method']}, Date: {p['payment_date']}")

# Test 8: Get single payment
print("\n=== GET SINGLE PAYMENT ===")
response = requests.get(f"{base_url}/payments/{payment1_data['id']}")
print(f"Status: {response.status_code}")
payment = response.json()
print(f"Payment ID: {payment['id']}")
print(f"Member: {payment['member_id']}, Amount: {payment['amount']}, Method: {payment['payment_method']}")

# Test 9: Get all payments
print("\n=== GET ALL PAYMENTS ===")
response = requests.get(f"{base_url}/payments")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Total payments: {result['total']}")
print(f"Total amount: {result['total_amount']}")
print(f"Items returned: {len(result['items'])}")

# Test 10: Get payments by method (cash)
print("\n=== GET PAYMENTS BY METHOD (CASH) ===")
response = requests.get(f"{base_url}/payments/method/cash")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Payments with cash method: {result['total']}")
print(f"Total amount (cash): {result['total_amount']}")

# Test 11: Get payments by method (transfer)
print("\n=== GET PAYMENTS BY METHOD (TRANSFER) ===")
response = requests.get(f"{base_url}/payments/method/transfer")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Payments with transfer method: {result['total']}")
print(f"Total amount (transfer): {result['total_amount']}")

# Test 12: Get monthly payments
print("\n=== GET MONTHLY PAYMENTS (Current Month) ===")
now = datetime.utcnow()
response = requests.get(f"{base_url}/payments/monthly/{now.year}/{now.month}")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Payments in month {now.month}/{now.year}: {result['total']}")
print(f"Total amount: {result['total_amount']}")

# Test 13: Get payment statistics
print("\n=== GET PAYMENT STATISTICS ===")
response = requests.get(f"{base_url}/payments/statistics")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Total payments: {result['total_payments']}")
print(f"Total amount: {result['total_amount']}")
print("By method:")
for method in result['by_method']:
    print(f"  - {method['method'].upper()}: {method['count']} payments, "
          f"{method['total_amount']} COP ({method['percentage']}%)")

# Test 14: Get current month statistics
print("\n=== GET CURRENT MONTH STATISTICS ===")
response = requests.get(f"{base_url}/payments/statistics/current-month")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Total payments: {result['total_payments']}")
print(f"Total amount: {result['total_amount']}")
print(f"Date range: {result['payment_date_range']}")
print("By method:")
for method in result['by_method']:
    print(f"  - {method['method'].upper()}: {method['count']} payments, "
          f"{method['total_amount']} COP ({method['percentage']}%)")

# Test 15: Error validation - invalid method
print("\n=== ERROR VALIDATION: INVALID METHOD ===")
payment_data = {
    "member_id": member_id,
    "amount": 10000,
    "payment_method": "invalid"
}
response = requests.post(
    f"{base_url}/members/{member_id}/payments",
    json=payment_data
)
print(f"Status: {response.status_code} (should be 400)")
if response.status_code == 400:
    print(f"Error message: {response.json()['detail']}")

# Test 16: Error validation - invalid amount
print("\n=== ERROR VALIDATION: INVALID AMOUNT ===")
payment_data = {
    "member_id": member_id,
    "amount": -5000,
    "payment_method": "cash"
}
response = requests.post(
    f"{base_url}/members/{member_id}/payments",
    json=payment_data
)
print(f"Status: {response.status_code}")
if response.status_code != 201:
    print("Error caught (negative amount not allowed)")

print("\n" + "=" * 60)
print("[OK] PAYMENTS MODULE TEST COMPLETED!")
print("=" * 60)
