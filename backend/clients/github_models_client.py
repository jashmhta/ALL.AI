import os
import json
import requests
from typing import Dict, Any, Optional, List

class GitHubModelsClient:
    """
    Client for interacting with GitHub Marketplace Models.
    Supports models like GPT-4.1-mini, DeepSeek-V3-0324, and Llama 4 Scout.
    """
    
    def __init__(self, pat_token: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the GitHub Models client.
        
        Args:
            pat_token: GitHub Personal Access Token
            model: Default model to use for this client instance
        """
        self.pat_token = pat_token or os.environ.get("GITHUB_PAT_TOKEN", "")
        self.base_url = "https://api.github.com/models"
        self.available_models = {
            "gpt-4.1-mini": {
                "provider": "azure-openai",
                "model_id": "gpt-4-1-mini",
                "max_tokens": 4096,
                "supports_vision": False
            },
            "deepseek-v3-0324": {
                "provider": "deepseek",
                "model_id": "deepseek-v3-0324",
                "max_tokens": 4096,
                "supports_vision": False
            },
            "llama-4-scout-17b-16e": {
                "provider": "meta",
                "model_id": "llama-4-scout-17b-16e-instruct",
                "max_tokens": 4096,
                "supports_vision": False
            }
        }
        # Set the default model, either from parameter or fallback to gpt-4.1-mini
        self.default_model = model if model and model in self.available_models else "gpt-4.1-mini"
    
    def query(self, 
             prompt: str, 
             model: Optional[str] = None, 
             max_tokens: int = 1000, 
             temperature: float = 0.7,
             system_message: Optional[str] = None) -> str:
        """
        Query the GitHub Models API.
        
        Args:
            prompt: User prompt
            model: Model to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            system_message: Optional system message
            
        Returns:
            Generated text response
        """
        # Validate and set model
        model = model or self.default_model
        if model not in self.available_models:
            model = self.default_model
        
        # Get model details
        model_details = self.available_models[model]
        provider = model_details["provider"]
        model_id = model_details["model_id"]
        
        # Check if PAT token is available
        if not self.pat_token:
            return "GitHub PAT token not provided. Please add your token in the settings."
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.pat_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        # Prepare messages
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        # Add user message
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Prepare request data
        data = {
            "provider": provider,
            "model": model_id,
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
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"]
                
                return "No valid response from GitHub Models API."
            else:
                error_msg = f"GitHub Models API Error: {response.status_code} - {response.text}"
                print(error_msg)
                return f"Error: {error_msg}"
        
        except Exception as e:
            error_msg = f"Error querying GitHub Models API: {str(e)}"
            print(error_msg)
            return f"Error: {error_msg}"
    
    async def query_async(self, 
                         prompt: str, 
                         model: Optional[str] = None, 
                         max_tokens: int = 1000, 
                         temperature: float = 0.7,
                         system_message: Optional[str] = None) -> str:
        """
        Asynchronous version of query method.
        
        Args:
            prompt: User prompt
            model: Model to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            system_message: Optional system message
            
        Returns:
            Generated text response
        """
        import aiohttp
        
        # Validate and set model
        model = model or self.default_model
        if model not in self.available_models:
            model = self.default_model
        
        # Get model details
        model_details = self.available_models[model]
        provider = model_details["provider"]
        model_id = model_details["model_id"]
        
        # Check if PAT token is available
        if not self.pat_token:
            return "GitHub PAT token not provided. Please add your token in the settings."
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.pat_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        # Prepare messages
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        # Add user message
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Prepare request data
        data = {
            "provider": provider,
            "model": model_id,
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
                        if "choices" in result and len(result["choices"]) > 0:
                            choice = result["choices"][0]
                            if "message" in choice and "content" in choice["message"]:
                                return choice["message"]["content"]
                        
                        return "No valid response from GitHub Models API."
                    else:
                        response_text = await response.text()
                        error_msg = f"GitHub Models API Error: {response.status} - {response_text}"
                        print(error_msg)
                        return f"Error: {error_msg}"
        
        except Exception as e:
            error_msg = f"Error querying GitHub Models API: {str(e)}"
            print(error_msg)
            return f"Error: {error_msg}"
    
    def generate_response(self, 
                         prompt: str, 
                         max_tokens: int = 1000, 
                         temperature: float = 0.7,
                         conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Generate a response based on prompt and conversation history.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            conversation_history: Optional conversation history
            
        Returns:
            Generated text response
        """
        # Format conversation history into a system message
        system_message = ""
        if conversation_history:
            for message in conversation_history:
                role = message.get("role", "")
                content = message.get("content", "")
                if role == "user":
                    system_message += f"User: {content}\n"
                elif role == "assistant":
                    system_message += f"Assistant: {content}\n"
        
        # Query the model
        return self.query(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            system_message=system_message if system_message else None
        )
    
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
        Check if the PAT token is valid.
        
        Returns:
            True if valid, False otherwise
        """
        if not self.pat_token:
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.pat_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(
                "https://api.github.com/user",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception:
            return False
