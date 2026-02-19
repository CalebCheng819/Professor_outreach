import sys
import os
import logging
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search import image_scraper
from services.vision import get_vision_service

logging.basicConfig(level=logging.INFO)

def check_url(url):
    print(f"\n--- Checking URL: {url} ---")
    
    # 1. Scrape
    candidates = image_scraper.get_image_candidates(url)
    print(f"Scraper found {len(candidates)} candidates.")
    for c in candidates:
        print(f"  Candidate: {c}")

    if not candidates:
        print("  ❌ No candidates found.")
        return

    # 2. Vision
    vision = get_vision_service()
    print(f"  Vision Model: {vision.vision_model}")
    
    found = False
    for img_url in candidates[:5]:
        print(f"\n  Analyzing: {img_url}")
        content = image_scraper.download_image(img_url)
        if not content:
            print("    ❌ Download failed.")
            continue
            
        result = vision.verify_avatar(content)
        print(f"    Vision Result: {result}")
        
        if result.get("is_valid") and result.get("confidence", 0) >= 0.75:
            print("    ✅ ACCEPTED")
            found = True
        else:
            print("    ❌ REJECTED")

    if not found:
        print("\n  ❌ All candidates rejected.")

if __name__ == "__main__":
    load_dotenv()
    # Test common variations found
    check_url("https://chentang.cc")
    check_url("https://www.american.edu/kogod/faculty/chentang.cfm")
    check_url("https://samueli.ucla.edu/people/chen-tang/")
