import os
import json
import time
import hashlib
import sqlite3
from typing import Dict, Any, Optional, Tuple

class CacheManager:
    """
    Manages caching of AI responses to improve performance and reduce API calls.
    Implements a SQLite-based persistent cache with TTL (Time-To-Live) functionality.
    """
    
    def __init__(self, cache_dir: str = None, ttl: int = 3600):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store the cache database
            ttl: Default Time-To-Live for cache entries in seconds (default: 1 hour)
        """
        # Set up cache directory
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Set default TTL
        self.default_ttl = ttl
        
        # Initialize database
        self.db_path = os.path.join(self.cache_dir, "response_cache.db")
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database and create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create cache table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS response_cache (
            key TEXT PRIMARY KEY,
            model TEXT,
            response TEXT,
            created_at INTEGER,
            expires_at INTEGER
        )
        ''')
        
        # Create index for faster expiration checks
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON response_cache(expires_at)')
        
        conn.commit()
        conn.close()
    
    def _generate_key(self, prompt: str, model: str, params: Dict[str, Any]) -> str:
        """
        Generate a unique cache key based on prompt, model, and parameters.
        
        Args:
            prompt: The user prompt
            model: The AI model name
            params: Additional parameters for the request
            
        Returns:
            A unique hash key for the cache entry
        """
        # Create a string representation of the request
        key_data = {
            "prompt": prompt,
            "model": model,
            "params": params
        }
        key_str = json.dumps(key_data, sort_keys=True)
        
        # Generate a hash
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, prompt: str, model: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached response if available and not expired.
        
        Args:
            prompt: The user prompt
            model: The AI model name
            params: Additional parameters for the request
            
        Returns:
            The cached response or None if not found or expired
        """
        params = params or {}
        key = self._generate_key(prompt, model, params)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get the cached response
        cursor.execute(
            'SELECT response, expires_at FROM response_cache WHERE key = ?',
            (key,)
        )
        result = cursor.fetchone()
        
        if result:
            response_str, expires_at = result
            current_time = int(time.time())
            
            # Check if the cache entry has expired
            if expires_at > current_time:
                conn.close()
                return json.loads(response_str)
            else:
                # Remove expired entry
                cursor.execute('DELETE FROM response_cache WHERE key = ?', (key,))
                conn.commit()
        
        conn.close()
        return None
    
    def set(self, prompt: str, model: str, response: Dict[str, Any], 
            params: Dict[str, Any] = None, ttl: int = None) -> None:
        """
        Store a response in the cache.
        
        Args:
            prompt: The user prompt
            model: The AI model name
            response: The response to cache
            params: Additional parameters for the request
            ttl: Time-To-Live in seconds (uses default if not specified)
        """
        params = params or {}
        key = self._generate_key(prompt, model, params)
        
        # Set expiration time
        ttl = ttl or self.default_ttl
        current_time = int(time.time())
        expires_at = current_time + ttl
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store the response
        cursor.execute(
            'INSERT OR REPLACE INTO response_cache (key, model, response, created_at, expires_at) VALUES (?, ?, ?, ?, ?)',
            (key, model, json.dumps(response), current_time, expires_at)
        )
        
        conn.commit()
        conn.close()
    
    def clear_expired(self) -> int:
        """
        Clear all expired cache entries.
        
        Returns:
            Number of entries cleared
        """
        current_time = int(time.time())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM response_cache WHERE expires_at <= ?', (current_time,))
        cleared_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return cleared_count
    
    def clear_all(self) -> int:
        """
        Clear all cache entries regardless of expiration.
        
        Returns:
            Number of entries cleared
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM response_cache')
        cleared_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        current_time = int(time.time())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total entries
        cursor.execute('SELECT COUNT(*) FROM response_cache')
        total_entries = cursor.fetchone()[0]
        
        # Get active entries (not expired)
        cursor.execute('SELECT COUNT(*) FROM response_cache WHERE expires_at > ?', (current_time,))
        active_entries = cursor.fetchone()[0]
        
        # Get expired entries
        cursor.execute('SELECT COUNT(*) FROM response_cache WHERE expires_at <= ?', (current_time,))
        expired_entries = cursor.fetchone()[0]
        
        # Get model distribution
        cursor.execute('SELECT model, COUNT(*) FROM response_cache GROUP BY model')
        model_distribution = {model: count for model, count in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "model_distribution": model_distribution
        }
