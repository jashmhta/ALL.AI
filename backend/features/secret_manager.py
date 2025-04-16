import os
import toml
import streamlit as st

class SecretManager:
    """
    Manages API keys and secrets for the Multi-AI application.
    Provides secure access to credentials across different environments.
    """
    
    def __init__(self):
        """Initialize the secret manager."""
        self.secrets = {}
        self.is_huggingface_space = self._check_if_huggingface_space()
        self.load_secrets()
    
    def _check_if_huggingface_space(self) -> bool:
        """
        Check if the application is running on HuggingFace Spaces.
        
        Returns:
            True if running on HuggingFace Spaces, False otherwise
        """
        return os.environ.get("SPACE_ID") is not None
    
    def load_secrets(self) -> None:
        """Load secrets from the appropriate source based on the environment."""
        if self.is_huggingface_space:
            self._load_secrets_from_huggingface()
        else:
            self._load_secrets_from_file()
    
    def _load_secrets_from_huggingface(self) -> None:
        """Load secrets from HuggingFace Spaces environment variables."""
        # HuggingFace Spaces automatically loads secrets.toml into st.secrets
        try:
            # OpenAI
            self.secrets["OPENAI_API_KEY"] = st.secrets.get("OPENAI_API_KEY", "")
            
            # Claude/Anthropic
            self.secrets["CLAUDE_API_KEY"] = st.secrets.get("CLAUDE_API_KEY", "")
            
            # Gemini
            self.secrets["GEMINI_API_KEY"] = st.secrets.get("GEMINI_API_KEY", "")
            
            # Llama
            self.secrets["LLAMA_API_KEY"] = st.secrets.get("LLAMA_API_KEY", "")
            
            # HuggingFace
            self.secrets["HUGGINGFACE_API_KEY"] = st.secrets.get("HUGGINGFACE_API_KEY", "")
            
            # OpenRouter
            self.secrets["OPENROUTER_API_KEY"] = st.secrets.get("OPENROUTER_API_KEY", "")
            self.secrets["OPENROUTER_API_KEY_2"] = st.secrets.get("OPENROUTER_API_KEY_2", "")
            
            # DeepSeek
            self.secrets["DEEPSEEK_API_KEY"] = st.secrets.get("DEEPSEEK_API_KEY", "")
            
            # GitHub
            self.secrets["GITHUB_TOKEN"] = st.secrets.get("GITHUB_TOKEN", "")
            self.secrets["GITHUB_TOKEN_ALT"] = st.secrets.get("GITHUB_TOKEN_ALT", "")
            
            print("Loaded secrets from HuggingFace Spaces environment")
        except Exception as e:
            print(f"Error loading secrets from HuggingFace Spaces: {e}")
            # Initialize with empty values as fallback
            self._initialize_empty_secrets()
    
    def _load_secrets_from_file(self) -> None:
        """Load secrets from local secrets.toml file."""
        try:
            # Check for .streamlit/secrets.toml first (Streamlit standard)
            streamlit_secrets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".streamlit", "secrets.toml")
            
            # Then check for secrets.toml in the root directory
            root_secrets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "secrets.toml")
            
            # Finally check for secrets.toml in the current directory
            local_secrets_path = os.path.join(os.path.dirname(__file__), "secrets.toml")
            
            # Try to load from one of the paths
            if os.path.exists(streamlit_secrets_path):
                secrets_dict = toml.load(streamlit_secrets_path)
                print(f"Loaded secrets from {streamlit_secrets_path}")
            elif os.path.exists(root_secrets_path):
                secrets_dict = toml.load(root_secrets_path)
                print(f"Loaded secrets from {root_secrets_path}")
            elif os.path.exists(local_secrets_path):
                secrets_dict = toml.load(local_secrets_path)
                print(f"Loaded secrets from {local_secrets_path}")
            else:
                print("No secrets.toml file found, using environment variables")
                self._load_secrets_from_env()
                return
            
            # Extract secrets from the loaded dictionary
            # OpenAI
            if "openai" in secrets_dict:
                self.secrets["OPENAI_API_KEY"] = secrets_dict["openai"].get("OPENAI_API_KEY", "")
            else:
                self.secrets["OPENAI_API_KEY"] = secrets_dict.get("OPENAI_API_KEY", "")
            
            # Claude/Anthropic
            if "claude" in secrets_dict:
                self.secrets["CLAUDE_API_KEY"] = secrets_dict["claude"].get("CLAUDE_API_KEY", "")
            else:
                self.secrets["CLAUDE_API_KEY"] = secrets_dict.get("CLAUDE_API_KEY", "")
            
            # Gemini
            if "gemini" in secrets_dict:
                self.secrets["GEMINI_API_KEY"] = secrets_dict["gemini"].get("GEMINI_API_KEY", "")
            else:
                self.secrets["GEMINI_API_KEY"] = secrets_dict.get("GEMINI_API_KEY", "")
            
            # Llama
            if "llama" in secrets_dict:
                self.secrets["LLAMA_API_KEY"] = secrets_dict["llama"].get("LLAMA_API_KEY", "")
            else:
                self.secrets["LLAMA_API_KEY"] = secrets_dict.get("LLAMA_API_KEY", "")
            
            # HuggingFace
            if "huggingface" in secrets_dict:
                self.secrets["HUGGINGFACE_API_KEY"] = secrets_dict["huggingface"].get("HUGGINGFACE_API_KEY", "")
            else:
                self.secrets["HUGGINGFACE_API_KEY"] = secrets_dict.get("HUGGINGFACE_API_KEY", "")
            
            # OpenRouter
            if "openrouter" in secrets_dict:
                self.secrets["OPENROUTER_API_KEY"] = secrets_dict["openrouter"].get("OPENROUTER_API_KEY", "")
                self.secrets["OPENROUTER_API_KEY_2"] = secrets_dict["openrouter"].get("OPENROUTER_API_KEY_2", "")
            else:
                self.secrets["OPENROUTER_API_KEY"] = secrets_dict.get("OPENROUTER_API_KEY", "")
                self.secrets["OPENROUTER_API_KEY_2"] = secrets_dict.get("OPENROUTER_API_KEY_2", "")
            
            # DeepSeek
            if "deepseek" in secrets_dict:
                self.secrets["DEEPSEEK_API_KEY"] = secrets_dict["deepseek"].get("DEEPSEEK_API_KEY", "")
            else:
                self.secrets["DEEPSEEK_API_KEY"] = secrets_dict.get("DEEPSEEK_API_KEY", "")
            
            # GitHub
            if "github" in secrets_dict:
                self.secrets["GITHUB_TOKEN"] = secrets_dict["github"].get("GITHUB_TOKEN", "")
                self.secrets["GITHUB_TOKEN_ALT"] = secrets_dict["github"].get("GITHUB_TOKEN_ALT", "")
            else:
                self.secrets["GITHUB_TOKEN"] = secrets_dict.get("GITHUB_TOKEN", "")
                self.secrets["GITHUB_TOKEN_ALT"] = secrets_dict.get("GITHUB_TOKEN_ALT", "")
            
        except Exception as e:
            print(f"Error loading secrets from file: {e}")
            # Try environment variables as fallback
            self._load_secrets_from_env()
    
    def _load_secrets_from_env(self) -> None:
        """Load secrets from environment variables."""
        try:
            # OpenAI
            self.secrets["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")
            
            # Claude/Anthropic
            self.secrets["CLAUDE_API_KEY"] = os.environ.get("CLAUDE_API_KEY", "")
            
            # Gemini
            self.secrets["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY", "")
            
            # Llama
            self.secrets["LLAMA_API_KEY"] = os.environ.get("LLAMA_API_KEY", "")
            
            # HuggingFace
            self.secrets["HUGGINGFACE_API_KEY"] = os.environ.get("HUGGINGFACE_API_KEY", "")
            
            # OpenRouter
            self.secrets["OPENROUTER_API_KEY"] = os.environ.get("OPENROUTER_API_KEY", "")
            self.secrets["OPENROUTER_API_KEY_2"] = os.environ.get("OPENROUTER_API_KEY_2", "")
            
            # DeepSeek
            self.secrets["DEEPSEEK_API_KEY"] = os.environ.get("DEEPSEEK_API_KEY", "")
            
            # GitHub
            self.secrets["GITHUB_TOKEN"] = os.environ.get("GITHUB_TOKEN", "")
            self.secrets["GITHUB_TOKEN_ALT"] = os.environ.get("GITHUB_TOKEN_ALT", "")
            
            print("Loaded secrets from environment variables")
        except Exception as e:
            print(f"Error loading secrets from environment variables: {e}")
            # Initialize with empty values as fallback
            self._initialize_empty_secrets()
    
    def _initialize_empty_secrets(self) -> None:
        """Initialize empty secrets as fallback."""
        self.secrets = {
            "OPENAI_API_KEY": "",
            "CLAUDE_API_KEY": "",
            "GEMINI_API_KEY": "",
            "LLAMA_API_KEY": "",
            "HUGGINGFACE_API_KEY": "",
            "OPENROUTER_API_KEY": "",
            "OPENROUTER_API_KEY_2": "",
            "DEEPSEEK_API_KEY": "",
            "GITHUB_TOKEN": "",
            "GITHUB_TOKEN_ALT": ""
        }
        print("Initialized empty secrets as fallback")
    
    def get_secret(self, key: str) -> str:
        """
        Get a secret by key.
        
        Args:
            key: The key of the secret to get
            
        Returns:
            The secret value, or an empty string if not found
        """
        return self.secrets.get(key, "")
    
    def set_secret(self, key: str, value: str) -> None:
        """
        Set a secret value (only for local development).
        
        Args:
            key: The key of the secret to set
            value: The value to set
        """
        if not self.is_huggingface_space:
            self.secrets[key] = value
    
    def has_valid_secrets(self) -> bool:
        """
        Check if valid secrets are available.
        
        Returns:
            True if at least one valid API key is available, False otherwise
        """
        # Check if at least one API key is available
        return any([
            self.secrets.get("OPENAI_API_KEY", ""),
            self.secrets.get("CLAUDE_API_KEY", ""),
            self.secrets.get("GEMINI_API_KEY", ""),
            self.secrets.get("LLAMA_API_KEY", ""),
            self.secrets.get("HUGGINGFACE_API_KEY", ""),
            self.secrets.get("OPENROUTER_API_KEY", ""),
            self.secrets.get("DEEPSEEK_API_KEY", "")
        ])
    
    def get_available_models(self) -> dict:
        """
        Get a dictionary of available models based on API keys.
        
        Returns:
            Dict mapping model categories to availability status
        """
        return {
            "openai": bool(self.secrets.get("OPENAI_API_KEY", "")),
            "claude": bool(self.secrets.get("CLAUDE_API_KEY", "")),
            "gemini": bool(self.secrets.get("GEMINI_API_KEY", "")),
            "llama": bool(self.secrets.get("LLAMA_API_KEY", "")),
            "huggingface": bool(self.secrets.get("HUGGINGFACE_API_KEY", "")),
            "openrouter": bool(self.secrets.get("OPENROUTER_API_KEY", "")),
            "deepseek": bool(self.secrets.get("DEEPSEEK_API_KEY", ""))
        }
    
    def create_secrets_toml(self, directory: str) -> bool:
        """
        Create a secrets.toml file with the current secrets.
        
        Args:
            directory: Directory to create the file in
            
        Returns:
            True if creation was successful, False otherwise
        """
        if self.is_huggingface_space:
            print("Cannot create secrets.toml in HuggingFace Spaces environment")
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(directory, exist_ok=True)
            
            # Create secrets.toml content
            content = """# API Keys for Multi-AI App
# This file contains API keys for various AI services

[openai]
OPENAI_API_KEY = "{}"

[claude]
CLAUDE_API_KEY = "{}"

[gemini]
GEMINI_API_KEY = "{}"

[llama]
LLAMA_API_KEY = "{}"

[huggingface]
HUGGINGFACE_API_KEY = "{}"

[openrouter]
OPENROUTER_API_KEY = "{}"
OPENROUTER_API_KEY_2 = "{}"

[deepseek]
DEEPSEEK_API_KEY = "{}"

[github]
GITHUB_TOKEN = "{}"
GITHUB_TOKEN_ALT = "{}"
""".format(
                self.secrets.get("OPENAI_API_KEY", ""),
                self.secrets.get("CLAUDE_API_KEY", ""),
                self.secrets.get("GEMINI_API_KEY", ""),
                self.secrets.get("LLAMA_API_KEY", ""),
                self.secrets.get("HUGGINGFACE_API_KEY", ""),
                self.secrets.get("OPENROUTER_API_KEY", ""),
                self.secrets.get("OPENROUTER_API_KEY_2", ""),
                self.secrets.get("DEEPSEEK_API_KEY", ""),
                self.secrets.get("GITHUB_TOKEN", ""),
                self.secrets.get("GITHUB_TOKEN_ALT", "")
            )
            
            # Write to file
            filepath = os.path.join(directory, "secrets.toml")
            with open(filepath, "w") as f:
                f.write(content)
            
            print(f"Created secrets.toml at {filepath}")
            return True
        except Exception as e:
            print(f"Error creating secrets.toml: {e}")
            return False
