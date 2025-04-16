import asyncio
from typing import Dict, Any, List, Optional
import json

class SynthesisClient:
    """
    Client for synthesizing responses from multiple AI models.
    Uses Llama or another capable model to combine and analyze responses.
    """
    
    def __init__(self, llama_client=None):
        """
        Initialize the synthesis client.
        
        Args:
            llama_client: Client for Llama API (or another capable model)
        """
        self.llama_client = llama_client
        
    async def synthesize_responses(self, prompt: str, responses: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Synthesize responses from multiple AI models.
        
        Args:
            prompt: The original user prompt
            responses: List of responses from different models
            **kwargs: Additional parameters for the synthesis
            
        Returns:
            Dict containing the synthesized response
        """
        if not self.llama_client:
            return {
                "text": "Synthesis is not available. Please configure a Llama API key.",
                "model": "synthesis",
                "success": False,
                "error": "synthesis_unavailable"
            }
        
        # Filter successful responses
        successful_responses = [r for r in responses if r.get("success", False)]
        
        if not successful_responses:
            return {
                "text": "No successful responses to synthesize.",
                "model": "synthesis",
                "success": False,
                "error": "no_successful_responses"
            }
        
        # Create a synthesis prompt
        synthesis_prompt = self._create_synthesis_prompt(prompt, successful_responses)
        
        # Get temperature from kwargs or use default
        temperature = kwargs.get("temperature", 0.7)
        
        try:
            # Use Llama to synthesize the responses
<<<<<<< HEAD
            synthesis_response = await self.llama_client.generate_response(
=======
            synthesis_response = await self.llama_client.get_response(
>>>>>>> main
                synthesis_prompt,
                temperature=temperature,
                max_tokens=kwargs.get("max_tokens", 1500)
            )
            
            if synthesis_response.get("success", False):
                # Extract the synthesized text
                synthesized_text = synthesis_response.get("text", "")
                
                # Clean up the synthesized text if needed
                synthesized_text = self._clean_synthesis_output(synthesized_text)
                
                return {
                    "text": synthesized_text,
                    "model": "synthesis (via Llama)",
                    "success": True,
                    "usage": synthesis_response.get("usage", {})
                }
            else:
                return {
                    "text": "Failed to synthesize responses.",
                    "model": "synthesis",
                    "success": False,
                    "error": "synthesis_failed"
                }
        except Exception as e:
            return {
                "text": f"Error during synthesis: {str(e)}",
                "model": "synthesis",
                "success": False,
                "error": "synthesis_error"
            }
    
    def _create_synthesis_prompt(self, original_prompt: str, responses: List[Dict[str, Any]]) -> str:
        """
        Create a prompt for the synthesis model.
        
        Args:
            original_prompt: The original user prompt
            responses: List of successful responses from different models
            
        Returns:
            str: The synthesis prompt
        """
        # Start with a clear instruction
        synthesis_prompt = """You are a synthesis AI that combines and analyzes responses from multiple AI models to provide the most comprehensive and accurate answer. Your task is to:

1. Analyze the strengths and unique insights from each model's response
2. Combine the best elements into a cohesive, well-structured answer
3. Resolve any contradictions between different responses
4. Ensure the final answer is accurate, helpful, and complete
5. Maintain a neutral, balanced perspective

Here is the original user question:

"""
        
        # Add the original prompt
        synthesis_prompt += f'"{original_prompt}"\n\n'
        synthesis_prompt += "Here are the responses from different AI models:\n\n"
        
        # Add each model's response
        for i, response in enumerate(responses):
            model_name = response.get("model", f"Model {i+1}")
            response_text = response.get("text", "").strip()
            
            synthesis_prompt += f"=== {model_name} Response ===\n{response_text}\n\n"
        
        # Add final instruction
        synthesis_prompt += """Based on these responses, provide a comprehensive synthesis that:
- Combines the most accurate and helpful information from all models
- Resolves any contradictions or inconsistencies
- Provides a complete answer to the original question
- Is well-structured and easy to understand
- Cites specific models when they provided unique insights

Your synthesized response:"""
        
        return synthesis_prompt
    
    def _clean_synthesis_output(self, text: str) -> str:
        """
        Clean up the synthesized output.
        
        Args:
            text: The raw synthesized text
            
        Returns:
            str: The cleaned synthesized text
        """
        # Remove any "Synthesized Response:" prefix
        if text.startswith("Synthesized Response:"):
            text = text[len("Synthesized Response:"):].strip()
            
        # Remove any markdown-style model citations if they're too verbose
        lines = text.split("\n")
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that are just model attribution headers
            if line.strip().startswith("(From ") and line.strip().endswith(")"):
                continue
            cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines)
