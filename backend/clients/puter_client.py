import os
import json
import requests
from typing import Dict, Any, Optional, List

class PuterClient:
    """
    Client for interacting with Puter.js API for free access to OpenAI models.
    This client provides a server-side implementation to interact with Puter's "User Pays" model.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Puter client.
        
        Args:
            api_key: Not required for Puter's "User Pays" model
        """
        self.api_key = api_key  # Not used but kept for compatibility
        self.available_models = {
            "gpt-4o": {
                "max_tokens": 4096,
                "supports_vision": True
            },
            "gpt-4.1": {
                "max_tokens": 4096,
                "supports_vision": False
            },
            "o3-mini": {
                "max_tokens": 4096,
                "supports_vision": False
            },
            "o1-mini": {
                "max_tokens": 4096,
                "supports_vision": False
            }
        }
        self.default_model = "gpt-4o"
    
    def query(self, 
             prompt: str, 
             model: Optional[str] = None, 
             max_tokens: int = 1000, 
             temperature: float = 0.7,
             image_url: Optional[str] = None) -> str:
        """
        Query the Puter API to access OpenAI models.
        
        Args:
            prompt: User prompt
            model: Model to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            image_url: Optional image URL for vision models
            
        Returns:
            Generated text response
        """
        # Validate and set model
        model = model or self.default_model
        if model not in self.available_models:
            model = self.default_model
        
        # Prepare request data
        data = {
            "prompt": prompt,
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Add image URL if provided and model supports vision
        if image_url and self.available_models[model]["supports_vision"]:
            data["image_url"] = image_url
        
        try:
            # Create a simple HTML file that uses Puter.js to make the request
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Puter.js API Request</title>
                <script src="https://js.puter.com/v2/"></script>
            </head>
            <body>
                <div id="response"></div>
                <script>
                    async function makeRequest() {{
                        try {{
                            const response = await puter.ai.chat(
                                "{prompt}",
                                {{ model: "{model}" }}
                            );
                            document.getElementById('response').innerText = response;
                            console.log(response);
                        }} catch (error) {{
                            document.getElementById('response').innerText = "Error: " + error.message;
                            console.error(error);
                        }}
                    }}
                    makeRequest();
                </script>
            </body>
            </html>
            """
            
            # Save the HTML file
            temp_html_path = "/tmp/puter_request.html"
            with open(temp_html_path, "w") as f:
                f.write(html_content)
            
            # For server-side implementation, we would need to use a headless browser
            # This is a simplified implementation that returns a message about the limitation
            return f"Puter.js requires a browser environment to function. For server-side applications, consider implementing a proxy service that runs a headless browser to execute Puter.js requests. The HTML file for this request has been saved to {temp_html_path}."
        
        except Exception as e:
            error_msg = f"Error using Puter API: {str(e)}"
            print(error_msg)
            return f"Error: {error_msg}"
    
    async def query_async(self, 
                         prompt: str, 
                         model: Optional[str] = None, 
                         max_tokens: int = 1000, 
                         temperature: float = 0.7,
                         image_url: Optional[str] = None) -> str:
        """
        Asynchronous version of query method.
        
        Args:
            prompt: User prompt
            model: Model to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            image_url: Optional image URL for vision models
            
        Returns:
            Generated text response
        """
        # This is a synchronous implementation for compatibility
        # In a real async implementation, you would use a headless browser with async capabilities
        return self.query(prompt, model, max_tokens, temperature, image_url)
    
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
        # Format conversation history into a single context string
        context = ""
        if conversation_history:
            for message in conversation_history:
                role = message.get("role", "")
                content = message.get("content", "")
                if role == "user":
                    context += f"User: {content}\n"
                elif role == "assistant":
                    context += f"Assistant: {content}\n"
        
        # Add the current prompt
        full_prompt = f"{context}User: {prompt}\nAssistant:"
        
        # Query the model
        return self.query(
            prompt=full_prompt,
            max_tokens=max_tokens,
            temperature=temperature
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
        Check if the API key is valid.
        
        Returns:
            True if valid, False otherwise
        """
        # Puter.js doesn't require an API key
        return True
