import re
import json

def extract_professor_card(text: str) -> dict:
    """
    Heuristically extracts structured data from professor's raw text.
    """
    card = {
        "summary": "",
        "research_interests": [],
        "selected_publications": []
    }
    
    if not text:
        return card

    # 1. Extract Research Interests
    # Look for lines starting with "Research Interests", "Interests", "Research Areas"
    interests_pattern = re.compile(r"(?i)(research\s+)?(interests|areas|focus)\s*[:\-\u2013\u2014]?\s*(.*)")
    
    lines = text.split('\n')
    for line in lines:
        match = interests_pattern.search(line)
        if match:
            # Found header, take the rest of the line or next few lines
            content = match.group(3).strip()
            if not content:
                # If header is on its own line, look at next lines until empty
                pass # TODO: Implement multi-line extraction
            else:
                # Split by commas or semicolons
                items = [item.strip() for item in re.split(r'[,;]', content) if item.strip()]
                card["research_interests"].extend(items)
            break # Assume only one interests section for now

    # Fallback: limit interests to top 5 if too many
    if len(card["research_interests"]) > 5:
        card["research_interests"] = card["research_interests"][:5]

    # 2. Extract Publications (Simple keyword search for now)
    # This is hard without LLM. We'll look for lines that look like citations (Year, "et al", etc)
    # near a "Publications" header.
    
    pub_header_idx = -1
    for i, line in enumerate(lines):
        if re.search(r"(?i)selected\s+publications|recent\s+publications|publications", line):
            pub_header_idx = i
            break
            
    if pub_header_idx != -1:
        # Scan next 20 lines for potential publications
        count = 0
        for i in range(pub_header_idx + 1, min(len(lines), pub_header_idx + 50)):
            line = lines[i].strip()
            if not line: continue
            
            # Heuristic: Line contains a year (1990-2030) and is long enough
            if re.search(r"\b(19|20)\d{2}\b", line) and len(line) > 50:
                card["selected_publications"].append(line)
                count += 1
                if count >= 3: # Limit to 3 for card
                    break

    # 3. Summary (First non-empty paragraph? Or just first 200 chars)
    # Heuristic: Take the first paragraph that has "Professor" or "Ph.D." or looks like bio.
    # For now, just take the first substantial paragraph ( > 100 chars).
    for line in lines[:20]: # Check first 20 lines
        if len(line.strip()) > 100:
            card["summary"] = line.strip()[:300] + "..."
            break

    return card
