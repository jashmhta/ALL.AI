import asyncio
import time
from typing import Dict, Any, Optional, Callable, List, Set
import uuid

class RateLimiter:
    """
    Implements rate limiting for API calls to prevent quota exhaustion.
    Uses the token bucket algorithm for flexible rate limiting.
    """
    
    def __init__(self, rate: float, per: float, burst: int = 1):
        """
        Initialize the rate limiter.
        
        Args:
            rate: Number of tokens to add per time period
            per: Time period in seconds
            burst: Maximum number of tokens that can be accumulated
        """
        self.rate = rate
        self.per = per
        self.burst = burst
        
        self.tokens = burst
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """
        Acquire a token from the bucket.
        
        Returns:
            True if a token was acquired, False otherwise
        """
        async with self.lock:
            # Update tokens based on elapsed time
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * (self.rate / self.per))
            self.last_update = now
            
            # Check if we have a token available
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            else:
                return False
    
    async def wait(self) -> None:
        """Wait until a token is available."""
        while True:
            if await self.acquire():
                return
            
            # Calculate time to wait before next token
            async with self.lock:
                time_to_next_token = (1 - self.tokens) * (self.per / self.rate)
                
            # Wait a bit before trying again
            await asyncio.sleep(min(time_to_next_token, 1.0))

class RequestQueue:
    """
    Manages a queue of requests to control concurrency and prioritize requests.
    """
    
    def __init__(self, max_concurrent: int = 10, max_queue_size: int = 100):
        """
        Initialize the request queue.
        
        Args:
            max_concurrent: Maximum number of concurrent requests
            max_queue_size: Maximum size of the queue
        """
        self.max_concurrent = max_concurrent
        self.max_queue_size = max_queue_size
        
        self.active_requests: Set[str] = set()
        self.queue: List[Dict[str, Any]] = []
        self.lock = asyncio.Lock()
        self.not_full = asyncio.Condition(self.lock)
        self.not_empty = asyncio.Condition(self.lock)
    
    async def add_request(self, request_id: str, priority: int = 0) -> bool:
        """
        Add a request to the queue.
        
        Args:
            request_id: Unique identifier for the request
            priority: Priority level (higher values = higher priority)
            
        Returns:
            True if the request was added, False if the queue is full
        """
        async with self.lock:
            # Check if queue is full
            if len(self.queue) >= self.max_queue_size:
                return False
            
            # Add request to queue
            self.queue.append({
                "id": request_id,
                "priority": priority,
                "timestamp": time.time()
            })
            
            # Sort queue by priority (higher first) and then by timestamp (older first)
            self.queue.sort(key=lambda x: (-x["priority"], x["timestamp"]))
            
            # Notify that queue is not empty
            async with self.not_empty:
                self.not_empty.notify()
            
            return True
    
    async def get_next_request(self) -> Optional[str]:
        """
        Get the next request from the queue if we're below max_concurrent.
        
        Returns:
            Request ID or None if no requests are available or at max concurrency
        """
        async with self.lock:
            # Wait until queue is not empty
            while len(self.queue) == 0:
                async with self.not_empty:
                    await self.not_empty.wait()
            
            # Check if we're at max concurrency
            if len(self.active_requests) >= self.max_concurrent:
                return None
            
            # Get next request
            request = self.queue.pop(0)
            request_id = request["id"]
            
            # Add to active requests
            self.active_requests.add(request_id)
            
            # Notify that queue is not full
            async with self.not_full:
                self.not_full.notify()
            
            return request_id
    
    async def complete_request(self, request_id: str) -> None:
        """
        Mark a request as completed.
        
        Args:
            request_id: Unique identifier for the request
        """
        async with self.lock:
            # Remove from active requests
            if request_id in self.active_requests:
                self.active_requests.remove(request_id)
            
            # Notify that we're below max concurrency
            async with self.not_full:
                self.not_full.notify()
    
    async def process_queue(self, processor: Callable[[str], Any]) -> None:
        """
        Process requests from the queue.
        
        Args:
            processor: Function to process each request
        """
        while True:
            request_id = await self.get_next_request()
            
            if request_id:
                # Process the request in a separate task
                asyncio.create_task(self._process_request(request_id, processor))
            else:
                # Wait a bit before checking again
                await asyncio.sleep(0.1)
    
    async def _process_request(self, request_id: str, processor: Callable[[str], Any]) -> None:
        """Process a single request and mark it as completed."""
        try:
            await processor(request_id)
        except Exception as e:
            # Log the error but don't crash the queue processor
            print(f"Error processing request {request_id}: {e}")
        finally:
            # Always mark the request as completed
            await self.complete_request(request_id)

