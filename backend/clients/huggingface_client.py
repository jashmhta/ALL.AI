import os
import json
import requests
from typing import Dict, Any, Optional, List

class HuggingFaceClient:
    """
    Client for interacting with HuggingFace Inference API.
    Supports various models hosted on HuggingFace.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the HuggingFace client.
        
        Args:
            api_key: HuggingFace API key
        """
        self.api_key = api_key or os.environ.get("HUGGINGFACE_API_KEY", "")
        self.base_url = "https://api-inference.huggingface.co/models"
        self.available_models = {
            "mistral-7b": {
                "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
                "max_tokens": 8192,
                "supports_vision": False
            },
            "falcon-40b": {
                "model_id": "tiiuae/falcon-40b-instruct",
                "max_tokens": 2048,
                "supports_vision": False
            },
            "llama-2-13b": {
                "model_id": "meta-llama/Llama-2-13b-chat-hf",
                "max_tokens": 4096,
                "supports_vision": False
            }
        }
        self.default_model = "mistral-7b"
    
    def query(self, 
             prompt: str, 
             model: Optional[str] = None, 
             max_tokens: int = 1000, 
             temperature: float = 0.7,
             system_message: Optional[str] = None,
             image_urls: Optional[List[str]] = None) -> str:
        """
        Query the HuggingFace Inference API.
        
        Args:
            prompt: User prompt
            model: Model to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            system_message: Optional system message
            image_urls: Optional list of image URLs (not supported for most models)
            
        Returns:
            Generated text response
        """
        # Validate and set model
        model = model or self.default_model
        if model not in self.available_models:
            model = self.default_model
        
        model_id = self.available_models[model]["model_id"]
        
        # Check if API key is available
        if not self.api_key:
            return "HuggingFace API key not provided. Please add your API key in the settings."
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare full prompt with system message if provided
        full_prompt = prompt
        if system_message:
            full_prompt = f"{system_message}\n\n{prompt}"
        
        # Prepare request data based on model type
        if "mistral" in model_id.lower():
            # Mistral format
            data = {
                "inputs": f"<s>[INST] {full_prompt} [/INST]",
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
        elif "llama" in model_id.lower():
            # Llama format
            data = {
                "inputs": f"<s>[INST] {full_prompt} [/INST]",
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
        elif "falcon" in model_id.lower():
            # Falcon format
            data = {
                "inputs": f"User: {full_prompt}\nAssistant:",
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
        else:
            # Generic format
            data = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
        
        try:
            # Make API request
            response = requests.post(
                f"{self.base_url}/{model_id}",
                headers=headers,
                json=data,
                timeout=60
            )
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    if "generated_text" in result[0]:
                        return result[0]["generated_text"]
                    else:
                        return str(result[0])
                elif isinstance(result, dict):
                    if "generated_text" in result:
                        return result["generated_text"]
                    else:
                        return str(result)
                else:
                    return str(result)
            else:
                error_msg = f"HuggingFace API Error: {response.status_code} - {response.text}"
                print(error_msg)
                return f"Error: {error_msg}"
        
        except Exception as e:
            error_msg = f"Error querying HuggingFace API: {str(e)}"
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
            image_urls: Optional list of image URLs (not supported for most models)
            
        Returns:
            Generated text response
        """
        import aiohttp
        
        # Validate and set model
        model = model or self.default_model
        if model not in self.available_models:
            model = self.default_model
        
        model_id = self.available_models[model]["model_id"]
        
        # Check if API key is available
        if not self.api_key:
            return "HuggingFace API key not provided. Please add your API key in the settings."
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare full prompt with system message if provided
        full_prompt = prompt
        if system_message:
            full_prompt = f"{system_message}\n\n{prompt}"
        
        # Prepare request data based on model type
        if "mistral" in model_id.lower():
            # Mistral format
            data = {
                "inputs": f"<s>[INST] {full_prompt} [/INST]",
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
        elif "llama" in model_id.lower():
            # Llama format
            data = {
                "inputs": f"<s>[INST] {full_prompt} [/INST]",
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
        elif "falcon" in model_id.lower():
            # Falcon format
            data = {
                "inputs": f"User: {full_prompt}\nAssistant:",
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
        else:
            # Generic format
            data = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
        
        try:
            # Make API request asynchronously
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{model_id}",
                    headers=headers,
                    json=data,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Handle different response formats
                        if isinstance(result, list) and len(result) > 0:
                            if "generated_text" in result[0]:
                                return result[0]["generated_text"]
                            else:
                                return str(result[0])
                        elif isinstance(result, dict):
                            if "generated_text" in result:
                                return result["generated_text"]
                            else:
                                return str(result)
                        else:
                            return str(result)
                    else:
                        response_text = await response.text()
                        error_msg = f"HuggingFace API Error: {response.status} - {response_text}"
                        print(error_msg)
                        return f"Error: {error_msg}"
        
        except Exception as e:
            error_msg = f"Error querying HuggingFace API: {str(e)}"
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
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.get(
                "https://huggingface.co/api/whoami",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception:
            return False
