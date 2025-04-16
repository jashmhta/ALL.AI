import os
import asyncio
from typing import Dict, Any, List, Optional
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io
import base64
from datetime import datetime

class FeedbackManager:
    """
    Manages user feedback for the Multi-AI application.
    Collects, stores, and analyzes feedback on model responses.
    """
    
    def __init__(self):
        """Initialize the feedback manager."""
        self.storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "feedback")
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize feedback data
        self.feedback_data = self._load_feedback_data()
    
    def _load_feedback_data(self) -> Dict[str, Any]:
        """
        Load feedback data from storage.
        
        Returns:
            Dict containing feedback data
        """
        filepath = os.path.join(self.storage_dir, "feedback_data.json")
        
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading feedback data: {e}")
                return self._initialize_feedback_data()
        else:
            return self._initialize_feedback_data()
    
    def _initialize_feedback_data(self) -> Dict[str, Any]:
        """
        Initialize empty feedback data structure.
        
        Returns:
            Dict containing empty feedback data
        """
        return {
            "models": {},
            "ratings": [],
            "comments": [],
            "comparisons": []
        }
    
    def _save_feedback_data(self) -> bool:
        """
        Save feedback data to storage.
        
        Returns:
            True if saving was successful, False otherwise
        """
        filepath = os.path.join(self.storage_dir, "feedback_data.json")
        
        try:
            with open(filepath, "w") as f:
                json.dump(self.feedback_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving feedback data: {e}")
            return False
    
    def add_rating(self, model: str, rating: int, prompt: str, response: str, 
                  conversation_id: Optional[str] = None, comment: Optional[str] = None) -> bool:
        """
        Add a rating for a model response.
        
        Args:
            model: The model that generated the response
            rating: Rating value (1-5)
            prompt: The prompt that was sent to the model
            response: The response that was generated
            conversation_id: Unique identifier for the conversation
            comment: Optional comment about the rating
            
        Returns:
            True if adding the rating was successful, False otherwise
        """
        try:
            # Validate rating
            rating = max(1, min(5, rating))
            
            # Initialize model data if it doesn't exist
            if model not in self.feedback_data["models"]:
                self.feedback_data["models"][model] = {
                    "ratings": [],
                    "average_rating": 0,
                    "total_ratings": 0
                }
            
            # Create rating entry
            rating_entry = {
                "model": model,
                "rating": rating,
                "prompt": prompt,
                "response": response,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat(),
                "comment": comment
            }
            
            # Add to ratings list
            self.feedback_data["ratings"].append(rating_entry)
            
            # Add to model ratings
            self.feedback_data["models"][model]["ratings"].append(rating)
            
            # Update model average rating
            ratings = self.feedback_data["models"][model]["ratings"]
            self.feedback_data["models"][model]["average_rating"] = sum(ratings) / len(ratings)
            self.feedback_data["models"][model]["total_ratings"] = len(ratings)
            
            # Add comment if provided
            if comment:
                self.add_comment(model, comment, prompt, response, conversation_id)
            
            # Save feedback data
            return self._save_feedback_data()
        except Exception as e:
            print(f"Error adding rating: {e}")
            return False
    
    def add_comment(self, model: str, comment: str, prompt: str, response: str,
                   conversation_id: Optional[str] = None) -> bool:
        """
        Add a comment about a model response.
        
        Args:
            model: The model that generated the response
            comment: Comment text
            prompt: The prompt that was sent to the model
            response: The response that was generated
            conversation_id: Unique identifier for the conversation
            
        Returns:
            True if adding the comment was successful, False otherwise
        """
        try:
            # Create comment entry
            comment_entry = {
                "model": model,
                "comment": comment,
                "prompt": prompt,
                "response": response,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to comments list
            self.feedback_data["comments"].append(comment_entry)
            
            # Save feedback data
            return self._save_feedback_data()
        except Exception as e:
            print(f"Error adding comment: {e}")
            return False
    
    def add_comparison(self, prompt: str, responses: List[Dict[str, Any]], 
                      preferred_model: str, conversation_id: Optional[str] = None,
                      reason: Optional[str] = None) -> bool:
        """
        Add a comparison between multiple model responses.
        
        Args:
            prompt: The prompt that was sent to the models
            responses: List of response dictionaries with model and text
            preferred_model: The model that was preferred
            conversation_id: Unique identifier for the conversation
            reason: Optional reason for the preference
            
        Returns:
            True if adding the comparison was successful, False otherwise
        """
        try:
            # Create comparison entry
            comparison_entry = {
                "prompt": prompt,
                "responses": responses,
                "preferred_model": preferred_model,
                "conversation_id": conversation_id,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to comparisons list
            self.feedback_data["comparisons"].append(comparison_entry)
            
            # Save feedback data
            return self._save_feedback_data()
        except Exception as e:
            print(f"Error adding comparison: {e}")
            return False
    
    def get_model_ratings(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get ratings for a specific model or all models.
        
        Args:
            model: The model to get ratings for, or None for all models
            
        Returns:
            Dict containing rating data
        """
        if model:
            return self.feedback_data["models"].get(model, {
                "ratings": [],
                "average_rating": 0,
                "total_ratings": 0
            })
        else:
            return {
                "models": self.feedback_data["models"],
                "total_ratings": len(self.feedback_data["ratings"])
            }
    
    def get_comments(self, model: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get comments for a specific model or all models.
        
        Args:
            model: The model to get comments for, or None for all models
            limit: Maximum number of comments to return
            
        Returns:
            List of comment dictionaries
        """
        comments = self.feedback_data["comments"]
        
        if model:
            comments = [c for c in comments if c["model"] == model]
        
        # Sort by timestamp (newest first)
        comments.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return comments[:limit]
    
    def get_comparisons(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get model comparisons.
        
        Args:
            limit: Maximum number of comparisons to return
            
        Returns:
            List of comparison dictionaries
        """
        comparisons = self.feedback_data["comparisons"]
        
        # Sort by timestamp (newest first)
        comparisons.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return comparisons[:limit]
    
    def generate_rating_chart(self) -> Optional[str]:
        """
        Generate a chart of model ratings.
        
        Returns:
            Base64-encoded PNG image of the chart, or None if generation failed
        """
        try:
            # Get model data
            models = self.feedback_data["models"]
            
            if not models:
                return None
            
            # Prepare data for chart
            model_names = []
            avg_ratings = []
            total_ratings = []
            
            for model, data in models.items():
                if data["total_ratings"] > 0:
                    model_names.append(model)
                    avg_ratings.append(data["average_rating"])
                    total_ratings.append(data["total_ratings"])
            
            if not model_names:
                return None
            
            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            
            # Plot average ratings
            bars = ax1.bar(model_names, avg_ratings, color='skyblue')
            ax1.set_title('Average Ratings by Model')
            ax1.set_xlabel('Model')
            ax1.set_ylabel('Average Rating (1-5)')
            ax1.set_ylim(0, 5.5)
            ax1.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{height:.2f}', ha='center', va='bottom')
            
            # Plot total ratings
            bars = ax2.bar(model_names, total_ratings, color='lightgreen')
            ax2.set_title('Total Ratings by Model')
            ax2.set_xlabel('Model')
            ax2.set_ylabel('Number of Ratings')
            ax2.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}', ha='center', va='bottom')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            
            # Encode as base64
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            
            # Close the figure
            plt.close(fig)
            
            return img_str
        except Exception as e:
            print(f"Error generating rating chart: {e}")
            return None
    
    def generate_comparison_chart(self) -> Optional[str]:
        """
        Generate a chart of model comparisons.
        
        Returns:
            Base64-encoded PNG image of the chart, or None if generation failed
        """
        try:
            # Get comparison data
            comparisons = self.feedback_data["comparisons"]
            
            if not comparisons:
                return None
            
            # Count preferences
            preferences = {}
            
            for comp in comparisons:
                preferred = comp["preferred_model"]
                if preferred not in preferences:
                    preferences[preferred] = 0
                preferences[preferred] += 1
            
            if not preferences:
                return None
            
            # Prepare data for chart
            models = list(preferences.keys())
            counts = list(preferences.values())
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Plot preferences
            bars = ax.bar(models, counts, color='lightcoral')
            ax.set_title('Preferred Models in Comparisons')
            ax.set_xlabel('Model')
            ax.set_ylabel('Number of Times Preferred')
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{int(height)}', ha='center', va='bottom')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            
            # Encode as base64
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            
            # Close the figure
            plt.close(fig)
            
            return img_str
        except Exception as e:
            print(f"Error generating comparison chart: {e}")
            return None
    
    def export_feedback_data(self, format: str = "json") -> Optional[str]:
        """
        Export feedback data in the specified format.
        
        Args:
            format: Export format (json or csv)
            
        Returns:
            Path to the exported file, or None if export failed
        """
        try:
            if format.lower() == "json":
                # Export as JSON
                filepath = os.path.join(self.storage_dir, "feedback_export.json")
                
                with open(filepath, "w") as f:
                    json.dump(self.feedback_data, f, indent=2)
                
                return filepath
            elif format.lower() == "csv":
                # Export ratings as CSV
                ratings_filepath = os.path.join(self.storage_dir, "ratings_export.csv")
                
                # Convert ratings to DataFrame
                ratings_data = []
                
                for rating in self.feedback_data["ratings"]:
                    ratings_data.append({
                        "model": rating["model"],
                        "rating": rating["rating"],
                        "timestamp": rating["timestamp"],
                        "conversation_id": rating.get("conversation_id", ""),
                        "comment": rating.get("comment", "")
                    })
                
                if ratings_data:
                    df = pd.DataFrame(ratings_data)
                    df.to_csv(ratings_filepath, index=False)
                else:
                    with open(ratings_filepath, "w") as f:
                        f.write("model,rating,timestamp,conversation_id,comment\n")
                
                return ratings_filepath
            else:
                print(f"Unsupported export format: {format}")
                return None
        except Exception as e:
            print(f"Error exporting feedback data: {e}")
            return None
    
    def clear_feedback_data(self) -> bool:
        """
        Clear all feedback data.
        
        Returns:
            True if clearing was successful, False otherwise
        """
        try:
            self.feedback_data = self._initialize_feedback_data()
            return self._save_feedback_data()
        except Exception as e:
            print(f"Error clearing feedback data: {e}")
            return False
