import os
import requests
from typing import Dict, Any, Optional

class LlamaClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Llama client with API key."""
        self.api_key = api_key or os.getenv("LLAMA_API_KEY")
        if not self.api_key:
            raise ValueError("Llama API key is required")
        
        try:
            # Using the Together.ai API for Llama access
            self.api_url = "https://api.together.xyz/v1/completions"
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.model = "togethercomputer/llama-2-7b-chat"  # Using a more accessible model
            self.initialized = True
        except Exception as e:
            print(f"Error initializing Llama client: {e}")
            self.initialized = False
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response from Llama API."""
        if not self.initialized:
            return {
                "text": "Llama client is not properly initialized.",
                "model": "llama-2-7b-chat",
                "success": False
            }
            
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000)
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return {
                "text": result["choices"][0]["text"],
                "model": self.model,
                "success": True
            }
        except Exception as e:
            return {
                "text": f"Error with Llama API: {str(e)}",
                "model": self.model,
                "success": False
            }
