"""Public endpoint attribution, with explicit separation from origin/ownership."""
import ipaddress
import re
import time
import threading
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit, urljoin, quote
from fusion_transport import public_json, timestamp

_cache = {}
_lock = threading.Lock()

def ip_context(address, resolve):
    address = str(ipaddress.ip_address(address))
    if not ipaddress.ip_address(address).is_global:
        raise ValueError('Only public IP addresses can be enriched.')
    with _lock:
        cached = _cache.get(address)
    if cached and time.monotonic()-cached[0] < 600:
        return cached[1] | {'cached':True}
    failures=[]
    item=None
    for provider,url in [('ipapi','https://ipapi.co/'+quote(address,safe=':')+'/json/'),('ipwho','https://ipwho.is/'+quote(address,safe=':'))]:
        try:
            data,source=public_json(url,resolve,limit=100000)
            valid=(not data.get('error')) if provider=='ipapi' else data.get('success') is True
            if not valid or data.get('ip')!=address:raise ValueError('No matching IP observation')
            network=data.get('org') if provider=='ipapi' else data.get('connection',{}).get('org')
            asn=data.get('asn') if provider=='ipapi' else data.get('connection',{}).get('asn')
            item={'ip':address,'state':'OBSERVED','source':source,'observed_at':timestamp(),
                  'city':data.get('city'),'region':data.get('region'),'country':data.get('country_name',data.get('country')),
                  'network':network,'isp':data.get('connection',{}).get('isp'),
                  'asn':str(asn).removeprefix('AS') if asn else None,
                  'location_scope':'Approximate IP database location; not a server or owner address.', 'provider_failures':failures}
            break
        except Exception as exc:failures.append({'provider':provider,'error':type(exc).__name__})
    if item is None:raise ValueError('Both IP location providers were unavailable or returned no matching data.')
    with _lock:
        if len(_cache)>=256: _cache.pop(next(iter(_cache)))
        _cache[address]=(time.monotonic(),item)
    return item

def hosting_snapshot(domain, resolve):
    addresses=resolve(domain)
    def enrich(address):
        try:return ip_context(address,resolve)
        except Exception as exc:
            return {'ip':address,'state':'UNKNOWN','source':'ipapi.co / ipwho.is','observed_at':timestamp(),
                    'detail':type(exc).__name__+': location providers unavailable; the DNS address remains recorded.'}
    with ThreadPoolExecutor(max_workers=2) as pool:
        items=list(pool.map(enrich,addresses[:2]))
    return {'status':'SUCCESS' if all(x['state']=='OBSERVED' for x in items) else 'PARTIAL',
            'source':'Public DNS and IP network/location providers','observed_at':timestamp(),
            'data':{'endpoints':items,'total_addresses':len(addresses),'note':'At most two current public addresses enriched. IP metadata is context, not ownership proof.'}}

class SourceReader(HTMLParser):
    def __init__(self,domain):
        super().__init__();self.domain=domain;self.sources=set();self.public_pages=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        value=attrs.get('src') if tag in ('script','img','iframe','source','video') else attrs.get('href') if tag in ('link','a') else None
        if not value:return
        try:
            parsed=urlsplit(urljoin('https://'+self.domain+'/',value))
            if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password:return
            if tag!='a' and len(self.sources)<30:self.sources.add(parsed.hostname)
            if tag=='a' and parsed.hostname==self.domain and re.search(r'about|contact|privacy|legal|imprint|terms',parsed.path,re.I) and len(self.public_pages)<15:
                url=parsed._replace(query='',fragment='').geturl()
                if url not in self.public_pages:self.public_pages.append(url)
        except ValueError:pass

def attribution(case):
    results=case.get('results',{});web=results.get('web',{}).get('data',{});dns=results.get('dns',{}).get('data',{})
    endpoints=results.get('hosting',{}).get('data',{}).get('endpoints',[])
    headers=web.get('headers',{});signals=[]
    if 'cloudflare' in headers.get('server','').lower():signals.append('Root response identifies Cloudflare in its Server header (self-reported).')
    if headers.get('cf-ray'):signals.append('CF-Ray response header observed; indicates Cloudflare processing, not origin location.')
    if any(str(x.get('asn'))=='13335' or 'cloudflare' in str(x.get('network','')).lower() for x in endpoints):signals.append('Public address metadata identifies the Cloudflare network.')
    cloudflare=bool(signals)
    parser=SourceReader(case['domain']);parser.feed(web.get('body','')[:131072])
    reg=results.get('registration',{});rd=reg.get('data',{})
    return {'endpoints':endpoints,'cdn_signals':signals,'cloudflare_observed':cloudflare,
            'edge_code':headers.get('cf-ray','').rsplit('-',1)[-1] if re.fullmatch(r'[a-fA-F0-9]+-[A-Z]{3}',headers.get('cf-ray','')) else None,
            'nameservers':dns.get('NS',[]),'aliases':dns.get('CNAME',[]),
            'origin':{'state':'NOT_ESTABLISHED','detail':'Cloudflare edge observed. Its upstream file source is not disclosed by these observations.' if cloudflare else 'A public endpoint was observed; an upstream origin and physical server location are not established.'},
            'organization':{'state':'PUBLIC_RECORD' if rd.get('registrant_organization') else 'NOT_DISCLOSED',
                            'name':rd.get('registrant_organization'),'registrar':rd.get('registrar'),'source':reg.get('source'),
                            'detail':'A registry organization field is a public attribution clue, not verified identity. Privacy/proxy services may appear instead of the operator.'},
            'resource_hosts':sorted(parser.sources),'public_pages':parser.public_pages,
            'note':'Resource hosts are URLs referenced by the sampled HTML, not evidence of where a CDN receives original files. Nameservers, registrar and network provider have different roles from the website operator.'}
