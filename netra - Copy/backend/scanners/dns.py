import dns.resolver
import time
import requests
import socket
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.logger import log_module_start, log_module_complete, log_module_error, setup_logger
from utils.cache import dns_cache
import os


def get_accuracy_note(confidence: int) -> str:
    """Generate user-friendly accuracy note based on confidence score."""
    if confidence >= 90:
        return "High accuracy - multiple sources agree"
    elif confidence >= 70:
        return "Good accuracy - cross-referenced from multiple sources"
    elif confidence >= 50:
        return "Moderate accuracy - based on single source"
    else:
        return "Low accuracy - limited data available"


def scan_dns(domain: str, timeout: float = 5.0, use_cache: bool = True) -> Dict[str, Any]:
    """
    Perform DNS lookup for a domain with timeout, caching, and parallel queries.
    
    Args:
        domain: Domain to query
        timeout: Query timeout in seconds (default: 5.0)
        use_cache: Whether to use cached results (default: True)
    
    Returns:
        Standardized JSON response with DNS data
    """
    logger = setup_logger()
    start_time = time.time()
    
    # Check cache first
    cache_key = f"dns:{domain}"
    if use_cache:
        cached_result = dns_cache.get(cache_key)
        if cached_result:
            logger.info(f"DNS cache hit for {domain}")
            return cached_result
    
    log_module_start(logger, "DNS", domain)
    
    # Configure resolver with timeout
    logger.info(f"DNS: Configuring resolver with {timeout}s timeout")
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = timeout
    
    def query_record(record_type):
        """Query a single DNS record type."""
        try:
            if record_type == 'A':
                records = resolver.resolve(domain, 'A')
                return ('a_records', [str(rdata) for rdata in records])
            elif record_type == 'AAAA':
                records = resolver.resolve(domain, 'AAAA')
                return ('aaaa_records', [str(rdata) for rdata in records])
            elif record_type == 'MX':
                records = resolver.resolve(domain, 'MX')
                return ('mx_records', [{"exchange": str(rdata.exchange), "priority": rdata.preference} for rdata in records])
            elif record_type == 'TXT':
                records = resolver.resolve(domain, 'TXT')
                return ('txt_records', [str(rdata).strip('"') for rdata in records])
            elif record_type == 'NS':
                records = resolver.resolve(domain, 'NS')
                return ('ns_records', [str(rdata) for rdata in records])
            elif record_type == 'SOA':
                records = resolver.resolve(domain, 'SOA')
                soa = records[0]
                return ('soa', {
                    "mname": str(soa.mname),
                    "rname": str(soa.rname),
                    "serial": soa.serial,
                    "refresh": soa.refresh,
                    "retry": soa.retry,
                    "expire": soa.expire,
                    "minimum": soa.minimum
                })
            elif record_type == 'CNAME':
                records = resolver.resolve(domain, 'CNAME')
                return ('cname', [str(rdata) for rdata in records])
        except:
            if record_type in ['A', 'AAAA', 'MX', 'TXT', 'NS']:
                return (f"{record_type.lower()}_records", [])
            elif record_type == 'SOA':
                return ('soa', None)
            elif record_type == 'CNAME':
                return ('cname', None)
    
    try:
        data = {}
        
        # Run all DNS queries in parallel
        logger.info("DNS: Starting parallel DNS queries for 7 record types")
        record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'SOA', 'CNAME']
        
        with ThreadPoolExecutor(max_workers=7) as executor:
            future_to_type = {executor.submit(query_record, rtype): rtype for rtype in record_types}
            
            for future in as_completed(future_to_type):
                key, value = future.result()
                data[key] = value
                logger.info(f"DNS: Retrieved {key} ({len(value) if isinstance(value, list) else 1 if value else 0} records)")
        
        logger.info("DNS: All DNS queries completed")
        
        # Get IP geolocation for first A record using MaxMind as primary provider
        if data.get('a_records') and len(data['a_records']) > 0:
            ip_address = data['a_records'][0]
            logger.info(f"DNS: Starting IP geolocation for {ip_address}")
            
            # Perform reverse DNS lookup
            reverse_dns = None
            try:
                logger.info(f"DNS: Performing reverse DNS lookup for {ip_address}")
                reverse_dns = socket.gethostbyaddr(ip_address)[0]
                logger.info(f"DNS: Reverse DNS result - {reverse_dns}")
            except socket.herror:
                logger.info(f"DNS: No reverse DNS record found for {ip_address}")
            except Exception as e:
                logger.warning(f"DNS: Reverse DNS lookup failed - {str(e)}")
            
            data['reverse_dns'] = reverse_dns
            
            # Try MaxMind first (highest accuracy)
            maxmind_result = None
            try:
                # Check if MaxMind database or credentials are available
                db_path = os.getenv('MAXMIND_DATABASE_PATH')
                license_key = os.getenv('MAXMIND_LICENSE_KEY')
                account_id = os.getenv('MAXMIND_ACCOUNT_ID')
                
                if db_path and os.path.exists(db_path) or (license_key and account_id):
                    logger.info("DNS: Attempting MaxMind geolocation lookup...")
                    from utils.geolocation.maxmind_provider import MaxMindProvider
                    with MaxMindProvider(account_id=account_id, license_key=license_key, database_path=db_path) as provider:
                        maxmind_result = provider.lookup(ip_address)
                        if maxmind_result:
                            logger.info(f"DNS: MaxMind geolocation success - {maxmind_result.get('country')} - {maxmind_result.get('city')}")
                        else:
                            logger.warning("DNS: MaxMind geolocation returned no result")
                else:
                    logger.info("DNS: MaxMind not configured, using fallback providers")
            except Exception as e:
                logger.warning(f"DNS: MaxMind geolocation failed: {str(e)}")
            
            # Fallback to other providers if MaxMind fails
            if not maxmind_result:
                logger.info("DNS: Using fallback geolocation providers")
                # Country name normalization map
                country_normalization = {
                    'United States': 'US',
                    'United States of America': 'US',
                    'USA': 'US',
                    'Australia': 'AU',
                    'United Kingdom': 'GB',
                    'Great Britain': 'GB',
                    'Indonesia': 'ID',
                    'Singapore': 'SG',
                }
                
                # Use only working providers based on network testing
                providers = [
                    ('ipinfo.io', f'https://ipinfo.io/{ip_address}/json'),
                    ('freeipapi.com', f'https://freeipapi.com/api/json/{ip_address}')
                ]
                
                results = []
                for provider_name, url in providers:
                    try:
                        logger.info(f"DNS: Querying {provider_name}...")
                        geo_response = requests.get(url, timeout=5)
                        if geo_response.status_code == 200:
                            geo_data = geo_response.json()
                            
                            # Parse based on provider
                            if provider_name == 'ipinfo.io':
                                if geo_data.get('country'):
                                    lat, lon = None, None
                                    if geo_data.get('loc'):
                                        coords = geo_data['loc'].split(',')
                                        if len(coords) == 2:
                                            lat, lon = float(coords[0]), float(coords[1])
                                    country = geo_data.get('country')
                                    country = country_normalization.get(country, country)
                                    results.append({
                                        'country': country,
                                        'country_code': geo_data.get('country'),
                                        'city': geo_data.get('city'),
                                        'region': geo_data.get('region'),
                                        'isp': geo_data.get('org'),
                                        'org': geo_data.get('org'),
                                        'timezone': geo_data.get('timezone'),
                                        'lat': lat,
                                        'lon': lon,
                                        'source': provider_name
                                    })
                            elif provider_name == 'freeipapi.com':
                                if geo_data.get('countryName'):
                                    country = geo_data.get('countryName')
                                    country = country_normalization.get(country, country)
                                    results.append({
                                        'country': country,
                                        'country_code': geo_data.get('countryCode'),
                                        'city': geo_data.get('cityName'),
                                        'region': geo_data.get('regionName'),
                                        'isp': geo_data.get('isp'),
                                        'org': geo_data.get('isp'),
                                        'timezone': geo_data.get('timeZone'),
                                        'lat': geo_data.get('latitude'),
                                        'lon': geo_data.get('longitude'),
                                        'source': provider_name
                                    })
                            
                            logger.info(f"DNS: {provider_name} returned {results[-1].get('country')}")
                        else:
                            logger.warning(f"DNS: {provider_name} returned status {geo_response.status_code}")
                    except Exception as e:
                        logger.warning(f"DNS: {provider_name} failed: {str(e)}")
                        continue
                
                # Compute consensus from fallback results
                if results:
                    logger.info(f"DNS: Computing consensus from {len(results)} provider results")
                    from collections import Counter
                    country_votes = Counter(r.get('country') for r in results if r.get('country'))
                    if country_votes:
                        primary_country = country_votes.most_common(1)[0][0]
                        primary_result = next((r for r in results if r.get('country') == primary_country), results[0])
                        
                        # Calculate confidence - cap at 75% for fallback providers (not 100%)
                        confidence = (len(results) / len(providers)) * 75
                        if len(results) > 1:
                            confidence += 10
                        confidence = min(75, confidence)
                        
                        logger.info(f"DNS: Consensus - {primary_country} ({confidence}% confidence - fallback providers)")
                        maxmind_result = {
                            'ip': ip_address,
                            'country': primary_result.get('country'),
                            'country_code': primary_result.get('country_code'),
                            'city': primary_result.get('city'),
                            'region': primary_result.get('region'),
                            'region_code': None,
                            'postal_code': None,
                            'continent': None,
                            'continent_code': None,
                            'isp': primary_result.get('isp'),
                            'org': primary_result.get('org'),
                            'timezone': primary_result.get('timezone'),
                            'latitude': primary_result.get('lat'),
                            'longitude': primary_result.get('lon'),
                            'confidence': confidence,
                            'accuracy_radius': None,
                            'asn': None,
                            'asn_organization': None,
                            'network': None,
                            'domain': None,
                            'connection_type': None,
                            'source': 'fallback'
                        }
                else:
                    logger.warning("DNS: No geolocation providers returned results")
            
            # Use MaxMind result if available
            if maxmind_result:
                confidence = maxmind_result.get('confidence', 75)
                logger.info(f"DNS: Final infrastructure intelligence result - {maxmind_result.get('country')} ({confidence}% confidence)")
                
                # Determine source note
                source_note = "MaxMind GeoLite2" if maxmind_result.get('source') == 'maxmind' else "Fallback providers (limited accuracy)"
                
                # Add accuracy radius to note if available
                if maxmind_result.get('accuracy_radius'):
                    source_note += f" (±{maxmind_result['accuracy_radius']}km)"
                
                # Separate infrastructure intelligence components
                data['infrastructure_intelligence'] = {
                    'ip_address': ip_address,
                    'ip_ownership': {
                        'isp': maxmind_result.get('isp'),
                        'organization': maxmind_result.get('org') or maxmind_result.get('asn_organization'),
                        'asn': maxmind_result.get('asn'),
                        'asn_organization': maxmind_result.get('asn_organization'),
                        'network': maxmind_result.get('network')
                    },
                    'hosting_provider': maxmind_result.get('isp'),
                    'geographic_estimate': {
                        'country': maxmind_result.get('country'),
                        'country_code': maxmind_result.get('country_code'),
                        'city': maxmind_result.get('city'),
                        'region': maxmind_result.get('region'),
                        'region_code': maxmind_result.get('region_code'),
                        'postal_code': maxmind_result.get('postal_code'),
                        'continent': maxmind_result.get('continent'),
                        'continent_code': maxmind_result.get('continent_code'),
                        'latitude': maxmind_result.get('latitude'),
                        'longitude': maxmind_result.get('longitude'),
                        'timezone': maxmind_result.get('timezone'),
                        'accuracy_radius': maxmind_result.get('accuracy_radius')
                    },
                    'confidence': {
                        'score': round(confidence),
                        'level': 'HIGH' if confidence >= 80 else 'MODERATE' if confidence >= 60 else 'LOW',
                        'source': maxmind_result.get('source', 'unknown'),
                        'note': source_note
                    },
                    'additional_info': {
                        'domain': maxmind_result.get('domain'),
                        'connection_type': maxmind_result.get('connection_type'),
                        'reverse_dns': reverse_dns
                    }
                }
                logger.info(f"Infrastructure intelligence: {maxmind_result.get('country')} ({confidence}% confidence)")
            else:
                data['infrastructure_intelligence'] = None
        else:
            data['infrastructure_intelligence'] = None
            data['ip_info'] = None  # Keep for backward compatibility
        
        execution_time = time.time() - start_time
        log_module_complete(logger, "DNS", domain, execution_time)
        
        result = {
            "module": "DNS",
            "status": "SUCCESS",
            "severity": "INFO",
            "message": "DNS data retrieved successfully",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 100,
            "data": data
        }
        
        # Cache the result
        if use_cache:
            dns_cache.set(cache_key, result)
        
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_message = str(e)
        log_module_error(logger, "DNS", domain, error_message)
        
        return {
            "module": "DNS",
            "status": "FAILED",
            "severity": "ERROR",
            "message": f"DNS lookup failed: {error_message}",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 0,
            "data": {}
        }
