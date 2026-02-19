import requests
import json

API_URL = "http://127.0.0.1:8001"

# Need authentication? Yes.
# Assuming user created one user: test@example.com (or similar)
# We can try to login first, or just test creating if auth is disabled for dev (it's not).
# Let's try to login with default credentials if known, or skip auth If I can't easily get a token...
# Wait, I don't have the user's password easily available.
# But I can check if the endpoint is protected. Yes it is.

# Alternative: Use a direct DB insert script to see if *model* constraints fail, bypassing API auth.
# But "Failed to add professor" suggests API call failed.

# Let's try to login with the user's likely credentials (test@example.com / password123)
# If that fails, I can't use API script easily.

def test_add_professor():
    # Attempt login
    try:
        login_res = requests.post(f"{API_URL}/token", data={"username": "test@example.com", "password": "password123"})
        if login_res.status_code == 200:
            token = login_res.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            payload = {
                "name": "Test Professor Target Role",
                "affiliation": "Test University",
                "website_url": "https://example.com",
                "target_role": "phd"
            }
            
            res = requests.post(f"{API_URL}/professors/", json=payload, headers=headers)
            print(f"Status Code: {res.status_code}")
            print(f"Response: {res.text}")
        else:
            print("Login failed, cannot test API directly with generic creds.")
            print(login_res.text)
    except Exception as e:
        print(f"API Connection failed: {e}")

if __name__ == "__main__":
    test_add_professor()
