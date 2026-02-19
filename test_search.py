from duckduckgo_search import DDGS

def test_search():
    print("Testing DuckDuckGo Search...")
    query = "Andrew Ng Stanford"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                print("No results found.")
            else:
                print(f"Found {len(results)} results:")
                for r in results:
                    print(f"- {r.get('title')} ({r.get('href')})")
    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    test_search()
