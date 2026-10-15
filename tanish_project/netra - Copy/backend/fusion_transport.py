"""Verified, public-address-pinned HTTPS collection and explicit TLS states."""
import http.client
import json
import socket
import ssl
import time
from datetime import datetime, timezone
from urllib.parse import urlsplit, urljoin

def timestamp():
    return datetime.now(timezone.utc).isoformat()

def pinned_connection(host, resolve):
    addresses = resolve(host)
    last = None
    # Prefer IPv4, then try another validated public endpoint on network failure.
    for address in sorted(addresses,key=lambda x: ':' in x)[:3]:
        connection = http.client.HTTPSConnection(host, timeout=8)
        raw = None
        try:
            raw = socket.create_connection((address,443),timeout=8)
            connection.sock=ssl.create_default_context().wrap_socket(raw,server_hostname=host)
            return connection,addresses
        except ssl.SSLCertVerificationError:
            if raw:raw.close()
            connection.close()
            raise
        except OSError as exc:
            if raw:raw.close()
            connection.close()
            last=exc
    if last:raise last
    raise ValueError('No validated public endpoint available.')


def certificate_failure(exc):
    message = str(getattr(exc, 'verify_message', '')).lower()
    state = 'EXPIRED' if 'expired' in message else 'HOSTNAME_MISMATCH' if 'hostname mismatch' in message or 'ip address mismatch' in message else 'NOT_YET_VALID' if 'not yet valid' in message else 'TRUST_FAILED'
    return {'tls_state': state, 'verified': False, 'verification_code': getattr(exc, 'verify_code', None),
            'note': 'This client rejected the certificate. Confirm trust failures using another client; local trust configuration or interception may affect results.'}

def capture_web(domain, resolve):
    observed = timestamp()
    try:
        conn, addresses = pinned_connection(domain, resolve)
    except ssl.SSLCertVerificationError as exc:
        return {'status':'PARTIAL', 'source':'Verified TLS handshake', 'observed_at':observed, 'data':certificate_failure(exc)}
    data = {}
    try:
        cert = conn.sock.getpeercert()
        days = int((ssl.cert_time_to_seconds(cert['notAfter']) - time.time()) / 86400)
        data = {'tls_state':'VALID', 'verified':True, 'days_remaining':days, 'protocol':conn.sock.version(),
                'issuer':str(cert.get('issuer', [])), 'addresses':addresses, 'certificate_names':[v for k,v in cert.get('subjectAltName',[]) if k=='DNS'],
                'expires_at':datetime.fromtimestamp(ssl.cert_time_to_seconds(cert['notAfter']),timezone.utc).isoformat()}
        conn.request('GET','/',headers={'User-Agent':'NETRA-Fusion/3.1 (public website checkup)','Accept':'text/html'})
        response = conn.getresponse()
        headers = {k.lower():v for k,v in response.getheaders()}
        data.update(headers=headers, status_code=response.status, body=response.read(131072).decode('utf-8',errors='replace'), redirect=headers.get('location'))
        return {'status':'SUCCESS','source':'HTTPS root response + verified TLS handshake','observed_at':observed,'data':data}
    except (OSError, http.client.HTTPException) as exc:
        return {'status':'PARTIAL','source':'TLS succeeded; HTTP collection unavailable','observed_at':observed,'data':data,'error':type(exc).__name__}
    finally:
        conn.close()

def public_json(url, resolve, limit=2000000, redirects=2):
    """Revalidate every redirect and pin every connection; never use proxies."""
    deadline = time.monotonic() + 25
    for attempt in range(redirects + 1):
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.port not in (None,443):
            raise ValueError('The provider must use a public HTTPS endpoint.')
        if time.monotonic() >= deadline:
            raise TimeoutError('Provider deadline exceeded')
        conn, _ = pinned_connection(parsed.hostname, resolve)
        try:
            conn.request('GET', parsed.path + ('?' + parsed.query if parsed.query else ''), headers={'Accept':'application/rdap+json, application/json','User-Agent':'NETRA-Fusion/3.1'})
            response = conn.getresponse()
            if response.status in (301,302,303,307,308):
                if attempt == redirects or not response.getheader('Location'):
                    raise ValueError('Provider redirect limit reached')
                url = urljoin(url,response.getheader('Location'))
                continue
            if response.status != 200:
                raise ValueError('Provider returned HTTP ' + str(response.status))
            payload = bytearray()
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('Provider deadline exceeded')
                if conn.sock:
                    conn.sock.settimeout(min(8,remaining))
                chunk = response.read1(min(65536,limit + 1 - len(payload)))
                if not chunk:
                    break
                payload.extend(chunk)
                if len(payload)>limit:
                    raise ValueError('Provider response exceeds size limit')
            return json.loads(payload), url
        finally:
            conn.close()
