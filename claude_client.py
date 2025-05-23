import os
from anthropic import Anthropic
from typing import Dict, Any, Optional

class ClaudeClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Claude client with API key."""
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError("Claude API key is required")
        
        try:
            # Initialize Anthropic client with just the API key
            self.client = Anthropic(api_key=self.api_key)
            self.model = "claude-3-opus-20240229"
        except Exception as e:
            print(f"Error initializing Claude client: {e}")
            self.client = None
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response from Claude API."""
        if not self.client:
            return {
                "text": "Claude client is not properly initialized.",
                "model": "claude-3-opus-20240229",
                "success": False
            }
            
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "text": response.content[0].text,
                "model": self.model,
                "success": True
            }
        except Exception as e:
            return {
                "text": f"Error with Claude API: {str(e)}",
                "model": self.model,
                "success": False
            }
