import re
import json

def extract_professor_card(text: str) -> dict:
    """
    Heuristically extracts structured data from professor's raw text.
    """
    card = {
        "summary": "",
        "research_interests": [],
        "selected_publications": [],
        "hiring_signals": []
    }
    
    if not text:
        return card

    # 1. Parsing Helpers
    lines = text.split('\n')
    text_lower = text.lower()

    # --- A. Hiring Signal Matcher ---
    # Look for strong signals of active hiring
    hiring_keywords = [
        r"looking for (Ph\.?D\.?|students|postdocs|research assistants)",
        r"openings? for",
        r"recruiting (Ph\.?D\.?|students)",
        r"accepting (new )?students",
        r"join (my|our) (lab|group|team)",
        r"available positions?",
        r"apply for",
        r"fall 202[4-9]", # Update year logic dynamically if needed, but this covers next few years
    ]
    
    # Store unique detected signals
    detected_signals = set()
    
    # Scan first 100 lines for efficiency (hiring info usually at top)
    for line in lines[:100]:
        line_lower = line.lower()
        for pattern in hiring_keywords:
            if re.search(pattern, line_lower):
                # Clean up the line for display (truncate if too long)
                clean_signal = line.strip()
                if len(clean_signal) > 100:
                   clean_signal = clean_signal[:100] + "..."
                detected_signals.add(clean_signal)
    
    card["hiring_signals"] = list(detected_signals)

    # --- B. Extract Research Interests ---
    # Improve existing logic
    interests_pattern = re.compile(r"(?i)(current )?(research\s+)?(interests|areas|focus)\s*[:\-\u2013\u2014]?\s*(.*)")
    
    found_explicit_interests = False
    for i, line in enumerate(lines):
        match = interests_pattern.search(line)
        if match:
            content = match.group(4).strip()
            
            # If explicit interests are on the same line
            if content and len(content) > 3:
                items = [item.strip() for item in re.split(r'[,;]', content) if len(item.strip()) > 2]
                card["research_interests"].extend(items)
                found_explicit_interests = True
            # If header is on its own line, look at next lines
            else:
                # heuristic: look at next 3 lines, stop if empty or starts with bullet
                for j in range(1, 5):
                    if i + j >= len(lines): break
                    next_line = lines[i+j].strip()
                    if not next_line: continue
                    if re.match(r"(?i)(selected|public|award|teaching)", next_line): break # hit next section
                    
                    # Split comma separated lists or take bullet points
                    items = [item.strip() for item in re.split(r'[,;•\-\*]', next_line) if len(item.strip()) > 3 and len(item.strip()) < 50]
                    card["research_interests"].extend(items)
                    if items: found_explicit_interests = True
            
            if found_explicit_interests:
                break 

    # --- C. Keyword Extractor (Fallback) ---
    # If no explicit interests found, do a simple frequency analysis of capitalized phrases
    if not card["research_interests"]:
        # Exclude common words
        common_stops = {"the", "and", "for", "with", "university", "professor", "department", "science", "school", "research"}
        
        # Find 2-3 word phrases that appear frequently or are capitalized (Concept, Machine Learning, etc)
        # This is a dumb heuristic replacing NLP for now
        candidates = {}
        # Look for Title Case phrases in the text
        phrase_pattern = re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)?\b')
        matches = phrase_pattern.findall(text)
        
        for m in matches:
            if m.lower() in candidates:
                candidates[m.lower()]['count'] += 1
            else:
                # Filter out likely names or boring headers
                if any(w.lower() in common_stops for w in m.split()): continue
                candidates[m.lower()] = {'text': m, 'count': 1}
        
        # Sort by count
        sorted_candidates = sorted(candidates.values(), key=lambda x: x['count'], reverse=True)
        card["research_interests"] = [item['text'] for item in sorted_candidates[:5]]

    # Fallback: limit interests
    if len(card["research_interests"]) > 6:
        card["research_interests"] = card["research_interests"][:6]


    # --- D. Extract Publications ---
    pub_header_idx = -1
    for i, line in enumerate(lines):
        if re.search(r"(?i)(selected|recent)\s+publications|publications", line):
            pub_header_idx = i
            break
            
    if pub_header_idx != -1:
        count = 0
        # Look for lines that look like citations
        for i in range(pub_header_idx + 1, min(len(lines), pub_header_idx + 100)):
            line = lines[i].strip()
            if not line: continue
            
            # Heuristic: Contains Year (199x-202x) AND (Author-ish or Quotes)
            # 1. Check Year
            if re.search(r"\b(19|20)\d{2}\b", line) and len(line) > 40:
                # 2. Check for typical paper indicators: "et al", quoted title, conference acronyms
                if re.search(r"et al|pp\.|vol\.|proc\.|conf\.|arXiv|CVPR|ICML|NeurIPS|ICLR|ECCV", line, re.IGNORECASE) or '"' in line:
                    card["selected_publications"].append(line)
                    count += 1
            
            if count >= 3:
                break

    # --- E. Summary ---
    # Take the first substantial paragraph that isn't a header
    for line in lines[:25]:
        clean = line.strip()
        if len(clean) > 80:
             # Skip if it looks like a list item or citation
             if re.match(r"^[\-•\*]", clean) or re.search(r"\b(19|20)\d{2}\b", clean):
                 continue
             card["summary"] = clean[:300] + "..."
             break

    return card
