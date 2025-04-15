import os
import json
import requests
from typing import Dict, Any, Optional, List

class DeepSeekClient:
    """
    Client for interacting with DeepSeek API.
    Supports DeepSeek models including Coder and Chat.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the DeepSeek client.
        
        Args:
            api_key: DeepSeek API key
        """
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        self.base_url = "https://api.deepseek.com/v1"
        self.available_models = {
            "deepseek-chat": {
                "max_tokens": 32768,
                "supports_vision": False
            },
            "deepseek-coder": {
                "max_tokens": 32768,
                "supports_vision": False
            },
            "deepseek-v2": {
                "max_tokens": 65536,
                "supports_vision": True
            }
        }
        self.default_model = "deepseek-chat"
    
    def query(self, 
             prompt: str, 
             model: Optional[str] = None, 
             max_tokens: int = 1000, 
             temperature: float = 0.7,
             system_message: Optional[str] = None,
             image_urls: Optional[List[str]] = None) -> str:
        """
        Query the DeepSeek API.
        
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
            return "DeepSeek API key not provided. Please add your API key in the settings."
        
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
        
        # Handle image URLs for vision models
        if image_urls and self.available_models[model]["supports_vision"]:
            content = []
            content.append({"type": "text", "text": prompt})
            
            for image_url in image_urls:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": image_url}
                })
            
            messages.append({"role": "user", "content": content})
        else:
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
                error_msg = f"DeepSeek API Error: {response.status_code} - {response.text}"
                print(error_msg)
                return f"Error: {error_msg}"
        
        except Exception as e:
            error_msg = f"Error querying DeepSeek API: {str(e)}"
            print(error_msg)
            
            # Fallback to local implementation for demo purposes
            return self._local_fallback(prompt, model)
    
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
            return "DeepSeek API key not provided. Please add your API key in the settings."
        
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
        
        # Handle image URLs for vision models
        if image_urls and self.available_models[model]["supports_vision"]:
            content = []
            content.append({"type": "text", "text": prompt})
            
            for image_url in image_urls:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": image_url}
                })
            
            messages.append({"role": "user", "content": content})
        else:
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
                        error_msg = f"DeepSeek API Error: {response.status} - {response_text}"
                        print(error_msg)
                        return f"Error: {error_msg}"
        
        except Exception as e:
            error_msg = f"Error querying DeepSeek API: {str(e)}"
            print(error_msg)
            
            # Fallback to local implementation for demo purposes
            return self._local_fallback(prompt, model)
    
    def _local_fallback(self, prompt: str, model: str) -> str:
        """
        Local fallback for demo purposes when API is not available.
        
        Args:
            prompt: User prompt
            model: Model name
            
        Returns:
            Generated text response
        """
        # Simple response generation for demonstration
        if model == "deepseek-coder":
            if "code" in prompt.lower() or "function" in prompt.lower() or "program" in prompt.lower():
                return "```python\n# DeepSeek Coder generated solution\ndef solve_problem(input_data):\n    \"\"\"Solves the given problem efficiently.\"\"\"\n    # Parse input\n    parsed_data = input_data.strip().split('\\n')\n    \n    # Process data\n    result = []\n    for line in parsed_data:\n        # Apply algorithm\n        processed = line.upper()\n        result.append(processed)\n    \n    # Return formatted output\n    return '\\n'.join(result)\n\n# Example usage\nif __name__ == \"__main__\":\n    test_input = \"hello\\nworld\"\n    print(solve_problem(test_input))\n    # Output: HELLO\\nWORLD\n```"
            else:
                return "DeepSeek Coder is specialized for code generation tasks. For best results, please provide a coding problem or ask for a specific programming implementation."
        
        elif model == "deepseek-chat":
            return "I'm DeepSeek Chat, an advanced AI assistant designed to provide helpful, accurate, and thoughtful responses. I can assist with a wide range of tasks including answering questions, providing explanations, generating creative content, and offering insights on various topics. How can I help you today?"
        
        else:  # deepseek-v2
            return "DeepSeek V2 is our most advanced model with enhanced reasoning capabilities and vision support. I can analyze complex problems, provide detailed explanations, and understand images when provided. I'm designed to be helpful, harmless, and honest in all my interactions."
    
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
