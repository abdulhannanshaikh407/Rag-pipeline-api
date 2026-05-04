import asyncio
import httpx
import os

API_URL = "http://localhost:8000"
TEST_FILE = "eiffel.txt"

with open(TEST_FILE, "w") as f:
    f.write("The Eiffel Tower is located in Paris. It was built in 1889.")

async def run_test():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Register User
        print("Registering user...")
        res = await client.post(f"{API_URL}/auth/register", json={
            "username": "testuser6",
            "email": "test6@example.com",
            "password": "password123"
        })
        if res.status_code not in (200, 400):
            print(f"Failed to register: {res.text}")
            return False
            
        # 2. Login
        print("Logging in...")
        res = await client.post(f"{API_URL}/auth/token", data={
            "username": "testuser6",
            "password": "password123"
        })
        if res.status_code != 200:
            print(f"Failed to login: {res.text}")
            return False
            
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Upload Document
        print("Uploading document...")
        with open(TEST_FILE, "rb") as f:
            files = {"file": ("eiffel.txt", f, "text/plain")}
            res = await client.post(f"{API_URL}/upload", headers=headers, files=files)
            if res.status_code != 200:
                print(f"Failed to upload: {res.text}")
                return False
        
        # Give it a second to process in background
        await asyncio.sleep(2)
        
        # 4. Query
        print("Querying...")
        res = await client.post(f"{API_URL}/query", headers=headers, json={
            "question": "Where is the Eiffel Tower located?",
            "stream": False
        })
        
        if res.status_code != 200:
            print(f"Failed to query: {res.text}")
            return False
            
        data = res.json()
        print("\n--- RESULT ---")
        print(f"Answer: {data.get('answer')}")
        print("--------------")
        
        if "Paris" in data.get('answer', ''):
            print("\nPASS")
            return True
        else:
            print("\nFAIL - 'Paris' not found in answer")
            return False

if __name__ == "__main__":
    asyncio.run(run_test())
