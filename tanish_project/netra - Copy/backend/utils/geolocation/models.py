"""
Data models for the geolocation intelligence engine.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ProviderData:
    """Normalized data from a single geolocation provider."""
    ip: str
    country: Optional[str] = None
    country_code: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    isp: Optional[str] = None
    organization: Optional[str] = None
    asn: Optional[str] = None
    proxy: bool = False
    vpn: bool = False
    hosting: bool = False
    mobile: bool = False
    tor: bool = False
    source: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'ip': self.ip,
            'country': self.country,
            'country_code': self.country_code,
            'region': self.region,
            'city': self.city,
            'postal_code': self.postal_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timezone': self.timezone,
            'isp': self.isp,
            'organization': self.organization,
            'asn': self.asn,
            'proxy': self.proxy,
            'vpn': self.vpn,
            'hosting': self.hosting,
            'mobile': self.mobile,
            'tor': self.tor,
            'source': self.source
        }


@dataclass
class SecurityFlags:
    """Security detection flags."""
    vpn: bool = False
    proxy: bool = False
    tor: bool = False
    hosting: bool = False
    mobile: bool = False
    
    def to_dict(self) -> Dict[str, bool]:
        return {
            'vpn': self.vpn,
            'proxy': self.proxy,
            'tor': self.tor,
            'hosting': self.hosting,
            'mobile': self.mobile
        }


@dataclass
class Location:
    """Final location data."""
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'country': self.country,
            'state': self.state,
            'city': self.city,
            'postal_code': self.postal_code,
            'latitude': self.latitude,
            'longitude': self.longitude
        }


@dataclass
class NetworkInfo:
    """Network information."""
    isp: Optional[str] = None
    organization: Optional[str] = None
    asn: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            'isp': self.isp,
            'organization': self.organization,
            'asn': self.asn
        }


@dataclass
class GeoLocationResult:
    """Final geolocation result with confidence scoring."""
    ip: str
    location: Location = field(default_factory=Location)
    network: NetworkInfo = field(default_factory=NetworkInfo)
    security: SecurityFlags = field(default_factory=SecurityFlags)
    confidence: float = 0.0
    confidence_level: str = "LOW"
    explanation: str = ""
    provider_breakdown: List[Dict[str, Any]] = field(default_factory=list)
    providers_used: List[str] = field(default_factory=list)
    cached: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            'ip': self.ip,
            'location': self.location.to_dict(),
            'network': self.network.to_dict(),
            'security': self.security.to_dict(),
            'confidence': round(self.confidence, 1),
            'confidence_level': self.confidence_level,
            'explanation': self.explanation,
            'provider_breakdown': self.provider_breakdown,
            'providers_used': self.providers_used,
            'cached': self.cached,
            'timestamp': self.timestamp.isoformat()
        }
