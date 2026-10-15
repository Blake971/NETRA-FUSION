"""
Geolocation Investigation Script
Tests multiple IPs against all providers and compares results
"""

import requests
import json
from typing import Dict, List, Any
from collections import Counter


def test_provider(provider_name: str, url: str, ip: str) -> Dict[str, Any]:
    """Test a single provider with an IP address."""
    result = {
        'provider': provider_name,
        'ip': ip,
        'status_code': None,
        'success': False,
        'data': None,
        'error': None,
        'response_time': None
    }
    
    try:
        import time
        start = time.time()
        response = requests.get(url, timeout=5)
        result['response_time'] = time.time() - start
        result['status_code'] = response.status_code
        
        if response.status_code == 200:
            data = response.json()
            result['data'] = data
            result['success'] = True
        else:
            result['error'] = f"HTTP {response.status_code}"
    except Exception as e:
        result['error'] = str(e)
    
    return result


def parse_provider_data(provider_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse provider-specific data into unified format."""
    if provider_name == 'ip-api.com':
        if data.get('status') == 'success':
            return {
                'country': data.get('country'),
                'country_code': data.get('countryCode'),
                'city': data.get('city'),
                'region': data.get('regionName'),
                'isp': data.get('isp'),
                'org': data.get('org'),
                'timezone': data.get('timezone'),
                'lat': data.get('lat'),
                'lon': data.get('lon'),
                'proxy': data.get('proxy', False),
                'hosting': data.get('hosting', False),
                'mobile': data.get('mobile', False),
                'asn': data.get('as')
            }
    elif provider_name == 'ipinfo.io':
        if data.get('country'):
            lat, lon = None, None
            if data.get('loc'):
                coords = data['loc'].split(',')
                if len(coords) == 2:
                    lat, lon = float(coords[0]), float(coords[1])
            return {
                'country': data.get('country'),
                'country_code': data.get('country'),
                'city': data.get('city'),
                'region': data.get('region'),
                'isp': data.get('org'),
                'org': data.get('org'),
                'timezone': data.get('timezone'),
                'lat': lat,
                'lon': lon,
                'asn': data.get('org')
            }
    elif provider_name == 'ipapi.co':
        if data.get('country'):
            return {
                'country': data.get('country_name'),
                'country_code': data.get('country'),
                'city': data.get('city'),
                'region': data.get('region'),
                'isp': data.get('org'),
                'org': data.get('org'),
                'timezone': data.get('timezone'),
                'lat': data.get('latitude'),
                'lon': data.get('longitude'),
                'asn': data.get('asn')
            }
    elif provider_name == 'ipwho.is':
        if data.get('success') and data.get('country'):
            return {
                'country': data.get('country'),
                'country_code': data.get('country_code'),
                'city': data.get('city'),
                'region': data.get('region'),
                'isp': data.get('connection', {}).get('isp'),
                'org': data.get('connection', {}).get('organization'),
                'timezone': data.get('timezone', {}).get('id'),
                'lat': data.get('latitude'),
                'lon': data.get('longitude'),
                'asn': data.get('connection', {}).get('asn')
            }
    elif provider_name == 'freeipapi.com':
        if data.get('countryName'):
            return {
                'country': data.get('countryName'),
                'country_code': data.get('countryCode'),
                'city': data.get('cityName'),
                'region': data.get('regionName'),
                'isp': data.get('isp'),
                'org': data.get('isp'),
                'timezone': data.get('timeZone'),
                'lat': data.get('latitude'),
                'lon': data.get('longitude')
            }
    elif provider_name == 'geoplugin.net':
        if data.get('geoplugin_countryName'):
            return {
                'country': data.get('geoplugin_countryName'),
                'country_code': data.get('geoplugin_countryCode'),
                'city': data.get('geoplugin_city'),
                'region': data.get('geoplugin_regionName'),
                'isp': data.get('geoplugin_isp'),
                'org': data.get('geoplugin_isp'),
                'timezone': data.get('geoplugin_timezone'),
                'lat': data.get('geoplugin_latitude'),
                'lon': data.get('geoplugin_longitude')
            }
    return None


def test_ip(ip: str) -> Dict[str, Any]:
    """Test an IP against all providers."""
    print(f"\n{'='*60}")
    print(f"Testing IP: {ip}")
    print(f"{'='*60}")
    
    providers = [
        ('ip-api.com', f'http://ip-api.com/json/{ip}'),
        ('ipinfo.io', f'https://ipinfo.io/{ip}/json'),
        ('ipapi.co', f'https://ipapi.co/{ip}/json/'),
        ('ipwho.is', f'https://ipwho.is/{ip}'),
        ('freeipapi.com', f'https://freeipapi.com/api/json/{ip}'),
        ('geoplugin.net', f'http://www.geoplugin.net/json.gp?ip={ip}')
    ]
    
    results = []
    parsed_data = []
    
    for provider_name, url in providers:
        result = test_provider(provider_name, url, ip)
        results.append(result)
        
        print(f"\n{provider_name}:")
        print(f"  Status: {result['status_code']}")
        print(f"  Success: {result['success']}")
        print(f"  Response Time: {result['response_time']:.2f}s" if result['response_time'] else "  Response Time: N/A")
        
        if result['success']:
            parsed = parse_provider_data(provider_name, result['data'])
            if parsed:
                parsed_data.append(parsed)
                print(f"  Country: {parsed.get('country')}")
                print(f"  City: {parsed.get('city')}")
                print(f"  Region: {parsed.get('region')}")
                print(f"  ISP: {parsed.get('isp')}")
                print(f"  ASN: {parsed.get('asn')}")
                print(f"  Lat/Lon: {parsed.get('lat')}, {parsed.get('lon')}")
        else:
            print(f"  Error: {result['error']}")
    
    # Analyze consensus
    print(f"\n{'-'*60}")
    print("CONSENSUS ANALYSIS:")
    print(f"{'-'*60}")
    
    if parsed_data:
        countries = [p.get('country') for p in parsed_data if p.get('country')]
        if countries:
            country_votes = Counter(countries)
            print(f"Country votes: {dict(country_votes)}")
            print(f"Primary country: {country_votes.most_common(1)[0][0]}")
        
        cities = [p.get('city') for p in parsed_data if p.get('city')]
        if cities:
            city_votes = Counter(cities)
            print(f"City votes: {dict(city_votes)}")
        
        isps = [p.get('isp') for p in parsed_data if p.get('isp')]
        if isps:
            isp_votes = Counter(isps)
            print(f"ISP votes: {dict(isp_votes)}")
        
        # Calculate confidence
        confidence = (len(parsed_data) / len(providers)) * 100
        if len(parsed_data) > 1:
            confidence += 20
        confidence = min(100, confidence)
        print(f"Confidence: {confidence:.1f}%")
    else:
        print("No successful responses")
    
    return {
        'ip': ip,
        'results': results,
        'parsed_data': parsed_data
    }


def main():
    """Test multiple IPs from different regions."""
    test_ips = [
        '103.122.128.225',  # sbtet.telangana.gov.in (Government of Telangana)
        '142.251.223.174',  # Google (expected US)
        '8.8.8.8',          # Google DNS (expected US)
        '1.1.1.1',          # Cloudflare (expected US/Australia)
        '172.217.160.46',   # Google India
        '13.107.21.200',    # Microsoft (varies)
    ]
    
    all_results = {}
    
    for ip in test_ips:
        all_results[ip] = test_ip(ip)
    
    # Summary report
    print(f"\n{'='*60}")
    print("SUMMARY REPORT")
    print(f"{'='*60}")
    
    for ip, data in all_results.items():
        successful = sum(1 for r in data['results'] if r['success'])
        print(f"\n{ip}: {successful}/{len(data['results'])} providers responded")
        
        if data['parsed_data']:
            countries = [p.get('country') for p in data['parsed_data'] if p.get('country')]
            if countries:
                print(f"  Countries: {', '.join(set(countries))}")


if __name__ == '__main__':
    main()
