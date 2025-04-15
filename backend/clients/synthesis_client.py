import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

class SynthesisClient:
    """
    Handles the Mixture-of-Agents functionality, synthesizing outputs from multiple AI models.
    Uses Llama AI to combine and analyze responses from different models.
    """
    
    def __init__(self):
        """
        Initialize the synthesis client.
        """
        self.synthesis_methods = {
            "parallel": self._parallel_synthesis,
            "sequential": self._sequential_synthesis,
            "debate": self._debate_synthesis
        }
        self.default_method = "parallel"
    
    async def synthesize(self, 
                        prompt: str, 
                        models: List[Dict[str, Any]], 
                        method: str = "parallel",
                        llama_client = None,
                        max_tokens: int = 1000,
                        temperature: float = 0.7) -> Dict[str, Any]:
        """
        Synthesize responses from multiple models.
        
        Args:
            prompt: User prompt to send to models
            models: List of model clients to use
            method: Synthesis method (parallel, sequential, debate)
            llama_client: Llama client for synthesis
            max_tokens: Maximum tokens for responses
            temperature: Temperature for generation
            
        Returns:
            Dict with synthesized response and individual responses
        """
        if not models:
            return {
                "synthesized_response": "No models available for synthesis.",
                "individual_responses": [],
                "method": method,
                "timestamp": datetime.now().isoformat()
            }
        
        # Use default method if specified method not available
        if method not in self.synthesis_methods:
            method = self.default_method
        
        # Get synthesis function
        synthesis_func = self.synthesis_methods[method]
        
        # Execute synthesis
        try:
            result = await synthesis_func(
                prompt=prompt,
                models=models,
                llama_client=llama_client,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return result
        except Exception as e:
            return {
                "synthesized_response": f"Error during synthesis: {str(e)}",
                "individual_responses": [],
                "method": method,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _parallel_synthesis(self, 
                                prompt: str, 
                                models: List[Dict[str, Any]], 
                                llama_client = None,
                                max_tokens: int = 1000,
                                temperature: float = 0.7) -> Dict[str, Any]:
        """
        Parallel synthesis - query all models simultaneously and synthesize results.
        
        Args:
            prompt: User prompt to send to models
            models: List of model clients to use
            llama_client: Llama client for synthesis
            max_tokens: Maximum tokens for responses
            temperature: Temperature for generation
            
        Returns:
            Dict with synthesized response and individual responses
        """
        # Query all models in parallel
        individual_responses = []
        tasks = []
        
        for model_info in models:
            model_name = model_info.get("name", "Unknown")
            model_client = model_info.get("client")
            
            if not model_client:
                individual_responses.append({
                    "model": model_name,
                    "response": "Model client not available",
                    "error": True
                })
                continue
            
            # Create task for this model
            task = self._query_model(
                model_client=model_client,
                model_name=model_name,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        if tasks:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            individual_responses.extend(responses)
        
        # Filter out errors
        valid_responses = [r for r in individual_responses if not isinstance(r, Exception) and not r.get("error", False)]
        
        # If no valid responses, return error
        if not valid_responses:
            return {
                "synthesized_response": "No valid responses from any models.",
                "individual_responses": individual_responses,
                "method": "parallel",
                "timestamp": datetime.now().isoformat()
            }
        
        # Synthesize with Llama if available
        if llama_client:
            synthesized_response = await self._synthesize_with_llama(
                llama_client=llama_client,
                prompt=prompt,
                responses=valid_responses,
                method="parallel",
                max_tokens=max_tokens,
                temperature=temperature
            )
        else:
            # Simple synthesis without Llama
            synthesized_response = self._simple_synthesis(valid_responses)
        
        return {
            "synthesized_response": synthesized_response,
            "individual_responses": individual_responses,
            "method": "parallel",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _sequential_synthesis(self, 
                                   prompt: str, 
                                   models: List[Dict[str, Any]], 
                                   llama_client = None,
                                   max_tokens: int = 1000,
                                   temperature: float = 0.7) -> Dict[str, Any]:
        """
        Sequential synthesis - query models one after another, each seeing previous responses.
        
        Args:
            prompt: User prompt to send to models
            models: List of model clients to use
            llama_client: Llama client for synthesis
            max_tokens: Maximum tokens for responses
            temperature: Temperature for generation
            
        Returns:
            Dict with synthesized response and individual responses
        """
        individual_responses = []
        current_prompt = prompt
        
        # Query models sequentially
        for model_info in models:
            model_name = model_info.get("name", "Unknown")
            model_client = model_info.get("client")
            
            if not model_client:
                individual_responses.append({
                    "model": model_name,
                    "response": "Model client not available",
                    "error": True
                })
                continue
            
            # Query this model
            response = await self._query_model(
                model_client=model_client,
                model_name=model_name,
                prompt=current_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            individual_responses.append(response)
            
            # Update prompt with this response for next model
            if not response.get("error", False):
                current_prompt = f"{current_prompt}\n\n{model_name}'s response: {response['response']}\n\nBased on this information, please provide your response:"
        
        # Filter out errors
        valid_responses = [r for r in individual_responses if not r.get("error", False)]
        
        # If no valid responses, return error
        if not valid_responses:
            return {
                "synthesized_response": "No valid responses from any models.",
                "individual_responses": individual_responses,
                "method": "sequential",
                "timestamp": datetime.now().isoformat()
            }
        
        # Synthesize with Llama if available
        if llama_client:
            synthesized_response = await self._synthesize_with_llama(
                llama_client=llama_client,
                prompt=prompt,
                responses=valid_responses,
                method="sequential",
                max_tokens=max_tokens,
                temperature=temperature
            )
        else:
            # In sequential mode, the last response is often the best synthesis
            synthesized_response = valid_responses[-1]["response"]
        
        return {
            "synthesized_response": synthesized_response,
            "individual_responses": individual_responses,
            "method": "sequential",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _debate_synthesis(self, 
                               prompt: str, 
                               models: List[Dict[str, Any]], 
                               llama_client = None,
                               max_tokens: int = 1000,
                               temperature: float = 0.7,
                               rounds: int = 2) -> Dict[str, Any]:
        """
        Debate synthesis - models debate with each other for multiple rounds.
        
        Args:
            prompt: User prompt to send to models
            models: List of model clients to use
            llama_client: Llama client for synthesis
            max_tokens: Maximum tokens for responses
            temperature: Temperature for generation
            rounds: Number of debate rounds
            
        Returns:
            Dict with synthesized response and individual responses
        """
        if len(models) < 2:
            return await self._parallel_synthesis(
                prompt=prompt,
                models=models,
                llama_client=llama_client,
                max_tokens=max_tokens,
                temperature=temperature
            )
        
        debate_history = []
        current_prompt = f"You are participating in a debate to answer the following question: {prompt}\n\nProvide your initial thoughts."
        
        # Initial round - get initial responses from all models
        initial_responses = []
        tasks = []
        
        for model_info in models:
            model_name = model_info.get("name", "Unknown")
            model_client = model_info.get("client")
            
            if not model_client:
                continue
            
            # Create task for this model
            task = self._query_model(
                model_client=model_client,
                model_name=model_name,
                prompt=current_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        if tasks:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            for response in responses:
                if not isinstance(response, Exception) and not response.get("error", False):
                    initial_responses.append(response)
                    debate_history.append(response)
        
        # If no valid initial responses, return error
        if not initial_responses:
            return {
                "synthesized_response": "No valid responses from any models for debate.",
                "individual_responses": [],
                "method": "debate",
                "timestamp": datetime.now().isoformat()
            }
        
        # Debate rounds
        for round_num in range(rounds):
            round_responses = []
            tasks = []
            
            # Create debate prompt with all previous responses
            debate_prompt = f"Question: {prompt}\n\nDebate history:\n"
            for resp in debate_history:
                debate_prompt += f"{resp['model']}: {resp['response']}\n\n"
            
            debate_prompt += f"Round {round_num + 1}: Based on the debate so far, provide your updated answer. You may critique other responses and strengthen your own position."
            
            # Get responses for this round
            for model_info in models:
                model_name = model_info.get("name", "Unknown")
                model_client = model_info.get("client")
                
                if not model_client:
                    continue
                
                # Create task for this model
                task = self._query_model(
                    model_client=model_client,
                    model_name=model_name,
                    prompt=debate_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            if tasks:
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                for response in responses:
                    if not isinstance(response, Exception) and not response.get("error", False):
                        round_responses.append(response)
                        debate_history.append(response)
        
        # Synthesize with Llama if available
        if llama_client:
            synthesized_response = await self._synthesize_with_llama(
                llama_client=llama_client,
                prompt=prompt,
                responses=debate_history,
                method="debate",
                max_tokens=max_tokens,
                temperature=temperature
            )
        else:
            # Simple synthesis of final round responses
            final_round_responses = debate_history[-len(models):]
            synthesized_response = self._simple_synthesis(final_round_responses)
        
        return {
            "synthesized_response": synthesized_response,
            "individual_responses": debate_history,
            "method": "debate",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _query_model(self, 
                          model_client, 
                          model_name: str, 
                          prompt: str,
                          max_tokens: int = 1000,
                          temperature: float = 0.7) -> Dict[str, Any]:
        """
        Query a single model.
        
        Args:
            model_client: Client for the model
            model_name: Name of the model
            prompt: Prompt to send
            max_tokens: Maximum tokens for response
            temperature: Temperature for generation
            
        Returns:
            Dict with model response
        """
        try:
            # Check if client has async query method
            if hasattr(model_client, 'query_async'):
                response = await model_client.query_async(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            else:
                # Fall back to synchronous query in a thread
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: model_client.query(
                        prompt=prompt,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                )
            
            return {
                "model": model_name,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "model": model_name,
                "response": f"Error querying model: {str(e)}",
                "error": True,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _synthesize_with_llama(self, 
                                    llama_client, 
                                    prompt: str,
                                    responses: List[Dict[str, Any]],
                                    method: str,
                                    max_tokens: int = 1000,
                                    temperature: float = 0.7) -> str:
        """
        Synthesize responses using Llama.
        
        Args:
            llama_client: Llama client for synthesis
            prompt: Original user prompt
            responses: List of model responses
            method: Synthesis method used
            max_tokens: Maximum tokens for synthesis
            temperature: Temperature for generation
            
        Returns:
            Synthesized response
        """
        # Create synthesis prompt
        synthesis_prompt = f"""You are a synthesis AI that combines and analyzes responses from multiple AI models to provide the best possible answer.

Original question: {prompt}

Responses from different models:
"""
        
        for resp in responses:
            synthesis_prompt += f"\n{resp['model']}: {resp['response']}\n"
        
        synthesis_prompt += f"""
Based on these responses, synthesize a comprehensive answer that:
1. Incorporates the strengths of each model's response
2. Resolves any contradictions between models
3. Provides the most accurate and helpful information
4. Acknowledges any limitations or uncertainties

Your synthesis should be well-structured, informative, and directly address the original question.
"""
        
        try:
            # Check if client has async query method
            if hasattr(llama_client, 'query_async'):
                synthesis = await llama_client.query_async(
                    prompt=synthesis_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            else:
                # Fall back to synchronous query in a thread
                loop = asyncio.get_event_loop()
                synthesis = await loop.run_in_executor(
                    None,
                    lambda: llama_client.query(
                        prompt=synthesis_prompt,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                )
            
            return synthesis
        except Exception as e:
            # Fall back to simple synthesis if Llama fails
            return f"Llama synthesis failed: {str(e)}\n\n" + self._simple_synthesis(responses)
    
    def _simple_synthesis(self, responses: List[Dict[str, Any]]) -> str:
        """
        Simple synthesis without using Llama.
        
        Args:
            responses: List of model responses
            
        Returns:
            Synthesized response
        """
        if not responses:
            return "No responses available for synthesis."
        
        # If only one response, return it
        if len(responses) == 1:
            return responses[0]["response"]
        
        # Simple concatenation with headers
        synthesis = "Synthesis of model responses:\n\n"
        
        for resp in responses:
            synthesis += f"## {resp['model']}\n{resp['response']}\n\n"
        
        synthesis += "\nThis synthesis combines responses from multiple AI models. For the best results, consider the strengths and limitations of each model's perspective."
        
        return synthesis
