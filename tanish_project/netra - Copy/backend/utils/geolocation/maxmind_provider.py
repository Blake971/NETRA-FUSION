"""
MaxMind GeoIP2 Provider Integration
Supports both web service and local database lookup
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MaxMindProvider:
    """MaxMind GeoIP2 provider for IP geolocation"""
    
    def __init__(self, account_id: Optional[str] = None, license_key: Optional[str] = None,
                 database_path: Optional[str] = None):
        """
        Initialize MaxMind provider
        
        Args:
            account_id: MaxMind account ID for web service
            license_key: MaxMind license key for web service
            database_path: Path to local GeoLite2-City.mmdb database
        """
        self.account_id = account_id or os.getenv('MAXMIND_ACCOUNT_ID')
        self.license_key = license_key or os.getenv('MAXMIND_LICENSE_KEY')
        self.database_path = database_path or os.getenv('MAXMIND_DATABASE_PATH')
        
        self._web_client = None
        self._db_reader = None
        self._use_database = False
        
        # Try to initialize database first (preferred for performance)
        if self.database_path and os.path.exists(self.database_path):
            self._init_database()
        elif self.account_id and self.license_key:
            self._init_web_service()
        else:
            logger.warning("MaxMind provider: No database or credentials available")
    
    def _init_database(self):
        """Initialize local database reader"""
        try:
            import geoip2.database
            self._db_reader = geoip2.database.Reader(self.database_path)
            self._use_database = True
            logger.info(f"MaxMind provider: Using local database at {self.database_path}")
        except Exception as e:
            logger.error(f"MaxMind provider: Failed to load database: {e}")
            self._use_database = False
    
    def _init_web_service(self):
        """Initialize web service client"""
        try:
            import geoip2.webservice
            # Use geolite.info for GeoLite free tier
            self._web_client = geoip2.webservice.Client(
                self.account_id,
                self.license_key,
                host='geolite.info'
            )
            logger.info("MaxMind provider: Using web service")
        except Exception as e:
            logger.error(f"MaxMind provider: Failed to initialize web service: {e}")
    
    def lookup(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Look up IP address geolocation
        
        Args:
            ip_address: IP address to lookup
            
        Returns:
            Dictionary with geolocation data or None if lookup fails
        """
        if not ip_address:
            return None
        
        try:
            if self._use_database and self._db_reader:
                return self._lookup_database(ip_address)
            elif self._web_client:
                return self._lookup_web_service(ip_address)
            else:
                logger.warning("MaxMind provider: No initialized client available")
                return None
        except Exception as e:
            logger.error(f"MaxMind provider: Lookup failed for {ip_address}: {e}")
            return None
    
    def _lookup_database(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Lookup using local database"""
        try:
            response = self._db_reader.city(ip_address)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"MaxMind database lookup failed: {e}")
            return None
    
    def _lookup_web_service(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Lookup using web service"""
        try:
            response = self._web_client.city(ip_address)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"MaxMind web service lookup failed: {e}")
            return None
    
    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse MaxMind response into unified format"""
        try:
            ip_address = response.traits.ip_address
            
            data = {
                'ip': ip_address,
                'country': response.country.name if response.country.name else None,
                'country_code': response.country.iso_code if response.country.iso_code else None,
                'city': response.city.name if response.city.name else None,
                'region': response.subdivisions.most_specific.name if response.subdivisions.most_specific.name else None,
                'region_code': response.subdivisions.most_specific.iso_code if response.subdivisions.most_specific.iso_code else None,
                'postal_code': response.postal.code if response.postal.code else None,
                'continent': response.continent.name if response.continent.name else None,
                'continent_code': response.continent.code if response.continent.code else None,
                'latitude': response.location.latitude if response.location.latitude else None,
                'longitude': response.location.longitude if response.location.longitude else None,
                'accuracy_radius': response.location.accuracy_radius if response.location.accuracy_radius else None,
                'timezone': response.location.time_zone if response.location.time_zone else None,
                'asn': response.traits.autonomous_system_number if response.traits.autonomous_system_number else None,
                'asn_organization': response.traits.autonomous_system_organization if response.traits.autonomous_system_organization else None,
                'isp': response.traits.isp if hasattr(response.traits, 'isp') else None,
                'network': str(response.traits.network) if response.traits.network else None,
                'domain': self._reverse_dns_lookup(ip_address),
                'connection_type': self._get_connection_type(response),
                'source': 'maxmind'
            }
            
            # Add confidence based on accuracy radius
            if data['accuracy_radius']:
                # Smaller radius = higher confidence
                if data['accuracy_radius'] <= 50:
                    data['confidence'] = 95
                elif data['accuracy_radius'] <= 200:
                    data['confidence'] = 85
                elif data['accuracy_radius'] <= 500:
                    data['confidence'] = 70
                else:
                    data['confidence'] = 50
            else:
                data['confidence'] = 75  # Default confidence
            
            return data
        except Exception as e:
            logger.error(f"Failed to parse MaxMind response: {e}")
            return None
    
    def _reverse_dns_lookup(self, ip_address: str) -> Optional[str]:
        """Perform reverse DNS lookup to get domain name"""
        try:
            import socket
            domain = socket.gethostbyaddr(ip_address)[0]
            return domain
        except Exception:
            return None
    
    def _get_connection_type(self, response) -> Optional[str]:
        """
        Get connection type from MaxMind response
        Note: This requires MaxMind GeoIP2 paid edition (Connection Type database)
        For GeoLite2, this will return None
        """
        try:
            # GeoLite2 doesn't provide connection type
            # This would require GeoIP2 Connection Type database (paid)
            if hasattr(response.traits, 'connection_type'):
                connection_type = response.traits.connection_type
                # Map connection types to user-friendly names
                type_mapping = {
                    'dialup': 'Dialup',
                    'cable': 'Cable/DSL',
                    'dsl': 'Cable/DSL',
                    'fiber': 'Fiber',
                    'mobile': 'Mobile',
                    'satellite': 'Satellite',
                    'wireless': 'Wireless'
                }
                return type_mapping.get(connection_type, connection_type)
            return None
        except Exception:
            return None
    
    def close(self):
        """Close database reader if used"""
        if self._db_reader:
            self._db_reader.close()
            self._db_reader = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def test_maxmind_provider():
    """Test MaxMind provider with sample IPs"""
    # Test with web service (requires credentials)
    provider = MaxMindProvider(
        account_id=os.getenv('MAXMIND_ACCOUNT_ID'),
        license_key=os.getenv('MAXMIND_LICENSE_KEY')
    )
    
    test_ips = [
        '8.8.8.8',
        '103.122.128.225',
        '142.251.223.174'
    ]
    
    for ip in test_ips:
        result = provider.lookup(ip)
        if result:
            print(f"\n{ip}:")
            print(f"  Country: {result.get('country')}")
            print(f"  City: {result.get('city')}")
            print(f"  Region: {result.get('region')}")
            print(f"  ASN: {result.get('asn_organization')}")
            print(f"  Accuracy Radius: {result.get('accuracy_radius')} km")
            print(f"  Confidence: {result.get('confidence')}%")
        else:
            print(f"\n{ip}: No result")
    
    provider.close()


if __name__ == '__main__':
    test_maxmind_provider()
