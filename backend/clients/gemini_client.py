import os
import google.generativeai as genai
from typing import Dict, Any, Optional

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini client with API key."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response from Gemini API."""
        try:
            response = self.model.generate_content(prompt, **kwargs)
            return {
                "text": response.text,
                "model": "gemini-1.5-flash",
                "success": True
            }
        except Exception as e:
            return {
                "text": f"Error with Gemini API: {str(e)}",
                "model": "gemini-1.5-flash",
                "success": False
            }
