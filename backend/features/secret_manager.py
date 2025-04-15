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
        
        # Default API keys (for development/testing only)
        self.default_keys = {
            "openai": "",
            "claude": "",
            "gemini": "",
            "llama": "",
            "huggingface": "",
            "openrouter": "",
            "deepseek": ""
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
            for provider in ["openai", "claude", "gemini", "llama", "huggingface", "openrouter", "deepseek"]:
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
                for provider in ["openai", "claude", "gemini", "llama", "huggingface", "openrouter", "deepseek"]:
                    if provider in config:
                        secrets[provider] = config[provider]
            except Exception as e:
                print(f"Error loading config file: {str(e)}")
        
        # Try loading from environment variables
        for provider in ["openai", "claude", "gemini", "llama", "huggingface", "openrouter", "deepseek"]:
            env_var = f"{provider.upper()}_API_KEY"
            if env_var in os.environ:
                secrets[provider] = os.environ[env_var]
        
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
        
        for provider in ["openai", "claude", "gemini", "llama", "huggingface", "openrouter", "deepseek"]:
            env_var = f"{provider.upper()}_API_KEY"
            if env_var in os.environ and os.environ[env_var]:
                self.secrets[provider] = os.environ[env_var]
                results[provider] = True
            else:
                results[provider] = False
        
        # Save to config file if provided
        if self.config_path:
            self._save_secrets()
        
        return results
