import os
import json
import requests
from typing import Dict, Any, Optional, List

class ClaudeClient:
    """
    Client for interacting with Anthropic's Claude API.
    Supports Claude 3 Opus, Sonnet, and Haiku models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude client.
        
        Args:
            api_key: Anthropic API key
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.base_url = "https://api.anthropic.com/v1"
        self.available_models = {
            "claude-3-opus": {
                "max_tokens": 200000,
                "supports_vision": True
            },
            "claude-3-sonnet": {
                "max_tokens": 200000,
                "supports_vision": True
            },
            "claude-3-haiku": {
                "max_tokens": 200000,
                "supports_vision": True
            }
        }
        self.default_model = "claude-3-sonnet"
    
    def query(self, 
             prompt: str, 
             model: Optional[str] = None, 
             max_tokens: int = 1000, 
             temperature: float = 0.7,
             system_message: Optional[str] = None,
             image_urls: Optional[List[str]] = None) -> str:
        """
        Query the Claude API.
        
        Args:
            prompt: User prompt
            model: Model to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            system_message: Optional system message
            image_urls: Optional list of image URLs for vision models
            
        Returns:
            Generated text response
        """
        # Validate and set model
        model = model or self.default_model
        if model not in self.available_models:
            model = self.default_model
        
        # Check if API key is available
        if not self.api_key:
            return "Claude API key not provided. Please add your API key in the settings."
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Prepare messages
        messages = []
        
        # Handle image URLs for vision models
        if image_urls and self.available_models[model]["supports_vision"]:
            content = []
            content.append({"type": "text", "text": prompt})
            
            for image_url in image_urls:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": image_url
                    }
                })
            
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
        
        # Prepare request data
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Add system message if provided
        if system_message:
            data["system"] = system_message
        
        try:
            # Make API request
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=data,
                timeout=60
            )
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            else:
                error_msg = f"Claude API Error: {response.status_code} - {response.text}"
                print(error_msg)
                return f"Error: {error_msg}"
        
        except Exception as e:
            error_msg = f"Error querying Claude API: {str(e)}"
            print(error_msg)
            return f"Error: {error_msg}"
    
    async def query_async(self, 
                         prompt: str, 
                         model: Optional[str] = None, 
                         max_tokens: int = 1000, 
                         temperature: float = 0.7,
                         system_message: Optional[str] = None,
                         image_urls: Optional[List[str]] = None) -> str:
        """
        Asynchronous version of query method.
        
        Args:
            prompt: User prompt
            model: Model to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            system_message: Optional system message
            image_urls: Optional list of image URLs for vision models
            
        Returns:
            Generated text response
        """
        import aiohttp
        
        # Validate and set model
        model = model or self.default_model
        if model not in self.available_models:
            model = self.default_model
        
        # Check if API key is available
        if not self.api_key:
            return "Claude API key not provided. Please add your API key in the settings."
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Prepare messages
        messages = []
        
        # Handle image URLs for vision models
        if image_urls and self.available_models[model]["supports_vision"]:
            content = []
            content.append({"type": "text", "text": prompt})
            
            for image_url in image_urls:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": image_url
                    }
                })
            
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
        
        # Prepare request data
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Add system message if provided
        if system_message:
            data["system"] = system_message
        
        try:
            # Make API request asynchronously
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=data,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["content"][0]["text"]
                    else:
                        response_text = await response.text()
                        error_msg = f"Claude API Error: {response.status} - {response_text}"
                        print(error_msg)
                        return f"Error: {error_msg}"
        
        except Exception as e:
            error_msg = f"Error querying Claude API: {str(e)}"
            print(error_msg)
            return f"Error: {error_msg}"
    
    def get_token_count(self, text: str) -> int:
        """
        Estimate the number of tokens in a text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Simple estimation (approximately 4 chars per token)
        return len(text) // 4
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models.
        
        Returns:
            List of model names
        """
        return list(self.available_models.keys())
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model: Model name
            
        Returns:
            Model information
        """
        return self.available_models.get(model, {})
    
    def check_api_key(self) -> bool:
        """
        Check if the API key is valid.
        
        Returns:
            True if valid, False otherwise
        """
        if not self.api_key:
            return False
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception:
            return False
