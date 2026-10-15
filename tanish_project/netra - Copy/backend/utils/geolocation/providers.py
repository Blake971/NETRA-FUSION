"""
Provider adapters for different geolocation APIs.
Each provider implements a common interface for fetching and normalizing data.
"""

import requests
from typing import Optional, Dict, Any
from .models import ProviderData


class BaseProvider:
    """Base class for all geolocation providers."""
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight
    
    def fetch(self, ip: str, timeout: float = 3.0) -> Optional[ProviderData]:
        """Fetch geolocation data for an IP address."""
        raise NotImplementedError
    
    def normalize(self, raw_data: Dict[str, Any], ip: str) -> ProviderData:
        """Normalize provider-specific response to unified format."""
        raise NotImplementedError


class IpApiProvider(BaseProvider):
    """ip-api.com provider adapter."""
    
    def __init__(self):
        super().__init__("ip-api.com", weight=0.30)
    
    def fetch(self, ip: str, timeout: float = 3.0) -> Optional[ProviderData]:
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return self.normalize(data, ip)
        except Exception:
            pass
        return None
    
    def normalize(self, raw_data: Dict[str, Any], ip: str) -> ProviderData:
        return ProviderData(
            ip=ip,
            country=raw_data.get('country'),
            country_code=raw_data.get('countryCode'),
            region=raw_data.get('regionName'),
            city=raw_data.get('city'),
            postal_code=raw_data.get('zip'),
            latitude=raw_data.get('lat'),
            longitude=raw_data.get('lon'),
            timezone=raw_data.get('timezone'),
            isp=raw_data.get('isp'),
            organization=raw_data.get('org'),
            asn=raw_data.get('as'),
            proxy=raw_data.get('proxy', False),
            hosting=raw_data.get('hosting', False),
            mobile=raw_data.get('mobile', False),
            source=self.name,
            raw_data=raw_data
        )


