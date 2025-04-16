import os
import sys
from dotenv import load_dotenv
from backend.clients.openrouter_unified_client import create_openrouter_client

# Load environment variables
load_dotenv()

def initialize_backend():
    """
    Initialize the backend components including secret manager, clients, and features.
    
    Returns:
        Dictionary containing all backend components
    """
    print("Initializing backend...")
    
    # Initialize backend dictionary
    backend = {}
    
    # Initialize secret manager
    from backend.features.secret_manager import SecretManager
    secret_manager = SecretManager()
    backend["secret_manager"] = secret_manager
    
    # Get API keys
    openrouter_api_key = secret_manager.get_secret("OPENROUTER_API_KEY")
    gemini_api_key = secret_manager.get_secret("GEMINI_API_KEY")
    github_pat_token = secret_manager.get_secret("GITHUB_PAT_TOKEN")
    
    if not openrouter_api_key:
        print("Warning: OPENROUTER_API_KEY not found in secrets")
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
    
    if not github_pat_token:
        print("Warning: GITHUB_PAT_TOKEN not found in secrets")
        github_pat_token = os.getenv("GITHUB_PAT_TOKEN", "")
    
    # Initialize clients
    from backend.clients.gemini_client import GeminiClient
    from backend.clients.puter_client import PuterClient
    from backend.clients.github_models_client import GitHubModelsClient
    
    # Initialize clients using a mix of OpenRouter unified client and direct clients
    clients = {
        "openai": create_openrouter_client(openrouter_api_key, "openai"),
        "claude": create_openrouter_client(openrouter_api_key, "claude"),
        "gemini": GeminiClient(gemini_api_key),  # Use direct Gemini client for gemini-2.0-flash
        "llama": create_openrouter_client(openrouter_api_key, "llama"),
        "huggingface": create_openrouter_client(openrouter_api_key, "huggingface"),
        "deepseek": create_openrouter_client(openrouter_api_key, "deepseek"),
        "openrouter": create_openrouter_client(openrouter_api_key, "openrouter"),
        "puter": PuterClient(),  # Add Puter client for free OpenAI access
        "github_gpt4_mini": GitHubModelsClient(github_pat_token),  # GitHub Marketplace Models - GPT-4.1-mini
        "github_deepseek": GitHubModelsClient(github_pat_token),  # GitHub Marketplace Models - DeepSeek-V3
        "github_llama": GitHubModelsClient(github_pat_token)  # GitHub Marketplace Models - Llama 4 Scout
    }
    backend["clients"] = clients
    
    # Initialize synthesis client
    from backend.clients.synthesis_client import SynthesisClient
    synthesis_client = SynthesisClient()
    backend["synthesis_client"] = synthesis_client
    
    # Initialize features
    from backend.features.model_optimizer import ModelOptimizer
    model_optimizer = ModelOptimizer()
    backend["model_optimizer"] = model_optimizer
    
    from backend.features.feedback_manager import FeedbackManager
    feedback_manager = FeedbackManager()
    backend["feedback_manager"] = feedback_manager
    
    print("Backend initialization complete")
    return backend
