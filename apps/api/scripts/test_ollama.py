"""Test Ollama with format=json to force JSON-only output."""
import requests
import json

# 1. List available models
r = requests.get("http://localhost:11434/api/tags", timeout=5)
models = [m["name"] for m in r.json().get("models", [])]
print(f"Available models: {models}")

# 2. Test with format: json (Ollama's JSON mode)
print("\n=== Test: format=json ===")
r = requests.post("http://localhost:11434/api/chat", json={
    "model": "qwen3:4b",
    "messages": [
        {"role": "system", "content": "You extract professor info from search results. Output a JSON object with key 'results' containing an array of professor objects."},
        {"role": "user", "content": 'Query: "chen tang"\nResult 0: Title=\'Chen Tang - GitHub Pages\', Snippet=\'Research interests in AI and robotics\', Link=\'https://chentang.github.io\'\n\nExtract: name, affiliation (or null), role (or null), confidence (0-1), source_index (int).'}
    ],
    "stream": False,
    "think": False,
    "format": "json",
    "options": {"temperature": 0.1, "num_predict": 256}
}, timeout=120)

data = r.json()
msg = data.get("message", {})
content = msg.get("content", "")

with open("ollama_json_test.txt", "w", encoding="utf-8") as f:
    f.write(f"content ({len(content)} chars):\n{content}\n")
    f.write(f"\ndone_reason: {data.get('done_reason')}\n")
    f.write(f"duration: {data.get('total_duration',0)/1e9:.1f}s\n")

print(f"Content ({len(content)} chars): {content[:500]}")
print(f"Done reason: {data.get('done_reason')}")
print(f"Duration: {data.get('total_duration',0)/1e9:.1f}s")
print("\nSee ollama_json_test.txt for full output")
