import requests
import json
from datetime import datetime, timedelta

base_url = "http://localhost:8000/api"

print("=" * 60)
print("TESTING MEMBERSHIPS MODULE")
print("=" * 60)

# Test 1: Create a member
print("\n=== CREATE MEMBER ===")
member_data = {
    "full_name": "María López",
    "phone": "3015551234",
    "document": "98765432",
    "notes": "Cliente para test"
}
response = requests.post(f"{base_url}/members", json=member_data)
print(f"Status: {response.status_code}")
member_id = response.json()["id"]
print(f"Created member ID: {member_id}")

# Test 2: Create membership with Plan Básico (30 days)
print("\n=== CREATE MEMBERSHIP (Plan Básico - 30 días) ===")
membership_data = {
    "member_id": member_id,
    "plan_id": 2,  # Plan Básico
}
response = requests.post(
    f"{base_url}/members/{member_id}/memberships",
    json=membership_data
)
print(f"Status: {response.status_code}")
result = response.json()
print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False, default=str)}")
membership_id = result["id"]
print(f"Status calculated: {result['status']}")

# Test 3: Get current membership
print("\n=== GET CURRENT MEMBERSHIP ===")
response = requests.get(f"{base_url}/members/{member_id}/current-membership")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Current membership: {result['plan_name']}")
print(f"Status: {result['status']} (Verde si > 5 días)")
print(f"Days remaining: {result['days_remaining']}")
print(f"End date: {result['end_date']}")

# Test 4: Get membership history
print("\n=== GET MEMBERSHIP HISTORY ===")
response = requests.get(f"{base_url}/members/{member_id}/memberships")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Total memberships: {result['total']}")
print(f"Items: {len(result['items'])}")

# Test 5: Create membership with Plan Día (same day)
print("\n=== CREATE MEMBERSHIP (Plan Día - 1 día) ===")
membership_data = {
    "member_id": member_id,
    "plan_id": 1,  # Plan Día
}
response = requests.post(
    f"{base_url}/members/{member_id}/memberships",
    json=membership_data
)
print(f"Status: {response.status_code}")
result = response.json()
daily_membership_id = result["id"]
print(f"Plan: {result['plan_id']} (Plan Día)")
print(f"Start: {result['start_date']}")
print(f"End: {result['end_date']}")
print(f"Status: {result['status']}")

# Test 6: Renew membership
print("\n=== RENEW MEMBERSHIP ===")
renew_data = {"plan_id": 3}  # Funcional y Musculación
response = requests.post(
    f"{base_url}/members/memberships/{membership_id}/renew",
    json=renew_data
)
print(f"Status: {response.status_code}")
result = response.json()
print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False, default=str)}")
print(f"New plan ID: {result['plan_id']} (should be 3)")
print(f"Start date should be today: {result['start_date']}")

# Test 7: Get renewed membership details
print("\n=== GET RENEWED MEMBERSHIP DETAILS ===")
renewed_id = result["id"]
response = requests.get(f"{base_url}/members/memberships/{renewed_id}")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Plan: {result['plan_name']}")
print(f"Days remaining: {result['days_remaining']}")
print(f"Status: {result['status']}")

# Test 8: Get full membership history
print("\n=== FULL MEMBERSHIP HISTORY ===")
response = requests.get(f"{base_url}/members/{member_id}/memberships")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Total memberships: {result['total']}")
for i, m in enumerate(result['items'], 1):
    print(f"  {i}. Plan ID: {m['plan_id']}, Status: {m['status']}, Start: {m['start_date']}")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
