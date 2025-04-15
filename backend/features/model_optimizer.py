import os
import json
from typing import Dict, Any, Optional, List

class ModelOptimizer:
    """
    Optimizes model selection and parameters based on task type and user preferences.
    """
    
    def __init__(self):
        """
        Initialize the model optimizer.
        """
        self.task_types = {
            "general_conversation": {
                "description": "General conversation and chat",
                "recommended_models": {
                    "openai": ["gpt-3.5-turbo"],
                    "claude": ["claude-3-haiku"],
                    "gemini": ["gemini-pro"],
                    "llama": ["llama-3-8b"],
                    "deepseek": ["deepseek-chat"]
                },
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 800
                }
            },
            "creative_writing": {
                "description": "Creative writing, storytelling, and content generation",
                "recommended_models": {
                    "openai": ["gpt-4"],
                    "claude": ["claude-3-opus"],
                    "gemini": ["gemini-pro"],
                    "llama": ["llama-3-70b"],
                    "deepseek": ["deepseek-chat"]
                },
                "parameters": {
                    "temperature": 0.8,
                    "max_tokens": 1500
                }
            },
            "code_generation": {
                "description": "Code generation and programming assistance",
                "recommended_models": {
                    "openai": ["gpt-4"],
                    "claude": ["claude-3-opus"],
                    "gemini": ["gemini-pro"],
                    "llama": ["llama-3-70b"],
                    "deepseek": ["deepseek-coder"]
                },
                "parameters": {
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            },
            "data_analysis": {
                "description": "Data analysis and interpretation",
                "recommended_models": {
                    "openai": ["gpt-4"],
                    "claude": ["claude-3-opus"],
                    "gemini": ["gemini-pro"],
                    "llama": ["llama-3-70b"],
                    "deepseek": ["deepseek-chat"]
                },
                "parameters": {
                    "temperature": 0.2,
                    "max_tokens": 1500
                }
            },
            "summarization": {
                "description": "Text summarization",
                "recommended_models": {
                    "openai": ["gpt-3.5-turbo"],
                    "claude": ["claude-3-haiku"],
                    "gemini": ["gemini-pro"],
                    "llama": ["llama-3-8b"],
                    "deepseek": ["deepseek-chat"]
                },
                "parameters": {
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
            },
            "translation": {
                "description": "Language translation",
                "recommended_models": {
                    "openai": ["gpt-4"],
                    "claude": ["claude-3-sonnet"],
                    "gemini": ["gemini-pro"],
                    "llama": ["llama-3-70b"],
                    "deepseek": ["deepseek-chat"]
                },
                "parameters": {
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
            },
            "image_analysis": {
                "description": "Image analysis and description",
                "recommended_models": {
                    "openai": ["gpt-4-turbo"],
                    "claude": ["claude-3-opus"],
                    "gemini": ["gemini-pro-vision"],
                    "deepseek": ["deepseek-v2"]
                },
                "parameters": {
                    "temperature": 0.4,
                    "max_tokens": 1000
                }
            }
        }
        
        self.optimization_profiles = {
            "balanced": {
                "description": "Balanced performance and cost",
                "priority": ["quality", "cost"],
                "temperature_adjustment": 0.0,
                "max_tokens_adjustment": 0.0
            },
            "economy": {
                "description": "Optimize for lower cost",
                "priority": ["cost", "speed", "quality"],
                "temperature_adjustment": 0.1,
                "max_tokens_adjustment": -0.2
            },
            "performance": {
                "description": "Optimize for best quality",
                "priority": ["quality", "speed", "cost"],
                "temperature_adjustment": -0.1,
                "max_tokens_adjustment": 0.2
            },
            "speed": {
                "description": "Optimize for faster responses",
                "priority": ["speed", "cost", "quality"],
                "temperature_adjustment": 0.2,
                "max_tokens_adjustment": -0.3
            }
        }
    
    def detect_task_type(self, prompt: str) -> str:
        """
        Detect the most likely task type based on the prompt.
        
        Args:
            prompt: User prompt
            
        Returns:
            Detected task type
        """
        # Simple keyword-based detection
        prompt_lower = prompt.lower()
        
        # Check for code-related keywords
        if any(keyword in prompt_lower for keyword in ["code", "function", "program", "algorithm", "debug"]):
            return "code_generation"
        
        # Check for creative writing keywords
        if any(keyword in prompt_lower for keyword in ["write", "story", "creative", "poem", "novel", "fiction"]):
            return "creative_writing"
        
        # Check for data analysis keywords
        if any(keyword in prompt_lower for keyword in ["data", "analyze", "statistics", "graph", "chart", "trend"]):
            return "data_analysis"
        
        # Check for summarization keywords
        if any(keyword in prompt_lower for keyword in ["summarize", "summary", "tldr", "brief", "condense"]):
            return "summarization"
        
        # Check for translation keywords
        if any(keyword in prompt_lower for keyword in ["translate", "translation", "language", "spanish", "french", "german", "chinese", "japanese"]):
            return "translation"
        
        # Check for image analysis keywords
        if any(keyword in prompt_lower for keyword in ["image", "picture", "photo", "describe", "what's in this"]):
            return "image_analysis"
        
        # Default to general conversation
        return "general_conversation"
    
    def get_recommended_models(self, 
                              task_type: str, 
                              available_providers: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """
        Get recommended models for a specific task type.
        
        Args:
            task_type: Task type
            available_providers: Optional list of available providers
            
        Returns:
            Dictionary of provider to list of recommended models
        """
        if task_type not in self.task_types:
            task_type = "general_conversation"
        
        recommendations = self.task_types[task_type]["recommended_models"]
        
        if available_providers:
            filtered_recommendations = {}
            for provider in available_providers:
                if provider in recommendations:
                    filtered_recommendations[provider] = recommendations[provider]
            return filtered_recommendations
        
        return recommendations
    
    def get_optimal_parameters(self, 
                              task_type: str, 
                              profile: str = "balanced") -> Dict[str, Any]:
        """
        Get optimal parameters for a specific task type and optimization profile.
        
        Args:
            task_type: Task type
            profile: Optimization profile
            
        Returns:
            Dictionary of parameter name to value
        """
        if task_type not in self.task_types:
            task_type = "general_conversation"
        
        if profile not in self.optimization_profiles:
            profile = "balanced"
        
        # Get base parameters for task type
        base_params = self.task_types[task_type]["parameters"].copy()
        
        # Apply adjustments from profile
        profile_data = self.optimization_profiles[profile]
        
        # Adjust temperature
        base_params["temperature"] += profile_data["temperature_adjustment"]
        base_params["temperature"] = max(0.0, min(1.0, base_params["temperature"]))
        
        # Adjust max tokens
        adjustment_factor = 1.0 + profile_data["max_tokens_adjustment"]
        base_params["max_tokens"] = int(base_params["max_tokens"] * adjustment_factor)
        base_params["max_tokens"] = max(100, base_params["max_tokens"])
        
        return base_params
    
    def optimize_for_cost(self, 
                         task_type: str, 
                         available_providers: List[str],
                         credit_tracker) -> Dict[str, Any]:
        """
        Optimize model selection for cost.
        
        Args:
            task_type: Task type
            available_providers: List of available providers
            credit_tracker: Credit tracker instance
            
        Returns:
            Dictionary with optimized model and parameters
        """
        if task_type not in self.task_types:
            task_type = "general_conversation"
        
        # Get recommended models for task
        recommendations = self.get_recommended_models(task_type, available_providers)
        
        # Find lowest cost model
        lowest_cost = float('inf')
        best_provider = None
        best_model = None
        
        for provider, models in recommendations.items():
            for model in models:
                # Get cost per token
                cost_info = credit_tracker.get_cost_per_token(provider, model)
                cost_per_1k = cost_info["cost_per_1k_tokens"]
                
                if cost_per_1k < lowest_cost:
                    lowest_cost = cost_per_1k
                    best_provider = provider
                    best_model = model
        
        # If no model found, use default
        if not best_provider:
            best_provider = "openai"
            best_model = "gpt-3.5-turbo"
        
        # Get parameters optimized for economy
        params = self.get_optimal_parameters(task_type, "economy")
        
        return {
            "provider": best_provider,
            "model": best_model,
            "parameters": params
        }
    
    def optimize_for_quality(self, 
                            task_type: str, 
                            available_providers: List[str]) -> Dict[str, Any]:
        """
        Optimize model selection for quality.
        
        Args:
            task_type: Task type
            available_providers: List of available providers
            
        Returns:
            Dictionary with optimized model and parameters
        """
        if task_type not in self.task_types:
            task_type = "general_conversation"
        
        # Quality ranking of providers (subjective)
        quality_ranking = {
            "openai": {"gpt-4": 9, "gpt-4-turbo": 8.5, "gpt-3.5-turbo": 7},
            "claude": {"claude-3-opus": 9, "claude-3-sonnet": 8, "claude-3-haiku": 7},
            "gemini": {"gemini-pro": 7.5, "gemini-pro-vision": 8},
            "llama": {"llama-3-70b": 8, "llama-3-8b": 6.5},
            "deepseek": {"deepseek-chat": 7, "deepseek-coder": 8, "deepseek-v2": 7.5}
        }
        
        # Get recommended models for task
        recommendations = self.get_recommended_models(task_type, available_providers)
        
        # Find highest quality model
        highest_quality = -1
        best_provider = None
        best_model = None
        
        for provider, models in recommendations.items():
            if provider not in quality_ranking:
                continue
                
            for model in models:
                if model not in quality_ranking[provider]:
                    continue
                    
                quality_score = quality_ranking[provider][model]
                
                if quality_score > highest_quality:
                    highest_quality = quality_score
                    best_provider = provider
                    best_model = model
        
        # If no model found, use default
        if not best_provider:
            best_provider = "openai"
            best_model = "gpt-4"
        
        # Get parameters optimized for performance
        params = self.get_optimal_parameters(task_type, "performance")
        
        return {
            "provider": best_provider,
            "model": best_model,
            "parameters": params
        }
    
    def optimize_for_speed(self, 
                          task_type: str, 
                          available_providers: List[str]) -> Dict[str, Any]:
        """
        Optimize model selection for speed.
        
        Args:
            task_type: Task type
            available_providers: List of available providers
            
        Returns:
            Dictionary with optimized model and parameters
        """
        if task_type not in self.task_types:
            task_type = "general_conversation"
        
        # Speed ranking of providers (subjective)
        speed_ranking = {
            "openai": {"gpt-4": 6, "gpt-4-turbo": 7, "gpt-3.5-turbo": 9},
            "claude": {"claude-3-opus": 6, "claude-3-sonnet": 7, "claude-3-haiku": 9},
            "gemini": {"gemini-pro": 8, "gemini-pro-vision": 7},
            "llama": {"llama-3-70b": 6, "llama-3-8b": 8},
            "deepseek": {"deepseek-chat": 8, "deepseek-coder": 7, "deepseek-v2": 6}
        }
        
        # Get recommended models for task
        recommendations = self.get_recommended_models(task_type, available_providers)
        
        # Find fastest model
        highest_speed = -1
        best_provider = None
        best_model = None
        
        for provider, models in recommendations.items():
            if provider not in speed_ranking:
                continue
                
            for model in models:
                if model not in speed_ranking[provider]:
                    continue
                    
                speed_score = speed_ranking[provider][model]
                
                if speed_score > highest_speed:
                    highest_speed = speed_score
                    best_provider = provider
                    best_model = model
        
        # If no model found, use default
        if not best_provider:
            best_provider = "openai"
            best_model = "gpt-3.5-turbo"
        
        # Get parameters optimized for speed
        params = self.get_optimal_parameters(task_type, "speed")
        
        return {
            "provider": best_provider,
            "model": best_model,
            "parameters": params
        }
    
    def optimize_model_selection(self, 
                                prompt: str, 
                                available_providers: List[str],
                                optimization_goal: str = "balanced",
                                credit_tracker = None) -> Dict[str, Any]:
        """
        Optimize model selection based on prompt, available providers, and optimization goal.
        
        Args:
            prompt: User prompt
            available_providers: List of available providers
            optimization_goal: Optimization goal (balanced, cost, quality, speed)
            credit_tracker: Optional credit tracker for cost optimization
            
        Returns:
            Dictionary with optimized model and parameters
        """
        # Detect task type
        task_type = self.detect_task_type(prompt)
        
        # Optimize based on goal
        if optimization_goal == "cost":
            if credit_tracker:
                return self.optimize_for_cost(task_type, available_providers, credit_tracker)
            else:
                optimization_goal = "balanced"
        
        if optimization_goal == "quality":
            return self.optimize_for_quality(task_type, available_providers)
        
        if optimization_goal == "speed":
            return self.optimize_for_speed(task_type, available_providers)
        
        # Default: balanced optimization
        # Get recommended models for task
        recommendations = self.get_recommended_models(task_type, available_providers)
        
        # Choose first available provider and its first recommended model
        best_provider = None
        best_model = None
        
        for provider, models in recommendations.items():
            if models:
                best_provider = provider
                best_model = models[0]
                break
        
        # If no model found, use default
        if not best_provider:
            best_provider = "openai"
            best_model = "gpt-3.5-turbo"
        
        # Get balanced parameters
        params = self.get_optimal_parameters(task_type, "balanced")
        
        return {
            "provider": best_provider,
            "model": best_model,
            "parameters": params,
            "task_type": task_type
        }
