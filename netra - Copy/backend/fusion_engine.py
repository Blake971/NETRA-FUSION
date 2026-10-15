"""NETRA collection + deterministic evidence challenge.

No model, exploit execution, or compliance certification is implied by this engine.
"""
import hashlib
import http.client
import ipaddress
import json
import re
import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlsplit, quote
import dns.resolver
from fusion_policy import positive_hsts, sender_policy
import sys
from pathlib import Path
import requests

# Add scanners directory to path
scanners_path = Path(__file__).parent / 'scanners'
sys.path.insert(0, str(scanners_path))

try:
    from google_dork import scan_google_dorks
except ImportError:
    scan_google_dorks = None


def now():
    return datetime.now(timezone.utc).isoformat()


def normalize_domain(value):
    value = value.strip().lower()
    if '://' in value:
        parsed = urlsplit(value)
        if parsed.scheme not in ('http', 'https') or parsed.username or parsed.password or parsed.port:
            raise ValueError('Use a public domain without credentials or a custom port.')
        value = parsed.hostname or ''
    value = value.rstrip('.').encode('idna').decode('ascii')
    if len(value) > 253 or not re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}', value):
        raise ValueError('Enter a domain such as example.com.')
    if value.endswith(('.localhost', '.local', '.internal', '.test', '.invalid')):
        raise ValueError('Only publicly routable domains can be assessed.')
    return value


def public_addresses(domain):
    resolver = dns.resolver.Resolver()
    resolver.lifetime = 4
    addresses = []
    for kind in ('A', 'AAAA'):
        try:
            addresses.extend(str(x) for x in resolver.resolve(domain, kind))
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
    if not addresses or any(not ipaddress.ip_address(x).is_global for x in addresses):
        raise ValueError('The target must resolve exclusively to public IP addresses.')
    return sorted(set(addresses))


def web_snapshot(domain):
    # Pin the validated IP for the socket, preserving hostname verification and SNI.
    # Redirects are recorded, never followed; environment proxies are not used.
    addresses = public_addresses(domain)
    connection = http.client.HTTPSConnection(domain, timeout=8)
    raw = socket.create_connection((addresses[0], 443), timeout=8)
    try:
        connection.sock = ssl.create_default_context().wrap_socket(raw, server_hostname=domain)
        cert = connection.sock.getpeercert()
        protocol = connection.sock.version()
        connection.request('GET', '/', headers={'User-Agent': 'NETRA-Fusion/3.0 (domain posture assessment)', 'Accept': 'text/html'})
        response = connection.getresponse()
        headers = {k.lower(): v for k, v in response.getheaders()}
        body = response.read(131072).decode('utf-8', errors='replace')
        days = int((ssl.cert_time_to_seconds(cert['notAfter']) - datetime.now(timezone.utc).timestamp()) / 86400)
        return {'status': 'SUCCESS', 'source': 'HTTPS root response + verified TLS handshake', 'observed_at': now(),
                'data': {'headers': headers, 'status_code': response.status, 'protocol': protocol,
                         'days_remaining': days, 'issuer': str(cert.get('issuer', [])),
                         'addresses': addresses, 'body': body, 'redirect': headers.get('location')}}
    finally:
        connection.close()
        raw.close()


def dns_snapshot(domain):
    resolver = dns.resolver.Resolver()
    resolver.lifetime = 3
    records, errors = {}, {}
    for kind, name in [('A', domain), ('AAAA', domain), ('MX', domain), ('NS', domain), ('TXT', domain), ('CAA', domain), ('DMARC', '_dmarc.' + domain)]:
        try:
            records[kind] = [x.to_text().replace('" "', '').strip('"') for x in resolver.resolve(name, 'TXT' if kind == 'DMARC' else kind)]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            records[kind] = []
        except Exception as exc:
            errors[kind] = type(exc).__name__
    return {'status': 'PARTIAL' if errors else 'SUCCESS', 'source': 'System recursive DNS resolver', 'observed_at': now(), 'data': records, 'errors': errors}


