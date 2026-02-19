import requests
import json

BASE_URL = "http://localhost:8000"

def test_email_gen():
    print(f"Testing email generation at {BASE_URL}...")
    
    # 1. Get List of Professors
    resp = requests.get(f"{BASE_URL}/professors/")
    profs = resp.json()
    if not profs:
        print("No professors found. Please run test_extraction.py first.")
        return

    prof_id = profs[0]["id"]
    prof_name = profs[0]["name"]
    print(f"Using Professor: {prof_name} ({prof_id})")

    # 2. Generate Draft (Summer Intern)
    print("Generating 'summer_intern' draft...")
    gen_resp = requests.post(
        f"{BASE_URL}/professors/{prof_id}/generate-email?template=summer_intern"
    )
    if gen_resp.status_code != 200:
        print(f"Failed to generate email: {gen_resp.text}")
        return

    draft = gen_resp.json()
    print("\n[SUCCESS] Draft Generated:")
    print(f"Subject: {draft['subject']}")
    print("-" * 20)
    print(draft['body'])
    print("-" * 20)

if __name__ == "__main__":
    test_email_gen()
