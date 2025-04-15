import os
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Import client modules
from backend.clients.gemini_client import GeminiClient
from backend.clients.openai_client import OpenAIClient
from backend.clients.huggingface_client import HuggingFaceClient
from backend.clients.openrouter_client import OpenRouterClient
from backend.clients.claude_client import ClaudeClient
from backend.clients.llama_client import LlamaClient
from backend.clients.synthesis_client import SynthesisClient
from backend.router import MultiAIRouter

# Import performance enhancement modules
from backend.cache import CacheManager
from backend.utils import PerformanceMonitor, ResourceManager, with_timeout, retry_with_backoff, KeyManager

# Import feature modules
from backend.features import ConversationMemory, FileProcessor, FeedbackManager, ModelOptimizer

class MultiAIApp:
    def __init__(self):
        """Initialize the Multi-AI Application."""
        # Load environment variables
        load_dotenv()
        
        # Initialize key manager for secure API key handling
        self.key_manager = KeyManager()
        
        # Initialize performance enhancement components
        self.cache = CacheManager()
        self.monitor = PerformanceMonitor()
        self.resource_manager = ResourceManager()
        
        # Initialize feature components
        self.conversation_memory = ConversationMemory()
        self.file_processor = FileProcessor()
        self.feedback_manager = FeedbackManager()
        
        # Initialize clients
        self.clients = {}
        
        # Add available clients based on securely retrieved API keys
        gemini_key = self.key_manager.get_api_key("gemini")
        if gemini_key and self.key_manager.validate_key("gemini", gemini_key):
            try:
                self.clients["gemini"] = GeminiClient(api_key=gemini_key)
                self.key_manager.log_key_usage("gemini", "initialization")
            except Exception as e:
                print(f"Failed to initialize Gemini client: {e}")
        
        openai_key = self.key_manager.get_api_key("openai")
        if openai_key and self.key_manager.validate_key("openai", openai_key):
            try:
                self.clients["openai"] = OpenAIClient(api_key=openai_key)
                self.key_manager.log_key_usage("openai", "initialization")
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
        
        huggingface_key = self.key_manager.get_api_key("huggingface")
        if huggingface_key and self.key_manager.validate_key("huggingface", huggingface_key):
            try:
                self.clients["huggingface"] = HuggingFaceClient(api_key=huggingface_key)
                self.key_manager.log_key_usage("huggingface", "initialization")
            except Exception as e:
                print(f"Failed to initialize Hugging Face client: {e}")
        
        openrouter_key = self.key_manager.get_api_key("openrouter")
        if openrouter_key and self.key_manager.validate_key("openrouter", openrouter_key):
            try:
                self.clients["openrouter"] = OpenRouterClient(api_key=openrouter_key)
                self.key_manager.log_key_usage("openrouter", "initialization")
            except Exception as e:
                print(f"Failed to initialize OpenRouter client: {e}")
        
        claude_key = self.key_manager.get_api_key("claude")
        if claude_key and self.key_manager.validate_key("claude", claude_key):
            try:
                self.clients["claude"] = ClaudeClient(api_key=claude_key)
                self.key_manager.log_key_usage("claude", "initialization")
            except Exception as e:
                print(f"Failed to initialize Claude client: {e}")
        
        llama_key = self.key_manager.get_api_key("llama")
        if llama_key and self.key_manager.validate_key("llama", llama_key):
            try:
                self.clients["llama"] = LlamaClient(api_key=llama_key)
                self.key_manager.log_key_usage("llama", "initialization")
                # Initialize synthesis client with Llama
                self.synthesis_client = SynthesisClient(self.clients["llama"])
            except Exception as e:
                print(f"Failed to initialize Llama client: {e}")
                self.synthesis_client = SynthesisClient(None)
        else:
            self.synthesis_client = SynthesisClient(None)
        
        # Initialize router
        self.router = MultiAIRouter(self.clients)
        
        # Initialize model optimizer with feedback manager
        self.model_optimizer = ModelOptimizer(self.feedback_manager)
        
        # Periodically clean up expired cache entries
        asyncio.create_task(self._periodic_cache_cleanup())
    
    async def _periodic_cache_cleanup(self, interval: int = 3600):
        """Periodically clean up expired cache entries."""
        while True:
            # Wait for the specified interval
            await asyncio.sleep(interval)
            
            # Clean up expired cache entries
            cleared_count = self.cache.clear_expired()
            
            # Log cache stats
            cache_stats = self.cache.get_stats()
            self.monitor.log_cache_metrics(cache_stats)
            
            # Clean up stale requests
            self.monitor.cleanup_stale_requests()
    
    async def process_prompt(self, prompt: str, model: str = None, 
                            use_multiple: bool = False, synthesize: bool = False,
                            conversation_id: str = None, user_id: str = None,
                            file_path: str = None, **kwargs) -> Dict[str, Any]:
        """Process a user prompt and return AI response(s)."""
        # Generate a unique request ID for tracking
        request_id = str(uuid.uuid4())
        
        # Process file if provided
        if file_path:
            success, file_content, error = await self.file_processor.extract_text_from_file(file_path)
            if success:
                file_info = self.file_processor.get_file_info(file_path)
                prompt = self.file_processor.create_prompt_with_file_content(prompt, file_content, file_info)
            else:
                return {
                    "text": f"Error processing file: {error}",
                    "model": "system",
                    "success": False,
                    "error": "file_processing_error"
                }
        
        # Add conversation context if conversation_id provided
        if conversation_id:
            # Add the user's message to conversation history
            self.conversation_memory.add_message(conversation_id, "user", prompt)
            
            # Get conversation context for the prompt
            context = self.conversation_memory.get_context_for_prompt(conversation_id)
            if context:
                # Combine context with prompt
                prompt = f"{context}\n\nCurrent question: {prompt}"
        
        # Check cache first if not using multiple models
        if not use_multiple and model:
            cached_response = self.cache.get(prompt, model, kwargs)
            if cached_response:
                # If conversation_id provided, add response to conversation history
                if conversation_id and cached_response.get("success", False):
                    self.conversation_memory.add_message(
                        conversation_id, "assistant", cached_response["text"], cached_response["model"]
                    )
                return cached_response
        
        # Start tracking the request
        self.monitor.start_request(request_id, model or "auto")
        
        try:
            if use_multiple:
                # Get responses from multiple models
                responses = await self._get_multiple_responses(prompt, request_id, **kwargs)
                
                # If synthesis is requested, use Llama to synthesize the responses
                if synthesize and responses and any(r["success"] for r in responses):
                    synthesis = await self._get_synthesis(prompt, responses, request_id, **kwargs)
                    result = {
                        "responses": responses,
                        "synthesis": synthesis,
                        "success": True
                    }
                    
                    # If conversation_id provided, add synthesized response to conversation history
                    if conversation_id and synthesis.get("success", False):
                        self.conversation_memory.add_message(
                            conversation_id, "assistant", synthesis["text"], "synthesis"
                        )
                else:
                    result = {
                        "responses": responses,
                        "success": any(r["success"] for r in responses)
                    }
                    
                    # If conversation_id provided, add all successful responses to conversation history
                    if conversation_id:
                        for response in responses:
                            if response.get("success", False):
                                self.conversation_memory.add_message(
                                    conversation_id, "assistant", response["text"], response["model"]
                                )
                
                # End tracking with success if any model succeeded
                self.monitor.end_request(request_id, any(r["success"] for r in responses))
                
                return result
            else:
                # Use model optimizer to select the best model if none specified
                if not model:
                    model = self.model_optimizer.select_optimal_model(
                        prompt, self.router.available_models, user_id
                    )
                
                # Get response from a single model
                result = await self._get_single_response(prompt, model, request_id, **kwargs)
                
                # Update model optimizer with result
                if model:
                    self.model_optimizer.update_model_performance(
                        prompt, result["model"], result["success"]
                    )
                
                # Cache successful responses
                if result["success"]:
                    self.cache.set(prompt, result["model"], result, kwargs)
                    
                    # If conversation_id provided, add response to conversation history
                    if conversation_id:
                        self.conversation_memory.add_message(
                            conversation_id, "assistant", result["text"], result["model"]
                        )
                
                # End tracking with success status
                self.monitor.end_request(request_id, result["success"], 
                                        error_type=result.get("error"))
                
                return result
        except Exception as e:
            # Handle unexpected errors
            error_response = {
                "text": f"An unexpected error occurred: {str(e)}",
                "model": model or "auto",
                "success": False,
                "error": "unexpected_error"
            }
            
            # End tracking with error
            self.monitor.end_request(request_id, False, error_type="unexpected_error")
            
            return error_response
    
    async def _get_single_response(self, prompt: str, model: str, request_id: str, **kwargs) -> Dict[str, Any]:
        """Get response from a single model with resource management and error handling."""
        # Define the function to execute
        async def get_response():
            # Use optimized fallback sequence if model fails
            fallback_models = self.model_optimizer.get_fallback_sequence(
                model, self.router.available_models
            ) if model else []
            
            response = await self.router.get_response(prompt, model, fallback=False, **kwargs)
            
            # Log API key usage
            if model and response.get("success", False):
                tokens_used = response.get("usage", {}).get("total_tokens", 0)
                self.key_manager.log_key_usage(model, "completion", tokens_used)
            
            # If primary model fails and fallback models are available, try them
            if not response["success"] and fallback_models:
                for fallback_model in fallback_models:
                    fallback_response = await self.router.get_response(prompt, fallback_model, fallback=False, **kwargs)
                    
                    # Update fallback success rate
                    self.model_optimizer.update_fallback_success(
                        model, fallback_model, fallback_response["success"]
                    )
                    
                    # Log API key usage for fallback
                    if fallback_response.get("success", False):
                        tokens_used = fallback_response.get("usage", {}).get("total_tokens", 0)
                        self.key_manager.log_key_usage(fallback_model, "fallback_completion", tokens_used)
                        return fallback_response
            
            return response
        
        # Submit the request to the resource manager
        return await self.resource_manager.submit_request(
            model or "auto",
            retry_with_backoff,
            get_response,
            max_retries=2,
            initial_backoff=1.0
        )
    
    async def _get_multiple_responses(self, prompt: str, request_id: str, **kwargs) -> List[Dict[str, Any]]:
        """Get responses from multiple models with resource management and error handling."""
        models = self.router.available_models
        
        # Create tasks for each model
        tasks = []
        for model in models:
            # Define the function to execute for this model
            async def get_model_response(model_name=model):
                return await self._get_single_response(prompt, model_name, f"{request_id}_{model_name}", **kwargs)
            
            # Submit the request to the resource manager
            task = asyncio.create_task(get_model_response())
            tasks.append(task)
        
        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process responses
        processed_responses = []
        for i, response in enumerate(responses):
            model = models[i]
            
            # Handle exceptions
            if isinstance(response, Exception):
                processed_responses.append({
                    "text": f"Error getting response from {model}: {str(response)}",
                    "model": model,
                    "success": False,
                    "error": "execution_error"
                })
            else:
                processed_responses.append(response)
        
        return processed_responses
    
    async def _get_synthesis(self, prompt: str, responses: List[Dict[str, Any]], 
                           request_id: str, **kwargs) -> Dict[str, Any]:
        """Get synthesis of multiple responses with resource management and error handling."""
        # Define the function to execute
        async def get_synthesis():
            synthesis_response = await self.synthesis_client.synthesize_responses(prompt, responses, **kwargs)
            
            # Log API key usage for synthesis
            if synthesis_response.get("success", False):
                tokens_used = synthesis_response.get("usage", {}).get("total_tokens", 0)
                self.key_manager.log_key_usage("llama", "synthesis", tokens_used)
                
            return synthesis_response
        
        # Submit the request to the resource manager
        return await self.resource_manager.submit_request(
            "llama",
            retry_with_backoff,
            get_synthesis,
            max_retries=1,
            initial_backoff=1.0
        )
    
    async def process_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process an uploaded file and prepare it for AI analysis."""
        return await self.file_processor.process_file(file_content, filename)
    
    def get_available_models(self) -> list:
        """Get list of available AI models."""
        return self.router.available_models
    
    def is_synthesis_available(self) -> bool:
        """Check if synthesis functionality is available."""
        return "llama" in self.clients
    
    def get_performance_metrics(self, model: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics for the application."""
        metrics = self.monitor.get_metrics(model)
        
        # Add cache stats
        metrics["cache"] = self.cache.get_stats()
        
        return metrics
    
    def get_model_recommendations(self) -> Dict[str, Any]:
        """Get model recommendations for different query categories."""
        return self.model_optimizer.get_model_recommendations()
    
    def get_fallback_statistics(self) -> Dict[str, Any]:
        """Get statistics about fallback success rates."""
        return self.model_optimizer.get_fallback_statistics()
    
    def add_feedback(self, response_id: str, model: str, rating: int, 
                   comment: Optional[str] = None, user_id: Optional[str] = None) -> None:
        """
        Add user feedback for a response.
        
        Args:
            response_id: Unique identifier for the response
            model: The AI model that generated the response
            rating: Rating value (1-5)
            comment: Optional feedback comment
            user_id: Optional identifier for the user
        """
        # Add rating to feedback manager
        self.feedback_manager.add_response_rating(response_id, model, rating, user_id)
        
        # Add comment if provided
        if comment:
            self.feedback_manager.add_feedback_comment(response_id, model, comment, user_id)
        
    def save_conversation(self, conversation_id: str) -> Optional[str]:
        """
        Save the current conversation to a file.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            str: Path to the saved file, or None if saving failed
        """
        return self.conversation_memory.save_conversation(conversation_id)
