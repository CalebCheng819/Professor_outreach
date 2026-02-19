import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_fetcher_session():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })
    return session

def fetch_url(url: str, timeout: int = 15):
    session = get_fetcher_session()
    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        return {
            "source_url": url,
            "raw_html": response.text,
            "fetch_status": "ok",
            "error_msg": None
        }
    except Exception as e:
        return {
            "source_url": url,
            "raw_html": None,
            "fetch_status": "failed",
            "error_msg": str(e)
        }
