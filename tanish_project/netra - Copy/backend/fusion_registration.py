"""Domain RDAP via IANA bootstrap; no guess at the owner of a domain."""
import time
from datetime import datetime, timezone
from urllib.parse import quote
from fusion_transport import public_json, timestamp

_bootstrap = None
_loaded = 0

def registration_summary(data, domain):
    if data.get('objectClassName') != 'domain' or data.get('ldhName','').lower().rstrip('.') != domain:
        raise ValueError('Registry response does not match the requested domain.')
    events = {e.get('eventAction'):e.get('eventDate') for e in data.get('events',[]) if e.get('eventDate')}
    registrar = None
    organization = None
    for entity in data.get('entities',[]):
        if 'registrar' in entity.get('roles',[]):
            card = entity.get('vcardArray',[])
            registrar = next((x[3] for x in card[1] if len(x)>3 and x[0]=='fn'), None) if len(card)>1 else entity.get('handle')
        if 'registrant' in entity.get('roles',[]):
            card=entity.get('vcardArray',[])
            values=card[1] if len(card)>1 and isinstance(card[1],list) else []
            organization=next((x[3] for x in values if len(x)>3 and x[0]=='org'),None)
            if isinstance(organization,list):organization=', '.join(str(x) for x in organization)
    expiry = events.get('expiration')
    remaining = None
    if expiry:
        try:
            date = datetime.fromisoformat(expiry.replace('Z','+00:00'))
            if date.tzinfo:
                remaining = (date-datetime.now(timezone.utc)).days
        except ValueError:
            pass
    return {'events':events,'domain':domain,'registrar':registrar,'registrant_organization':organization,'registered_at':events.get('registration'), 'expires_at':expiry,
            'days_until_expiry':remaining, 'status':data.get('status',[]),
            'nameservers':[x.get('ldhName') for x in data.get('nameservers',[]) if x.get('ldhName')],
            'note':'Registry information is context, not proof of ownership, trustworthiness, or safety. Renewal dates may reflect registry lifecycle rules.'}

def rdap_snapshot(domain, resolve):
    global _bootstrap, _loaded
    if _bootstrap is None or time.monotonic()-_loaded > 3600:
        _bootstrap, _ = public_json('https://data.iana.org/rdap/dns.json',resolve)
        _loaded = time.monotonic()
    tld = domain.rsplit('.',1)[-1]
    urls = next((urls for suffixes, urls in _bootstrap.get('services',[]) if tld in suffixes), [])
    base = next((url for url in urls if url.startswith('https://')),None)
    if not base:
        raise ValueError('No HTTPS RDAP service listed for this domain ending.')
    data, source = public_json(base.rstrip('/')+'/domain/'+quote(domain,safe=''),resolve)
    return {'status':'SUCCESS','source':source,'observed_at':timestamp(),'data':registration_summary(data,domain)}
