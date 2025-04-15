import logging
import os
import time
from typing import Dict, Any, Optional, List

class PerformanceMonitor:
    """
    Monitors and logs performance metrics for the multi-AI application.
    Tracks response times, success rates, and resource usage.
    """
    
    def __init__(self, log_dir: str = None):
        """
        Initialize the performance monitor.
        
        Args:
            log_dir: Directory to store log files
        """
        # Set up logging directory
        self.log_dir = log_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Configure logger
        self.logger = self._setup_logger()
        
        # Initialize metrics storage
        self.request_times = {}
        self.success_rates = {}
        self.request_counts = {}
        self.error_counts = {}
        
        # Track current requests
        self.active_requests = {}
    
    def _setup_logger(self) -> logging.Logger:
        """Set up the performance logger."""
        logger = logging.getLogger("performance_monitor")
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = os.path.join(self.log_dir, "performance.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
        return logger
    
    def start_request(self, request_id: str, model: str) -> None:
        """
        Start tracking a new request.
        
        Args:
            request_id: Unique identifier for the request
            model: The AI model being used
        """
        self.active_requests[request_id] = {
            "model": model,
            "start_time": time.time(),
            "status": "in_progress"
        }
    
    def end_request(self, request_id: str, success: bool, error_type: str = None) -> float:
        """
        End tracking for a request and record metrics.
        
        Args:
            request_id: Unique identifier for the request
            success: Whether the request was successful
            error_type: Type of error if the request failed
            
        Returns:
            Duration of the request in seconds
        """
        if request_id not in self.active_requests:
            self.logger.warning(f"Attempted to end unknown request: {request_id}")
            return 0.0
        
        # Calculate duration
        request_data = self.active_requests[request_id]
        model = request_data["model"]
        start_time = request_data["start_time"]
        duration = time.time() - start_time
        
        # Update metrics
        if model not in self.request_times:
            self.request_times[model] = []
            self.success_rates[model] = {"success": 0, "total": 0}
            self.request_counts[model] = 0
            self.error_counts[model] = {}
        
        self.request_times[model].append(duration)
        self.success_rates[model]["total"] += 1
        self.request_counts[model] += 1
        
        if success:
            self.success_rates[model]["success"] += 1
            status = "success"
        else:
            status = "error"
            error_type = error_type or "unknown"
            if error_type not in self.error_counts[model]:
                self.error_counts[model][error_type] = 0
            self.error_counts[model][error_type] += 1
        
        # Log the request
        self.logger.info(
            f"Request {request_id} to {model} completed with status {status} in {duration:.2f}s"
        )
        
        # Remove from active requests
        self.active_requests.pop(request_id)
        
        return duration
    
    def get_metrics(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Args:
            model: Optional model name to filter metrics
            
        Returns:
            Dictionary with performance metrics
        """
        if model and model in self.request_times:
            return self._get_model_metrics(model)
        
        # Get metrics for all models
        metrics = {
            "overall": {
                "total_requests": sum(self.request_counts.values()),
                "average_response_time": self._calculate_overall_average(),
                "success_rate": self._calculate_overall_success_rate(),
                "error_distribution": self._calculate_overall_error_distribution()
            },
            "models": {}
        }
        
        for model_name in self.request_times:
            metrics["models"][model_name] = self._get_model_metrics(model_name)
        
        return metrics
    
    def _get_model_metrics(self, model: str) -> Dict[str, Any]:
        """Get metrics for a specific model."""
        times = self.request_times[model]
        success_data = self.success_rates[model]
        
        if not times:
            return {
                "requests": 0,
                "average_response_time": 0,
                "success_rate": 0,
                "error_types": {}
            }
        
        avg_time = sum(times) / len(times)
        success_rate = (success_data["success"] / success_data["total"]) * 100 if success_data["total"] > 0 else 0
        
        return {
            "requests": self.request_counts[model],
            "average_response_time": avg_time,
            "success_rate": success_rate,
            "error_types": self.error_counts.get(model, {})
        }
    
    def _calculate_overall_average(self) -> float:
        """Calculate the overall average response time across all models."""
        all_times = []
        for model in self.request_times:
            all_times.extend(self.request_times[model])
        
        if not all_times:
            return 0.0
        
        return sum(all_times) / len(all_times)
    
    def _calculate_overall_success_rate(self) -> float:
        """Calculate the overall success rate across all models."""
        total_success = sum(data["success"] for data in self.success_rates.values())
        total_requests = sum(data["total"] for data in self.success_rates.values())
        
        if total_requests == 0:
            return 0.0
        
        return (total_success / total_requests) * 100
    
    def _calculate_overall_error_distribution(self) -> Dict[str, int]:
        """Calculate the overall error distribution across all models."""
        error_distribution = {}
        
        for model in self.error_counts:
            for error_type, count in self.error_counts[model].items():
                if error_type not in error_distribution:
                    error_distribution[error_type] = 0
                error_distribution[error_type] += count
        
        return error_distribution
    
    def log_cache_metrics(self, cache_stats: Dict[str, Any]) -> None:
        """
        Log cache performance metrics.
        
        Args:
            cache_stats: Statistics from the cache manager
        """
        self.logger.info(f"Cache stats: {cache_stats}")
    
    def cleanup_stale_requests(self, timeout: float = 300.0) -> List[str]:
        """
        Clean up tracking for stale requests that were never completed.
        
        Args:
            timeout: Time in seconds after which a request is considered stale
            
        Returns:
            List of request IDs that were cleaned up
        """
        current_time = time.time()
        stale_requests = []
        
        for request_id, data in list(self.active_requests.items()):
            if current_time - data["start_time"] > timeout:
                model = data["model"]
                duration = current_time - data["start_time"]
                
                # Log the stale request
                self.logger.warning(
                    f"Request {request_id} to {model} timed out after {duration:.2f}s"
                )
                
                # Update metrics
                if model not in self.request_times:
                    self.request_times[model] = []
                    self.success_rates[model] = {"success": 0, "total": 0}
                    self.request_counts[model] = 0
                    self.error_counts[model] = {}
                
                self.request_times[model].append(duration)
                self.success_rates[model]["total"] += 1
                self.request_counts[model] += 1
                
                # Count as timeout error
                if "timeout" not in self.error_counts[model]:
                    self.error_counts[model]["timeout"] = 0
                self.error_counts[model]["timeout"] += 1
                
                # Remove from active requests
                self.active_requests.pop(request_id)
                stale_requests.append(request_id)
        
        return stale_requests
