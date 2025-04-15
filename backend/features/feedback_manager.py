import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

class FeedbackManager:
    """
    Manages user feedback and model performance tracking.
    """
    
    def __init__(self, storage_path: str = "feedback_data.json"):
        """
        Initialize the feedback manager.
        
        Args:
            storage_path: Path to store feedback data
        """
        self.storage_path = storage_path
        self.feedback_data = self._load_feedback_data()
    
    def _load_feedback_data(self) -> Dict[str, Any]:
        """
        Load feedback data from storage.
        
        Returns:
            Feedback data dictionary
        """
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading feedback data: {str(e)}")
                return self._initialize_feedback_data()
        else:
            return self._initialize_feedback_data()
    
    def _initialize_feedback_data(self) -> Dict[str, Any]:
        """
        Initialize feedback data structure.
        
        Returns:
            New feedback data dictionary
        """
        return {
            "models": {},
            "feedback_history": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_feedback_data(self) -> None:
        """
        Save feedback data to storage.
        """
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
        except Exception as e:
            print(f"Error saving feedback data: {str(e)}")
    
    def record_feedback(self, 
                       provider: str, 
                       model: str, 
                       prompt: str,
                       response: str,
                       rating: int,
                       feedback_text: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Record user feedback for a model response.
        
        Args:
            provider: Provider name
            model: Model name
            prompt: User prompt
            response: Model response
            rating: Rating (1-5)
            feedback_text: Optional feedback text
            tags: Optional tags
            metadata: Optional metadata
            
        Returns:
            Feedback record
        """
        # Validate rating
        rating = max(1, min(5, rating))
        
        # Create model key
        model_key = f"{provider}/{model}"
        
        # Ensure model exists in data
        if model_key not in self.feedback_data["models"]:
            self.feedback_data["models"][model_key] = {
                "total_ratings": 0,
                "rating_sum": 0,
                "rating_counts": {
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 0
                },
                "tags": {}
            }
        
        # Update model stats
        model_data = self.feedback_data["models"][model_key]
        model_data["total_ratings"] += 1
        model_data["rating_sum"] += rating
        model_data["rating_counts"][str(rating)] += 1
        
        # Update tags
        if tags:
            for tag in tags:
                if tag not in model_data["tags"]:
                    model_data["tags"][tag] = 0
                model_data["tags"][tag] += 1
        
        # Create feedback record
        feedback_record = {
            "id": f"feedback_{len(self.feedback_data['feedback_history']) + 1}",
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "response": response,
            "rating": rating,
            "feedback_text": feedback_text or "",
            "tags": tags or [],
            "metadata": metadata or {}
        }
        
        # Add to history
        self.feedback_data["feedback_history"].append(feedback_record)
        
        # Update last updated timestamp
        self.feedback_data["last_updated"] = datetime.now().isoformat()
        
        # Save data
        self._save_feedback_data()
        
        return feedback_record
    
    def get_model_performance(self, provider: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance metrics for models.
        
        Args:
            provider: Optional provider filter
            model: Optional model filter
            
        Returns:
            Performance metrics
        """
        results = {}
        
        for model_key, model_data in self.feedback_data["models"].items():
            # Parse model key
            parts = model_key.split("/")
            if len(parts) != 2:
                continue
                
            model_provider, model_name = parts
            
            # Apply filters
            if provider and model_provider != provider:
                continue
                
            if model and model_name != model:
                continue
            
            # Calculate average rating
            avg_rating = model_data["rating_sum"] / model_data["total_ratings"] if model_data["total_ratings"] > 0 else 0
            
            # Create result entry
            results[model_key] = {
                "average_rating": avg_rating,
                "total_ratings": model_data["total_ratings"],
                "rating_distribution": model_data["rating_counts"],
                "common_tags": self._get_top_tags(model_data["tags"], 5)
            }
        
        return results
    
    def _get_top_tags(self, tags: Dict[str, int], limit: int) -> Dict[str, int]:
        """
        Get top tags by count.
        
        Args:
            tags: Tags dictionary
            limit: Maximum number of tags to return
            
        Returns:
            Top tags
        """
        sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_tags[:limit])
    
    def get_feedback_history(self, 
                            provider: Optional[str] = None, 
                            model: Optional[str] = None,
                            min_rating: Optional[int] = None,
                            max_rating: Optional[int] = None,
                            tags: Optional[List[str]] = None,
                            start_time: Optional[str] = None,
                            end_time: Optional[str] = None,
                            limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get feedback history with optional filters.
        
        Args:
            provider: Optional provider filter
            model: Optional model filter
            min_rating: Optional minimum rating filter
            max_rating: Optional maximum rating filter
            tags: Optional tags filter (any match)
            start_time: Optional start time filter (ISO format)
            end_time: Optional end time filter (ISO format)
            limit: Optional limit on number of records
            
        Returns:
            List of feedback records
        """
        history = self.feedback_data["feedback_history"]
        
        # Apply provider filter
        if provider is not None:
            history = [record for record in history if record["provider"] == provider]
        
        # Apply model filter
        if model is not None:
            history = [record for record in history if record["model"] == model]
        
        # Apply rating filters
        if min_rating is not None:
            history = [record for record in history if record["rating"] >= min_rating]
        
        if max_rating is not None:
            history = [record for record in history if record["rating"] <= max_rating]
        
        # Apply tags filter
        if tags is not None:
            history = [record for record in history if any(tag in record["tags"] for tag in tags)]
        
        # Apply time filters
        if start_time is not None:
            start_dt = datetime.fromisoformat(start_time)
            history = [record for record in history if datetime.fromisoformat(record["timestamp"]) >= start_dt]
        
        if end_time is not None:
            end_dt = datetime.fromisoformat(end_time)
            history = [record for record in history if datetime.fromisoformat(record["timestamp"]) <= end_dt]
        
        # Sort by timestamp (newest first)
        history = sorted(history, key=lambda x: x["timestamp"], reverse=True)
        
        # Apply limit
        if limit is not None:
            history = history[:limit]
        
        return history
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """
        Get summary of all feedback.
        
        Returns:
            Feedback summary
        """
        # Get all feedback
        all_feedback = self.feedback_data["feedback_history"]
        
        # Calculate overall stats
        total_feedback = len(all_feedback)
        rating_sum = sum(record["rating"] for record in all_feedback)
        avg_rating = rating_sum / total_feedback if total_feedback > 0 else 0
        
        # Count ratings
        rating_counts = {
            "1": 0,
            "2": 0,
            "3": 0,
            "4": 0,
            "5": 0
        }
        
        for record in all_feedback:
            rating_counts[str(record["rating"])] += 1
        
        # Collect all tags
        all_tags = {}
        for record in all_feedback:
            for tag in record["tags"]:
                if tag not in all_tags:
                    all_tags[tag] = 0
                all_tags[tag] += 1
        
        # Get top providers and models
        providers = {}
        models = {}
        
        for record in all_feedback:
            provider = record["provider"]
            model = record["model"]
            
            if provider not in providers:
                providers[provider] = {
                    "count": 0,
                    "rating_sum": 0
                }
            
            providers[provider]["count"] += 1
            providers[provider]["rating_sum"] += record["rating"]
            
            model_key = f"{provider}/{model}"
            if model_key not in models:
                models[model_key] = {
                    "count": 0,
                    "rating_sum": 0
                }
            
            models[model_key]["count"] += 1
            models[model_key]["rating_sum"] += record["rating"]
        
        # Calculate averages
        for provider_data in providers.values():
            provider_data["average_rating"] = provider_data["rating_sum"] / provider_data["count"] if provider_data["count"] > 0 else 0
        
        for model_data in models.values():
            model_data["average_rating"] = model_data["rating_sum"] / model_data["count"] if model_data["count"] > 0 else 0
        
        # Sort providers and models by count
        top_providers = dict(sorted(providers.items(), key=lambda x: x[1]["count"], reverse=True)[:5])
        top_models = dict(sorted(models.items(), key=lambda x: x[1]["count"], reverse=True)[:5])
        
        return {
            "total_feedback": total_feedback,
            "average_rating": avg_rating,
            "rating_distribution": rating_counts,
            "top_tags": self._get_top_tags(all_tags, 10),
            "top_providers": top_providers,
            "top_models": top_models,
            "last_updated": self.feedback_data["last_updated"]
        }
    
    def get_improvement_suggestions(self, provider: Optional[str] = None, model: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get improvement suggestions based on low-rated feedback.
        
        Args:
            provider: Optional provider filter
            model: Optional model filter
            
        Returns:
            List of improvement suggestions
        """
        # Get low-rated feedback (ratings 1-2)
        low_rated = self.get_feedback_history(
            provider=provider,
            model=model,
            max_rating=2
        )
        
        # Group by common themes
        themes = {}
        
        for record in low_rated:
            # Use tags as themes if available
            if record["tags"]:
                for tag in record["tags"]:
                    if tag not in themes:
                        themes[tag] = []
                    themes[tag].append(record)
            # Otherwise use feedback text
            elif record["feedback_text"]:
                # Simple keyword extraction
                keywords = self._extract_keywords(record["feedback_text"])
                for keyword in keywords:
                    if keyword not in themes:
                        themes[keyword] = []
                    themes[keyword].append(record)
        
        # Create suggestions
        suggestions = []
        
        for theme, records in themes.items():
            if len(records) >= 2:  # Only include themes with at least 2 records
                suggestions.append({
                    "theme": theme,
                    "count": len(records),
                    "average_rating": sum(r["rating"] for r in records) / len(records),
                    "examples": [r["feedback_text"] for r in records if r["feedback_text"]][:3]
                })
        
        # Sort by count (most common issues first)
        suggestions = sorted(suggestions, key=lambda x: x["count"], reverse=True)
        
        return suggestions
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Input text
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction
        # In a real implementation, this would use NLP techniques
        
        # Convert to lowercase and split
        words = text.lower().split()
        
        # Remove common words
        common_words = {"the", "a", "an", "and", "or", "but", "is", "are", "was", "were", 
                       "in", "on", "at", "to", "for", "with", "by", "about", "like", 
                       "from", "of", "that", "this", "these", "those", "it", "they", 
                       "he", "she", "we", "you", "i", "not", "very", "too", "so"}
        
        keywords = [word for word in words if word not in common_words and len(word) > 3]
        
        # Return unique keywords
        return list(set(keywords))
    
    def compare_models(self, model1: str, model2: str) -> Dict[str, Any]:
        """
        Compare two models based on feedback.
        
        Args:
            model1: First model key (provider/model)
            model2: Second model key (provider/model)
            
        Returns:
            Comparison results
        """
        # Get performance data
        performance = self.get_model_performance()
        
        if model1 not in performance or model2 not in performance:
            return {"error": "One or both models not found in feedback data"}
        
        model1_data = performance[model1]
        model2_data = performance[model2]
        
        # Get feedback for each model
        model1_feedback = self.get_feedback_history(
            provider=model1.split("/")[0],
            model=model1.split("/")[1]
        )
        
        model2_feedback = self.get_feedback_history(
            provider=model2.split("/")[0],
            model=model2.split("/")[1]
        )
        
        # Compare ratings
        rating_diff = model1_data["average_rating"] - model2_data["average_rating"]
        
        # Compare tags
        model1_tags = set(model1_data["common_tags"].keys())
        model2_tags = set(model2_data["common_tags"].keys())
        
        common_tags = model1_tags.intersection(model2_tags)
        unique_model1_tags = model1_tags - model2_tags
        unique_model2_tags = model2_tags - model1_tags
        
        return {
            "model1": {
                "key": model1,
                "average_rating": model1_data["average_rating"],
                "total_ratings": model1_data["total_ratings"],
                "unique_strengths": list(unique_model1_tags)
            },
            "model2": {
                "key": model2,
                "average_rating": model2_data["average_rating"],
                "total_ratings": model2_data["total_ratings"],
                "unique_strengths": list(unique_model2_tags)
            },
            "comparison": {
                "rating_difference": rating_diff,
                "common_strengths": list(common_tags),
                "winner": model1 if rating_diff > 0 else (model2 if rating_diff < 0 else "tie")
            }
        }
    
    def get_supported_tags(self) -> List[str]:
        """
        Get list of supported feedback tags.
        
        Returns:
            List of supported tags
        """
        return [
            "accurate", "inaccurate", "helpful", "unhelpful", "creative", 
            "uncreative", "concise", "verbose", "clear", "unclear", 
            "relevant", "irrelevant", "fast", "slow", "complete", "incomplete",
            "code_quality", "code_error", "good_explanation", "poor_explanation",
            "hallucination", "factual", "biased", "unbiased"
        ]
