"""
Historical cache for geolocation results with intelligent TTL.
"""

import json
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .models import GeoLocationResult


class GeoLocationCache:
    """Cache for geolocation results with intelligent TTL based on IP type."""
    
    def __init__(self, cache_file: str = 'geolocation_cache.json'):
        self.cache_file = cache_file
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()
    
    def _load_cache(self):
        """Load cache from file."""
        try:
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.cache = {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception:
            pass
    
    def get(self, ip: str) -> Optional[GeoLocationResult]:
        """Get cached result if not expired."""
        if ip not in self.cache:
            return None
        
        cached = self.cache[ip]
        timestamp = datetime.fromisoformat(cached['timestamp'])
        ttl = self._get_ttl(cached.get('is_hosting', False), cached.get('is_cloudflare', False))
        
        if datetime.utcnow() - timestamp > timedelta(seconds=ttl):
            # Expired
            del self.cache[ip]
            self._save_cache()
            return None
        
        # Return cached result
        result = GeoLocationResult(
            ip=ip,
            cached=True,
            timestamp=timestamp
        )
        
        # Restore location data
        if 'location' in cached:
            from .models import Location, NetworkInfo, SecurityFlags
            result.location = Location(**cached['location'])
            result.network = NetworkInfo(**cached.get('network', {}))
            result.security = SecurityFlags(**cached.get('security', {}))
            result.confidence = cached.get('confidence', 0.0)
            result.confidence_level = cached.get('confidence_level', 'LOW')
            result.explanation = cached.get('explanation', '')
            result.provider_breakdown = cached.get('provider_breakdown', [])
            result.providers_used = cached.get('providers_used', [])
        
        return result
    
    def set(self, result: GeoLocationResult, is_hosting: bool = False, is_cloudflare: bool = False):
        """Cache a result with appropriate TTL."""
        ttl = self._get_ttl(is_hosting, is_cloudflare)
        
        self.cache[result.ip] = {
            'location': result.location.to_dict(),
            'network': result.network.to_dict(),
            'security': result.security.to_dict(),
            'confidence': result.confidence,
            'confidence_level': result.confidence_level,
            'explanation': result.explanation,
            'provider_breakdown': result.provider_breakdown,
            'providers_used': result.providers_used,
            'timestamp': result.timestamp.isoformat(),
            'is_hosting': is_hosting,
            'is_cloudflare': is_cloudflare,
            'ttl': ttl
        }
        
        self._save_cache()
    
    def _get_ttl(self, is_hosting: bool, is_cloudflare: bool) -> int:
        """Determine TTL based on IP type."""
        if is_cloudflare:
            return 7 * 24 * 3600  # 7 days for Cloudflare
        elif is_hosting:
            return 7 * 24 * 3600  # 7 days for hosting
        else:
            return 24 * 3600  # 24 hours for residential/unknown
    
    def clear(self):
        """Clear the entire cache."""
        self.cache = {}
        self._save_cache()
    
    def cleanup_expired(self):
        """Remove expired entries from cache."""
        now = datetime.utcnow()
        expired_keys = []
        
        for ip, data in self.cache.items():
            timestamp = datetime.fromisoformat(data['timestamp'])
            ttl = data.get('ttl', 24 * 3600)
            if now - timestamp > timedelta(seconds=ttl):
                expired_keys.append(ip)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self._save_cache()
