import requests
import json
import sseclient

base_url = "http://localhost:8000"

print("--- 1. Auth Flow ---")
# Register
res = requests.post(f"{base_url}/auth/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
})
print("Register:", res.status_code, res.text)

# Login
res = requests.post(f"{base_url}/auth/token", data={
    "username": "testuser",
    "password": "password123"
})
print("Login:", res.status_code)
if res.status_code == 200:
    token = res.json()["access_token"]
    print("Token obtained.")
else:
    print(res.text)
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

print("\n--- 2. Upload Flow ---")
# Create sample file
with open("sample.txt", "w") as f:
    f.write("A Golden Retriever is a Scottish breed of retriever dog of medium size. It is characterized by a gentle and affectionate nature and a striking golden coat.")

with open("sample.txt", "rb") as f:
    res = requests.post(f"{base_url}/upload", headers=headers, files={"file": f})
print("Upload:", res.status_code, res.text)

print("\n--- 3. Query Flow (Normal) ---")
res = requests.post(f"{base_url}/query", headers=headers, json={
    "question": "What is a Golden Retriever?",
    "stream": False
})
print("Query:", res.status_code)
print(json.dumps(res.json(), indent=2)[:500] if res.status_code == 200 else res.text)

print("\n--- 4. Query Flow (Streaming) ---")
res = requests.post(f"{base_url}/query", headers=headers, json={
    "question": "Describe the nature of a Golden Retriever.",
    "stream": True
}, stream=True)
print("Query Stream:", res.status_code)
if res.status_code == 200:
    client = sseclient.SSEClient(res)
    for event in client.events():
        print(event.data, end="")
    print("\nStream finished.")
else:
    print(res.text)
