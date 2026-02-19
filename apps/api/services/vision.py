import requests
import base64
import os
import json
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.vision_model = os.getenv("VISION_MODEL", "llama3.2-vision")
    
    def verify_avatar(self, image_bytes: bytes) -> Dict:
        """
        Verifies if the image is a professional human face.
        Returns: {"is_valid": bool, "confidence": float, "reason": str}
        """
        try:
            # Encode image to base64
            b64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            prompt = """Analyze this image. determine if it contains a human face.
            Return a JSON object with these keys:
            - "is_human_face": boolean (true if a clear human face is present)
            - "confidence": float (0.0 to 1.0)
            - "reason": string (short explanation)
            """

            logger.info(f"[Vision] Sending request to {self.vision_model}...")
            resp = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.vision_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                            "images": [b64_image]
                        }
                    ],
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": 0.1, "num_predict": 128}
                },
                timeout=45 # Increased timeout
            )
            resp.raise_for_status()
            
            # Parse response
            data = resp.json()
            content = data.get("message", {}).get("content", "")
            logger.info(f"[Vision] Raw Response: {content}")
            
            try:
                result = json.loads(content)
                
                is_human = result.get("is_human_face", False)
                confidence = result.get("confidence", 0.0)
                
                # Decision logic (RELAXED: Just needs to be a human)
                is_valid = is_human and confidence >= 0.6 
                
                logger.info(f"[Vision] Decision: Valid={is_valid} (Human={is_human}, Conf={confidence})")
                
                return {
                    "is_valid": is_valid,
                    "confidence": confidence,
                    "reason": result.get("reason", "No reason provided")
                }
                
            except json.JSONDecodeError:
                logger.error(f"[Vision] JSON decode failed: {content}")
                return {"is_valid": False, "confidence": 0.0, "reason": "JSON Parse Error"}

        except Exception as e:
            logger.error(f"[Vision] Verification failed: {e}")
            return {"is_valid": False, "confidence": 0.0, "reason": str(e)}

# Singleton
_vision_service = None

def get_vision_service() -> VisionService:
    global _vision_service
    if not _vision_service:
        _vision_service = VisionService()
    return _vision_service
