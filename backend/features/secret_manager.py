import os
import json
import toml
import streamlit as st
from typing import Dict, Any, Optional, List

class SecretManager:
    """
    Manages API keys and secrets for various AI providers.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the secret manager.
        
        Args:
            config_path: Optional path to config file
        """
        self.config_path = config_path
        self.secrets = self._load_secrets()
        self.is_huggingface_space = "SPACE_ID" in os.environ
        
        # Default API keys (for development/testing only)
        self.default_keys = {
            "openai": "",
            "claude": "",
            "gemini": "",
            "llama": "",
            "huggingface": "",
            "openrouter": "",
            "deepseek": "",
            "github_pat_token": "",
            "puter": "free"  # Puter is always available as it's free
        }
    
    def _load_secrets(self) -> Dict[str, str]:
        """
        Load secrets from various sources.
        
        Returns:
            Dictionary of provider to API key
        """
        secrets = {}
        
        # Try loading from Streamlit secrets
        try:
            for provider in ["openai", "claude", "gemini", "llama", "huggingface", "openrouter", "deepseek", "github_pat_token", "puter"]:
                if hasattr(st, "secrets") and provider in st.secrets:
                    secrets[provider] = st.secrets[provider]
        except:
            pass
        
        # Try loading from config file
        if self.config_path and os.path.exists(self.config_path):
            try:
                if self.config_path.endswith(".json"):
                    with open(self.config_path, 'r') as f:
                        config = json.load(f)
                elif self.config_path.endswith(".toml"):
                    with open(self.config_path, 'r') as f:
                        config = toml.load(f)
                else:
                    config = {}
                
                # Extract API keys
                for provider in ["openai", "claude", "gemini", "llama", "huggingface", "openrouter", "deepseek", "github_pat_token", "puter"]:
                    if provider in config:
                        secrets[provider] = config[provider]
            except Exception as e:
                print(f"Error loading config file: {str(e)}")
        
        # Try loading from environment variables
        for provider in ["openai", "claude", "gemini", "llama", "huggingface", "openrouter", "deepseek", "github_pat_token"]:
            env_var = f"{provider.upper()}_API_KEY"
            if env_var in os.environ:
                secrets[provider] = os.environ[env_var]
        
        # Puter is always available as it's free
        secrets["puter"] = "free"
        
        return secrets
    
    def get_api_key(self, provider: str) -> str:
        """
        Get API key for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            API key
        """
        # Check if key exists in secrets
        if provider in self.secrets and self.secrets[provider]:
            return self.secrets[provider]
        
        # Return default key (empty string if not set)
        return self.default_keys.get(provider, "")
    
    def get_secret(self, key: str) -> str:
        """
        Get secret by key name.
        
        Args:
            key: Secret key name
            
        Returns:
            Secret value
        """
        # Handle API keys with provider name in key
        for provider in ["OPENAI", "CLAUDE", "GEMINI", "LLAMA", "HUGGINGFACE", "OPENROUTER", "DEEPSEEK", "GITHUB_PAT_TOKEN"]:
            if key == f"{provider}_API_KEY" or key == provider:
                return self.get_api_key(provider.lower())
        
        # Try to get from Streamlit secrets
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
        
        # Try to get from environment variables
        if key in os.environ:
            return os.environ[key]
        
        # Return empty string if not found
        return ""
    
    def set_api_key(self, provider: str, api_key: str) -> None:
        """
        Set API key for a provider.
        
        Args:
            provider: Provider name
            api_key: API key
        """
        self.secrets[provider] = api_key
        
        # Update default keys
        self.default_keys[provider] = api_key
        
        # Save to config file if provided
        if self.config_path:
            self._save_secrets()
    
    def set_secret(self, key: str, value: str) -> None:
        """
        Set secret by key name.
        
        Args:
            key: Secret key name
            value: Secret value
        """
        # Handle API keys with provider name in key
        for provider in ["OPENAI", "CLAUDE", "GEMINI", "LLAMA", "HUGGINGFACE", "OPENROUTER", "DEEPSEEK", "GITHUB_PAT_TOKEN"]:
            if key == f"{provider}_API_KEY" or key == provider:
                self.set_api_key(provider.lower(), value)
                return
        
        # Store in secrets dictionary
        self.secrets[key] = value
        
        # Save to config file if provided
        if self.config_path:
            self._save_secrets()
    
    def _save_secrets(self) -> None:
        """
        Save secrets to config file.
        """
        if not self.config_path:
            return
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            if self.config_path.endswith(".json"):
                with open(self.config_path, 'w') as f:
                    json.dump(self.secrets, f, indent=2)
            elif self.config_path.endswith(".toml"):
                with open(self.config_path, 'w') as f:
                    toml.dump(self.secrets, f)
        except Exception as e:
            print(f"Error saving secrets: {str(e)}")
    
    def has_api_key(self, provider: str) -> bool:
        """
        Check if API key exists for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            True if API key exists, False otherwise
        """
        # Puter is always available as it's free
        if provider == "puter":
            return True
            
        return provider in self.secrets and bool(self.secrets[provider])
    
    def get_all_providers(self) -> List[str]:
        """
        Get list of all providers.
        
        Returns:
            List of provider names
        """
        return list(self.default_keys.keys())
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of providers with API keys.
        
        Returns:
            List of provider names with API keys
        """
        return [provider for provider in self.secrets if self.has_api_key(provider)]
    
    def get_available_models(self) -> Dict[str, bool]:
        """
        Get dictionary of available models based on API keys.
        
        Returns:
            Dictionary of provider to availability status
        """
        # Check if GitHub PAT token is available for GitHub Marketplace Models
        github_pat_available = self.has_api_key("github_pat_token")
        
        return {
            "openai": self.has_api_key("openai"),
            "claude": self.has_api_key("claude"),
            "gemini": self.has_api_key("gemini"),
            "llama": self.has_api_key("llama"),
            "huggingface": self.has_api_key("huggingface"),
            "openrouter": self.has_api_key("openrouter"),
            "deepseek": self.has_api_key("deepseek"),
            "github_pat_token": github_pat_available,  # For GitHub Marketplace Models
            "github_gpt4_mini": github_pat_available,  # GitHub GPT-4.1-mini
            "github_deepseek": github_pat_available,   # GitHub DeepSeek-V3
            "github_llama": github_pat_available,      # GitHub Llama 4 Scout
            "puter": True  # Puter is always available as it's free
        }
    
    def clear_api_key(self, provider: str) -> None:
        """
        Clear API key for a provider.
        
        Args:
            provider: Provider name
        """
        if provider in self.secrets:
            self.secrets[provider] = ""
            
            # Save to config file if provided
            if self.config_path:
                self._save_secrets()
    
    def clear_all_api_keys(self) -> None:
        """
        Clear all API keys.
        """
        for provider in self.secrets:
            if provider != "puter":  # Keep puter as it's always free
                self.secrets[provider] = ""
        
        # Save to config file if provided
        if self.config_path:
            self._save_secrets()
    
    def import_keys_from_env(self) -> Dict[str, bool]:
        """
        Import keys from environment variables.
        
        Returns:
            Dictionary of provider to success status
        """
        results = {}
        
        for provider in ["openai", "claude", "gemini", "llama", "huggingface", "openrouter", "deepseek", "github_pat_token"]:
            env_var = f"{provider.upper()}_API_KEY"
            if env_var in os.environ and os.environ[env_var]:
                self.secrets[provider] = os.environ[env_var]
                results[provider] = True
            else:
                results[provider] = False
        
        # Puter is always available
        results["puter"] = True
        self.secrets["puter"] = "free"
        
        # Save to config file if provided
        if self.config_path:
            self._save_secrets()
        
        return results
    
    def create_secrets_toml(self, directory_path: str) -> bool:
        """
        Create secrets.toml file in .streamlit directory.
        
        Args:
            directory_path: Directory path for .streamlit folder
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create .streamlit directory if it doesn't exist
            streamlit_dir = os.path.join(directory_path, ".streamlit")
            os.makedirs(streamlit_dir, exist_ok=True)
            
            # Create secrets.toml file
            secrets_path = os.path.join(streamlit_dir, "secrets.toml")
            
            # Prepare secrets data
            secrets_data = {}
            for provider in ["openai", "claude", "gemini", "llama", "huggingface", "openrouter", "deepseek", "github_pat_token"]:
                if self.has_api_key(provider):
                    secrets_data[f"{provider}_api_key"] = self.get_api_key(provider)
            
            # Write to file
            with open(secrets_path, 'w') as f:
                toml.dump(secrets_data, f)
            
            return True
        except Exception as e:
            print(f"Error creating secrets.toml: {str(e)}")
            return False
