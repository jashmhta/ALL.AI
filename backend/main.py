import os
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

# Import client modules
from backend.clients.gemini_client import GeminiClient
from backend.clients.openai_client import OpenAIClient
from backend.clients.huggingface_client import HuggingFaceClient
from backend.clients.openrouter_client import OpenRouterClient
from backend.clients.claude_client import ClaudeClient
from backend.clients.llama_client import LlamaClient
from backend.router import MultiAIRouter

class MultiAIApp:
    def __init__(self):
        """Initialize the Multi-AI Application."""
        # Load environment variables
        load_dotenv()
        
        # Initialize clients
        self.clients = {}
        
        # Add available clients based on environment variables
        if os.getenv("GEMINI_API_KEY"):
            try:
                self.clients["gemini"] = GeminiClient()
            except Exception as e:
                print(f"Failed to initialize Gemini client: {e}")
        
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.clients["openai"] = OpenAIClient()
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
        
        if os.getenv("HUGGINGFACE_API_KEY"):
            try:
                self.clients["huggingface"] = HuggingFaceClient()
            except Exception as e:
                print(f"Failed to initialize Hugging Face client: {e}")
        
        if os.getenv("OPENROUTER_API_KEY"):
            try:
                self.clients["openrouter"] = OpenRouterClient()
            except Exception as e:
                print(f"Failed to initialize OpenRouter client: {e}")
        
        if os.getenv("CLAUDE_API_KEY"):
            try:
                self.clients["claude"] = ClaudeClient()
            except Exception as e:
                print(f"Failed to initialize Claude client: {e}")
        
        if os.getenv("LLAMA_API_KEY"):
            try:
                self.clients["llama"] = LlamaClient()
            except Exception as e:
                print(f"Failed to initialize Llama client: {e}")
        
        # Initialize router
        self.router = MultiAIRouter(self.clients)
    
    async def process_prompt(self, prompt: str, model: str = None, 
                            use_multiple: bool = False, **kwargs) -> Dict[str, Any]:
        """Process a user prompt and return AI response(s)."""
        if use_multiple:
            responses = await self.router.get_multiple_responses(prompt, **kwargs)
            return {
                "responses": responses,
                "success": any(r["success"] for r in responses)
            }
        else:
            return await self.router.get_response(prompt, model, **kwargs)
    
    def get_available_models(self) -> list:
        """Get list of available AI models."""
        return self.router.available_models

# Example usage
async def main():
    app = MultiAIApp()
    available_models = app.get_available_models()
    print(f"Available models: {available_models}")
    
    if available_models:
        response = await app.process_prompt("Explain quantum computing in simple terms.")
        print(f"Response from {response['model']}: {response['text']}")
    else:
        print("No AI models available. Please check your API keys.")

if __name__ == "__main__":
    asyncio.run(main())