class ResourceManager:
    """
    Manages resources for the multi-AI application.
    Handles rate limiting, request queuing, and connection pooling.
    """
    
    def __init__(self):
        """Initialize the resource manager."""
        # Rate limiters for each model
        self.rate_limiters = {
            "openai": RateLimiter(rate=60, per=60, burst=10),  # 60 requests per minute
            "gemini": RateLimiter(rate=60, per=60, burst=10),  # 60 requests per minute
            "huggingface": RateLimiter(rate=30, per=60, burst=5),  # 30 requests per minute
            "claude": RateLimiter(rate=40, per=60, burst=5),  # 40 requests per minute
            "llama": RateLimiter(rate=20, per=60, burst=3),  # 20 requests per minute
            "openrouter": RateLimiter(rate=20, per=60, burst=3),  # 20 requests per minute
        }
        
        # Request queue
        self.request_queue = RequestQueue(max_concurrent=20, max_queue_size=100)
        
        # Start queue processor
        asyncio.create_task(self.request_queue.process_queue(self._process_request))
        
        # Track active requests
        self.active_requests = {}
    
    async def submit_request(
        self,
        model: str,
        func: Callable[..., Any],
        *args: Any,
        priority: int = 0,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Submit a request to be processed with resource management.
        
        Args:
            model: The AI model to use
            func: Function to execute
            *args: Arguments to pass to the function
            priority: Priority level (higher values = higher priority)
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Result of the function or error response
        """
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # Store request details
        self.active_requests[request_id] = {
            "model": model,
            "func": func,
            "args": args,
            "kwargs": kwargs,
            "future": asyncio.Future()
        }
        
        # Add to queue
        if not await self.request_queue.add_request(request_id, priority):
            # Queue is full
            return {
                "text": f"System is currently overloaded. Please try again later.",
                "model": model,
                "success": False,
                "error": "queue_full"
            }
        
        # Wait for result
        try:
            result = await self.active_requests[request_id]["future"]
            return result
        except asyncio.CancelledError:
            # Request was cancelled
            return {
                "text": f"Request was cancelled.",
                "model": model,
                "success": False,
                "error": "cancelled"
            }
        finally:
            # Clean up
            if request_id in self.active_requests:
                self.active_requests.pop(request_id)
    
    async def _process_request(self, request_id: str) -> None:
        """Process a request from the queue."""
        if request_id not in self.active_requests:
            return
        
        request = self.active_requests[request_id]
        model = request["model"]
        func = request["func"]
        args = request["args"]
        kwargs = request["kwargs"]
        future = request["future"]
        
        # Apply rate limiting
        if model in self.rate_limiters:
            await self.rate_limiters[model].wait()
        
        # Execute the function
        try:
            result = await func(*args, **kwargs)
            future.set_result(result)
        except Exception as e:
            # Set exception on future
            future.set_exception(e)
    
    def cancel_request(self, request_id: str) -> bool:
        """
        Cancel a pending request.
        
        Args:
            request_id: Unique identifier for the request
            
        Returns:
            True if the request was cancelled, False otherwise
        """
        if request_id in self.active_requests:
            future = self.active_requests[request_id]["future"]
            future.cancel()
            return True
        return False
