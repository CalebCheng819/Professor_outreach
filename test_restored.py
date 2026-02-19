import requests
import time
import sys

# Ensure we can import from apps/api if running locally, 
# but here we test via HTTP so standard requests is fine.

BASE_URL = "http://localhost:8000"

def test_restored_backend():
    print(f"Testing backend at {BASE_URL}...")
    try:
        # 1. Check health/list
        resp = requests.get(f"{BASE_URL}/professors/")
        if resp.status_code != 200:
            print(f"Failed to connect to backend: {resp.status_code}")
            return False
        print("Backend is accessible.")
        
        # 2. Create a professor
        print("Creating test professor...")
        prof_data = {
            "name": "Restoration Test",
            "affiliation": "Recovery Univ",
            "website_url": "http://example.com"
        }
        resp = requests.post(f"{BASE_URL}/professors/", json=prof_data)
        if resp.status_code == 200:
            print(f"Professor created: {resp.json()['id']}")
            return True
        else:
            print(f"Failed to create professor: {resp.text}")
            return False
            
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    if test_restored_backend():
        print("Restoration verification PASSED.")
    else:
        print("Restoration verification FAILED.")
