"""NETRA collection + SALMON-inspired deterministic evidence challenge.

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
from fusion_transport import capture_web
from fusion_registration import rdap_snapshot
from fusion_email import dmarc_policy
from fusion_hosting import hosting_snapshot
from concurrent.futures import ThreadPoolExecutor


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
            addresses.extend(str(x) for x in resolve_retry(resolver,domain,kind)[0])
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
    if not addresses or any(not ipaddress.ip_address(x).is_global for x in addresses):
        raise ValueError('The target must resolve exclusively to public IP addresses.')
    return sorted(set(addresses))


def web_snapshot(domain):
    return capture_web(domain, public_addresses)


def resolve_retry(resolver,name,kind):
    try:return resolver.resolve(name,kind),False
    except (dns.resolver.LifetimeTimeout,dns.resolver.NoNameservers):
        return resolver.resolve(name,kind),True

def dns_snapshot(domain):
    records, errors, retried = {}, {}, []
    def one(pair):
        kind,name=pair;resolver=dns.resolver.Resolver();resolver.lifetime=3
        try:
            answer,retry=resolve_retry(resolver,name,'TXT' if kind=='DMARC' else kind)
            return kind,[x.to_text().replace('" "','').strip('"') for x in answer],None,retry
        except (dns.resolver.NoAnswer,dns.resolver.NXDOMAIN):return kind,[],None,False
        except Exception as exc:return kind,None,type(exc).__name__,False
    pairs=[(kind,domain) for kind in ('A','AAAA','CNAME','MX','NS','TXT','CAA')]+[('DMARC','_dmarc.'+domain)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for kind,values,error,retry in pool.map(one,pairs):
            if error:errors[kind]=error
            else:records[kind]=values
            if retry:retried.append(kind)
    return {'status':'PARTIAL' if errors else 'SUCCESS','source':'System recursive DNS resolver','observed_at':now(),'data':records,'errors':errors,'retried_records':retried}


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


COLLECTORS = {'web': web_snapshot, 'dns': dns_snapshot, 'certificates': ct_snapshot, 'registration': lambda domain: rdap_snapshot(domain, public_addresses), 'hosting': lambda domain: hosting_snapshot(domain, public_addresses)}


def collect(name, domain):
    for attempt in range(2):
        try:
            result=COLLECTORS[name](domain)
            result['attempts']=attempt+1
            return result
        except Exception as exc:
            transient=isinstance(exc,(TimeoutError,ConnectionError,dns.resolver.LifetimeTimeout))
            if transient and attempt==0:continue
            kind=type(exc).__name__
            reason='The provider timed out after a bounded retry.' if transient else 'The provider or network could not return usable evidence.'
            return {'status':'UNKNOWN','source':name,'observed_at':now(),'data':{},'attempts':attempt+1,
                    'error':kind+': '+reason+' No deduction applied.','next_step':'Run another checkup later; inspect network access and provider availability.'}


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
    tls_valid = wd.get('tls_state') == 'VALID' or web.get('status') == 'SUCCESS'
    expired = wd.get('tls_state') == 'EXPIRED'
    check('tls_expiry', 'TLS', 'Certificate renewal window', expired or (tls_valid and wd.get('days_remaining') is not None), expired or wd.get('days_remaining', 999) < 30, 15,
          ("TLS verification reported an expired certificate." if expired else f"Certificate expires in {wd.get('days_remaining')} days."), 'A missed renewal can interrupt trusted connections.', 'Enable automatic certificate renewal and expiry alerts.')
    check('tls_protocol', 'TLS', 'Modern negotiated TLS', tls_valid and wd.get('protocol') is not None, wd.get('protocol') not in ('TLSv1.2', 'TLSv1.3'), 15,
          'Negotiated protocol: ' + str(wd.get('protocol')), 'Modern TLS protects transport confidentiality. This checks one handshake, not all supported protocols.', 'Configure TLS 1.2 or newer and review the complete server configuration.')
    spf_ok, spf_evidence = sender_policy(dd.get('TXT', []))
    check('spf', 'Email', 'Sender authorization record', known('TXT'), not spf_ok, 10,
          spf_evidence, 'An SPF policy declares permitted mail senders; this limited check does not evaluate its full semantics.', 'Inventory legitimate senders and publish a reviewed SPF policy, including a non-sending policy if applicable.')
    policy = dmarc_policy(dd.get('DMARC', []))
    dmarc = policy['detail']
    enforcing = policy['state'] == 'OBSERVED'
    check('dmarc', 'Email', 'DMARC enforcement policy', known('DMARC'), not enforcing, 15,
          dmarc or 'No DMARC policy found in a successful DNS query.', 'The direct-domain policy needs review. Inherited policy, alignment and delivery are not tested.', 'Review aggregate reports and sender alignment before moving to quarantine or reject.')
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
    technologies = [{'name': headers[k], 'evidence': k + ' response header', 'confidence': 'Self-reported; unverified'} for k in ('server', 'x-powered-by') if headers.get(k)]
    body = wd.get('body', '')
    for marker, name in [('wp-content/', 'WordPress'), ('/_next/', 'Next.js'), ('data-reactroot', 'React')]:
        if marker in body:
            technologies.append({'name': name, 'evidence': 'HTML marker: ' + marker, 'confidence': 'Heuristic; not a version or vulnerability claim'})
    ranked = sorted(findings, key=lambda x: (-x['points'], x['id']))
    return {'score': score, 'coverage': coverage, 'checks': checks, 'findings': ranked, 'challenged': challenged, 'categories': categories,
            'graph': {'nodes': nodes[:120], 'edges': [{'source': domain, 'target': n['id'], 'relation': n['source']} for n in nodes[1:120]]},
            'technologies': technologies,
            'briefing': {'mode': 'Deterministic evidence synthesis', 'summary': f"{domain}: {len(findings)} configuration gaps across {len(observed)} observed checks. Evidence coverage is {coverage}%. " + ('Resolve collection gaps before drawing a full posture conclusion.' if coverage < 100 else 'Prioritize the highest-impact observed gaps.'),
                         'priorities': [x['title'] + ': ' + x['remediation'] for x in ranked[:3]],
                         'limits': 'Public DNS, root-page HTTPS, one TLS handshake and certificate logs only. No exploit verification, complete inventory, breach attribution, or compliance certification.'},
            'methodology': 'Score v1.3: 100 minus observed deductions (maximum 85), bounded at zero. Unknown checks never deduct; incomplete coverage makes the score provisional. Missing CAA is advisory with zero deduction because inherited policy is not checked. DMARC checks direct-record structure and testing mode; inherited policy is not evaluated. HSTS checks positive max-age; SPF checks record count and obvious broad authorization. Confidence is a rule heuristic, not a statistical probability.'}


def demo_results(improved=False):
    result = {'web': {'status': 'SUCCESS', 'source': 'Synthetic competition fixture', 'observed_at': now(), 'data': {'status_code': 200, 'headers': {'server': 'nginx', 'content-security-policy': "default-src 'self'; frame-ancestors 'self'"}, 'protocol': 'TLSv1.3', 'days_remaining': 18, 'body': '<html><a href="https://github.com/northstar-demo">Code</a><a href="/reports/annual-review.pdf">Report</a></html>'}},
            'dns': {'status': 'SUCCESS', 'source': 'Synthetic competition fixture', 'observed_at': now(), 'data': {'A': ['203.0.113.42'], 'AAAA': [], 'MX': ['10 mail.northstar.example'], 'NS': ['ns1.northstar.example'], 'TXT': ['v=spf1 -all'], 'DMARC': ['v=DMARC1; p=none'], 'CAA': []}},
            'certificates': {'status': 'SUCCESS', 'source': 'Synthetic competition fixture', 'observed_at': now(), 'data': {'names': ['northstar.example', 'api.northstar.example', 'staging.northstar.example', 'status.northstar.example'], 'note': 'Synthetic historical names'}}}

    result['registration'] = {'status':'SUCCESS','source':'Synthetic competition fixture','observed_at':now(),'data':{'domain':'northstar.example','registrar':'Example registrar (fictional)','events':{'registration':'2020-01-01T00:00:00Z','expiration':'2030-01-01T00:00:00Z'},'status':['active'],'note':'Fictional registration for the classroom demonstration.'}}
    result['hosting']={'status':'SUCCESS','source':'Synthetic competition fixture','observed_at':now(),'data':{'endpoints':[{'ip':'203.0.113.42','state':'OBSERVED','network':'Example hosting network (fictional)','city':'Example city','country':'Fictional location','source':'Synthetic fixture','location_scope':'Fictional illustration; not a real server location.'}]}}
    if improved:
        result['web']['data']['headers'].update({'strict-transport-security': 'max-age=31536000', 'x-content-type-options': 'nosniff'})
        result['web']['data']['days_remaining'] = 180
        result['dns']['data']['DMARC'] = ['v=DMARC1; p=reject']
        result['dns']['data']['CAA'] = ['0 issue "example-ca.invalid"']
    return result


def evidence_digest(results):
    return hashlib.sha256(json.dumps(results, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
