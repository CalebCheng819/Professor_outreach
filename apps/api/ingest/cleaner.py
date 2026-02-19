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
