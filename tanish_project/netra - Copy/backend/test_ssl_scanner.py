"""
Test SSL scanner with known good domains to identify issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanners.ssl import scan_ssl

# Test domains with known valid SSL certificates
test_domains = [
    'google.com',
    'github.com',
    'chatgpt.com',
    'openai.com',
    'microsoft.com',
    'cloudflare.com'
]

print("Testing SSL Scanner with Known Good Domains")
print("=" * 60)

for domain in test_domains:
    print(f"\nScanning {domain}...")
    try:
        result = scan_ssl(domain)
        
        print(f"  Status: {result.get('status')}")
        print(f"  Severity: {result.get('severity')}")
        print(f"  Message: {result.get('message')}")
        print(f"  Execution Time: {result.get('execution_time')}s")
        
        if result.get('data'):
            data = result['data']
            print(f"  Valid: {data.get('valid')}")
            print(f"  Protocol: {data.get('protocol')}")
            print(f"  Days Remaining: {data.get('days_remaining')}")
            print(f"  Issuer: {data.get('issuer')}")
            print(f"  Subject: {data.get('subject')}")
        else:
            print("  No SSL data retrieved")
            
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete")
