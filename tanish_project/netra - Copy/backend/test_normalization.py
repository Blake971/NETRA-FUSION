"""
Test normalization layer with scanner results
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanners.ssl import scan_ssl
from scanners.whois import scan_whois
from scanners.headers import scan_headers
from scanners.dns import scan_dns
from utils.normalization import (
    normalize_infrastructure_intelligence,
    normalize_whois,
    normalize_dns,
    normalize_ssl,
    normalize_headers
)

test_domain = 'google.com'

print("=" * 80)
print("NORMALIZATION LAYER TEST")
print("=" * 80)

# Run scanners
print(f"\nRunning scanners for {test_domain}...")
ssl_result = scan_ssl(test_domain)
whois_result = scan_whois(test_domain)
headers_result = scan_headers(test_domain)
dns_result = scan_dns(test_domain, timeout=5.0, use_cache=False)

print("\n--- SSL Normalization ---")
try:
    normalized_ssl = normalize_ssl(ssl_result)
    print(f"Simple Summary: {normalized_ssl.get('simple_summary')}")
    print(f"Explanation: {normalized_ssl.get('explanation')[:100]}...")
    print(f"Confidence: {normalized_ssl.get('confidence')}")
    print(f"Technical Keys: {list(normalized_ssl.get('technical_details', {}).keys())}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n--- WHOIS Normalization ---")
try:
    normalized_whois = normalize_whois(whois_result)
    print(f"Simple Summary: {normalized_whois.get('simple_summary')}")
    print(f"Explanation: {normalized_whois.get('explanation')[:100]}...")
    print(f"Confidence: {normalized_whois.get('confidence')}")
    print(f"Technical Keys: {list(normalized_whois.get('technical_details', {}).keys())}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n--- DNS Normalization ---")
try:
    normalized_dns = normalize_dns(dns_result)
    print(f"Simple Summary: {normalized_dns.get('simple_summary')}")
    print(f"Explanation: {normalized_dns.get('explanation')[:100]}...")
    print(f"Confidence: {normalized_dns.get('confidence')}")
    print(f"Technical Keys: {list(normalized_dns.get('technical_details', {}).keys())}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Headers Normalization ---")
try:
    normalized_headers = normalize_headers(headers_result)
    print(f"Simple Summary: {normalized_headers.get('simple_summary')}")
    print(f"Explanation: {normalized_headers.get('explanation')[:100]}...")
    print(f"Confidence: {normalized_headers.get('confidence')}")
    print(f"Technical Keys: {list(normalized_headers.get('technical_details', {}).keys())}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Infrastructure Intelligence Normalization ---")
try:
    normalized_infra = normalize_infrastructure_intelligence(dns_result.get('data', {}))
    print(f"Simple Summary: {normalized_infra.get('simple_summary')}")
    print(f"Explanation: {normalized_infra.get('explanation')[:100]}...")
    print(f"Confidence: {normalized_infra.get('confidence')}")
    print(f"Source: {normalized_infra.get('source')}")
    print(f"Technical Keys: {list(normalized_infra.get('technical_details', {}).keys())}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("NORMALIZATION TEST COMPLETE")
print("=" * 80)
