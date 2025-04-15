import os
import time
import json
from typing import Dict, Any, Optional, List

class CacheManager:
    """
    Manages caching for the Multi-AI application.
    Stores responses to avoid redundant API calls and improve performance.
    """
    
    def __init__(self, max_cache_size: int = 1000, cache_ttl: int = 3600):
        """
        Initialize the cache manager.
        
        Args:
            max_cache_size: Maximum number of items to store in cache
            cache_ttl: Time-to-live for cache entries in seconds
        """
        self.max_cache_size = max_cache_size
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "active_entries": 0,
            "evictions": 0
        }
        self.storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache")
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Load persistent cache if available
        self._load_persistent_cache()
    
    def get(self, prompt: str, model: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get a cached response.
        
        Args:
            prompt: The user prompt
            model: The model used
            params: Additional parameters used for the request
            
        Returns:
            Cached response or None if not found
        """
        # Create cache key
        cache_key = self._create_cache_key(prompt, model, params)
        
        # Check if key exists in cache
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            
            # Check if entry is expired
            if time.time() - cache_entry["timestamp"] > self.cache_ttl:
                # Remove expired entry
                del self.cache[cache_key]
                self.cache_stats["active_entries"] -= 1
                self.cache_stats["misses"] += 1
                return None
            
            # Update access time and hit count
            cache_entry["last_accessed"] = time.time()
            cache_entry["hits"] += 1
            
            # Update cache stats
            self.cache_stats["hits"] += 1
            
            return cache_entry["response"]
        
        # Cache miss
        self.cache_stats["misses"] += 1
        return None
    
    def set(self, prompt: str, model: str, response: Dict[str, Any], params: Dict[str, Any]) -> None:
        """
        Set a cache entry.
        
        Args:
            prompt: The user prompt
            model: The model used
            response: The response to cache
            params: Additional parameters used for the request
        """
        # Create cache key
        cache_key = self._create_cache_key(prompt, model, params)
        
        # Check if cache is full
        if len(self.cache) >= self.max_cache_size:
            # Evict least recently used entry
            self._evict_lru()
        
        # Add entry to cache
        self.cache[cache_key] = {
            "prompt": prompt,
            "model": model,
            "response": response,
            "params": params,
            "timestamp": time.time(),
            "last_accessed": time.time(),
            "hits": 0
        }
        
        # Update cache stats
        self.cache_stats["active_entries"] += 1
        
        # Periodically save cache to disk
        if self.cache_stats["active_entries"] % 10 == 0:
            self._save_persistent_cache()
    
    def clear(self) -> int:
        """
        Clear the entire cache.
        
        Returns:
            Number of entries cleared
        """
        entries_cleared = len(self.cache)
        self.cache = {}
        self.cache_stats["active_entries"] = 0
        
        return entries_cleared
    
    def clear_expired(self) -> int:
        """
        Clear expired cache entries.
        
        Returns:
            Number of entries cleared
        """
        current_time = time.time()
        expired_keys = []
        
        # Find expired entries
        for key, entry in self.cache.items():
            if current_time - entry["timestamp"] > self.cache_ttl:
                expired_keys.append(key)
        
        # Remove expired entries
        for key in expired_keys:
            del self.cache[key]
        
        # Update cache stats
        self.cache_stats["active_entries"] -= len(expired_keys)
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict containing cache statistics
        """
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "active_entries": self.cache_stats["active_entries"],
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "evictions": self.cache_stats["evictions"],
            "hit_rate": hit_rate
        }
    
    def _create_cache_key(self, prompt: str, model: str, params: Dict[str, Any]) -> str:
        """
        Create a cache key from prompt, model, and params.
        
        Args:
            prompt: The user prompt
            model: The model used
            params: Additional parameters
            
        Returns:
            Cache key string
        """
        # Extract relevant parameters that affect the response
        relevant_params = {}
        for key in ["temperature", "max_tokens"]:
            if key in params:
                relevant_params[key] = params[key]
        
        # Create a string representation
        key_parts = [
            prompt.strip(),
            model,
            json.dumps(relevant_params, sort_keys=True)
        ]
        
        # Join and hash
        import hashlib
        key_string = "||".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _evict_lru(self) -> None:
        """Evict the least recently used cache entry."""
        if not self.cache:
            return
        
        # Find the least recently accessed entry
        lru_key = min(self.cache.keys(), key=lambda k: self.cache[k]["last_accessed"])
        
        # Remove the entry
        del self.cache[lru_key]
        
        # Update cache stats
        self.cache_stats["active_entries"] -= 1
        self.cache_stats["evictions"] += 1
    
    def _save_persistent_cache(self) -> None:
        """Save cache to disk for persistence."""
        try:
            # Create a filename
            filename = "cache.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Prepare the data (only save a subset of entries to avoid large files)
            # Sort by hits (most used first)
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1]["hits"],
                reverse=True
            )
            
            # Take top 100 entries
            top_entries = dict(sorted_entries[:100])
            
            # Save to file
            with open(filepath, "w") as f:
                json.dump({
                    "cache": top_entries,
                    "stats": self.cache_stats,
                    "timestamp": time.time()
                }, f)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _load_persistent_cache(self) -> None:
        """Load cache from disk."""
        try:
            # Create a filename
            filename = "cache.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Check if file exists
            if not os.path.exists(filepath):
                return
            
            # Read from file
            with open(filepath, "r") as f:
                data = json.load(f)
            
            # Load cache entries
            self.cache = data.get("cache", {})
            
            # Load cache stats
            self.cache_stats = data.get("stats", {
                "hits": 0,
                "misses": 0,
                "active_entries": len(self.cache),
                "evictions": 0
            })
            
            # Update active entries count
            self.cache_stats["active_entries"] = len(self.cache)
            
            # Clear expired entries
            self.clear_expired()
        except Exception as e:
            print(f"Error loading cache: {e}")
            # Initialize empty cache
            self.cache = {}
            self.cache_stats = {
                "hits": 0,
                "misses": 0,
                "active_entries": 0,
                "evictions": 0
            }
