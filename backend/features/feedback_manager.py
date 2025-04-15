import os
import json
from typing import Dict, Any, List, Optional, Tuple

class FeedbackManager:
    """
    Manages user feedback on AI responses for continuous improvement.
    Tracks ratings, comments, and preferences to optimize model selection.
    """
    
    def __init__(self):
        """Initialize the feedback manager."""
        # Set up storage directory
        self.storage_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "feedback")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize feedback storage
        self.feedback_file = os.path.join(self.storage_dir, "feedback_data.json")
        self.feedback_data = self._load_feedback_data()
        
        # Initialize model performance tracking
        if "model_ratings" not in self.feedback_data:
            self.feedback_data["model_ratings"] = {}
        
        if "user_preferences" not in self.feedback_data:
            self.feedback_data["user_preferences"] = {}
        
        if "feedback_comments" not in self.feedback_data:
            self.feedback_data["feedback_comments"] = []
    
    def _load_feedback_data(self) -> Dict[str, Any]:
        """Load feedback data from disk."""
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r') as f:
                    return json.load(f)
            except Exception:
                # Return default structure if file is corrupted
                return {
                    "model_ratings": {},
                    "user_preferences": {},
                    "feedback_comments": []
                }
        else:
            # Return default structure if file doesn't exist
            return {
                "model_ratings": {},
                "user_preferences": {},
                "feedback_comments": []
            }
    
    def _save_feedback_data(self) -> None:
        """Save feedback data to disk."""
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
        except Exception as e:
            print(f"Error saving feedback data: {e}")
    
    def add_response_rating(self, response_id: str, model: str, rating: int, 
                          user_id: Optional[str] = None) -> None:
        """
        Add a rating for an AI response.
        
        Args:
            response_id: Unique identifier for the response
            model: The AI model that generated the response
            rating: Rating value (1-5)
            user_id: Optional identifier for the user
        """
        # Validate rating
        rating = max(1, min(5, rating))
        
        # Initialize model in ratings if not exists
        if model not in self.feedback_data["model_ratings"]:
            self.feedback_data["model_ratings"][model] = {
                "total_ratings": 0,
                "rating_sum": 0,
                "rating_counts": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "responses": {}
            }
        
        # Add rating for specific response
        self.feedback_data["model_ratings"][model]["responses"][response_id] = {
            "rating": rating,
            "timestamp": os.times().elapsed,
            "user_id": user_id
        }
        
        # Update aggregated stats
        self.feedback_data["model_ratings"][model]["total_ratings"] += 1
        self.feedback_data["model_ratings"][model]["rating_sum"] += rating
        self.feedback_data["model_ratings"][model]["rating_counts"][rating] += 1
        
        # Update user preferences if user_id provided
        if user_id:
            if user_id not in self.feedback_data["user_preferences"]:
                self.feedback_data["user_preferences"][user_id] = {
                    "model_ratings": {},
                    "favorite_models": []
                }
            
            if model not in self.feedback_data["user_preferences"][user_id]["model_ratings"]:
                self.feedback_data["user_preferences"][user_id]["model_ratings"][model] = {
                    "total_ratings": 0,
                    "rating_sum": 0
                }
            
            self.feedback_data["user_preferences"][user_id]["model_ratings"][model]["total_ratings"] += 1
            self.feedback_data["user_preferences"][user_id]["model_ratings"][model]["rating_sum"] += rating
            
            # Update favorite models for user
            self._update_user_favorites(user_id)
        
        # Save updated data
        self._save_feedback_data()
    
    def add_feedback_comment(self, response_id: str, model: str, comment: str,
                           user_id: Optional[str] = None) -> None:
        """
        Add a feedback comment for an AI response.
        
        Args:
            response_id: Unique identifier for the response
            model: The AI model that generated the response
            comment: Feedback comment text
            user_id: Optional identifier for the user
        """
        # Add comment to feedback data
        feedback_entry = {
            "response_id": response_id,
            "model": model,
            "comment": comment,
            "timestamp": os.times().elapsed,
            "user_id": user_id
        }
        
        self.feedback_data["feedback_comments"].append(feedback_entry)
        
        # Save updated data
        self._save_feedback_data()
    
    def _update_user_favorites(self, user_id: str) -> None:
        """Update favorite models for a user based on ratings."""
        if user_id not in self.feedback_data["user_preferences"]:
            return
        
        user_prefs = self.feedback_data["user_preferences"][user_id]
        model_ratings = user_prefs["model_ratings"]
        
        # Calculate average rating for each model
        avg_ratings = {}
        for model, data in model_ratings.items():
            if data["total_ratings"] > 0:
                avg_ratings[model] = data["rating_sum"] / data["total_ratings"]
        
        # Sort models by average rating
        sorted_models = sorted(avg_ratings.items(), key=lambda x: x[1], reverse=True)
        
        # Update favorite models (top 3 with rating >= 4)
        favorites = [model for model, rating in sorted_models if rating >= 4][:3]
        user_prefs["favorite_models"] = favorites
    
    def get_model_performance(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance metrics for models based on user feedback.
        
        Args:
            model: Optional model name to filter metrics
            
        Returns:
            Dictionary with performance metrics
        """
        if model and model in self.feedback_data["model_ratings"]:
            return self._get_single_model_performance(model)
        
        # Get metrics for all models
        all_models = {}
        for model_name in self.feedback_data["model_ratings"]:
            all_models[model_name] = self._get_single_model_performance(model_name)
        
        return {
            "models": all_models,
            "overall_best": self._get_best_performing_model()
        }
    
    def _get_single_model_performance(self, model: str) -> Dict[str, Any]:
        """Get performance metrics for a single model."""
        model_data = self.feedback_data["model_ratings"].get(model, {
            "total_ratings": 0,
            "rating_sum": 0,
            "rating_counts": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        })
        
        # Calculate average rating
        avg_rating = 0
        if model_data["total_ratings"] > 0:
            avg_rating = model_data["rating_sum"] / model_data["total_ratings"]
        
        # Calculate rating distribution percentages
        rating_distribution = {}
        for rating, count in model_data["rating_counts"].items():
            if model_data["total_ratings"] > 0:
                percentage = (count / model_data["total_ratings"]) * 100
            else:
                percentage = 0
            rating_distribution[rating] = {
                "count": count,
                "percentage": percentage
            }
        
        return {
            "average_rating": avg_rating,
            "total_ratings": model_data["total_ratings"],
            "rating_distribution": rating_distribution
        }
    
    def _get_best_performing_model(self) -> Optional[str]:
        """Get the best performing model based on average ratings."""
        best_model = None
        best_rating = 0
        min_ratings_threshold = 5  # Minimum number of ratings to consider
        
        for model, data in self.feedback_data["model_ratings"].items():
            if data["total_ratings"] >= min_ratings_threshold:
                avg_rating = data["rating_sum"] / data["total_ratings"]
                if avg_rating > best_rating:
                    best_rating = avg_rating
                    best_model = model
        
        return best_model
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get preferences for a specific user.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            Dictionary with user preferences
        """
        if user_id not in self.feedback_data["user_preferences"]:
            return {
                "favorite_models": [],
                "model_ratings": {}
            }
        
        return self.feedback_data["user_preferences"][user_id]
    
    def get_recommended_model(self, user_id: Optional[str] = None) -> str:
        """
        Get recommended model for a user based on their preferences.
        
        Args:
            user_id: Optional identifier for the user
            
        Returns:
            Recommended model name
        """
        # If user_id provided and user has preferences, use their favorite model
        if user_id and user_id in self.feedback_data["user_preferences"]:
            favorites = self.feedback_data["user_preferences"][user_id]["favorite_models"]
            if favorites:
                return favorites[0]
        
        # Otherwise, use the best performing model overall
        best_model = self._get_best_performing_model()
        if best_model:
            return best_model
        
        # If no data available, return None
        return None
    
    def get_recent_feedback(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent feedback comments.
        
        Args:
            limit: Maximum number of comments to return
            
        Returns:
            List of recent feedback comments
        """
        # Sort comments by timestamp (newest first)
        sorted_comments = sorted(
            self.feedback_data["feedback_comments"],
            key=lambda x: x.get("timestamp", 0),
            reverse=True
        )
        
        # Return limited number of comments
        return sorted_comments[:limit]
