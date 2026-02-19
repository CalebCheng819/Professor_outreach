import sys
import os
import socket
import logging

# Add parent path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search import image_scraper

logging.basicConfig(level=logging.INFO)

url = "https://chentangmark.github.io/assets/img/prof_pic.jpg?e78d09b411a57d4537ff19da512eb5f1"
print(f"Testing is_safe_url for: {url}")

try:
    hostname = "chentangmark.github.io"
    ip = socket.gethostbyname(hostname)
    print(f"Resolved IP: {ip}")
    
    is_safe = image_scraper.is_safe_url(url)
    print(f"is_safe_url result: {is_safe}")
    
    if not is_safe:
        print("❌ URL blocked by SSRF check")
    else:
        print("✅ URL passed SSRF check")
        
except Exception as e:
    print(f"Error: {e}")
