import os
from openai import OpenAI
from typing import Dict, Any, Optional

class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI client with API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize OpenAI client without proxies parameter
        self.client = OpenAI(api_key=self.api_key)
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response from OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1000)
            )
            return {
                "text": response.choices[0].message.content,
                "model": "gpt-3.5-turbo",
                "success": True
            }
        except Exception as e:
            return {
                "text": f"Error with OpenAI API: {str(e)}",
                "model": "gpt-3.5-turbo",
                "success": False
            }
