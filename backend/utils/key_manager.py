import os
import json
import base64
import hashlib
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import streamlit as st

class KeyManager:
    """
    Secure API key management system for the Multi-AI application.
    Handles key retrieval, encryption, rotation, and validation.
    """
    
    def __init__(self):
        """Initialize the KeyManager with encryption capabilities."""
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self.last_rotation_check = datetime.now()
        self.rotation_check_interval = timedelta(hours=24)
        
    def _get_or_create_encryption_key(self):
        """Get existing encryption key or create a new one."""
        # Check if key exists in environment
        env_key = os.getenv("ENCRYPTION_KEY")
        if env_key:
            try:
                # Validate the key is proper Fernet format
                return env_key.encode() if isinstance(env_key, str) else env_key
            except Exception:
                pass
                
        # Try to get from Streamlit secrets
        try:
            if "encryption" in st.secrets and "key" in st.secrets.encryption:
                key = st.secrets.encryption.key
                if key and len(key) >= 32:
                    # Convert to proper Fernet key format if needed
                    key_bytes = key.encode() if isinstance(key, str) else key
                    return base64.urlsafe_b64encode(hashlib.sha256(key_bytes).digest())
        except Exception:
            pass
            
        # Generate a new key if none exists
        return base64.urlsafe_b64encode(os.urandom(32))
    
    def get_api_key(self, service_name):
        """
        Get API key for the specified service.
        
        Args:
            service_name: Name of the service (e.g., 'openai', 'gemini')
            
        Returns:
            str: The API key if found, None otherwise
        """
        # Check if rotation is needed
        self._check_rotation_schedule()
        
        # First try to get from Streamlit secrets (most secure)
        try:
            if "api_keys" in st.secrets and service_name in st.secrets.api_keys:
                return st.secrets.api_keys[service_name]
        except Exception:
            pass
            
        # Then try environment variables
        env_var_name = f"{service_name.upper()}_API_KEY"
        api_key = os.getenv(env_var_name)
        if api_key:
            return api_key
            
        # Finally check .env file directly as fallback
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv(env_var_name)
            if api_key:
                return api_key
        except Exception:
            pass
            
        return None
    
    def encrypt_key(self, api_key):
        """
        Encrypt an API key for secure storage.
        
        Args:
            api_key: The API key to encrypt
            
        Returns:
            str: Encrypted API key
        """
        if not api_key:
            return None
            
        try:
            encrypted = self.cipher.encrypt(api_key.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            print(f"Error encrypting API key: {e}")
            return None
    
    def decrypt_key(self, encrypted_key):
        """
        Decrypt an encrypted API key.
        
        Args:
            encrypted_key: The encrypted API key
            
        Returns:
            str: Decrypted API key
        """
        if not encrypted_key:
            return None
            
        try:
            decoded = base64.urlsafe_b64decode(encrypted_key)
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            print(f"Error decrypting API key: {e}")
            return None
    
    def validate_key(self, service_name, api_key):
        """
        Validate if an API key is properly formatted for the given service.
        
        Args:
            service_name: Name of the service
            api_key: The API key to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not api_key:
            return False
            
        # Service-specific validation patterns
        validation_patterns = {
            'openai': lambda k: k.startswith(('sk-', 'sk-org-')),
            'gemini': lambda k: len(k) > 20,  # Google API keys are typically long
            'claude': lambda k: k.startswith('sk-ant-'),
            'openrouter': lambda k: k.startswith('sk-or-'),
            'huggingface': lambda k: k.startswith('hf_'),
            'llama': lambda k: len(k) == 36 and k.count('-') == 4,  # UUID format
            'botpress': lambda k: k.startswith('wkspace_')
        }
        
        validator = validation_patterns.get(service_name.lower(), lambda k: len(k) > 8)
        return validator(api_key)
    
    def _check_rotation_schedule(self):
        """Check if key rotation is needed based on configured schedule."""
        now = datetime.now()
        
        # Only check once per day to avoid performance impact
        if now - self.last_rotation_check < self.rotation_check_interval:
            return
            
        self.last_rotation_check = now
        
        # Check if key rotation is enabled
        try:
            if "security" in st.secrets and st.secrets.security.get("enable_key_rotation", False):
                rotation_days = st.secrets.security.get("key_rotation_interval_days", 30)
                self._handle_key_rotation(rotation_days)
        except Exception as e:
            print(f"Error checking key rotation schedule: {e}")
    
    def _handle_key_rotation(self, rotation_days):
        """
        Handle key rotation logic if needed.
        This is a placeholder for actual key rotation implementation.
        In a production system, this would integrate with a key management service.
        
        Args:
            rotation_days: Number of days between rotations
        """
        # This would be implemented with actual key rotation logic
        # For example, calling API provider's key rotation endpoints
        # or notifying administrators that rotation is needed
        pass
    
    def log_key_usage(self, service_name, request_type, tokens_used=0):
        """
        Log API key usage for monitoring and rate limiting.
        
        Args:
            service_name: Name of the service
            request_type: Type of request made
            tokens_used: Number of tokens used in the request
        """
        try:
            if "security" in st.secrets and st.secrets.security.get("enable_request_logging", False):
                # In a production system, this would log to a secure database
                # For now, we'll just print to console in development
                print(f"API Usage: {service_name} - {request_type} - {tokens_used} tokens")
        except Exception:
            pass
