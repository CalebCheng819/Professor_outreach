from readability import Document
from bs4 import BeautifulSoup

def clean_html(raw_html: str):
    if not raw_html:
        return ""
    
    try:
        doc = Document(raw_html)
        summary_html = doc.summary()
        
        soup = BeautifulSoup(summary_html, "lxml")
        text = soup.get_text(separator="\n", strip=True)
        return text
    except Exception as e:
        # Fallback if readability fails
        try:
            soup = BeautifulSoup(raw_html, "lxml")
            return soup.get_text(separator="\n", strip=True)
        except:
            return ""

def extract_images(raw_html: str, source_url: str):
    """
    Extracts potential profile images from raw HTML.
    Returns the best guess for an avatar URL, or None.
    """
    if not raw_html:
        return None
        
    try:
        soup = BeautifulSoup(raw_html, "lxml")
        
        # 1. Open Graph Image (High confidence)
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return _make_absolute(og_image["content"], source_url)
            
        # 2. Twitter Image
        twitter_image = soup.find("meta", name="twitter:image")
        if twitter_image and twitter_image.get("content"):
            return _make_absolute(twitter_image["content"], source_url)
            
        # 3. Heuristic: Look for images with "profile", "avatar", "portrait" in src, class, or id.
        # This is risky but useful for academic sites.
        images = soup.find_all("img")
        for img in images:
            src = img.get("src", "")
            alt = img.get("alt", "")
            cls = " ".join(img.get("class", []))
            id_ = img.get("id", "")
            
            score = 0
            combined = (src + alt + cls + id_).lower()
            
            if "profile" in combined: score += 2
            if "avatar" in combined: score += 2
            if "portrait" in combined: score += 1
            if "photo" in combined: score += 1
            if "me" in combined.split(): score += 1  # reckless? maybe.
            
            if score >= 2 and src:
                return _make_absolute(src, source_url)

        # 4. Fallback: Find the largest image? (Maybe too risky)
        
    except Exception as e:
        print(f"Image extraction error: {e}")
        return None
        
    return None

def _make_absolute(url: str, base: str):
    if not url: return None
    from urllib.parse import urljoin
    return urljoin(base, url)
