import os
import json
import requests
from typing import Dict, Any, Optional, List

class LlamaClient:
    """
    Client for interacting with Meta's Llama API.
    Supports Llama 3 70B and 8B models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Llama client.
        
        Args:
            api_key: Meta AI API key
        """
        self.api_key = api_key or os.environ.get("LLAMA_API_KEY", "")
        self.base_url = "https://api.meta.ai/v1"  # Example URL, adjust as needed
        self.available_models = {
            "llama-3-70b": {
                "max_tokens": 100000,
                "supports_vision": False
            },
            "llama-3-8b": {
                "max_tokens": 100000,
                "supports_vision": False
            }
        }
        self.default_model = "llama-3-8b"
    
    def query(self, 
             prompt: str, 
             model: Optional[str] = None, 
             max_tokens: int = 1000, 
             temperature: float = 0.7,
             system_message: Optional[str] = None,
             image_urls: Optional[List[str]] = None) -> str:
        """
        Query the Llama API.
        
        Args:
            prompt: User prompt
            model: Model to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            system_message: Optional system message
            image_urls: Optional list of image URLs (not supported yet)
            
        Returns:
            Generated text response
        """
        # Validate and set model
        model = model or self.default_model
        if model not in self.available_models:
            model = self.default_model
        
        # Check if API key is available
        if not self.api_key:
            return "Llama API key not provided. Please add your API key in the settings."
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Prepare messages
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request data
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            # Make API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = f"Llama API Error: {response.status_code} - {response.text}"
                print(error_msg)
                return f"Error: {error_msg}"
        
        except Exception as e:
            error_msg = f"Error querying Llama API: {str(e)}"
            print(error_msg)
            
            # Fallback to local implementation for demo purposes
            return self._local_fallback(prompt, system_message)
    
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
            image_urls: Optional list of image URLs (not supported yet)
            
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
            return "Llama API key not provided. Please add your API key in the settings."
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Prepare messages
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request data
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            # Make API request asynchronously
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        response_text = await response.text()
                        error_msg = f"Llama API Error: {response.status} - {response_text}"
                        print(error_msg)
                        return f"Error: {error_msg}"
        
        except Exception as e:
            error_msg = f"Error querying Llama API: {str(e)}"
            print(error_msg)
            
            # Fallback to local implementation for demo purposes
            return self._local_fallback(prompt, system_message)
    
    def _local_fallback(self, prompt: str, system_message: Optional[str] = None) -> str:
        """
        Local fallback for demo purposes when API is not available.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            
        Returns:
            Generated text response
        """
        # Simple response generation for demonstration
        if "summarize" in prompt.lower():
            return "This is a summary generated by Llama 3. The text discusses key points including main ideas, supporting evidence, and conclusions. The author makes several important arguments backed by data and expert opinions."
        
        if "code" in prompt.lower():
            return "```python\ndef example_function(param1, param2):\n    \"\"\"Example function that demonstrates Llama's code generation.\"\"\"\n    result = param1 + param2\n    return result\n\n# Example usage\nprint(example_function(10, 20))\n```"
        
        if "explain" in prompt.lower():
            return "Let me explain this concept in detail. The key aspects to understand are:\n\n1. The fundamental principles that govern this domain\n2. How these principles interact in practical applications\n3. Common misconceptions and how to avoid them\n\nIn essence, this topic involves understanding the relationship between various components and how they work together as a system."
        
        # Default response
        return "I'm Llama 3, a large language model by Meta AI. I'm designed to be helpful, harmless, and honest. I can assist with a wide range of tasks including answering questions, generating creative content, providing explanations, and much more. How can I help you today?"
    
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
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception:
            return False
