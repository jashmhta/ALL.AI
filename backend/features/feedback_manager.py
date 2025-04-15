import os
import asyncio
from typing import Dict, Any, Optional, List
import json
import numpy as np
from datetime import datetime

class FeedbackManager:
    """
    Manages user feedback for AI responses.
    Collects, stores, and analyzes feedback to improve model selection.
    """
    
    def __init__(self):
        """Initialize the feedback manager."""
        self.storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "feedback")
        self.ratings = {}  # In-memory cache of ratings
        self.comments = {}  # In-memory cache of comments
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Load existing feedback data
        self._load_feedback_data()
    
    def add_response_rating(self, response_id: str, model: str, rating: int, user_id: Optional[str] = None) -> None:
        """
        Add a rating for an AI response.
        
        Args:
            response_id: Unique identifier for the response
            model: The AI model that generated the response
            rating: Rating value (1-5)
            user_id: Optional identifier for the user
        """
        # Validate rating
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Create rating entry
        rating_entry = {
            "response_id": response_id,
            "model": model,
            "rating": rating,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to in-memory cache
        if model not in self.ratings:
            self.ratings[model] = []
        
        self.ratings[model].append(rating_entry)
        
        # Save to disk
        self._save_rating(rating_entry)
    
    def add_feedback_comment(self, response_id: str, model: str, comment: str, user_id: Optional[str] = None) -> None:
        """
        Add a comment for an AI response.
        
        Args:
            response_id: Unique identifier for the response
            model: The AI model that generated the response
            comment: Feedback comment
            user_id: Optional identifier for the user
        """
        # Create comment entry
        comment_entry = {
            "response_id": response_id,
            "model": model,
            "comment": comment,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to in-memory cache
        if model not in self.comments:
            self.comments[model] = []
        
        self.comments[model].append(comment_entry)
        
        # Save to disk
        self._save_comment(comment_entry)
    
    def get_model_ratings(self, model: str) -> List[Dict[str, Any]]:
        """
        Get all ratings for a specific model.
        
        Args:
            model: The AI model
            
        Returns:
            List of rating entries
        """
        return self.ratings.get(model, [])
    
    def get_model_comments(self, model: str) -> List[Dict[str, Any]]:
        """
        Get all comments for a specific model.
        
        Args:
            model: The AI model
            
        Returns:
            List of comment entries
        """
        return self.comments.get(model, [])
    
    def get_average_rating(self, model: str) -> Optional[float]:
        """
        Get the average rating for a specific model.
        
        Args:
            model: The AI model
            
        Returns:
            Average rating or None if no ratings exist
        """
        ratings = self.ratings.get(model, [])
        
        if not ratings:
            return None
        
        return sum(r["rating"] for r in ratings) / len(ratings)
    
    def get_rating_distribution(self, model: str) -> Dict[int, int]:
        """
        Get the distribution of ratings for a specific model.
        
        Args:
            model: The AI model
            
        Returns:
            Dictionary mapping rating values to counts
        """
        ratings = self.ratings.get(model, [])
        
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for rating in ratings:
            distribution[rating["rating"]] += 1
        
        return distribution
    
    def get_model_comparison(self) -> Dict[str, Any]:
        """
        Get a comparison of all models based on ratings.
        
        Returns:
            Dictionary with model comparison data
        """
        comparison = {}
        
        for model in self.ratings:
            avg_rating = self.get_average_rating(model)
            rating_count = len(self.ratings[model])
            
            comparison[model] = {
                "average_rating": avg_rating,
                "rating_count": rating_count,
                "distribution": self.get_rating_distribution(model)
            }
        
        return comparison
    
    def get_recent_feedback(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent feedback (ratings and comments).
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent feedback entries
        """
        # Combine ratings and comments
        all_feedback = []
        
        for model in self.ratings:
            all_feedback.extend(self.ratings[model])
        
        for model in self.comments:
            all_feedback.extend(self.comments[model])
        
        # Sort by timestamp (newest first)
        all_feedback.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Limit the number of entries
        return all_feedback[:limit]
    
    def _save_rating(self, rating: Dict[str, Any]) -> None:
        """
        Save a rating to disk.
        
        Args:
            rating: Rating entry
        """
        try:
            # Create a filename with the response ID
            filename = f"rating_{rating['response_id']}.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Write to file
            with open(filepath, "w") as f:
                json.dump(rating, f, indent=2)
        except Exception as e:
            print(f"Error saving rating: {e}")
    
    def _save_comment(self, comment: Dict[str, Any]) -> None:
        """
        Save a comment to disk.
        
        Args:
            comment: Comment entry
        """
        try:
            # Create a filename with the response ID
            filename = f"comment_{comment['response_id']}.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Write to file
            with open(filepath, "w") as f:
                json.dump(comment, f, indent=2)
        except Exception as e:
            print(f"Error saving comment: {e}")
    
    def _load_feedback_data(self) -> None:
        """Load existing feedback data from disk."""
        try:
            # List all files in the storage directory
            for filename in os.listdir(self.storage_dir):
                filepath = os.path.join(self.storage_dir, filename)
                
                try:
                    # Read the file
                    with open(filepath, "r") as f:
                        data = json.load(f)
                    
                    # Add to the appropriate cache
                    if filename.startswith("rating_"):
                        model = data.get("model")
                        
                        if model:
                            if model not in self.ratings:
                                self.ratings[model] = []
                            
                            self.ratings[model].append(data)
                    elif filename.startswith("comment_"):
                        model = data.get("model")
                        
                        if model:
                            if model not in self.comments:
                                self.comments[model] = []
                            
                            self.comments[model].append(data)
                except Exception as e:
                    print(f"Error loading feedback file {filename}: {e}")
        except Exception as e:
            print(f"Error loading feedback data: {e}")
    
    def get_model_strengths(self) -> Dict[str, List[str]]:
        """
        Analyze comments to identify model strengths.
        
        Returns:
            Dictionary mapping models to lists of strengths
        """
        # This is a simplified implementation
        # In a real application, this would use NLP to analyze comments
        
        strengths = {}
        
        # Predefined strengths for each model
        strengths["gpt"] = ["Detailed explanations", "Code examples", "Creative writing"]
        strengths["claude"] = ["Thorough analysis", "Safety considerations", "Balanced responses"]
        strengths["gemini"] = ["Concise responses", "Practical solutions", "Technical accuracy"]
        strengths["llama"] = ["Fast responses", "Efficient code", "Straightforward answers"]
        
        return strengths
