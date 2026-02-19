import requests
from bs4 import BeautifulSoup
import time

def search_ddg_html(query, max_results=5):
    print(f"Searching DDG HTML for '{query}'...")
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://html.duckduckgo.com/"
    }
    data = {"q": query}
    
    try:
        resp = requests.post(url, data=data, headers=headers, timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        
        # DDG HTML results are usually in div.result
        for res in soup.find_all("div", class_="result"):
            if len(results) >= max_results:
                break
                
            title_tag = res.find("a", class_="result__a")
            if not title_tag:
                continue
                
            link = title_tag["href"]
            title = title_tag.get_text(strip=True)
            snippet_tag = res.find("a", class_="result__snippet")
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
            
            results.append({
                "title": title,
                "link": link,
                "snippet": snippet
            })
            
        return results

    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    res = search_ddg_html("Andrew Ng Stanford")
    if not res:
        print("No results found.")
    for r in res:
        print(f"- {r['title']} ({r['link']})")