def ct_snapshot(domain):
    connection = http.client.HTTPSConnection('crt.sh', timeout=10)
    try:
        connection.request('GET', '/?q=' + quote('%.' + domain) + '&output=json', headers={'User-Agent': 'NETRA-Fusion/3.0'})
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError('Certificate log provider returned HTTP ' + str(response.status))
        payload = response.read(2000001)
        if len(payload) > 2000000:
            return {'status': 'UNKNOWN', 'source': 'crt.sh', 'observed_at': now(), 'data': {}, 'error': 'Provider response exceeds size limit; discovery incomplete.'}
        names = set()
        for entry in json.loads(payload):
            for name in entry.get('name_value', '').lower().splitlines():
                name = name.removeprefix('*.')
                if name == domain or name.endswith('.' + domain):
                    names.add(name)
        return {'status': 'SUCCESS', 'source': 'crt.sh certificate transparency', 'observed_at': now(), 'data': {'names': sorted(names)[:100], 'total': len(names), 'note': 'Historical certificate names; not proof of a live service.'}}
    finally:
        connection.close()


def geolocation_snapshot(ip_addresses):
    """Get geolocation and provider information for IP addresses.
    
    Uses ipinfo.io as primary provider with fallback to freeipapi.com.
    Returns ISP, ASN, organization, and location data for each IP.
    """
    results = {}
    
    for ip in ip_addresses:
        # Try ipinfo.io first
        try:
            response = requests.get(f'https://ipinfo.io/{ip}/json', timeout=3)
            if response.status_code == 200:
                data = response.json()
                results[ip] = {
                    'ip': ip,
                    'country': data.get('country'),
                    'country_code': data.get('country'),
                    'region': data.get('region'),
                    'city': data.get('city'),
                    'postal_code': data.get('postal'),
                    'latitude': None,
                    'longitude': None,
                    'timezone': data.get('timezone'),
                    'isp': data.get('org'),
                    'organization': data.get('org'),
                    'asn': data.get('org'),
                    'source': 'ipinfo.io',
                    'raw_data': data
                }
                # Parse coordinates if available
                if data.get('loc'):
                    coords = data['loc'].split(',')
                    if len(coords) == 2:
                        results[ip]['latitude'] = float(coords[0])
                        results[ip]['longitude'] = float(coords[1])
                continue
        except Exception:
            pass
        
        # Fallback to freeipapi.com
        try:
            response = requests.get(f'https://freeipapi.com/api/json/{ip}', timeout=3)
            if response.status_code == 200:
                data = response.json()
                results[ip] = {
                    'ip': ip,
                    'country': data.get('countryName'),
                    'country_code': data.get('countryCode'),
                    'region': data.get('regionName'),
                    'city': data.get('cityName'),
                    'postal_code': data.get('zipCode'),
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'timezone': data.get('timeZone'),
                    'isp': data.get('isp'),
                    'organization': data.get('isp'),
                    'source': 'freeipapi.com',
                    'raw_data': data
                }
        except Exception:
            # If both fail, mark as unknown
            results[ip] = {
                'ip': ip,
                'error': 'Geolocation lookup failed for this IP address',
                'source': 'none'
            }
    
    return {
        'status': 'SUCCESS' if results else 'UNKNOWN',
        'source': 'Geolocation provider lookup',
        'observed_at': now(),
        'data': {
            'total_ips': len(ip_addresses),
            'successful_lookups': len([r for r in results.values() if 'error' not in r]),
            'ip_data': results
        }
    }


def google_dork_snapshot(domain):
    """Generate Google Dork queries for OSINT reconnaissance.
    
    This function ONLY generates queries - it never executes searches or scrapes Google.
    The queries are provided to the user for manual execution in search engines.
    """
    if scan_google_dorks is None:
        return {'status': 'UNKNOWN', 'source': 'Google Dork scanner', 'observed_at': now(), 'data': {}, 'error': 'Google Dork scanner module not available.'}
    
    try:
        result = scan_google_dorks(domain)
        return {
            'status': 'SUCCESS',
            'source': 'Google Dork query generator',
            'observed_at': now(),
            'data': {
                'total_queries': result.get('data', {}).get('total_queries', 0),
                'queries': result.get('data', {}).get('queries', []),
                'disclaimer': result.get('data', {}).get('disclaimer', '')
            }
        }
    except Exception as exc:
        return {'status': 'UNKNOWN', 'source': 'Google Dork scanner', 'observed_at': now(), 'data': {}, 'error': type(exc).__name__ + ': Google Dork query generation failed.'}


