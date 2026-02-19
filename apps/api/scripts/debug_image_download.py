import requests

url = "https://chentangmark.github.io/assets/img/prof_pic.jpg?e78d09b411a57d4537ff19da512eb5f1"

print(f"Testing download: {url}")
try:
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    print(f"Status Code: {resp.status_code}")
    print(f"Headers: {resp.headers}")
    if resp.status_code != 200:
        print("❌ Failed: Status not 200")
    else:
        print(f"✅ Success. Size: {len(resp.content)} bytes")
except Exception as e:
    print(f"❌ Exception: {e}")
