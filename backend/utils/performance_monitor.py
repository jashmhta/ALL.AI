import os
import time
from typing import Dict, Any, Optional, List

class PerformanceMonitor:
    """
    Monitors performance metrics for the Multi-AI application.
    Tracks response times, success rates, and other performance indicators.
    """
    
    def __init__(self, metrics_retention_period: int = 3600):
        """
        Initialize the performance monitor.
        
        Args:
            metrics_retention_period: Time in seconds to retain metrics
        """
        self.metrics_retention_period = metrics_retention_period
        self.requests = {}
        self.model_metrics = {}
        self.last_cleanup = time.time()
    
    def start_request(self, request_id: str, model: str) -> None:
        """
        Start tracking a request.
        
        Args:
            request_id: Unique identifier for the request
            model: The model or service being used
        """
        self.requests[request_id] = {
            "model": model,
            "start_time": time.time(),
            "end_time": None,
            "success": None,
            "error_type": None
        }
    
    def end_request(self, request_id: str, success: bool, error_type: Optional[str] = None) -> None:
        """
        End tracking a request.
        
        Args:
            request_id: Unique identifier for the request
            success: Whether the request was successful
            error_type: Type of error if the request failed
        """
        if request_id not in self.requests:
            return
        
        # Update request data
        self.requests[request_id]["end_time"] = time.time()
        self.requests[request_id]["success"] = success
        self.requests[request_id]["error_type"] = error_type
        
        # Calculate response time
        start_time = self.requests[request_id]["start_time"]
        end_time = self.requests[request_id]["end_time"]
        response_time = end_time - start_time
        
        # Get model
        model = self.requests[request_id]["model"]
        
        # Update model metrics
        if model not in self.model_metrics:
            self.model_metrics[model] = {
                "requests": 0,
                "successful_requests": 0,
                "total_response_time": 0,
                "error_counts": {}
            }
        
        self.model_metrics[model]["requests"] += 1
        
        if success:
            self.model_metrics[model]["successful_requests"] += 1
        elif error_type:
            if error_type not in self.model_metrics[model]["error_counts"]:
                self.model_metrics[model]["error_counts"][error_type] = 0
            self.model_metrics[model]["error_counts"][error_type] += 1
        
        self.model_metrics[model]["total_response_time"] += response_time
        
        # Periodically clean up old requests
        current_time = time.time()
        if current_time - self.last_cleanup > 300:  # Clean up every 5 minutes
            self.cleanup_stale_requests()
            self.last_cleanup = current_time
    
    def cleanup_stale_requests(self) -> None:
        """Clean up stale request data."""
        current_time = time.time()
        stale_requests = []
        
        for request_id, request_data in self.requests.items():
            # If the request has ended and is older than the retention period
            if request_data["end_time"] and current_time - request_data["end_time"] > self.metrics_retention_period:
                stale_requests.append(request_id)
        
        # Remove stale requests
        for request_id in stale_requests:
            del self.requests[request_id]
    
    def get_metrics(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Args:
            model: Optional model to get metrics for
            
        Returns:
            Dict containing performance metrics
        """
        metrics = {
            "overall": self._calculate_overall_metrics(),
            "models": {}
        }
        
        # Add metrics for each model
        for model_name, model_data in self.model_metrics.items():
            if model and model != model_name:
                continue
                
            metrics["models"][model_name] = self._calculate_model_metrics(model_name)
        
        return metrics
    
    def _calculate_overall_metrics(self) -> Dict[str, Any]:
        """
        Calculate overall performance metrics.
        
        Returns:
            Dict containing overall metrics
        """
        total_requests = sum(model_data["requests"] for model_data in self.model_metrics.values())
        successful_requests = sum(model_data["successful_requests"] for model_data in self.model_metrics.values())
        total_response_time = sum(model_data["total_response_time"] for model_data in self.model_metrics.values())
        
        if total_requests > 0:
            success_rate = (successful_requests / total_requests) * 100
            average_response_time = total_response_time / total_requests
        else:
            success_rate = 0
            average_response_time = 0
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": success_rate,
            "average_response_time": average_response_time
        }
    
    def _calculate_model_metrics(self, model: str) -> Dict[str, Any]:
        """
        Calculate metrics for a specific model.
        
        Args:
            model: The model to calculate metrics for
            
        Returns:
            Dict containing model metrics
        """
        model_data = self.model_metrics.get(model, {
            "requests": 0,
            "successful_requests": 0,
            "total_response_time": 0,
            "error_counts": {}
        })
        
        if model_data["requests"] > 0:
            success_rate = (model_data["successful_requests"] / model_data["requests"]) * 100
            average_response_time = model_data["total_response_time"] / model_data["requests"]
        else:
            success_rate = 0
            average_response_time = 0
        
        return {
            "requests": model_data["requests"],
            "successful_requests": model_data["successful_requests"],
            "success_rate": success_rate,
            "average_response_time": average_response_time,
            "error_counts": model_data["error_counts"]
        }
    
    def log_cache_metrics(self, cache_stats: Dict[str, Any]) -> None:
        """
        Log cache metrics.
        
        Args:
            cache_stats: Statistics from the cache
        """
        # This would typically store cache metrics for reporting
        # For now, we'll just print them
        print(f"Cache stats: {cache_stats}")
