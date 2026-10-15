"""
Test DNS geolocation with MaxMind integration
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanners.dns import scan_dns

# Test domains
test_domains = [
    'google.com',
    'sbtet.telangana.gov.in',
    'example.com'
]

print("Testing DNS Geolocation with MaxMind Integration")
print("=" * 60)

for domain in test_domains:
    print(f"\nScanning {domain}...")
    try:
        result = scan_dns(domain, timeout=5.0, use_cache=False)
        
        if result.get('data', {}).get('ip_info'):
            ip_info = result['data']['ip_info']
            print(f"  IP: {ip_info.get('ip')}")
            print(f"  Country: {ip_info.get('country')}")
            print(f"  City: {ip_info.get('city')}")
            print(f"  Region: {ip_info.get('region')}")
            print(f"  Postal Code: {ip_info.get('postal_code') or 'N/A'}")
            print(f"  Continent: {ip_info.get('continent') or 'N/A'}")
            print(f"  ISP: {ip_info.get('isp')}")
            print(f"  Organization: {ip_info.get('asn_organization') or 'N/A'}")
            print(f"  ASN: {ip_info.get('asn') or 'N/A'}")
            print(f"  Network: {ip_info.get('network') or 'N/A'}")
            print(f"  Domain: {ip_info.get('domain') or 'N/A'}")
            print(f"  Connection Type: {ip_info.get('connection_type') or 'N/A'}")
            print(f"  Confidence: {ip_info.get('confidence')}%")
            print(f"  Source: {ip_info.get('sources')}")
            print(f"  Note: {ip_info.get('accuracy_note')}")
            if ip_info.get('accuracy_radius'):
                print(f"  Accuracy Radius: ±{ip_info.get('accuracy_radius')}km")
        else:
            print("  No IP geolocation data available")
            
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "=" * 60)
print("Test complete")
