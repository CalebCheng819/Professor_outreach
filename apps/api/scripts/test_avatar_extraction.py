import sys
import os
import logging
from dotenv import load_dotenv

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search import image_scraper
from services.vision import get_vision_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_extraction(url: str):
    print(f"\n--- Testing Extraction for: {url} ---")
    
    # 1. Scrape
    candidates = image_scraper.get_image_candidates(url)
    print(f"Found {len(candidates)} candidates:")
    for c in candidates:
        print(f" - {c}")

    if not candidates:
        print("No candidates found.")
        return

    # 2. Vision
    vision = get_vision_service()
    print(f"\nChecking candidates with Vision Model ({vision.vision_model})...")

    for img_url in candidates[:3]:
        print(f"\nAnalyzing: {img_url}")
        content = image_scraper.download_image(img_url)
        if not content:
            print("  Failed to download.")
            continue
            
        result = vision.verify_avatar(content)
        print(f"  Result: {result}")
        
        if result.get("is_valid") and result.get("confidence", 0) >= 0.75:
            print(f"  ✅ MATCH FOUND! Avatar URL: {img_url}")
            return

    print("\n❌ No valid avatar found.")

if __name__ == "__main__":
    load_dotenv()
    # Test with Wikipedia (reliable source)
    test_extraction("https://en.wikipedia.org/wiki/Geoffrey_Hinton")
