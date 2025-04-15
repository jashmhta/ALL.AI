import os
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

class CreditTracker:
    """
    Tracks API usage and remaining credits for each AI model.
    """
    
    def __init__(self, storage_path: str = "credits_data.json"):
        """
        Initialize the credit tracker.
        
        Args:
            storage_path: Path to store credit data
        """
        self.storage_path = storage_path
        self.credits_data = self._load_credits_data()
        
        # Default credit costs per 1000 tokens (input + output)
        self.default_costs = {
            "openai": {
                "gpt-4": 0.03,
                "gpt-4-turbo": 0.01,
                "gpt-3.5-turbo": 0.0015
            },
            "claude": {
                "claude-3-opus": 0.015,
                "claude-3-sonnet": 0.008,
                "claude-3-haiku": 0.0025
            },
            "gemini": {
                "gemini-pro": 0.0025,
                "gemini-pro-vision": 0.0035
            },
            "llama": {
                "llama-3-70b": 0.0015,
                "llama-3-8b": 0.0005
            },
            "huggingface": {
                "mistral-7b": 0.0005,
                "falcon-40b": 0.0010,
                "llama-2-13b": 0.0008
            },
            "openrouter": {
                "openai/gpt-4-turbo": 0.01,
                "anthropic/claude-3-opus": 0.015,
                "meta-llama/llama-3-70b-instruct": 0.0015,
                "google/gemini-pro": 0.0025,
                "mistralai/mistral-large": 0.0008
            },
            "deepseek": {
                "deepseek-chat": 0.0010,
                "deepseek-coder": 0.0015,
                "deepseek-v2": 0.0020
            }
        }
    
    def _load_credits_data(self) -> Dict[str, Any]:
        """
        Load credits data from storage.
        
        Returns:
            Credits data dictionary
        """
        if os.path.exists(self.storage_path) and self.storage_path != ":memory:":
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading credits data: {str(e)}")
                return self._initialize_credits_data()
        else:
            return self._initialize_credits_data()
    
    def _initialize_credits_data(self) -> Dict[str, Any]:
        """
        Initialize credits data structure.
        
        Returns:
            New credits data dictionary
        """
        return {
            "providers": {
                "openai": {
                    "total_credits": 10.0,
                    "used_credits": 0.0,
                    "last_updated": datetime.now().isoformat()
                },
                "claude": {
                    "total_credits": 10.0,
                    "used_credits": 0.0,
                    "last_updated": datetime.now().isoformat()
                },
                "gemini": {
                    "total_credits": 10.0,
                    "used_credits": 0.0,
                    "last_updated": datetime.now().isoformat()
                },
                "llama": {
                    "total_credits": 10.0,
                    "used_credits": 0.0,
                    "last_updated": datetime.now().isoformat()
                },
                "huggingface": {
                    "total_credits": 10.0,
                    "used_credits": 0.0,
                    "last_updated": datetime.now().isoformat()
                },
                "openrouter": {
                    "total_credits": 10.0,
                    "used_credits": 0.0,
                    "last_updated": datetime.now().isoformat()
                },
                "deepseek": {
                    "total_credits": 10.0,
                    "used_credits": 0.0,
                    "last_updated": datetime.now().isoformat()
                }
            },
            "usage_history": [],
            "last_sync": datetime.now().isoformat()
        }
    
    def _save_credits_data(self) -> None:
        """
        Save credits data to storage.
        """
        if self.storage_path == ":memory:":
            return
            
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.credits_data, f, indent=2)
        except Exception as e:
            print(f"Error saving credits data: {str(e)}")
    
    def get_remaining_credits(self, provider: str) -> float:
        """
        Get remaining credits for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Remaining credits
        """
        if provider not in self.credits_data["providers"]:
            return 0.0
        
        provider_data = self.credits_data["providers"][provider]
        return provider_data["total_credits"] - provider_data["used_credits"]
    
    def get_all_remaining_credits(self) -> Dict[str, float]:
        """
        Get remaining credits for all providers.
        
        Returns:
            Dictionary of provider names to remaining credits
        """
        result = {}
        for provider in self.credits_data["providers"]:
            result[provider] = self.get_remaining_credits(provider)
        return result
    
    def track_usage(self, 
                   provider: str, 
                   model: str, 
                   input_tokens: int, 
                   output_tokens: int,
                   custom_cost: Optional[float] = None) -> Dict[str, Any]:
        """
        Track API usage and update credits.
        
        Args:
            provider: Provider name
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            custom_cost: Optional custom cost per 1000 tokens
            
        Returns:
            Usage information
        """
        # Ensure provider exists
        if provider not in self.credits_data["providers"]:
            self.credits_data["providers"][provider] = {
                "total_credits": 10.0,
                "used_credits": 0.0,
                "last_updated": datetime.now().isoformat()
            }
        
        # Calculate cost
        cost_per_1k = custom_cost
        if cost_per_1k is None:
            if provider in self.default_costs and model in self.default_costs[provider]:
                cost_per_1k = self.default_costs[provider][model]
            else:
                # Default fallback cost
                cost_per_1k = 0.001
        
        # Calculate total cost
        input_cost = (input_tokens / 1000) * cost_per_1k
        output_cost = (output_tokens / 1000) * cost_per_1k * 2  # Output typically costs more
        total_cost = input_cost + output_cost
        
        # Update provider data
        provider_data = self.credits_data["providers"][provider]
        provider_data["used_credits"] += total_cost
        provider_data["last_updated"] = datetime.now().isoformat()
        
        # Create usage record
        usage_record = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": total_cost
        }
        
        # Add to history
        self.credits_data["usage_history"].append(usage_record)
        
        # Save data
        self._save_credits_data()
        
        return usage_record
    
    def add_credits(self, provider: str, amount: float) -> Dict[str, Any]:
        """
        Add credits to a provider.
        
        Args:
            provider: Provider name
            amount: Amount to add
            
        Returns:
            Updated provider data
        """
        # Ensure provider exists
        if provider not in self.credits_data["providers"]:
            self.credits_data["providers"][provider] = {
                "total_credits": amount,
                "used_credits": 0.0,
                "last_updated": datetime.now().isoformat()
            }
        else:
            # Update provider data
            provider_data = self.credits_data["providers"][provider]
            provider_data["total_credits"] += amount
            provider_data["last_updated"] = datetime.now().isoformat()
        
        # Save data
        self._save_credits_data()
        
        return self.credits_data["providers"][provider]
    
    def reset_credits(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Reset credits for a provider or all providers.
        
        Args:
            provider: Provider name, or None for all providers
            
        Returns:
            Updated credits data
        """
        if provider is None:
            # Reset all providers
            for provider_name in self.credits_data["providers"]:
                provider_data = self.credits_data["providers"][provider_name]
                provider_data["used_credits"] = 0.0
                provider_data["last_updated"] = datetime.now().isoformat()
        else:
            # Reset specific provider
            if provider in self.credits_data["providers"]:
                provider_data = self.credits_data["providers"][provider]
                provider_data["used_credits"] = 0.0
                provider_data["last_updated"] = datetime.now().isoformat()
        
        # Save data
        self._save_credits_data()
        
        return self.credits_data
    
    def get_usage_history(self, 
                         provider: Optional[str] = None, 
                         start_time: Optional[str] = None,
                         end_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get usage history, optionally filtered.
        
        Args:
            provider: Optional provider filter
            start_time: Optional start time filter (ISO format)
            end_time: Optional end time filter (ISO format)
            
        Returns:
            List of usage records
        """
        history = self.credits_data["usage_history"]
        
        # Apply provider filter
        if provider is not None:
            history = [record for record in history if record["provider"] == provider]
        
        # Apply time filters
        if start_time is not None:
            start_dt = datetime.fromisoformat(start_time)
            history = [record for record in history if datetime.fromisoformat(record["timestamp"]) >= start_dt]
        
        if end_time is not None:
            end_dt = datetime.fromisoformat(end_time)
            history = [record for record in history if datetime.fromisoformat(record["timestamp"]) <= end_dt]
        
        return history
    
    def get_usage_summary(self, 
                         provider: Optional[str] = None,
                         start_time: Optional[str] = None,
                         end_time: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage summary, optionally filtered.
        
        Args:
            provider: Optional provider filter
            start_time: Optional start time filter (ISO format)
            end_time: Optional end time filter (ISO format)
            
        Returns:
            Usage summary
        """
        # Get filtered history
        history = self.get_usage_history(provider, start_time, end_time)
        
        # Initialize summary
        summary = {
            "total_cost": 0.0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "request_count": len(history),
            "providers": {},
            "models": {}
        }
        
        # Calculate totals
        for record in history:
            summary["total_cost"] += record["cost"]
            summary["total_input_tokens"] += record["input_tokens"]
            summary["total_output_tokens"] += record["output_tokens"]
            
            # Provider breakdown
            provider_name = record["provider"]
            if provider_name not in summary["providers"]:
                summary["providers"][provider_name] = {
                    "cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "request_count": 0
                }
            
            provider_summary = summary["providers"][provider_name]
            provider_summary["cost"] += record["cost"]
            provider_summary["input_tokens"] += record["input_tokens"]
            provider_summary["output_tokens"] += record["output_tokens"]
            provider_summary["request_count"] += 1
            
            # Model breakdown
            model_name = record["model"]
            if model_name not in summary["models"]:
                summary["models"][model_name] = {
                    "cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "request_count": 0
                }
            
            model_summary = summary["models"][model_name]
            model_summary["cost"] += record["cost"]
            model_summary["input_tokens"] += record["input_tokens"]
            model_summary["output_tokens"] += record["output_tokens"]
            model_summary["request_count"] += 1
        
        return summary
    
    def sync_with_provider_api(self, provider: str) -> Dict[str, Any]:
        """
        Sync credit data with provider API (placeholder for future implementation).
        
        Args:
            provider: Provider name
            
        Returns:
            Updated provider data
        """
        # This would be implemented to connect to each provider's API
        # and get actual credit/usage information
        
        # For now, just update the last sync time
        self.credits_data["last_sync"] = datetime.now().isoformat()
        self._save_credits_data()
        
        return self.credits_data["providers"].get(provider, {})
    
    def get_cost_per_token(self, provider: str, model: str) -> Dict[str, float]:
        """
        Get cost per token for a specific model.
        
        Args:
            provider: Provider name
            model: Model name
            
        Returns:
            Dictionary with input and output costs per token
        """
        cost_per_1k = 0.001  # Default fallback
        
        if provider in self.default_costs and model in self.default_costs[provider]:
            cost_per_1k = self.default_costs[provider][model]
        
        return {
            "input_cost_per_token": cost_per_1k / 1000,
            "output_cost_per_token": (cost_per_1k * 2) / 1000,  # Output typically costs more
            "cost_per_1k_tokens": cost_per_1k
        }
