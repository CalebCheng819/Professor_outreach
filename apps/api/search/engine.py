from duckduckgo_search import DDGS

def search_professor(query: str, max_results: int = 5):
    """
    Searches for professors using DuckDuckGo.
    Returns a list of dictionaries with title, href, and body.
    """
    results = []
    try:
        with DDGS() as ddgs:
            # simple text search
            # we can append "professor" or "university" to query if needed, 
            # but user might type "Andrew Ng Stanford", which is good enough.
            ddgs_gen = ddgs.text(query, max_results=max_results)
            if ddgs_gen:
                for r in ddgs_gen:
                    results.append({
                        "title": r.get("title", ""),
                        "link": r.get("href", ""),
                        "snippet": r.get("body", "")
                    })
    except Exception as e:
        print(f"Search error: {e}")
        return []

    return results
