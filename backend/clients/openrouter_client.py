import os
import asyncio
from typing import Dict, Any, Optional, List
import aiohttp
import json

class OpenRouterClient:
    """
    Client for interacting with the OpenRouter API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenRouter client.
        
        Args:
            api_key: API key for OpenRouter API (optional, will use environment variable if not provided)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.api_base_url = "https://openrouter.ai/api/v1"
        self.default_model = "anthropic/claude-3-opus"
        
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a response from the OpenRouter API.
        
        Args:
            prompt: The prompt to send to the API
            **kwargs: Additional parameters for the API
            
        Returns:
            Dict containing the response
        """
        if not self.api_key:
            return {
                "text": "OpenRouter API key not configured.",
                "model": "openrouter",
                "success": False,
                "error": "api_key_missing"
            }
        
        # Get model from kwargs or use default
        model = kwargs.get("model", self.default_model)
        
        try:
            # Prepare the request payload
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000)
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://all-ai.streamlit.app",  # Replace with your actual app URL
                "X-Title": "ALL.AI"  # Your app name
            }
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Extract the generated text
                        generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                        model_used = result.get("model", model)
                        
                        return {
                            "text": generated_text,
                            "model": f"openrouter/{model_used.split('/')[-1]}",
                            "success": True,
                            "usage": result.get("usage", {})
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "text": f"Error from OpenRouter API: {error_text}",
                            "model": "openrouter",
                            "success": False,
                            "error": "api_error",
                            "status_code": response.status
                        }
        except asyncio.TimeoutError:
            return {
                "text": "Request to OpenRouter API timed out.",
                "model": "openrouter",
                "success": False,
                "error": "timeout"
            }
        except Exception as e:
            return {
                "text": f"Error calling OpenRouter API: {str(e)}",
                "model": "openrouter",
                "success": False,
                "error": "request_error"
            }
    
    async def list_models(self) -> Dict[str, Any]:
        """
        List available models from the OpenRouter API.
        
        Returns:
            Dict containing the list of models
        """
        if not self.api_key:
            return {
                "models": [],
                "success": False,
                "error": "api_key_missing"
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/models",
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        return {
                            "models": result.get("data", []),
                            "success": True
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "models": [],
                            "success": False,
                            "error": "api_error",
                            "status_code": response.status,
                            "error_text": error_text
                        }
        except Exception as e:
            return {
                "models": [],
                "success": False,
                "error": "request_error",
                "error_text": str(e)
            }
