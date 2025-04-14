import os
import requests
from typing import Dict, Any, Optional

class OpenRouterClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenRouter client with API key."""
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_response(self, prompt: str, model: str = "openai/gpt-3.5-turbo", **kwargs) -> Dict[str, Any]:
        """Generate a response from OpenRouter API."""
        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                **kwargs
            }
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return {
                "text": result["choices"][0]["message"]["content"],
                "model": model,
                "success": True
            }
        except Exception as e:
            return {
                "text": f"Error with OpenRouter API: {str(e)}",
                "model": model,
                "success": False
            }
