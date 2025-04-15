import asyncio
import functools
from typing import Any, Callable, Dict, Optional, TypeVar, cast

T = TypeVar('T')

class TimeoutError(Exception):
    """Exception raised when a function call times out."""
    pass

def with_timeout(timeout: float):
    """
    Decorator that adds timeout functionality to async functions.
    
    Args:
        timeout: Maximum execution time in seconds
        
    Returns:
        Decorated function with timeout handling
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                # Create a task for the function
                task = asyncio.create_task(func(*args, **kwargs))
                
                # Wait for the task to complete with timeout
                return await asyncio.wait_for(task, timeout=timeout)
            except asyncio.TimeoutError:
                # Cancel the task if it times out
                task.cancel()
                
                # Determine the function name and arguments for error reporting
                func_name = func.__name__
                model_name = "unknown"
                
                # Try to extract model name from arguments if available
                if len(args) > 0 and hasattr(args[0], '__class__'):
                    class_name = args[0].__class__.__name__
                    if 'Client' in class_name:
                        model_name = class_name.replace('Client', '').lower()
                
                # Return error response
                return {
                    "text": f"Request to {model_name} timed out after {timeout} seconds.",
                    "model": model_name,
                    "success": False,
                    "error": "timeout"
                }
        
        return wrapper
    
    return decorator

async def retry_with_backoff(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = 3,
    initial_backoff: float = 1.0,
    backoff_factor: float = 2.0,
    **kwargs: Any
) -> Any:
    """
    Execute a function with exponential backoff retry logic.
    
    Args:
        func: Async function to execute
        *args: Arguments to pass to the function
        max_retries: Maximum number of retry attempts
        initial_backoff: Initial backoff time in seconds
        backoff_factor: Factor to multiply backoff time by after each attempt
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Result of the function or error response after max retries
    """
    retries = 0
    backoff = initial_backoff
    
    while retries <= max_retries:
        try:
            result = await func(*args, **kwargs)
            
            # If the result indicates success or it's not a dict, return it
            if not isinstance(result, dict) or result.get("success", True):
                return result
            
            # If it's a timeout error, don't retry
            if result.get("error") == "timeout":
                return result
            
            # For other errors, retry with backoff
            retries += 1
            if retries > max_retries:
                return result
            
            # Wait before retrying
            await asyncio.sleep(backoff)
            backoff *= backoff_factor
            
        except Exception as e:
            # For exceptions, retry with backoff
            retries += 1
            if retries > max_retries:
                # Determine model name for error reporting
                model_name = "unknown"
                if len(args) > 0 and hasattr(args[0], '__class__'):
                    class_name = args[0].__class__.__name__
                    if 'Client' in class_name:
                        model_name = class_name.replace('Client', '').lower()
                
                return {
                    "text": f"Error after {max_retries} retries: {str(e)}",
                    "model": model_name,
                    "success": False,
                    "error": "max_retries_exceeded"
                }
            
            # Wait before retrying
            await asyncio.sleep(backoff)
            backoff *= backoff_factor
    
    # This should never be reached due to the return in the loop
    return {
        "text": "Unknown error in retry logic",
        "model": "unknown",
        "success": False,
        "error": "retry_logic_error"
    }

class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern to prevent repeated calls to failing services.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 60.0,
        half_open_timeout: float = 30.0
    ):
        """
        Initialize the circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening the circuit
            reset_timeout: Time in seconds before attempting to reset (close) the circuit
            half_open_timeout: Time in seconds to wait in half-open state before fully closing
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_timeout = half_open_timeout
        
        # Circuit state: 'closed' (normal), 'open' (failing), 'half-open' (testing)
        self.state = 'closed'
        
        # Tracking
        self.failure_count = 0
        self.last_failure_time = 0
        self.last_success_time = 0
    
    async def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """
        Execute a function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Result of the function or error response if circuit is open
        """
        current_time = asyncio.get_event_loop().time()
        
        # Check if circuit is open
        if self.state == 'open':
            # Check if it's time to try resetting
            if current_time - self.last_failure_time >= self.reset_timeout:
                self.state = 'half-open'
            else:
                # Circuit is open, return error
                model_name = self._get_model_name(args)
                return {
                    "text": f"Service for {model_name} is currently unavailable due to repeated failures. Please try again later.",
                    "model": model_name,
                    "success": False,
                    "error": "circuit_open"
                }
        
        try:
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Check if the result indicates success
            if isinstance(result, dict) and not result.get("success", True):
                self._handle_failure(current_time)
            else:
                self._handle_success(current_time)
            
            return result
            
        except Exception as e:
            # Handle failure
            self._handle_failure(current_time)
            
            # Return error response
            model_name = self._get_model_name(args)
            return {
                "text": f"Error: {str(e)}",
                "model": model_name,
                "success": False,
                "error": "execution_error"
            }
    
    def _handle_success(self, current_time: float) -> None:
        """Handle successful execution."""
        self.last_success_time = current_time
        
        if self.state == 'half-open':
            # If we've been in half-open state long enough with success, close the circuit
            if current_time - self.last_failure_time >= self.half_open_timeout:
                self.state = 'closed'
                self.failure_count = 0
        else:
            # Reset failure count on success in closed state
            self.failure_count = 0
    
    def _handle_failure(self, current_time: float) -> None:
        """Handle failed execution."""
        self.last_failure_time = current_time
        self.failure_count += 1
        
        # If we've reached the threshold, open the circuit
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
    
    def _get_model_name(self, args: tuple) -> str:
        """Extract model name from arguments if possible."""
        model_name = "unknown"
        if len(args) > 0 and hasattr(args[0], '__class__'):
            class_name = args[0].__class__.__name__
            if 'Client' in class_name:
                model_name = class_name.replace('Client', '').lower()
        return model_name
