import os
import asyncio
from typing import Dict, Any, Optional, List
import json
import numpy as np
from datetime import datetime

class ModelOptimizer:
    """
    Optimizes model selection based on feedback and performance metrics.
    Provides recommendations for which models to use for different query types.
    """
    
    def __init__(self, feedback_manager):
        """
        Initialize the model optimizer.
        
        Args:
            feedback_manager: FeedbackManager instance for accessing feedback data
        """
        self.feedback_manager = feedback_manager
        self.fallback_success = {}  # Track fallback success rates
        self.query_categories = {
            "overall_best": [],
            "creative": [],
            "factual": [],
            "technical": [],
            "mathematical": [],
            "analytical": [],
            "instructional": []
        }
        self.model_performance = {}  # Track model performance for different queries
        
        # Initialize model performance data
        self._initialize_model_performance()
    
    def _initialize_model_performance(self):
        """Initialize model performance data with default values."""
        # This would typically be loaded from a database or file
        # For now, we'll use some reasonable defaults
        
        # Default performance scores (0-100) for different query categories
        default_performance = {
            "gpt": {
                "overall_best": 90,
                "creative": 95,
                "factual": 85,
                "technical": 88,
                "mathematical": 80,
                "analytical": 92,
                "instructional": 90
            },
            "claude": {
                "overall_best": 88,
                "creative": 90,
                "factual": 92,
                "technical": 85,
                "mathematical": 82,
                "analytical": 95,
                "instructional": 88
            },
            "gemini": {
                "overall_best": 85,
                "creative": 88,
                "factual": 90,
                "technical": 92,
                "mathematical": 90,
                "analytical": 85,
                "instructional": 85
            },
            "llama": {
                "overall_best": 82,
                "creative": 85,
                "factual": 80,
                "technical": 90,
                "mathematical": 85,
                "analytical": 80,
                "instructional": 82
            },
            "openrouter": {
                "overall_best": 86,
                "creative": 88,
                "factual": 85,
                "technical": 86,
                "mathematical": 84,
                "analytical": 88,
                "instructional": 86
            },
            "huggingface": {
                "overall_best": 80,
                "creative": 82,
                "factual": 78,
                "technical": 85,
                "mathematical": 80,
                "analytical": 78,
                "instructional": 80
            }
        }
        
        # Initialize model performance with default values
        self.model_performance = default_performance
        
        # Update query categories based on model performance
        self._update_query_categories()
    
    def _update_query_categories(self):
        """Update query categories based on model performance."""
        # Clear existing categories
        for category in self.query_categories:
            self.query_categories[category] = []
        
        # Get all models
        models = list(self.model_performance.keys())
        
        # For each category, sort models by performance and add to category
        for category in self.query_categories:
            # Sort models by performance in this category
            sorted_models = sorted(
                models,
                key=lambda m: self.model_performance.get(m, {}).get(category, 0),
                reverse=True
            )
            
            # Add top models to category
            for model in sorted_models[:3]:  # Top 3 models
                score = self.model_performance.get(model, {}).get(category, 0)
                self.query_categories[category].append({
                    "model": model,
                    "score": score
                })
    
    def select_optimal_model(self, prompt: str, available_models: List[str], user_id: Optional[str] = None) -> str:
        """
        Select the optimal model for a given prompt.
        
        Args:
            prompt: The user prompt
            available_models: List of available models
            user_id: Optional identifier for the user
            
        Returns:
            Name of the selected model
        """
        if not available_models:
            return None
        
        # Determine query category based on prompt content
        category = self._categorize_prompt(prompt)
        
        # Get recommended models for this category
        recommended_models = self.query_categories.get(category, [])
        
        # Filter to only include available models
        available_recommended = [
            r["model"] for r in recommended_models
            if r["model"] in available_models
        ]
        
        # If we have a recommendation that's available, use it
        if available_recommended:
            return available_recommended[0]
        
        # Otherwise, use the first available model
        return available_models[0]
    
    def _categorize_prompt(self, prompt: str) -> str:
        """
        Categorize a prompt based on its content.
        
        Args:
            prompt: The user prompt
            
        Returns:
            Category name
        """
        # This is a simplified implementation
        # In a real application, this would use NLP or ML to categorize
        
        prompt_lower = prompt.lower()
        
        # Check for creative content
        if any(word in prompt_lower for word in ["story", "creative", "imagine", "fiction", "poem", "write"]):
            return "creative"
        
        # Check for factual queries
        if any(word in prompt_lower for word in ["fact", "history", "science", "true", "real", "explain"]):
            return "factual"
        
        # Check for technical content
        if any(word in prompt_lower for word in ["code", "program", "function", "api", "technical", "debug"]):
            return "technical"
        
        # Check for mathematical content
        if any(word in prompt_lower for word in ["math", "calculate", "equation", "solve", "number", "formula"]):
            return "mathematical"
        
        # Check for analytical content
        if any(word in prompt_lower for word in ["analyze", "compare", "evaluate", "assess", "review"]):
            return "analytical"
        
        # Check for instructional content
        if any(word in prompt_lower for word in ["how to", "steps", "guide", "tutorial", "instructions"]):
            return "instructional"
        
        # Default to overall best
        return "overall_best"
    
    def update_model_performance(self, prompt: str, model: str, success: bool) -> None:
        """
        Update model performance based on success or failure.
        
        Args:
            prompt: The user prompt
            model: The model used
            success: Whether the response was successful
        """
        if not model:
            return
        
        # Determine query category
        category = self._categorize_prompt(prompt)
        
        # Ensure model exists in performance data
        if model not in self.model_performance:
            self.model_performance[model] = {
                "overall_best": 80,
                "creative": 80,
                "factual": 80,
                "technical": 80,
                "mathematical": 80,
                "analytical": 80,
                "instructional": 80
            }
        
        # Update performance score
        current_score = self.model_performance[model].get(category, 80)
        
        if success:
            # Increase score slightly for success
            new_score = min(100, current_score + 1)
        else:
            # Decrease score more significantly for failure
            new_score = max(0, current_score - 5)
        
        self.model_performance[model][category] = new_score
        
        # Also update overall score
        current_overall = self.model_performance[model].get("overall_best", 80)
        
        if success:
            new_overall = min(100, current_overall + 0.5)
        else:
            new_overall = max(0, current_overall - 2)
        
        self.model_performance[model]["overall_best"] = new_overall
        
        # Update query categories
        self._update_query_categories()
    
    def update_fallback_success(self, primary_model: str, fallback_model: str, success: bool) -> None:
        """
        Update fallback success rates.
        
        Args:
            primary_model: The primary model that failed
            fallback_model: The fallback model used
            success: Whether the fallback was successful
        """
        if not primary_model or not fallback_model:
            return
        
        # Initialize if needed
        if primary_model not in self.fallback_success:
            self.fallback_success[primary_model] = {}
        
        if fallback_model not in self.fallback_success[primary_model]:
            self.fallback_success[primary_model][fallback_model] = {
                "success_count": 0,
                "total_count": 0
            }
        
        # Update counts
        self.fallback_success[primary_model][fallback_model]["total_count"] += 1
        
        if success:
            self.fallback_success[primary_model][fallback_model]["success_count"] += 1
    
    def get_fallback_sequence(self, primary_model: str, available_models: List[str]) -> List[str]:
        """
        Get the optimal fallback sequence for a primary model.
        
        Args:
            primary_model: The primary model
            available_models: List of available models
            
        Returns:
            List of models to try as fallbacks, in order
        """
        if not primary_model or primary_model not in self.fallback_success:
            # If no data, return all available models except primary
            return [m for m in available_models if m != primary_model]
        
        # Get fallback success rates
        fallbacks = self.fallback_success[primary_model]
        
        # Calculate success rates
        success_rates = {}
        for fallback, data in fallbacks.items():
            if data["total_count"] > 0:
                success_rate = data["success_count"] / data["total_count"]
            else:
                success_rate = 0.5  # Default if no data
            
            success_rates[fallback] = success_rate
        
        # Sort by success rate (highest first)
        sorted_fallbacks = sorted(
            [m for m in available_models if m != primary_model],
            key=lambda m: success_rates.get(m, 0.5),
            reverse=True
        )
        
        return sorted_fallbacks
    
    def get_model_recommendations(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get model recommendations for different query categories.
        
        Returns:
            Dict mapping categories to lists of recommended models
        """
        return self.query_categories
    
    def get_fallback_statistics(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get statistics about fallback success rates.
        
        Returns:
            Dict mapping primary models to lists of fallback statistics
        """
        stats = {}
        
        for primary, fallbacks in self.fallback_success.items():
            stats[primary] = []
            
            for fallback, data in fallbacks.items():
                if data["total_count"] > 0:
                    success_rate = data["success_count"] / data["total_count"]
                else:
                    success_rate = 0
                
                stats[primary].append({
                    "model": fallback,
                    "success_rate": success_rate * 100,
                    "total_count": data["total_count"]
                })
            
            # Sort by success rate (highest first)
            stats[primary].sort(key=lambda x: x["success_rate"], reverse=True)
        
        return stats
