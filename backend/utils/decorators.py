import asyncio
import functools
import time
from typing import Callable, Any, Optional

def with_timeout(timeout_seconds: float = 30.0):
    """
    Decorator to add timeout to async functions.
    
    Args:
        timeout_seconds: Maximum execution time in seconds
        
    Returns:
        Decorated function with timeout
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                return {
                    "text": f"Request timed out after {timeout_seconds} seconds.",
                    "model": kwargs.get("model", "unknown"),
                    "success": False,
                    "error": "timeout"
                }
        return wrapper
    return decorator

def retry_with_backoff(max_retries: int = 3, initial_backoff: float = 1.0, 
                      backoff_factor: float = 2.0, max_backoff: float = 10.0):
    """
    Decorator to retry async functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_backoff: Initial backoff time in seconds
        backoff_factor: Factor to increase backoff time with each retry
        max_backoff: Maximum backoff time in seconds
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            backoff = initial_backoff
            
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    
                    if retries > max_retries:
                        # If it's a dict-like error response, return it
                        if isinstance(e, dict) and "success" in e and not e["success"]:
                            return e
                            
                        # Otherwise, create an error response
                        return {
                            "text": f"Error after {max_retries} retries: {str(e)}",
                            "model": kwargs.get("model", "unknown"),
                            "success": False,
                            "error": "max_retries_exceeded"
                        }
                    
                    # Calculate backoff time
                    backoff = min(backoff * backoff_factor, max_backoff)
                    
                    # Wait before retrying
                    await asyncio.sleep(backoff)
        return wrapper
    return decorator

def measure_performance(func):
    """
    Decorator to measure function execution time.
    
    Args:
        func: Function to measure
        
    Returns:
        Decorated function with performance measurement
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            
            # Add execution time to result if it's a dict
            if isinstance(result, dict):
                result["execution_time"] = time.time() - start_time
                
            return result
        except Exception as e:
            # If an exception occurs, return an error response with execution time
            return {
                "text": f"Error: {str(e)}",
                "model": kwargs.get("model", "unknown"),
                "success": False,
                "error": "execution_error",
                "execution_time": time.time() - start_time
            }
    return wrapper

def log_api_call(func):
    """
    Decorator to log API calls.
    
    Args:
        func: Function to log
        
    Returns:
        Decorated function with logging
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract model name from kwargs
        model = kwargs.get("model", "unknown")
        
        # Log the API call
        print(f"API Call: {func.__name__} to {model} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Call the original function
        result = await func(*args, **kwargs)
        
        # Log the result status
        success = result.get("success", False)
        print(f"API Result: {func.__name__} to {model} - {'Success' if success else 'Failed'}")
        
        return result
    return wrapper
