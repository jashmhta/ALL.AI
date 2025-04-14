import os
import requests
from typing import Dict, Any, Optional, List

class SynthesisClient:
    def __init__(self, llama_client=None):
        """Initialize the Synthesis client using Llama for combining outputs."""
        self.llama_client = llama_client
    
    async def synthesize_responses(self, prompt: str, responses: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Synthesize the best response from multiple AI outputs using Llama.
        
        Args:
            prompt: The original user prompt
            responses: List of responses from different AI models
            
        Returns:
            A synthesized response with the best elements from all models
        """
        if not responses or len(responses) == 0:
            return {
                "text": "No responses available to synthesize.",
                "model": "synthesis",
                "success": False
            }
        
        # If only one response, return it directly
        if len(responses) == 1:
            return responses[0]
        
        # Filter out unsuccessful responses
        successful_responses = [r for r in responses if r.get("success", False)]
        if not successful_responses:
            return {
                "text": "No successful responses available to synthesize.",
                "model": "synthesis",
                "success": False
            }
        
        # Create a prompt for Llama to synthesize the responses
        synthesis_prompt = f"""
You are an expert AI response synthesizer. Your task is to create the best possible response by combining insights from multiple AI models.

Original user question: {prompt}

Responses from different AI models:
"""
        
        for i, response in enumerate(successful_responses):
            model_name = response.get("model", f"Model {i+1}")
            response_text = response.get("text", "No response")
            synthesis_prompt += f"\n--- {model_name} ---\n{response_text}\n"
        
        synthesis_prompt += """
Based on the above responses, create a single comprehensive response that:
1. Combines the best insights from all models
2. Resolves any contradictions between models
3. Provides the most accurate and helpful information
4. Is well-structured and easy to understand
5. Directly addresses the user's original question

Your synthesized response:
"""
        
        # Use Llama to synthesize the responses
        if self.llama_client:
            try:
                llama_response = await self.llama_client.generate_response(synthesis_prompt, **kwargs)
                if llama_response.get("success", False):
                    return {
                        "text": llama_response["text"],
                        "model": "synthesis (via Llama)",
                        "success": True
                    }
            except Exception as e:
                pass  # Fall back to manual synthesis if Llama fails
        
        # Fallback: Simple concatenation if Llama is not available or fails
        combined_text = "Synthesized response (combined from multiple models):\n\n"
        for i, response in enumerate(successful_responses):
            model_name = response.get("model", f"Model {i+1}")
            response_text = response.get("text", "No response")
            combined_text += f"--- From {model_name} ---\n{response_text}\n\n"
        
        return {
            "text": combined_text,
            "model": "synthesis (manual combination)",
            "success": True
        }
