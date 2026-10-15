"""Transient Leak-Lookup breach exposure checks."""
import asyncio
import http.client
import json
import os
import re
import time
from urllib.parse import urlencode

from fastapi import HTTPException

_BUSY = False
_NEXT_ALLOWED = 0.0


def provider_lookup(query, search_type, key):
    connection = http.client.HTTPSConnection('leak-lookup.com', timeout=12)
    try:
        params = urlencode({'key': key, 'type': search_type, 'query': query})
        connection.request('POST', '/api/search', body=params, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'NETRA-Fusion-Educational-Breach-Check',
        })
        response = connection.getresponse()
        payload = response.read(1000001)
        if len(payload) > 1000000:
            raise ValueError('Leak-Lookup response exceeded the output limit.')
        if response.status != 200:
            return response.status, None
        try:
            return response.status, json.loads(payload)
        except json.JSONDecodeError:
            print(f"Leak-Lookup returned non-JSON response: {payload[:500]}")
            return response.status, {'error': 'true', 'message': 'Invalid JSON response from Leak-Lookup'}
    finally:
        connection.close()


def get_api_stats(key):
    connection = http.client.HTTPSConnection('leak-lookup.com', timeout=12)
    try:
        params = urlencode({'key': key})
        connection.request('POST', '/api/stats', body=params, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'NETRA-Fusion-Educational-Breach-Check',
        })
        response = connection.getresponse()
        payload = response.read(1000001)
        if len(payload) > 1000000:
            raise ValueError('Leak-Lookup response exceeded the output limit.')
        return response.status, json.loads(payload) if response.status == 200 else None
    finally:
        connection.close()


def normalize_breaches(data, search_type):
    if not isinstance(data, dict) or data.get('error') == 'true':
        return []
    message = data.get('message', {})
    if not isinstance(message, dict):
        return []
    # Leak-Lookup returns breach site names as keys with arrays as values
    # Public API returns empty arrays, just showing which sites have the data
    breaches = []
    for site_name, site_data in message.items():
        if isinstance(site_data, list):
            # For public API, site_data is empty array
            # For private API, site_data contains actual records
            if site_data:
                # Private API - extract details from first record
                record = site_data[0] if isinstance(site_data[0], dict) else {}
                breaches.append({
                    'name': str(site_name)[:200],
                    'title': str(record.get('email_address', record.get('username', site_name)))[:200],
                    'domain': str(record.get('domain_name', ''))[:253],
                    'date': str(record.get('breachdate', 'Unknown'))[:30],
                    'data_classes': [f'{search_type} address'],  # Public API doesn't show data classes
                    'verified': True,
                    'spam_list': False,
                })
            else:
                # Public API - just show site name
                breaches.append({
                    'name': str(site_name)[:200],
                    'title': str(site_name)[:200],
                    'domain': '',
                    'date': 'Unknown',
                    'data_classes': [f'{search_type} address'],
                    'verified': True,
                    'spam_list': False,
                })
    return breaches[:100]


async def check_breach(query, search_type, consent):
    global _BUSY, _NEXT_ALLOWED
    if not consent:
        raise HTTPException(422, 'Confirm you have permission to check this data.')
    query = query.strip()
    
    # Validate based on search type
    if search_type == 'email_address':
        if not re.fullmatch(r'[^\s@\x00-\x1f]+@[^\s@\x00-\x1f]+\.[^\s@\x00-\x1f]+', query):
            raise HTTPException(422, 'Enter a valid email address.')
    elif search_type == 'username':
        if not query or len(query) < 3:
            raise HTTPException(422, 'Enter a valid username (at least 3 characters).')
    elif search_type == 'domain':
        if not re.fullmatch(r'[^\s@\x00-\x1f]+\.[^\s@\x00-\x1f]+', query):
            raise HTTPException(422, 'Enter a valid domain.')
    else:
        raise HTTPException(422, 'Invalid search type.')
    
    key = os.environ.get('LEAK_LOOKUP_API_KEY')
    if not key:
        raise HTTPException(503, 'LEAK_LOOKUP_API_KEY is not configured. No breach check was performed.')
    now = time.monotonic()
    if _BUSY or now < _NEXT_ALLOWED:
        raise HTTPException(429, 'Please wait before starting another breach check.')
    _BUSY = True
    _NEXT_ALLOWED = now + 6
    try:
        status, data = await asyncio.to_thread(provider_lookup, query, search_type, key)
        if not data:
            raise HTTPException(503, 'Leak-Lookup returned invalid response.')
        if data.get('error') == 'true':
            error_msg = data.get('message', 'Unknown error')
            if 'RATE LIMIT REACHED' in error_msg:
                _NEXT_ALLOWED = time.monotonic() + 60
                raise HTTPException(429, 'Leak-Lookup rate limit reached. Please wait and try again.')
            if 'REQUEST LIMIT REACHED' in error_msg:
                _NEXT_ALLOWED = time.monotonic() + 86400
                raise HTTPException(429, 'Leak-Lookup daily request limit reached. Please wait until tomorrow.')
            if 'INVALID API KEY' in error_msg or 'INACTIVE API KEY' in error_msg:
                raise HTTPException(503, 'Leak-Lookup rejected the configured API credentials. No conclusion is available.')
            raise HTTPException(503, f'Leak-Lookup error: {error_msg}')
        breaches = normalize_breaches(data, search_type)
        return {
            'state': 'MATCHES' if breaches else 'NO_KNOWN_MATCH',
            'breaches': breaches,
            'stored': False,
            'detail': f'Reported by Leak-Lookup for {search_type}. This does not prove the account itself was compromised; no known match does not prove safety.',
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Breach check error: {exc}")
        raise HTTPException(503, 'The breach provider could not be checked. No exposure conclusion is available.') from exc
    finally:
        _BUSY = False


async def check_email(email, consent):
    return await check_breach(email, 'email_address', consent)


async def get_stats():
    key = os.environ.get('LEAK_LOOKUP_API_KEY')
    if not key:
        raise HTTPException(503, 'LEAK_LOOKUP_API_KEY is not configured.')
    try:
        status, data = await asyncio.to_thread(get_api_stats, key)
        if not data:
            raise HTTPException(503, 'Leak-Lookup returned invalid response.')
        if data.get('error') == 'true':
            raise HTTPException(503, f'Leak-Lookup error: {data.get("message", "Unknown error")}')
        return data.get('message', {})
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(503, 'Could not retrieve API stats.') from exc
