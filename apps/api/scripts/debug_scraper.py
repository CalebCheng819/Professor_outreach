import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def check(url):
    print(f"\n--- Checking {url} ---")
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('Content-Type')}")
        
        soup = BeautifulSoup(resp.content, "html.parser")
        title = soup.title.string.strip() if soup.title else 'No Title'
        print(f"Page Title: {title}")
        
        imgs = soup.find_all("img")
        print(f"Found {len(imgs)} img tags")
        
        for i, img in enumerate(imgs[:5]): # Show first 5
            src = img.get("src")
            print(f" - [{i}] SRC: {src}")
            if src:
                full = urljoin(url, src)
                print(f"       FULL: {full}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check("https://www.cs.toronto.edu/~hinton/")
    check("https://www.stanford.edu")
