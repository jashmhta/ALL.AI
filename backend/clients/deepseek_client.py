import os
import aiohttp
import json
import asyncio
from typing import Dict, Any, List, Optional

class DeepSeekClient:
    """
    Client for the DeepSeek API.
    Provides methods for generating text responses using DeepSeek models.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the DeepSeek client.
        
        Args:
            api_key: DeepSeek API key
        """
        self.api_key = api_key
        self.api_base = "https://api.deepseek.com/v1"
        self.models = {
            "deepseek-chat": "deepseek-chat",
            "deepseek-coder": "deepseek-coder",
            "deepseek-llm-67b": "deepseek-llm-67b-chat"
        }
    
    async def generate_response(self, prompt: str, context: str = "", 
                              model: str = "deepseek-chat", 
                              params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response using the DeepSeek API.
        
        Args:
            prompt: The prompt to send to the model
            context: Optional conversation context
            model: The model to use
            params: Additional parameters for the API call
            
        Returns:
            Dict containing the response and metadata
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "DeepSeek API key not provided",
                "content": "I'm sorry, but the DeepSeek API key is not configured. Please add your API key in the settings."
            }
        
        try:
            # Get the model ID
            model_id = self.models.get(model, "deepseek-chat")
            
            # Set default parameters
            if params is None:
                params = {}
            
            temperature = params.get("temperature", 0.7)
            max_tokens = params.get("max_tokens", 1000)
            
            # Prepare the messages
            messages = []
            
            # Add context as a system message if provided
            if context:
                messages.append({
                    "role": "system",
                    "content": context
                })
            
            # Add the user prompt
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Prepare the request payload
            payload = {
                "model": model_id,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Add optional parameters if provided
            if "top_p" in params:
                payload["top_p"] = params["top_p"]
            
            if "presence_penalty" in params:
                payload["presence_penalty"] = params["presence_penalty"]
            
            if "frequency_penalty" in params:
                payload["frequency_penalty"] = params["frequency_penalty"]
            
            # Make the API request
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                async with session.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Extract the response content
                        content = result["choices"][0]["message"]["content"]
                        
                        # Extract token usage
                        tokens = {
                            "prompt_tokens": result["usage"]["prompt_tokens"],
                            "completion_tokens": result["usage"]["completion_tokens"],
                            "total_tokens": result["usage"]["total_tokens"]
                        }
                        
                        return {
                            "success": True,
                            "content": content,
                            "model": model_id,
                            "tokens": tokens
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"API Error: {response.status} - {error_text}",
                            "content": f"I'm sorry, but there was an error with the DeepSeek API: {response.status} - {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception: {str(e)}",
                "content": f"I'm sorry, but an error occurred while generating a response: {str(e)}"
            }
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available models from the DeepSeek API.
        
        Returns:
            List of model information dictionaries
        """
        if not self.api_key:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                async with session.get(
                    f"{self.api_base}/models",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data", [])
                    else:
                        print(f"Error getting models: {response.status}")
                        return []
        except Exception as e:
            print(f"Exception getting models: {str(e)}")
            return []
