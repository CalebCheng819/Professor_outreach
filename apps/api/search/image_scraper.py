import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import socket
import ipaddress
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# SSRF Protection: Block internal IPs
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]

def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        
        hostname = parsed.hostname
        if not hostname:
            return False

        # Resolve IP
        ip = socket.gethostbyname(hostname)
        ip_addr = ipaddress.ip_address(ip)

        for network in BLOCKED_NETWORKS:
            if ip_addr in network:
                logger.warning(f"Blocked SSRF attempt: {url} points to {ip}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"SSRF check failed for {url}: {e}")
        return False

def get_image_candidates(website_url: str, timeout: int = 10) -> List[str]:
    """
    Scrapes a website for image candidates suitable for a profile picture.
    Returns a list of absolute URLs, sorted by relevance score.
    """
    if not is_safe_url(website_url):
        return []

    try:
        # 1. Fetch HTML
        resp = requests.get(website_url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        
        candidates = []
        seen_urls = set()

        # 2. Extract <img> tags
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue
            
            full_url = urljoin(website_url, src)
            if full_url in seen_urls:
                continue
            
            # Basic filter (extensions)
            if not any(full_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                # Allow query params but check path
                path = urlparse(full_url).path.lower()
                if not any(path.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    continue

            # Calculate Score
            score = 0
            alt = (img.get("alt") or "").lower()
            src_lower = src.lower()
            classes = " ".join(img.get("class", [])).lower()

            # Keywords boost
            keywords = ["profile", "avatar", "photo", "me", "headshot", "face", "portrait"]
            for kw in keywords:
                if kw in alt: score += 10
                if kw in src_lower: score += 5
                if kw in classes: score += 5

            # Negative keywords
            neg_keywords = ["logo", "icon", "banner", "footer", "header", "sprite", "shim", "blank"]
            if any(nw in src_lower or nw in alt or nw in classes for nw in neg_keywords):
                score -= 50

            # Store candidate
            candidates.append({
                "url": full_url,
                "score": score,
                "alt": alt
            })
            seen_urls.add(full_url)

        # 3. Extract Meta OG Image (High confidence usually)
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            og_url = urljoin(website_url, og_image["content"])
            if og_url not in seen_urls:
                candidates.append({
                    "url": og_url,
                    "score": 20, # High baseline score for OG image
                    "alt": "og:image"
                })

        # 4. Sort and return Top 5
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return [c["url"] for c in candidates if c["score"] > -10][:5]

    except Exception as e:
        logger.error(f"Image scraping failed for {website_url}: {e}")
        return []

def download_image(url: str, max_size_mb: int = 5, timeout: int = 10) -> Optional[bytes]:
    """
    Downloads image with size limit protection.
    """
    if not is_safe_url(url):
        logger.warning(f"Unsafe URL blocked: {url}")
        return None

    try:
        # Stream request to check headers first
        with requests.get(url, stream=True, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"}) as r:
            r.raise_for_status()
            
            # Check Content-Length if available
            content_length = r.headers.get("Content-Length")
            if content_length and int(content_length) > max_size_mb * 1024 * 1024:
                logger.warning(f"Image too large (header): {url} ({content_length} bytes)")
                return None
            
            # Read chunks and enforce limit
            content = b""
            for chunk in r.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > max_size_mb * 1024 * 1024:
                    logger.warning(f"Image too large: {url}")
                    return None
            
            return content
    except Exception as e:
        logger.error(f"Download failed {url}: {e}")
        return None
