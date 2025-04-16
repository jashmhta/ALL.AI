import os
import asyncio
from typing import Dict, Any, Optional, List
import aiohttp
import json

class HuggingFaceClient:
    """
    Client for interacting with the HuggingFace Inference API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the HuggingFace client.
        
        Args:
            api_key: API key for HuggingFace API (optional, will use environment variable if not provided)
        """
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        self.api_base_url = "https://api-inference.huggingface.co/models"
        self.default_model = "mistralai/Mistral-7B-Instruct-v0.2"
        
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a response from the HuggingFace API.
        
        Args:
            prompt: The prompt to send to the API
            **kwargs: Additional parameters for the API
            
        Returns:
            Dict containing the response
        """
        if not self.api_key:
            return {
                "text": "HuggingFace API key not configured.",
                "model": "huggingface",
                "success": False,
                "error": "api_key_missing"
            }
        
        # Get model from kwargs or use default
        model = kwargs.get("model", self.default_model)
        
        try:
            # Prepare the request payload
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": kwargs.get("max_tokens", 1000),
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "do_sample": True
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/{model}",
                    headers=headers,
                    json=payload,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Extract the generated text
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get("generated_text", "")
                        else:
                            generated_text = str(result)
                        
                        return {
                            "text": generated_text,
                            "model": f"huggingface/{model.split('/')[-1]}",
                            "success": True
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "text": f"Error from HuggingFace API: {error_text}",
                            "model": "huggingface",
                            "success": False,
                            "error": "api_error",
                            "status_code": response.status
                        }
        except asyncio.TimeoutError:
            return {
                "text": "Request to HuggingFace API timed out.",
                "model": "huggingface",
                "success": False,
                "error": "timeout"
            }
        except Exception as e:
            return {
                "text": f"Error calling HuggingFace API: {str(e)}",
                "model": "huggingface",
                "success": False,
                "error": "request_error"
            }
    
    async def get_embedding(self, text: str, model: str = "sentence-transformers/all-MiniLM-L6-v2") -> Dict[str, Any]:
        """
        Get an embedding from the HuggingFace API.
        
        Args:
            text: The text to embed
            model: The model to use for embedding
            
        Returns:
            Dict containing the embedding
        """
        if not self.api_key:
            return {
                "embedding": None,
                "model": "huggingface",
                "success": False,
                "error": "api_key_missing"
            }
        
        try:
            # Prepare the request payload
            payload = {
                "inputs": text
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/{model}",
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        return {
                            "embedding": result,
                            "model": f"huggingface/{model.split('/')[-1]}",
                            "success": True
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "embedding": None,
                            "model": "huggingface",
                            "success": False,
                            "error": "api_error",
                            "status_code": response.status,
                            "error_text": error_text
                        }
        except Exception as e:
            return {
                "embedding": None,
                "model": "huggingface",
                "success": False,
                "error": "request_error",
                "error_text": str(e)
            }
