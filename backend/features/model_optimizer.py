import os
import json
from typing import Dict, Any, List, Optional, Tuple

class ModelOptimizer:
    """
    Optimizes AI model selection based on query type, performance metrics, and user preferences.
    Implements intelligent routing and fallback mechanisms.
    """
    
    def __init__(self, feedback_manager=None):
        """
        Initialize the model optimizer.
        
        Args:
            feedback_manager: Optional FeedbackManager instance for accessing user feedback
        """
        self.feedback_manager = feedback_manager
        
        # Set up storage directory
        self.storage_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "optimization")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Load or initialize optimization data
        self.optimization_file = os.path.join(self.storage_dir, "model_optimization.json")
        self.optimization_data = self._load_optimization_data()
        
        # Define query categories and their keywords
        self.query_categories = {
            "creative": [
                "write", "create", "story", "poem", "creative", "imagine", "fiction",
                "design", "generate", "invent", "novel", "artistic"
            ],
            "factual": [
                "what is", "explain", "how does", "facts", "information", "history",
                "science", "data", "research", "define", "describe", "details"
            ],
            "technical": [
                "code", "programming", "function", "algorithm", "debug", "software",
                "technical", "engineering", "implementation", "syntax", "compile"
            ],
            "mathematical": [
                "calculate", "math", "equation", "formula", "solve", "computation",
                "numerical", "statistics", "probability", "arithmetic", "algebra"
            ],
            "analytical": [
                "analyze", "compare", "evaluate", "assess", "review", "critique",
                "pros and cons", "advantages", "disadvantages", "opinion", "perspective"
            ],
            "instructional": [
                "how to", "steps", "guide", "tutorial", "instructions", "teach",
                "learn", "procedure", "method", "process", "walkthrough"
            ]
        }
        
        # Initialize category performance if not exists
        if "category_performance" not in self.optimization_data:
            self.optimization_data["category_performance"] = {
                category: {"preferred_models": {}} for category in self.query_categories
            }
        
        # Initialize model strengths if not exists
        if "model_strengths" not in self.optimization_data:
            self.optimization_data["model_strengths"] = {}
        
        # Initialize fallback success rates if not exists
        if "fallback_success_rates" not in self.optimization_data:
            self.optimization_data["fallback_success_rates"] = {}
    
    def _load_optimization_data(self) -> Dict[str, Any]:
        """Load optimization data from disk."""
        if os.path.exists(self.optimization_file):
            try:
                with open(self.optimization_file, 'r') as f:
                    return json.load(f)
            except Exception:
                # Return default structure if file is corrupted
                return {
                    "category_performance": {},
                    "model_strengths": {},
                    "fallback_success_rates": {}
                }
        else:
            # Return default structure if file doesn't exist
            return {
                "category_performance": {},
                "model_strengths": {},
                "fallback_success_rates": {}
            }
    
    def _save_optimization_data(self) -> None:
        """Save optimization data to disk."""
        try:
            with open(self.optimization_file, 'w') as f:
                json.dump(self.optimization_data, f, indent=2)
        except Exception as e:
            print(f"Error saving optimization data: {e}")
    
    def categorize_query(self, query: str) -> str:
        """
        Categorize a query based on keywords and patterns.
        
        Args:
            query: The user query
            
        Returns:
            Category name or "general" if no specific category matches
        """
        query = query.lower()
        
        # Check each category for keyword matches
        category_scores = {}
        for category, keywords in self.query_categories.items():
            score = 0
            for keyword in keywords:
                if keyword in query:
                    score += 1
            category_scores[category] = score
        
        # Find category with highest score
        best_category = max(category_scores.items(), key=lambda x: x[1])
        
        # If score is 0, return "general"
        if best_category[1] == 0:
            return "general"
        
        return best_category[0]
    
    def select_optimal_model(self, query: str, available_models: List[str], 
                           user_id: Optional[str] = None) -> str:
        """
        Select the optimal model for a given query.
        
        Args:
            query: The user query
            available_models: List of available AI models
            user_id: Optional user identifier for personalized selection
            
        Returns:
            Name of the selected model
        """
        if not available_models:
            return None
        
        # Check user preferences if user_id provided and feedback_manager available
        if user_id and self.feedback_manager:
            recommended_model = self.feedback_manager.get_recommended_model(user_id)
            if recommended_model and recommended_model in available_models:
                return recommended_model
        
        # Categorize the query
        category = self.categorize_query(query)
        
        # Check if we have performance data for this category
        if category in self.optimization_data["category_performance"]:
            category_data = self.optimization_data["category_performance"][category]
            
            # Find the best performing model for this category that is available
            for model, score in sorted(category_data.get("preferred_models", {}).items(), 
                                     key=lambda x: x[1], reverse=True):
                if model in available_models:
                    return model
        
        # If no category-specific data, check overall model strengths
        model_strengths = self.optimization_data.get("model_strengths", {})
        for model, strength in sorted(model_strengths.items(), key=lambda x: x[1], reverse=True):
            if model in available_models:
                return model
        
        # If no optimization data available, return the first available model
        return available_models[0]
    
    def get_fallback_sequence(self, primary_model: str, available_models: List[str]) -> List[str]:
        """
        Get the optimal fallback sequence for a given primary model.
        
        Args:
            primary_model: The primary model that failed
            available_models: List of available AI models
            
        Returns:
            List of models to try in order
        """
        if primary_model not in available_models:
            return available_models
        
        # Remove primary model from available models
        fallback_models = [m for m in available_models if m != primary_model]
        
        if not fallback_models:
            return []
        
        # Check if we have fallback success rates for this primary model
        fallback_rates = self.optimization_data.get("fallback_success_rates", {}).get(primary_model, {})
        
        # Sort fallback models by success rate
        sorted_fallbacks = sorted(
            [(model, fallback_rates.get(model, 0)) for model in fallback_models],
            key=lambda x: x[1],
            reverse=True
        )
        
        return [model for model, _ in sorted_fallbacks]
    
    def update_model_performance(self, query: str, model: str, success: bool, 
                               response_quality: Optional[int] = None) -> None:
        """
        Update performance data for a model based on query results.
        
        Args:
            query: The user query
            model: The AI model used
            success: Whether the model successfully answered the query
            response_quality: Optional quality rating (1-5)
        """
        # Categorize the query
        category = self.categorize_query(query)
        
        # Initialize category if not exists
        if category not in self.optimization_data["category_performance"]:
            self.optimization_data["category_performance"][category] = {
                "preferred_models": {}
            }
        
        # Initialize model in category if not exists
        category_data = self.optimization_data["category_performance"][category]
        if model not in category_data["preferred_models"]:
            category_data["preferred_models"][model] = 0
        
        # Update model score based on success and quality
        if success:
            # Base score for success
            score_change = 1
            
            # Additional score based on quality rating
            if response_quality:
                score_change += (response_quality - 3) * 0.5  # -1 to +1 based on rating
            
            category_data["preferred_models"][model] += score_change
        else:
            # Penalty for failure
            category_data["preferred_models"][model] -= 1
        
        # Update model strengths
        if model not in self.optimization_data["model_strengths"]:
            self.optimization_data["model_strengths"][model] = 0
        
        if success:
            self.optimization_data["model_strengths"][model] += 0.5
        else:
            self.optimization_data["model_strengths"][model] -= 0.5
        
        # Save updated data
        self._save_optimization_data()
    
    def update_fallback_success(self, primary_model: str, fallback_model: str, success: bool) -> None:
        """
        Update fallback success rates.
        
        Args:
            primary_model: The primary model that failed
            fallback_model: The fallback model that was tried
            success: Whether the fallback model successfully answered the query
        """
        # Initialize primary model in fallback rates if not exists
        if primary_model not in self.optimization_data["fallback_success_rates"]:
            self.optimization_data["fallback_success_rates"][primary_model] = {}
        
        # Initialize fallback model for primary model if not exists
        fallback_rates = self.optimization_data["fallback_success_rates"][primary_model]
        if fallback_model not in fallback_rates:
            fallback_rates[fallback_model] = 0
        
        # Update success rate
        if success:
            fallback_rates[fallback_model] += 1
        else:
            fallback_rates[fallback_model] -= 0.5
        
        # Save updated data
        self._save_optimization_data()
    
    def get_model_recommendations(self) -> Dict[str, Any]:
        """
        Get model recommendations for different query categories.
        
        Returns:
            Dictionary with model recommendations
        """
        recommendations = {}
        
        # Get recommendations for each category
        for category in self.query_categories:
            if category in self.optimization_data["category_performance"]:
                category_data = self.optimization_data["category_performance"][category]
                preferred_models = category_data.get("preferred_models", {})
                
                if preferred_models:
                    # Get top 3 models for this category
                    top_models = sorted(preferred_models.items(), key=lambda x: x[1], reverse=True)[:3]
                    recommendations[category] = [{"model": model, "score": score} for model, score in top_models]
                else:
                    recommendations[category] = []
            else:
                recommendations[category] = []
        
        # Add overall best models
        model_strengths = self.optimization_data.get("model_strengths", {})
        if model_strengths:
            top_overall = sorted(model_strengths.items(), key=lambda x: x[1], reverse=True)[:3]
            recommendations["overall_best"] = [{"model": model, "score": score} for model, score in top_overall]
        else:
            recommendations["overall_best"] = []
        
        return recommendations
    
    def get_fallback_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about fallback success rates.
        
        Returns:
            Dictionary with fallback statistics
        """
        fallback_stats = {}
        
        for primary_model, fallbacks in self.optimization_data.get("fallback_success_rates", {}).items():
            if fallbacks:
                # Sort fallbacks by success rate
                sorted_fallbacks = sorted(fallbacks.items(), key=lambda x: x[1], reverse=True)
                fallback_stats[primary_model] = [
                    {"model": model, "success_rate": rate} for model, rate in sorted_fallbacks
                ]
            else:
                fallback_stats[primary_model] = []
        
        return fallback_stats
