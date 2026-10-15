import time
from typing import Dict, Any, Optional


class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, ttl: int = 3600):
        """
        Initialize cache.
        
        Args:
            ttl: Time to live in seconds (default: 1 hour)
        """
        self.cache: Dict[str, tuple] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if expired/not found
        """
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                # Expired, remove from cache
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache with current timestamp.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
    
    def delete(self, key: str) -> None:
        """
        Delete specific cache entry.
        
        Args:
            key: Cache key to delete
        """
        if key in self.cache:
            del self.cache[key]


# Global cache instance
dns_cache = SimpleCache(ttl=3600)  # 1 hour TTL for DNS results
