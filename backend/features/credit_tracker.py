import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class CreditTracker:
    """
    Tracks API usage and credits for various AI providers.
    """
    
    def __init__(self, credits_file: str = "credits.json"):
        """
        Initialize credit tracker.
        
        Args:
            credits_file: Path to credits data file
        """
        self.credits_file = credits_file
        self.default_costs = {
            "openai": {
                "gpt-4": 0.06,
                "gpt-4-turbo": 0.01,
                "gpt-3.5-turbo": 0.002
            },
            "anthropic": {
                "claude-3-opus": 0.15,
                "claude-3-sonnet": 0.03,
                "claude-3-haiku": 0.00025
            },
            "google": {
                "gemini-pro": 0.0025,
                "gemini-ultra": 0.01
            }
        }
        
        # Initialize or load credits data
        if os.path.exists(credits_file):
            with open(credits_file, 'r') as f:
                self.credits_data = json.load(f)
        else:
            self.credits_data = {
                "providers": {
                    "openai": {"credits": 10.0, "used": 0.0},
                    "anthropic": {"credits": 10.0, "used": 0.0},
                    "google": {"credits": 10.0, "used": 0.0},
                    "meta": {"credits": 10.0, "used": 0.0},
                    "huggingface": {"credits": 10.0, "used": 0.0},
                    "openrouter": {"credits": 10.0, "used": 0.0},
                    "deepseek": {"credits": 10.0, "used": 0.0}
                },
                "usage_history": [],
                "last_sync": datetime.now().isoformat()
            }
            self._save_credits_data()
    
    def _save_credits_data(self):
        """Save credits data to file."""
        with open(self.credits_file, 'w') as f:
            json.dump(self.credits_data, f, indent=2)
    
    def track_usage(self, 
                   provider: str, 
                   model: str, 
                   input_tokens: int, 
                   output_tokens: int,
                   custom_cost: Optional[float] = None,
                   prompt_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        Track API usage and update credits.
        
        Args:
            provider: Provider name
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            custom_cost: Optional custom cost per 1000 tokens
            prompt_tokens: Optional prompt tokens (used instead of input_tokens if provided)
            
        Returns:
            Usage information
        """
        # Use prompt_tokens instead of input_tokens if provided
        if prompt_tokens is not None:
            input_tokens = prompt_tokens
            
        # Ensure provider exists
        if provider not in self.credits_data["providers"]:
            self.credits_data["providers"][provider] = {
                "credits": 10.0,  # Default starting credits
                "used": 0.0
            }
        
        # Get cost per token
        cost_info = self.get_cost_per_token(provider, model)
        
        # Calculate cost
        if custom_cost is not None:
            cost = (input_tokens + output_tokens) * (custom_cost / 1000)
        else:
            cost = (input_tokens * cost_info["input_cost_per_token"]) + \
                   (output_tokens * cost_info["output_cost_per_token"])
        
        # Update provider usage
        provider_data = self.credits_data["providers"][provider]
        provider_data["used"] += cost
        
        # Record usage
        usage_record = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }
        
        self.credits_data["usage_history"].append(usage_record)
        
        # Save updated data
        self._save_credits_data()
        
        return usage_record
    
    def get_credits(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get credits information.
        
        Args:
            provider: Optional provider filter
            
        Returns:
            Credits information
        """
        if provider is not None:
            if provider in self.credits_data["providers"]:
                provider_data = self.credits_data["providers"][provider]
                return {
                    "provider": provider,
                    "credits": provider_data["credits"],
                    "used": provider_data["used"],
                    "remaining": provider_data["credits"] - provider_data["used"]
                }
            else:
                return {
                    "provider": provider,
                    "credits": 0.0,
                    "used": 0.0,
                    "remaining": 0.0
                }
        else:
            result = {
                "total_credits": 0.0,
                "total_used": 0.0,
                "total_remaining": 0.0,
                "providers": {}
            }
            
            for provider_name, provider_data in self.credits_data["providers"].items():
                credits = provider_data["credits"]
                used = provider_data["used"]
                remaining = credits - used
                
                result["providers"][provider_name] = {
                    "credits": credits,
                    "used": used,
                    "remaining": remaining
                }
                
                result["total_credits"] += credits
                result["total_used"] += used
                result["total_remaining"] += remaining
            
            return result
    
    def add_credits(self, provider: str, amount: float) -> Dict[str, Any]:
        """
        Add credits to a provider.
        
        Args:
            provider: Provider name
            amount: Amount to add
            
        Returns:
            Updated provider data
        """
        if provider not in self.credits_data["providers"]:
            self.credits_data["providers"][provider] = {
                "credits": 0.0,
                "used": 0.0
            }
        
        self.credits_data["providers"][provider]["credits"] += amount
        self._save_credits_data()
        
        return self.get_credits(provider)
    
    def reset_usage(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Reset usage for a provider or all providers.
        
        Args:
            provider: Optional provider name (None for all)
            
        Returns:
            Updated credits information
        """
        if provider is not None:
            if provider in self.credits_data["providers"]:
                self.credits_data["providers"][provider]["used"] = 0.0
                
                # Filter out usage history for this provider
                self.credits_data["usage_history"] = [
                    record for record in self.credits_data["usage_history"]
                    if record["provider"] != provider
                ]
        else:
            # Reset all providers
            for provider_data in self.credits_data["providers"].values():
                provider_data["used"] = 0.0
            
            # Clear all usage history
            self.credits_data["usage_history"] = []
        
        self._save_credits_data()
        return self.get_credits(provider)
    
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
