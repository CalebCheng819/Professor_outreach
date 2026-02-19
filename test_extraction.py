import requests
import time

BASE_URL = "http://localhost:8000"

def test_extraction():
    print(f"Testing extraction at {BASE_URL}...")
    
    # 1. Create a Professor with a real URL (using Yann LeCun as example)
    prof_data = {
        "name": "Yann LeCun",
        "affiliation": "NYU",
        "website_url": "http://yann.lecun.com/"
    }
    
    # Check if exists first to avoid duplicates or assume new
    print("1. Creating/Getting Professor...")
    resp = requests.post(f"{BASE_URL}/professors/", json=prof_data)
    if resp.status_code not in [200, 201]:
        print(f"Failed to create professor: {resp.text}")
        return
    
    prof_id = resp.json()["id"]
    print(f"   Professor ID: {prof_id}")

    # 2. Ingest content
    print("2. Ingesting Website (Fetching & Cleaning)...")
    ingest_resp = requests.post(f"{BASE_URL}/ingest", json={"professor_id": prof_id, "url": prof_data["website_url"]})
    if ingest_resp.status_code != 200:
        print(f"   Ingestion failed: {ingest_resp.text}")
        return
    print("   Ingestion successful.")

    # 3. Generate Card
    print("3. Generating Professor Card...")
    card_resp = requests.post(f"{BASE_URL}/professors/{prof_id}/generate-card")
    if card_resp.status_code != 200:
        print(f"   Card generation failed: {card_resp.text}")
        return
    
    card = card_resp.json()
    print("\n[SUCCESS] Card Generated:")
    print("--------------------------------------------------")
    print(card["card_md"])
    print("--------------------------------------------------")

if __name__ == "__main__":
    test_extraction()
