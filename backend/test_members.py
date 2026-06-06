import requests
import json

base_url = "http://localhost:8000/api"

# Test 1: Create a member
print("=== CREATE MEMBER ===")
member_data = {
    "full_name": "Juan García",
    "phone": "3001234567",
    "document": "12345678",
    "notes": "Cliente nuevo"
}
response = requests.post(f"{base_url}/members", json=member_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
member_id = response.json()["id"]

# Test 2: List members
print("\n=== LIST MEMBERS ===")
response = requests.get(f"{base_url}/members")
print(f"Status: {response.status_code}")
data = response.json()
print(f"Total: {data['total']}, Items: {len(data['items'])}")

# Test 3: Get member by ID
print(f"\n=== GET MEMBER {member_id} ===")
response = requests.get(f"{base_url}/members/{member_id}")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 4: Update member
print(f"\n=== UPDATE MEMBER {member_id} ===")
update_data = {"phone": "3009876543", "notes": "Actualizado"}
response = requests.put(f"{base_url}/members/{member_id}", json=update_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 5: Search members
print("\n=== SEARCH MEMBERS ===")
response = requests.get(f"{base_url}/members?search=Juan")
print(f"Status: {response.status_code}")
data = response.json()
print(f"Found: {data['total']} members")

# Test 6: Deactivate member
print(f"\n=== DEACTIVATE MEMBER {member_id} ===")
response = requests.delete(f"{base_url}/members/{member_id}")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

print("\n✅ All tests passed!")