COLLECTORS = {'web': web_snapshot, 'dns': dns_snapshot, 'certificates': ct_snapshot, 'google_dork': google_dork_snapshot, 'geolocation': geolocation_snapshot}


def collect(name, domain):
    try:
        return COLLECTORS[name](domain)
    except Exception as exc:
        return {'status': 'UNKNOWN', 'source': name, 'observed_at': now(), 'data': {}, 'error': type(exc).__name__ + ': collection unavailable; no deduction applied.'}


def analyze(domain, results):
    findings, checks, challenged = [], [], []
    def check(key, category, title, observed, missing, points, evidence, why, fix, snippet=None):
        state = 'UNKNOWN' if not observed else ('GAP' if missing else 'PASS')
        checks.append({'id': key, 'category': category, 'title': title, 'state': state, 'weight': points})
        if state != 'GAP':
            return
        findings.append({'id': key, 'category': category, 'title': title, 'severity': 'HIGH' if points >= 15 else 'MEDIUM' if points >= 8 else 'LOW',
                         'points': points, 'confidence': 90, 'evidence': evidence, 'explanation': why, 'remediation': fix,
                         'snippet': snippet, 'review': 'Evidence confirmed by deterministic skeptic; exploitability not tested.', 'status': 'CONFIRMED'})
    web, dns = results.get('web', {}), results.get('dns', {})
    wd, dd = web.get('data', {}), dns.get('data', {})
    headers = wd.get('headers', {})
    web_ok = web.get('status') == 'SUCCESS' and 200 <= wd.get('status_code', 0) < 400
    dns_ok = dns.get('status') in ('SUCCESS', 'PARTIAL')
    known = lambda key: dns_ok and key in dd and key not in dns.get('errors', {})
    hsts = headers.get('strict-transport-security', '')
    check('hsts', 'Web', 'HTTPS persistence policy', web_ok, not positive_hsts(hsts), 10,
          'No usable positive max-age found in Strict-Transport-Security: ' + (hsts or '(absent)'), 'Browsers may permit an initial insecure visit without an HTTPS persistence policy.',
          'After confirming HTTPS works throughout the intended scope, stage an HSTS policy.', 'add_header Strict-Transport-Security "max-age=86400" always;')
    check('csp', 'Web', 'Browser content policy', web_ok, not headers.get('content-security-policy'), 10,
          'Content-Security-Policy absent on root response.', 'A content policy can reduce the impact of content injection; its absence does not prove XSS.',
          'Inventory required resources, deploy report-only, review violations, then enforce.', 'add_header Content-Security-Policy-Report-Only "default-src \'self\'; object-src \'none\'; base-uri \'self\'" always;')
    framed = bool(re.search(r"(?:^|;)\s*frame-ancestors\s+(?:'none'|'self'|https?://[^;\s]+)(?:\s|;|$)", headers.get('content-security-policy', ''), re.I))
    xfo = headers.get('x-frame-options', '').strip().upper() in ('DENY', 'SAMEORIGIN')
    check('framing', 'Web', 'Frame embedding restriction', web_ok, not xfo and not framed, 5,
          'Neither X-Frame-Options nor CSP frame-ancestors observed.', 'Unrestricted framing can enable deceptive overlays on interactive pages.',
          'Confirm legitimate embedding requirements and restrict allowed ancestors.', 'add_header Content-Security-Policy "frame-ancestors \'self\'" always;')
    if web_ok and framed and not headers.get('x-frame-options'):
        challenged.append({'title': 'Missing X-Frame-Options', 'reason': 'Suppressed: CSP frame-ancestors already provides a framing control.'})
    check('nosniff', 'Web', 'Content type protection', web_ok, headers.get('x-content-type-options', '').lower() != 'nosniff', 5,
          'X-Content-Type-Options: nosniff not observed.', 'Content type enforcement limits browser MIME guessing.',
          'Serve correct content types and enable nosniff.', 'add_header X-Content-Type-Options "nosniff" always;')
    check('permissions_policy', 'Web', 'Browser feature permissions', web_ok, not headers.get('permissions-policy') and not headers.get('feature-policy'), 5,
          'Permissions-Policy (or legacy Feature-Policy) absent on root response.', 'A permissions policy controls browser features like geolocation, camera, and microphone access.',
          'Review required features and deploy a restrictive permissions policy.', 'add_header Permissions-Policy "geolocation=(), camera=(), microphone=()" always;')
    check('referrer_policy', 'Web', 'Referrer information control', web_ok, not headers.get('referrer-policy'), 3,
          'Referrer-Policy absent on root response.', 'Referrer policy controls how much referrer information is sent with navigation requests.',
          'Deploy a strict referrer policy to limit information leakage.', 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;')
    cors_origin = headers.get('access-control-allow-origin', '')
    check('cors', 'Web', 'Cross-origin resource sharing', web_ok, cors_origin and cors_origin == '*', 5,
          'CORS configured with wildcard origin: ' + cors_origin, 'Wildcard CORS allows any origin to access resources, which may be overly permissive.',
          'Restrict CORS to specific trusted origins if cross-origin access is needed.', 'add_header Access-Control-Allow-Origin "https://trusted.example.com" always;')
    days_remaining = wd.get('days_remaining', 999)
    expiry_points = 15 if days_remaining < 7 else 10 if days_remaining < 14 else 5 if days_remaining < 30 else 0
    check('tls_expiry', 'TLS', 'Certificate renewal window', web.get('status') == 'SUCCESS', expiry_points > 0, expiry_points,
          f"Certificate expires in {days_remaining} days.", 'A missed renewal can interrupt trusted connections.', 'Enable automatic certificate renewal and expiry alerts.')
    check('tls_protocol', 'TLS', 'Modern negotiated TLS', web.get('status') == 'SUCCESS', wd.get('protocol') not in ('TLSv1.2', 'TLSv1.3'), 15,
          'Negotiated protocol: ' + str(wd.get('protocol')), 'Modern TLS protects transport confidentiality. This checks one handshake, not all supported protocols.', 'Configure TLS 1.2 or newer and review the complete server configuration.')
    spf_ok, spf_evidence = sender_policy(dd.get('TXT', []))
    check('spf', 'Email', 'Sender authorization record', known('TXT'), not spf_ok, 10,
          spf_evidence, 'An SPF policy declares permitted mail senders; this limited check does not evaluate its full semantics.', 'Inventory legitimate senders and publish a reviewed SPF policy, including a non-sending policy if applicable.')
    dmarc = next((x for x in dd.get('DMARC', []) if x.lower().startswith('v=dmarc1')), '')
    enforcing = bool(re.search(r'(?:^|;)\s*p\s*=\s*(reject|quarantine)\s*(?:;|$)', dmarc, re.I))
    check('dmarc', 'Email', 'DMARC enforcement policy', known('DMARC'), not enforcing, 15,
          dmarc or 'No DMARC policy found in a successful DNS query.', 'Monitoring-only or absent DMARC provides less spoofing protection. Alignment and delivery are not tested.', 'Review aggregate reports and sender alignment before moving to quarantine or reject.')
    check('caa', 'DNS', 'Certificate issuer restriction', known('CAA'), not dd.get('CAA'), 0,
          'No CAA record observed at this domain.', 'CAA can restrict certificate issuance; inherited parent policies may apply and need review.', 'Check inherited CAA policies before publishing issuer restrictions.')
    for name, result in results.items():
        if result.get('status') == 'UNKNOWN':
            challenged.append({'title': name + ' collection unavailable', 'reason': 'No vulnerability inferred and no score deducted from unavailable evidence.'})
    observed = [x for x in checks if x['state'] != 'UNKNOWN']
    score = max(0, 100 - sum(x['points'] for x in findings)) if observed else None
    coverage = round(100 * len(observed) / len(checks))
    categories = [{ 'name': category, 'observed': sum(x['state'] != 'UNKNOWN' for x in checks if x['category'] == category),
                    'total': sum(x['category'] == category for x in checks), 'deductions': sum(x['points'] for x in findings if x['category'] == category)} for category in ('Web', 'TLS', 'Email', 'DNS')]
    nodes = [{'id': domain, 'kind': 'domain', 'source': 'Assessment scope'}]
    for ip in dd.get('A', []) + dd.get('AAAA', []):
        nodes.append({'id': ip, 'kind': 'address', 'source': 'DNS'})
    for name in results.get('certificates', {}).get('data', {}).get('names', []):
        if name != domain:
            nodes.append({'id': name, 'kind': 'certificate name', 'source': 'Historical CT observation'})
    for mx in dd.get('MX', []):
        nodes.append({'id': mx, 'kind': 'mail server', 'source': 'DNS MX'})
    nodes = list({n['id']: n for n in nodes}.values())
    technologies = [{'name': headers[k], 'evidence': k + ' response header', 'confidence': 'Self-reported; unverified'} for k in ('server', 'x-powered-by', 'x-aspnet-version') if headers.get(k)]
    body = wd.get('body', '')
    for marker, name in [('wp-content/', 'WordPress'), ('/_next/', 'Next.js'), ('data-reactroot', 'React'), ('vue', 'Vue.js'), ('angular', 'Angular'), ('jquery', 'jQuery'), ('bootstrap', 'Bootstrap'), ('tailwind', 'Tailwind CSS'), ('laravel', 'Laravel'), ('django', 'Django'), ('flask', 'Flask'), ('rails', 'Ruby on Rails'), ('express', 'Express.js'), ('gatsby', 'Gatsby'), ('nuxt', 'Nuxt.js'), ('svelte', 'Svelte')]:
        if marker in body.lower():
            technologies.append({'name': name, 'evidence': 'HTML marker: ' + marker, 'confidence': 'Heuristic; not a version or vulnerability claim'})
    ranked = sorted(findings, key=lambda x: (-x['points'], x['id']))
    return {'score': score, 'coverage': coverage, 'checks': checks, 'findings': ranked, 'challenged': challenged, 'categories': categories,
            'graph': {'nodes': nodes[:120], 'edges': [{'source': domain, 'target': n['id'], 'relation': n['source']} for n in nodes[1:120]]},
            'technologies': technologies,
            'briefing': {'mode': 'Deterministic evidence synthesis', 'summary': f"{domain}: {len(findings)} configuration gaps across {len(observed)} observed checks. Evidence coverage is {coverage}%. " + ('Resolve collection gaps before drawing a full posture conclusion.' if coverage < 100 else 'Prioritize the highest-impact observed gaps.'),
                         'priorities': [x['title'] + ': ' + x['remediation'] for x in ranked[:3]],
                         'limits': 'Public DNS, root-page HTTPS, one TLS handshake and certificate logs only. No exploit verification, complete inventory, breach attribution, or compliance certification.'},
            'methodology': 'Score v1.2: 100 minus observed deductions (maximum 85), bounded at zero. Unknown checks never deduct; incomplete coverage makes the score provisional. Missing CAA is advisory with zero deduction because inherited policy is not checked. HSTS checks positive max-age; SPF checks record count and obvious broad authorization. Confidence is a rule heuristic, not a statistical probability.'}


def demo_results(improved=False):
    result = {'web': {'status': 'SUCCESS', 'source': 'Synthetic competition fixture', 'observed_at': now(), 'data': {'status_code': 200, 'headers': {'server': 'nginx', 'content-security-policy': "default-src 'self'; frame-ancestors 'self'"}, 'protocol': 'TLSv1.3', 'days_remaining': 18, 'body': '<html><a href="https://github.com/northstar-demo">Code</a><a href="/reports/annual-review.pdf">Report</a></html>'}},
            'dns': {'status': 'SUCCESS', 'source': 'Synthetic competition fixture', 'observed_at': now(), 'data': {'A': ['203.0.113.42'], 'AAAA': [], 'MX': ['10 mail.northstar.example'], 'NS': ['ns1.northstar.example'], 'TXT': ['v=spf1 -all'], 'DMARC': ['v=DMARC1; p=none'], 'CAA': []}},
            'certificates': {'status': 'SUCCESS', 'source': 'Synthetic competition fixture', 'observed_at': now(), 'data': {'names': ['northstar.example', 'api.northstar.example', 'staging.northstar.example', 'status.northstar.example'], 'note': 'Synthetic historical names'}}}

    if improved:
        result['web']['data']['headers'].update({'strict-transport-security': 'max-age=31536000', 'x-content-type-options': 'nosniff', 'permissions-policy': 'geolocation=(), camera=(), microphone=()', 'referrer-policy': 'strict-origin-when-cross-origin'})
        result['web']['data']['days_remaining'] = 180
        result['dns']['data']['DMARC'] = ['v=DMARC1; p=reject']
        result['dns']['data']['CAA'] = ['0 issue "example-ca.invalid"']
    return result


def evidence_digest(results):
    return hashlib.sha256(json.dumps(results, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
