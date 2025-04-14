import os
import requests
from typing import Dict, Any, Optional

class HuggingFaceClient:
    def __init__(self, api_key: Optional[str] = None, model_id: str = "google/flan-t5-xxl"):
        """Initialize the Hugging Face client with API key."""
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("Hugging Face API key is required")
        
        self.model_id = model_id
        self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response from Hugging Face API."""
        try:
            payload = {"inputs": prompt, **kwargs}
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return {
                    "text": result[0].get("generated_text", ""),
                    "model": self.model_id,
                    "success": True
                }
            return {
                "text": str(result),
                "model": self.model_id,
                "success": True
            }
        except Exception as e:
            return {
                "text": f"Error with Hugging Face API: {str(e)}",
                "model": self.model_id,
                "success": False
            }
