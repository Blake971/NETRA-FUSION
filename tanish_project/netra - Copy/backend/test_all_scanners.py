"""
Test all scanners with validation domains to verify accuracy improvements
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanners.ssl import scan_ssl
from scanners.whois import scan_whois
from scanners.headers import scan_headers
from scanners.dns import scan_dns

# Test domains with known good configurations
test_domains = [
    'google.com',
    'github.com',
    'chatgpt.com',
    'openai.com',
    'microsoft.com',
    'cloudflare.com'
]

print("=" * 80)
print("SCANNER VALIDATION TEST")
print("=" * 80)

for domain in test_domains:
    print(f"\n{'=' * 80}")
    print(f"Testing: {domain}")
    print(f"{'=' * 80}")
    
    # Test SSL Scanner
    print(f"\n--- SSL Scanner ---")
    try:
        ssl_result = scan_ssl(domain)
        print(f"Status: {ssl_result.get('status')}")
        print(f"Confidence: {ssl_result.get('confidence')}%")
        print(f"Message: {ssl_result.get('message')}")
        print(f"Execution Time: {ssl_result.get('execution_time')}s")
        
        if ssl_result.get('status') == 'SUCCESS':
            data = ssl_result.get('data', {})
            print(f"Valid: {data.get('valid')}")
            print(f"Protocol: {data.get('protocol')}")
            print(f"Days Remaining: {data.get('days_remaining')}")
        elif ssl_result.get('status') == 'FAILED':
            error_data = ssl_result.get('data', {})
            print(f"Error Reason: {error_data.get('reason')}")
            print(f"Error Details: {error_data.get('details')}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test WHOIS Scanner
    print(f"\n--- WHOIS Scanner ---")
    try:
        whois_result = scan_whois(domain)
        print(f"Status: {whois_result.get('status')}")
        print(f"Confidence: {whois_result.get('confidence')}%")
        print(f"Message: {whois_result.get('message')}")
        print(f"Execution Time: {whois_result.get('execution_time')}s")
        
        if whois_result.get('status') == 'SUCCESS':
            data = whois_result.get('data', {})
            print(f"Registrar: {data.get('registrar')}")
            print(f"Created: {data.get('created')}")
            print(f"Expires: {data.get('expires')}")
        elif whois_result.get('status') in ['FAILED', 'UNKNOWN']:
            error_data = whois_result.get('data', {})
            print(f"Error Reason: {error_data.get('reason')}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test Headers Scanner
    print(f"\n--- Headers Scanner ---")
    try:
        headers_result = scan_headers(domain)
        print(f"Status: {headers_result.get('status')}")
        print(f"Confidence: {headers_result.get('confidence')}%")
        print(f"Message: {headers_result.get('message')}")
        print(f"Execution Time: {headers_result.get('execution_time')}s")
        
        if headers_result.get('status') == 'SUCCESS':
            data = headers_result.get('data', {})
            print(f"HSTS: {data.get('hsts')}")
            print(f"CSP: {data.get('csp')}")
            print(f"X-Frame-Options: {data.get('x_frame_options')}")
            print(f"Redirects: {data.get('redirects')}")
            print(f"Status Code: {data.get('status_code')}")
        elif headers_result.get('status') == 'FAILED':
            error_data = headers_result.get('data', {})
            print(f"Error Reason: {error_data.get('reason')}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test DNS Scanner
    print(f"\n--- DNS Scanner ---")
    try:
        dns_result = scan_dns(domain, timeout=5.0, use_cache=False)
        print(f"Status: {dns_result.get('status')}")
        print(f"Confidence: {dns_result.get('confidence')}%")
        print(f"Message: {dns_result.get('message')}")
        print(f"Execution Time: {dns_result.get('execution_time')}s")
        
        if dns_result.get('status') == 'SUCCESS':
            data = dns_result.get('data', {})
            print(f"A Records: {len(data.get('a_records', []))}")
            print(f"MX Records: {len(data.get('mx_records', []))}")
            print(f"NS Records: {len(data.get('ns_records', []))}")
            
            if data.get('ip_info'):
                ip_info = data['ip_info']
                print(f"IP Info Country: {ip_info.get('country')}")
                print(f"IP Info City: {ip_info.get('city')}")
                print(f"IP Info Confidence: {ip_info.get('confidence')}%")
        elif dns_result.get('status') == 'FAILED':
            error_data = dns_result.get('data', {})
            print(f"Error Reason: {error_data.get('reason')}")
    except Exception as e:
        print(f"Exception: {e}")

print(f"\n{'=' * 80}")
print("VALIDATION TEST COMPLETE")
print(f"{'=' * 80}")
