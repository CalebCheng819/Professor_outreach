import sys
import os
from dotenv import load_dotenv

# Load .env from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

print("--- AI Service Diagnostic ---")

# 1. Check Variables
enabled = os.getenv("LLM_PARSING_ENABLED")
provider = os.getenv("LLM_PROVIDER")
api_key = os.getenv("LLM_API_KEY")

print(f"LLM_PARSING_ENABLED: {enabled}")
print(f"LLM_PROVIDER: {provider}")
print(f"LLM_API_KEY Length: {len(api_key) if api_key else 0}")

if not api_key or "replace_with" in api_key:
    print("❌ ERROR: API Key is unset or still using the placeholder.")
    sys.exit(1)

# 2. Check Imports
print("\nChecking dependencies...")
try:
    if provider == "gemini":
        import google.generativeai as genai
        print("✅ google.generativeai installed")
    elif provider == "openai":
        import openai
        print("✅ openai installed")
except ImportError as e:
    print(f"❌ ImportError: {e}")
    sys.exit(1)

# 3. Test Connection
print(f"\nTesting {provider} connection...")
try:
    from services.llm import LLMService
    service = LLMService()
    
    if not service.enabled:
        print("❌ Service reports disabled (internal logic).")
    else:
        print("Service initialized. Sending test query...")
        results = [{"title": "Test Title", "snippet": "Test Snippet", "link": "http://test.com"}]
        parsed = service.parse_search_results("Test Query", results)
        print(f"✅ Success! Response: {parsed}")

except Exception as e:
    print(f"❌ Runtime Error: {e}")
    import traceback
    traceback.print_exc()
