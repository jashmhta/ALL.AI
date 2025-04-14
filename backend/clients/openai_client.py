import os
import openai
from typing import Dict, Any, Optional

class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI client with API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        openai.api_key = self.api_key
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response from OpenAI API."""
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                **kwargs
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
