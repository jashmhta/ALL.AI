import os
import asyncio
from typing import Dict, Any, Optional, List

class ResourceManager:
    """
    Manages resource allocation and request throttling for the Multi-AI application.
    Ensures fair distribution of resources and prevents overloading of API services.
    """
    
    def __init__(self, max_concurrent_requests: int = 10):
        """
        Initialize the resource manager.
        
        Args:
            max_concurrent_requests: Maximum number of concurrent requests allowed
        """
        self.max_concurrent_requests = max_concurrent_requests
        self.active_requests = {}
        self.request_semaphores = {}
        self.global_semaphore = asyncio.Semaphore(max_concurrent_requests)
    
    async def submit_request(self, model: str, decorator, func, *args, **kwargs) -> Dict[str, Any]:
        """
        Submit a request to be executed with resource management.
        
        Args:
            model: The model or service to use
            decorator: Decorator function to apply (e.g., retry_with_backoff)
            func: Async function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function execution
        """
        # Ensure model has a semaphore
        if model not in self.request_semaphores:
            # Limit each model to a portion of the total concurrent requests
            model_limit = max(1, self.max_concurrent_requests // 3)
            self.request_semaphores[model] = asyncio.Semaphore(model_limit)
            self.active_requests[model] = 0
        
        # Apply the decorator to the function
        decorated_func = decorator(func)
        
        # Acquire semaphores to manage concurrency
        async with self.global_semaphore:
            async with self.request_semaphores[model]:
                # Track active requests
                self.active_requests[model] += 1
                
                try:
                    # Execute the function
                    return await decorated_func(*args, **kwargs)
                finally:
                    # Release resources
                    self.active_requests[model] -= 1
    
    def get_active_request_count(self, model: Optional[str] = None) -> int:
        """
        Get the number of active requests.
        
        Args:
            model: Optional model to get count for
            
        Returns:
            Number of active requests
        """
        if model:
            return self.active_requests.get(model, 0)
        else:
            return sum(self.active_requests.values())
    
    def get_available_capacity(self, model: Optional[str] = None) -> int:
        """
        Get the available request capacity.
        
        Args:
            model: Optional model to get capacity for
            
        Returns:
            Number of additional requests that can be handled
        """
        if model:
            model_limit = self.request_semaphores[model]._value if model in self.request_semaphores else 0
            active = self.active_requests.get(model, 0)
            return max(0, model_limit - active)
        else:
            return max(0, self.global_semaphore._value)