class IpInfoProvider(BaseProvider):
    """ipinfo.io provider adapter."""
    
    def __init__(self):
        super().__init__("ipinfo.io", weight=0.25)
    
    def fetch(self, ip: str, timeout: float = 3.0) -> Optional[ProviderData]:
        try:
            response = requests.get(f'https://ipinfo.io/{ip}/json', timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if 'country' in data:
                    return self.normalize(data, ip)
        except Exception:
            pass
        return None
    
    def normalize(self, raw_data: Dict[str, Any], ip: str) -> ProviderData:
        # Parse coordinates from "lat,lon" format
        lat, lon = None, None
        if raw_data.get('loc'):
            coords = raw_data['loc'].split(',')
            if len(coords) == 2:
                lat, lon = float(coords[0]), float(coords[1])
        
        return ProviderData(
            ip=ip,
            country=raw_data.get('country'),
            country_code=raw_data.get('country'),
            region=raw_data.get('region'),
            city=raw_data.get('city'),
            postal_code=raw_data.get('postal'),
            latitude=lat,
            longitude=lon,
            timezone=raw_data.get('timezone'),
            isp=raw_data.get('org'),
            organization=raw_data.get('org'),
            asn=raw_data.get('org'),
            source=self.name,
            raw_data=raw_data
        )


class IpApiCoProvider(BaseProvider):
    """ipapi.co provider adapter."""
    
    def __init__(self):
        super().__init__("ipapi.co", weight=0.20)
    
    def fetch(self, ip: str, timeout: float = 3.0) -> Optional[ProviderData]:
        try:
            response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('country'):
                    return self.normalize(data, ip)
        except Exception:
            pass
        return None
    
    def normalize(self, raw_data: Dict[str, Any], ip: str) -> ProviderData:
        return ProviderData(
            ip=ip,
            country=raw_data.get('country_name'),
            country_code=raw_data.get('country'),
            region=raw_data.get('region'),
            city=raw_data.get('city'),
            postal_code=raw_data.get('postal'),
            latitude=raw_data.get('latitude'),
            longitude=raw_data.get('longitude'),
            timezone=raw_data.get('timezone'),
            isp=raw_data.get('org'),
            organization=raw_data.get('org'),
            asn=raw_data.get('asn'),
            source=self.name,
            raw_data=raw_data
        )


class IpWhoProvider(BaseProvider):
    """ipwho.is provider adapter."""
    
    def __init__(self):
        super().__init__("ipwho.is", weight=0.10)
    
    def fetch(self, ip: str, timeout: float = 3.0) -> Optional[ProviderData]:
        try:
            response = requests.get(f'https://ipwho.is/{ip}', timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return self.normalize(data, ip)
        except Exception:
            pass
        return None
    
    def normalize(self, raw_data: Dict[str, Any], ip: str) -> ProviderData:
        return ProviderData(
            ip=ip,
            country=raw_data.get('country'),
            country_code=raw_data.get('country_code'),
            region=raw_data.get('region'),
            city=raw_data.get('city'),
            postal_code=raw_data.get('postal'),
            latitude=raw_data.get('latitude'),
            longitude=raw_data.get('longitude'),
            timezone=raw_data.get('timezone', {}).get('id'),
            isp=raw_data.get('connection', {}).get('isp'),
            organization=raw_data.get('connection', {}).get('organization'),
            asn=raw_data.get('connection', {}).get('asn'),
            source=self.name,
            raw_data=raw_data
        )


class FreeIpApiProvider(BaseProvider):
    """freeipapi.com provider adapter."""
    
    def __init__(self):
        super().__init__("freeipapi.com", weight=0.10)
    
    def fetch(self, ip: str, timeout: float = 3.0) -> Optional[ProviderData]:
        try:
            response = requests.get(f'https://freeipapi.com/api/json/{ip}', timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('countryName'):
                    return self.normalize(data, ip)
        except Exception:
            pass
        return None
    
    def normalize(self, raw_data: Dict[str, Any], ip: str) -> ProviderData:
        return ProviderData(
            ip=ip,
            country=raw_data.get('countryName'),
            country_code=raw_data.get('countryCode'),
            region=raw_data.get('regionName'),
            city=raw_data.get('cityName'),
            postal_code=raw_data.get('zipCode'),
            latitude=raw_data.get('latitude'),
            longitude=raw_data.get('longitude'),
            timezone=raw_data.get('timeZone'),
            isp=raw_data.get('isp'),
            organization=raw_data.get('isp'),
            source=self.name,
            raw_data=raw_data
        )


class IpBaseProvider(BaseProvider):
    """ipbase.com provider adapter."""
    
    def __init__(self):
        super().__init__("ipbase.com", weight=0.05)
    
    def fetch(self, ip: str, timeout: float = 3.0) -> Optional[ProviderData]:
        try:
            response = requests.get(f'https://api.ipbase.com/v2/json/{ip}', timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    return self.normalize(data['data'], ip)
        except Exception:
            pass
        return None
    
    def normalize(self, raw_data: Dict[str, Any], ip: str) -> ProviderData:
        return ProviderData(
            ip=ip,
            country=raw_data.get('country', {}).get('name'),
            country_code=raw_data.get('country', {}).get('alpha2'),
            region=raw_data.get('region', {}).get('name'),
            city=raw_data.get('city', {}).get('name'),
            postal_code=raw_data.get('zip'),
            latitude=raw_data.get('latitude'),
            longitude=raw_data.get('longitude'),
            timezone=raw_data.get('timezone', {}).get('id'),
            isp=raw_data.get('connection', {}).get('isp'),
            organization=raw_data.get('connection', {}).get('organization'),
            asn=raw_data.get('connection', {}).get('asn'),
            source=self.name,
            raw_data=raw_data
        )


class GeoPluginProvider(BaseProvider):
    """geoplugin.net provider adapter."""
    
    def __init__(self):
        super().__init__("geoplugin.net", weight=0.05)
    
    def fetch(self, ip: str, timeout: float = 3.0) -> Optional[ProviderData]:
        try:
            response = requests.get(f'http://www.geoplugin.net/json.gp?ip={ip}', timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('geoplugin_countryName'):
                    return self.normalize(data, ip)
        except Exception:
            pass
        return None
    
    def normalize(self, raw_data: Dict[str, Any], ip: str) -> ProviderData:
        return ProviderData(
            ip=ip,
            country=raw_data.get('geoplugin_countryName'),
            country_code=raw_data.get('geoplugin_countryCode'),
            region=raw_data.get('geoplugin_regionName'),
            city=raw_data.get('geoplugin_city'),
            postal_code=raw_data.get('geoplugin_postalCode'),
            latitude=raw_data.get('geoplugin_latitude'),
            longitude=raw_data.get('geoplugin_longitude'),
            timezone=raw_data.get('geoplugin_timezone'),
            isp=raw_data.get('geoplugin_isp'),
            organization=raw_data.get('geoplugin_isp'),
            source=self.name,
            raw_data=raw_data
        )


def get_all_providers() -> list[BaseProvider]:
    """Return all available providers."""
    return [
        IpApiProvider(),
        IpInfoProvider(),
        IpApiCoProvider(),
        IpWhoProvider(),
        FreeIpApiProvider(),
        IpBaseProvider(),
        GeoPluginProvider()
    ]
