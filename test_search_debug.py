import duckduckgo_search
from duckduckgo_search import DDGS
import sys

print(f"Python version: {sys.version}")
print(f"duckduckgo_search version: {duckduckgo_search.__version__}")

def test_search():
    print("Testing DuckDuckGo Search...")
    query = "Andrew Ng Stanford"
    
    for backend in ["api", "html", "lite"]:
        print(f"\n--- Testing backend: {backend} ---")
        try:
            results = DDGS().text(query, max_results=3, backend=backend)
            results_list = list(results)
            
            if not results_list:
                print(f"[{backend}] No results found.")
            else:
                print(f"[{backend}] Found {len(results_list)} results:")
                for r in results_list:
                    print(f"- {r.get('title')} ({r.get('href')})")
                return # Stop if success
        except Exception as e:
            print(f"[{backend}] Search failed with error: {e}")

if __name__ == "__main__":
    test_search()
