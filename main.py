import os
import asyncio
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime

# Import clients
from backend.clients.openai_client import OpenAIClient
from backend.clients.claude_client import ClaudeClient
from backend.clients.gemini_client import GeminiClient
from backend.clients.llama_client import LlamaClient
from backend.clients.huggingface_client import HuggingFaceClient
from backend.clients.openrouter_client import OpenRouterClient
from backend.clients.synthesis_client import SynthesisClient

# Import features
from backend.features.conversation_memory import ConversationMemory
from backend.features.file_processor import FileProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("multi_ai_app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("MultiAIApp")

class MultiAIApp:
    """
    Main application class for the Multi-AI app.
    Manages clients, features, and orchestrates interactions.
    """
    
    def __init__(self):
        """Initialize the Multi-AI application."""
        logger.info("Initializing Multi-AI application")
        
        # Initialize API clients
        self._initialize_clients()
        
        # Initialize features
        self.conversation_memory = ConversationMemory()
        self.file_processor = FileProcessor()
        
        logger.info("Multi-AI application initialized successfully")
    
    def _initialize_clients(self):
        """Initialize API clients with API keys from environment variables."""
        try:
            # Initialize OpenAI client
            openai_api_key = os.getenv("OPENAI_API_KEY")
            self.openai_client = OpenAIClient(api_key=openai_api_key) if openai_api_key else None
            
            # Initialize Claude client
            claude_api_key = os.getenv("CLAUDE_API_KEY")
            self.claude_client = ClaudeClient(api_key=claude_api_key) if claude_api_key else None
            
            # Initialize Gemini client
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            self.gemini_client = GeminiClient(api_key=gemini_api_key) if gemini_api_key else None
            
            # Initialize Llama client
            llama_api_key = os.getenv("LLAMA_API_KEY")
            self.llama_client = LlamaClient(api_key=llama_api_key) if llama_api_key else None
            
            # Initialize HuggingFace client
            huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
            self.huggingface_client = HuggingFaceClient(api_key=huggingface_api_key) if huggingface_api_key else None
            
            # Initialize OpenRouter client
            openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            self.openrouter_client = OpenRouterClient(api_key=openrouter_api_key) if openrouter_api_key else None
            
            # Initialize Synthesis client (uses Llama for synthesis)
            self.synthesis_client = SynthesisClient(llama_client=self.llama_client) if self.llama_client else None
            
            # Log initialization status
            logger.info(f"OpenAI client initialized: {self.openai_client is not None}")
            logger.info(f"Claude client initialized: {self.claude_client is not None}")
            logger.info(f"Gemini client initialized: {self.gemini_client is not None}")
            logger.info(f"Llama client initialized: {self.llama_client is not None}")
            logger.info(f"HuggingFace client initialized: {self.huggingface_client is not None}")
            logger.info(f"OpenRouter client initialized: {self.openrouter_client is not None}")
            logger.info(f"Synthesis client initialized: {self.synthesis_client is not None}")
        
        except Exception as e:
            logger.error(f"Error initializing clients: {e}")
            raise
    
    async def process_prompt(self, prompt: str, model: Optional[str] = None, 
                            use_multiple: bool = False, synthesize: bool = False,
                            conversation_id: Optional[str] = None,
                            file_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Process a prompt using the specified model or multiple models.
        
        Args:
            prompt: The user prompt to process
            model: The model to use (if not using multiple)
            use_multiple: Whether to use multiple models
            synthesize: Whether to synthesize responses (if using multiple)
            conversation_id: Unique identifier for the conversation
            file_path: Path to a file to include in the prompt
            **kwargs: Additional parameters for the model
            
        Returns:
            Dict containing the response
        """
        try:
            # Generate a conversation ID if not provided
            if not conversation_id:
                conversation_id = str(datetime.now().timestamp())
            
            # Process file if provided
            enhanced_prompt = prompt
            if file_path and os.path.exists(file_path):
                logger.info(f"Processing file: {file_path}")
                
                # Get file info
                file_info = self.file_processor.get_file_info(file_path)
                
                # Extract text from file
                success, file_content, error = await self.file_processor.extract_text_from_file(file_path)
                
                if success and file_content:
                    # Create enhanced prompt with file content
                    enhanced_prompt = self.file_processor.create_prompt_with_file_content(
                        prompt=prompt,
                        file_content=file_content,
                        file_info=file_info
                    )
                    logger.info(f"Enhanced prompt with file content from {file_path}")
                else:
                    logger.warning(f"Failed to extract text from file: {error}")
            
            # Add user message to conversation memory
            self.conversation_memory.add_message(
                conversation_id=conversation_id,
                role="user",
                content=prompt
            )
            
            # Get conversation context
            context = self.conversation_memory.get_context_for_prompt(conversation_id)
            
            # Create full prompt with context
            full_prompt = f"{context}\n\n{enhanced_prompt}"
            
            if use_multiple:
                # Use multiple models
                return await self._process_with_multiple_models(
                    prompt=full_prompt,
                    synthesize=synthesize,
                    conversation_id=conversation_id,
                    **kwargs
                )
            else:
                # Use single model
                return await self._process_with_single_model(
                    prompt=full_prompt,
                    model=model,
                    conversation_id=conversation_id,
                    **kwargs
                )
        
        except Exception as e:
            logger.error(f"Error processing prompt: {e}")
            return {
                "text": f"Error processing prompt: {str(e)}",
                "model": "system",
                "success": False,
                "error": str(e)
            }
    
    async def _process_with_single_model(self, prompt: str, model: str, 
                                       conversation_id: str, **kwargs) -> Dict[str, Any]:
        """
        Process a prompt using a single model.
        
        Args:
            prompt: The full prompt to process
            model: The model to use
            conversation_id: Unique identifier for the conversation
            **kwargs: Additional parameters for the model
            
        Returns:
            Dict containing the response
        """
        logger.info(f"Processing prompt with model: {model}")
        
        try:
            # Select the appropriate client
            client = self._get_client_for_model(model)
            
            if not client:
                return {
                    "text": f"Model {model} is not available. Please check your API keys.",
                    "model": model,
                    "success": False,
                    "error": "model_unavailable"
                }
            
            # Generate response
            response = await client.generate_response(prompt, **kwargs)
            
            # Add assistant message to conversation memory
            if response.get("success", False):
                self.conversation_memory.add_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=response["text"],
                    model=response["model"]
                )
            
            return response
        
        except Exception as e:
            logger.error(f"Error processing with single model: {e}")
            return {
                "text": f"Error processing with model {model}: {str(e)}",
                "model": model,
                "success": False,
                "error": str(e)
            }
    
    async def _process_with_multiple_models(self, prompt: str, synthesize: bool,
                                          conversation_id: str, **kwargs) -> Dict[str, Any]:
        """
        Process a prompt using multiple models.
        
        Args:
            prompt: The full prompt to process
            synthesize: Whether to synthesize responses
            conversation_id: Unique identifier for the conversation
            **kwargs: Additional parameters for the models
            
        Returns:
            Dict containing the responses and synthesis
        """
        logger.info("Processing prompt with multiple models")
        
        try:
            # Get available clients
            clients = self._get_available_clients()
            
            if not clients:
                return {
                    "text": "No AI models are available. Please check your API keys.",
                    "model": "system",
                    "success": False,
                    "error": "no_models_available"
                }
            
            # Generate responses from all available models
            tasks = []
            for model, client in clients.items():
                tasks.append(client.generate_response(prompt, **kwargs))
            
            # Wait for all responses
            responses = await asyncio.gather(*tasks)
            
            # Process synthesis if requested and available
            synthesis = None
            if synthesize and self.synthesis_client and any(r.get("success", False) for r in responses):
                logger.info("Synthesizing responses")
                synthesis = await self.synthesis_client.synthesize_responses(
                    prompt=prompt,
                    responses=responses,
                    **kwargs
                )
                
                # Add synthesized response to conversation memory
                if synthesis.get("success", False):
                    self.conversation_memory.add_message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=synthesis["text"],
                        model="synthesis"
                    )
            else:
                # Add individual responses to conversation memory
                for response in responses:
                    if response.get("success", False):
                        self.conversation_memory.add_message(
                            conversation_id=conversation_id,
                            role="assistant",
                            content=response["text"],
                            model=response["model"]
                        )
            
            return {
                "success": True,
                "responses": responses,
                "synthesis": synthesis
            }
        
        except Exception as e:
            logger.error(f"Error processing with multiple models: {e}")
            return {
                "text": f"Error processing with multiple models: {str(e)}",
                "model": "system",
                "success": False,
                "error": str(e)
            }
    
    def _get_client_for_model(self, model: str):
        """
        Get the appropriate client for the specified model.
        
        Args:
            model: The model to use
            
        Returns:
            The client for the specified model, or None if not available
        """
        model = model.lower()
        
        if model in ["openai", "gpt"]:
            return self.openai_client
        elif model in ["anthropic", "claude"]:
            return self.claude_client
        elif model in ["google", "gemini"]:
            return self.gemini_client
        elif model in ["meta", "llama"]:
            return self.llama_client
        elif model in ["huggingface", "hf"]:
            return self.huggingface_client
        elif model in ["openrouter", "or"]:
            return self.openrouter_client
        else:
            logger.warning(f"Unknown model: {model}")
            return None
    
    def _get_available_clients(self) -> Dict[str, Any]:
        """
        Get all available clients.
        
        Returns:
            Dict mapping model names to clients
        """
        clients = {}
        
        if self.openai_client:
            clients["openai"] = self.openai_client
        
        if self.claude_client:
            clients["claude"] = self.claude_client
        
        if self.gemini_client:
            clients["gemini"] = self.gemini_client
        
        if self.llama_client:
            clients["llama"] = self.llama_client
        
        if self.huggingface_client:
            clients["huggingface"] = self.huggingface_client
        
        if self.openrouter_client:
            clients["openrouter"] = self.openrouter_client
        
        return clients
