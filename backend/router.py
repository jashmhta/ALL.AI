from typing import Dict, Any, List, Optional
import asyncio
import random

class MultiAIRouter:
    def __init__(self, clients: Dict[str, Any]):
        """Initialize the Multi-AI Router with client instances."""
        self.clients = clients
        self.available_models = list(clients.keys())
    
    async def get_response(self, prompt: str, model: Optional[str] = None, 
                          fallback: bool = True, **kwargs) -> Dict[str, Any]:
        """Get response from specified model with fallback option."""
        if model and model in self.available_models:
            # Use the specified model
            client = self.clients[model]
            response = await client.generate_response(prompt, **kwargs)
            
            # If fallback is enabled and the primary model failed, try others
            if not response["success"] and fallback:
                return await self._try_fallback_models(prompt, exclude=[model], **kwargs)
            
            return response
        elif not model:
            # If no model specified, use a random one with fallback
            return await self._try_fallback_models(prompt, **kwargs)
        else:
            return {
                "text": f"Model '{model}' not available. Available models: {', '.join(self.available_models)}",
                "model": "system",
                "success": False
            }
    
    async def _try_fallback_models(self, prompt: str, exclude: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Try multiple models until one succeeds."""
        exclude = exclude or []
        available = [m for m in self.available_models if m not in exclude]
        
        if not available:
            return {
                "text": "No available AI models to process your request.",
                "model": "system",
                "success": False
            }
        
        # Shuffle to randomize the order
        random.shuffle(available)
        
        for model_name in available:
            client = self.clients[model_name]
            response = await client.generate_response(prompt, **kwargs)
            if response["success"]:
                return response
        
        # If all models failed
        return {
            "text": "All available AI models failed to process your request.",
            "model": "system",
            "success": False
        }
    
    async def get_multiple_responses(self, prompt: str, models: List[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """Get responses from multiple models in parallel."""
        models = models or self.available_models
        valid_models = [m for m in models if m in self.available_models]
        
        if not valid_models:
            return [{
                "text": f"No valid models specified. Available models: {', '.join(self.available_models)}",
                "model": "system",
                "success": False
            }]
        
        tasks = [self.clients[model].generate_response(prompt, **kwargs) for model in valid_models]
        responses = await asyncio.gather(*tasks)
        
        return responses
