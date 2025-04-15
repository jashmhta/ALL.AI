import os
import asyncio
from typing import Dict, Any, Optional, List
import aiohttp
import json

class LlamaClient:
    """
    Client for interacting with the Llama API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Llama client.
        
        Args:
            api_key: API key for Llama API (optional, will use environment variable if not provided)
        """
        self.api_key = api_key or os.getenv("LLAMA_API_KEY")
        self.api_base_url = "https://api.llama-api.com"
        
    async def get_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Get a response from the Llama API.
        
        Args:
            prompt: The prompt to send to the API
            temperature: Temperature parameter for generation
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Dict containing the response
        """
        if not self.api_key:
            return {
                "text": "Llama API key not configured.",
                "model": "llama",
                "success": False,
                "error": "api_key_missing"
            }
        
        try:
            # Prepare the request payload
            payload = {
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "model": "llama-3-70b-instruct"  # Using the latest model
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/v1/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Extract the generated text
                        generated_text = result.get("choices", [{}])[0].get("text", "")
                        
                        # Extract usage information
                        usage = result.get("usage", {})
                        
                        return {
                            "text": generated_text,
                            "model": "llama-3-70b-instruct",
                            "success": True,
                            "usage": usage
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "text": f"Error from Llama API: {error_text}",
                            "model": "llama",
                            "success": False,
                            "error": "api_error",
                            "status_code": response.status
                        }
        except asyncio.TimeoutError:
            return {
                "text": "Request to Llama API timed out.",
                "model": "llama",
                "success": False,
                "error": "timeout"
            }
        except Exception as e:
            return {
                "text": f"Error calling Llama API: {str(e)}",
                "model": "llama",
                "success": False,
                "error": "request_error"
            }
    
    async def get_embedding(self, text: str) -> Dict[str, Any]:
        """
        Get an embedding from the Llama API.
        
        Args:
            text: The text to embed
            
        Returns:
            Dict containing the embedding
        """
        if not self.api_key:
            return {
                "embedding": None,
                "model": "llama",
                "success": False,
                "error": "api_key_missing"
            }
        
        try:
            # Prepare the request payload
            payload = {
                "input": text,
                "model": "llama-3-embedding"
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/v1/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Extract the embedding
                        embedding = result.get("data", [{}])[0].get("embedding", [])
                        
                        return {
                            "embedding": embedding,
                            "model": "llama-3-embedding",
                            "success": True
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "embedding": None,
                            "model": "llama",
                            "success": False,
                            "error": "api_error",
                            "status_code": response.status,
                            "error_text": error_text
                        }
        except Exception as e:
            return {
                "embedding": None,
                "model": "llama",
                "success": False,
                "error": "request_error",
                "error_text": str(e)
            }
    
    async def get_chat_response(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Get a chat response from the Llama API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Temperature parameter for generation
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Dict containing the response
        """
        if not self.api_key:
            return {
                "text": "Llama API key not configured.",
                "model": "llama",
                "success": False,
                "error": "api_key_missing"
            }
        
        try:
            # Prepare the request payload
            payload = {
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "model": "llama-3-70b-chat"
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Extract the generated text
                        generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                        
                        # Extract usage information
                        usage = result.get("usage", {})
                        
                        return {
                            "text": generated_text,
                            "model": "llama-3-70b-chat",
                            "success": True,
                            "usage": usage
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "text": f"Error from Llama API: {error_text}",
                            "model": "llama",
                            "success": False,
                            "error": "api_error",
                            "status_code": response.status
                        }
        except asyncio.TimeoutError:
            return {
                "text": "Request to Llama API timed out.",
                "model": "llama",
                "success": False,
                "error": "timeout"
            }
        except Exception as e:
            return {
                "text": f"Error calling Llama API: {str(e)}",
                "model": "llama",
                "success": False,
                "error": "request_error"
            }
