from googlesearch import search

def test_google():
    print("Testing Google Search...")
    query = "Andrew Ng Stanford"
    try:
        results = search(query, num_results=3, advanced=True)
        for r in results:
            print(f"- {r.title} ({r.url})")
            print(f"  {r.description}")
    except Exception as e:
        print(f"Google Search failed: {e}")

if __name__ == "__main__":
    test_google()
