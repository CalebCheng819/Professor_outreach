"""
LLM Service — Ollama Only (local, free, private)

Install Ollama: https://ollama.com
Pull a model:   ollama pull qwen3:4b
"""
import os
import json
import requests as http_requests
from typing import List, Dict, Optional
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)


class ParsedProfile(BaseModel):
    name: str
    affiliation: Optional[str] = None
    role: Optional[str] = None
    confidence: float = 0.5
    source_index: int


class LLMService:
    """Ollama-only LLM service. Calls local Ollama API."""

    def __init__(self):
        self.enabled = os.getenv("LLM_PARSING_ENABLED", "true").lower() == "true"
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen3:4b")

        if not self.enabled:
            print("[LLM] ⚠️  DISABLED by config.")
            return

        # Check if Ollama is running
        try:
            r = http_requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if r.status_code == 200:
                models = [m["name"] for m in r.json().get("models", [])]
                if self.ollama_model in models or any(self.ollama_model.split(":")[0] in m for m in models):
                    print(f"[LLM] ✅ Ollama ready: model={self.ollama_model}")
                elif models:
                    self.ollama_model = models[0]
                    print(f"[LLM] ✅ Ollama ready: using available model '{self.ollama_model}'")
                else:
                    print(f"[LLM] ❌ Ollama running but no models! Run: ollama pull {self.ollama_model}")
                    self.enabled = False
            else:
                print(f"[LLM] ❌ Ollama responded with {r.status_code}")
                self.enabled = False
        except Exception:
            print(f"[LLM] ❌ Ollama not reachable at {self.ollama_url}")
            print(f"[LLM]    Install: https://ollama.com  then: ollama pull {self.ollama_model}")
            self.enabled = False

    def parse_search_results(self, query: str, results: List[Dict]) -> List[ParsedProfile]:
        """Parse search results using local Ollama."""
        if not self.enabled:
            return []

        prompt = self._build_prompt(query, results)

        try:
            response_text = self._call_ollama(prompt)
            return self._parse_response(response_text)
        except Exception as e:
            print(f"[LLM] Parsing failed: {e}")
            return []

    def _build_prompt(self, query: str, results: List[Dict]) -> str:
        snippets = []
        for i, res in enumerate(results):
            snippets.append(
                f"Result {i}: Title='{res['title']}', Snippet='{res.get('snippet','')}', Link='{res.get('link','')}'"
            )
        joined = "\n".join(snippets)

        return f"""Query: "{query}"

{joined}

Extract professor info. Return a JSON object with key "results" containing an array.
Each item: "name" (string), "affiliation" (string or null), "role" (string or null), "confidence" (0.0-1.0), "source_index" (int).
If title is generic like "GitHub Pages", infer name from the query."""

    def chat(self, user_prompt: str, system_prompt: str = None) -> str:
        """Generic chat completion."""
        if not self.enabled:
            return ""
        return self._call_ollama(user_prompt, system_prompt)

    def _call_ollama(self, prompt: str, system_prompt: str = None) -> str:
        print(f"[LLM] Calling Ollama ({self.ollama_model})...")
        
        default_system = "You extract professor info from search results. Output a JSON object with key 'results' containing an array of professor objects."
        actual_system = system_prompt or default_system

        resp = http_requests.post(
            f"{self.ollama_url}/api/chat",
            json={
                "model": self.ollama_model,
                "messages": [
                    {"role": "system", "content": actual_system},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "think": False,
                "format": "json",
                "options": {"temperature": 0.7 if system_prompt else 0.1, "num_predict": 1024} # Higher temp/tokens for creative tasks
            },
            timeout=120
        )
        resp.raise_for_status()
        data = resp.json()
        result = data.get("message", {}).get("content", "")
        duration = data.get("total_duration", 0) / 1e9
        print(f"[LLM] Ollama responded ({len(result)} chars, {duration:.1f}s)")
        return result

    def _parse_response(self, text: str) -> List[ParsedProfile]:
        text = text.strip()
        if not text:
            return []

        try:
            data = json.loads(text)

            # Handle {"results": [...]} wrapper
            if isinstance(data, dict):
                data = data.get("results", data.get("professors", []))

            # Handle direct array
            if not isinstance(data, list):
                data = [data]

            profiles = []
            for item in data:
                try:
                    profiles.append(ParsedProfile(**item))
                except ValidationError:
                    continue
            return profiles
        except json.JSONDecodeError:
            logger.error(f"[LLM] JSON decode failed: {text[:200]}")
            return []
