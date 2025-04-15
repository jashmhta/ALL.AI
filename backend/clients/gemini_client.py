import os
import json
import requests
from typing import Dict, Any, Optional, List

class GeminiClient:
    """
    Client for interacting with Google's Gemini API.
    Supports Gemini Pro and Gemini Pro Vision models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Google API key
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.base_url = "https://generativelanguage.googleapis.com/v1"
        self.available_models = {
            "gemini-pro": {
                "max_tokens": 32768,
                "supports_vision": False
            },
            "gemini-pro-vision": {
                "max_tokens": 32768,
                "supports_vision": True
            }
        }
        self.default_model = "gemini-pro"
    
    def query(self, 
             prompt: str, 
             model: Optional[str] = None, 
             max_tokens: int = 1000, 
             temperature: float = 0.7,
             system_message: Optional[str] = None,
             image_urls: Optional[List[str]] = None) -> str:
        """
        Query the Gemini API.
        
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
            return "Gemini API key not provided. Please add your API key in the settings."
        
        # Prepare content parts
        content_parts = []
        
        # Add system message if provided
        if system_message:
            content_parts.append({
                "text": f"System: {system_message}"
            })
        
        # Add prompt text
        content_parts.append({
            "text": prompt
        })
        
        # Add images if provided and model supports vision
        if image_urls and self.available_models[model]["supports_vision"]:
            for image_url in image_urls:
                try:
                    # Download image and convert to base64
                    image_response = requests.get(image_url, timeout=10)
                    if image_response.status_code == 200:
                        import base64
                        image_data = base64.b64encode(image_response.content).decode('utf-8')
                        
                        content_parts.append({
                            "inline_data": {
                                "mime_type": image_response.headers.get('Content-Type', 'image/jpeg'),
                                "data": image_data
                            }
                        })
                except Exception as e:
                    print(f"Error processing image {image_url}: {str(e)}")
        
        # Prepare request data
        data = {
            "contents": [{
                "parts": content_parts
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        try:
            # Make API request
            response = requests.post(
                f"{self.base_url}/models/{model}:generateContent?key={self.api_key}",
                json=data,
                timeout=60
            )
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if len(parts) > 0 and "text" in parts[0]:
                            return parts[0]["text"]
                
                return "No valid response from Gemini API."
            else:
                error_msg = f"Gemini API Error: {response.status_code} - {response.text}"
                print(error_msg)
                return f"Error: {error_msg}"
        
        except Exception as e:
            error_msg = f"Error querying Gemini API: {str(e)}"
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
        import base64
        
        # Validate and set model
        model = model or self.default_model
        if model not in self.available_models:
            model = self.default_model
        
        # Check if API key is available
        if not self.api_key:
            return "Gemini API key not provided. Please add your API key in the settings."
        
        # Prepare content parts
        content_parts = []
        
        # Add system message if provided
        if system_message:
            content_parts.append({
                "text": f"System: {system_message}"
            })
        
        # Add prompt text
        content_parts.append({
            "text": prompt
        })
        
        # Add images if provided and model supports vision
        if image_urls and self.available_models[model]["supports_vision"]:
            async with aiohttp.ClientSession() as session:
                for image_url in image_urls:
                    try:
                        # Download image and convert to base64
                        async with session.get(image_url, timeout=10) as image_response:
                            if image_response.status == 200:
                                image_data = base64.b64encode(await image_response.read()).decode('utf-8')
                                
                                content_parts.append({
                                    "inline_data": {
                                        "mime_type": image_response.headers.get('Content-Type', 'image/jpeg'),
                                        "data": image_data
                                    }
                                })
                    except Exception as e:
                        print(f"Error processing image {image_url}: {str(e)}")
        
        # Prepare request data
        data = {
            "contents": [{
                "parts": content_parts
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        try:
            # Make API request asynchronously
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/models/{model}:generateContent?key={self.api_key}",
                    json=data,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if "candidates" in result and len(result["candidates"]) > 0:
                            candidate = result["candidates"][0]
                            if "content" in candidate and "parts" in candidate["content"]:
                                parts = candidate["content"]["parts"]
                                if len(parts) > 0 and "text" in parts[0]:
                                    return parts[0]["text"]
                        
                        return "No valid response from Gemini API."
                    else:
                        response_text = await response.text()
                        error_msg = f"Gemini API Error: {response.status} - {response_text}"
                        print(error_msg)
                        return f"Error: {error_msg}"
        
        except Exception as e:
            error_msg = f"Error querying Gemini API: {str(e)}"
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
            response = requests.get(
                f"{self.base_url}/models?key={self.api_key}",
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception:
            return False
