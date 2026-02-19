import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def extract_affiliation(title: str, snippet: str) -> str:
    """
    Extracts affiliation from title or snippet using heuristics.
    """
    # Keywords that strongly suggest an academic institution
    university_keywords = [
        "University", "Institute", "College", "School of", "Department of", 
        "Lab", "Center", "Faculty", "Academy", "Polytechnic"
    ]
    
    # invalid affiliations to filter out
    invalid_affiliations = ["Home", "Home Page", "Welcome", "Profile", "Bio", "About", "Google Scholar", "LinkedIn"]

    possible_affiliation = ""

    # Strategy 1: Title Split
    # Common patterns: "Name - University of X", "Name | University of X", "Name at University of X"
    separators = [" - ", " | ", " – ", " — ", " : ", " at "]
    for sep in separators:
        if sep in title:
            parts = title.split(sep)
            # Usually affiliation is after the name, so check parts[1:]
            for part in parts[1:]:
                clean_part = part.strip()
                # If it contains a keyword, it's a strong candidate
                if any(kw in clean_part for kw in university_keywords):
                    possible_affiliation = clean_part
                    break
            if possible_affiliation: break
    
    # Strategy 2: Regex on Title (if Strategy 1 failed or generic)
    if not possible_affiliation:
        # "University of X"
        match = re.search(r"(University of [A-Z][a-z]+(?: [A-Z][a-z]+)*)", title)
        if match:
            possible_affiliation = match.group(1)
        
        # "X University"
        if not possible_affiliation:
            match = re.search(r"([A-Z][a-z]+(?: [A-Z][a-z]+)* (?:University|Institute|College))", title)
            if match:
                possible_affiliation = match.group(1)

    # Strategy 3: Snippet (Fall back)
    # "Professor at X"
    if not possible_affiliation and snippet:
        match = re.search(r"(?:professor|researcher|lecturer|student) at ([A-Z][a-z]+(?: [A-Z][a-z]+)+(?: University| Institute| College)?)", snippet, re.IGNORECASE)
        if match:
            possible_affiliation = match.group(1)

    # Cleanup
    if possible_affiliation:
        # Remove trailing punctuation
        possible_affiliation = re.sub(r"[^\w\s)]+$", "", possible_affiliation).strip()
        
        # Filter out if it's just a generic word
        if possible_affiliation.lower() in [x.lower() for x in invalid_affiliations]:
            return ""
            
    return possible_affiliation

from cachetools import TTLCache
import logging

# Cache: 100 queries, TTL 1 hour
search_cache = TTLCache(maxsize=100, ttl=3600)
logger = logging.getLogger(__name__)

def search_professor(query: str, max_results: int = 5):
    """
    Searches for professors using DuckDuckGo HTML version.
    Fast rule-based only. AI parsing happens on click via /parse_search_result.
    """
    # 1. Check Cache
    if query in search_cache:
        logger.info(f"Cache hit for query: {query}")
        return search_cache[query]

    print(f"Searching for '{query}'...")
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://html.duckduckgo.com/"
    }
    data = {"q": query}
    
    raw_results = []
    
    try:
        resp = requests.post(url, data=data, headers=headers, timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for res in soup.find_all("div", class_="result"):
            if len(raw_results) >= max_results:
                break
                
            title_tag = res.find("a", class_="result__a")
            if not title_tag:
                continue
                
            link = title_tag["href"]
            if link.startswith("/l/?"):
                qs = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
                if 'uddg' in qs:
                    link = qs['uddg'][0]

            title = title_tag.get_text(strip=True)
            
            # Pre-filter junk
            if any(junk in title.lower() for junk in ["login", "sign up", "404", "index of"]):
                continue

            snippet_tag = res.find("a", class_="result__snippet")
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
            
            # Rule-based extraction (fast)
            affiliation = extract_affiliation(title, snippet)
            
            # Rule-based name extraction
            name = title
            GENERIC_TITLES = ["GitHub Pages", "Home", "Home Page", "Welcome", "Profile", "Bio", "About", "Index", "Default"]
            if name in GENERIC_TITLES or name.lower() in [t.lower() for t in GENERIC_TITLES]:
                name = query.title()
            else:
                separators = [" - ", " | ", " – ", " — ", " : ", " at "]
                for sep in separators:
                    if sep in title:
                        potential = title.split(sep)[0].strip()
                        if len(potential.split()) <= 4:
                            name = potential
                            break
            
            raw_results.append({
                "title": title,
                "name": name,
                "link": link,
                "snippet": snippet,
                "affiliation": affiliation
            })
            
    except Exception as e:
        print(f"Search error: {e}")
        return []

    # Cache and Return
    search_cache[query] = raw_results
    return raw_results

