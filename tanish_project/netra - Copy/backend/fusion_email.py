"""Policy structure and user-supplied DKIM selector checks; not mail delivery tests."""
import base64
import re
import dns.resolver
from fusion_transport import timestamp

def tags(record):
    result = {}
    for part in record.split(';'):
        if not part.strip():
            continue
        if '=' not in part:
            raise ValueError('Malformed tag')
        key, value = (x.strip() for x in part.split('=',1))
        key = key.lower()
        if key in result:
            raise ValueError('Duplicate tag: '+key)
        result[key] = value
    return result

def dmarc_policy(records):
    policies = [r for r in records if re.match(r'^v=DMARC1\s*(?:;|$)',r,re.I)]
    if len(policies)!=1:
        return {'state':'REVIEW','enforcing':False,'detail':f'Expected one directly published DMARC policy; observed {len(policies)}. Parent-policy discovery was not performed.'}
    try:
        parsed = tags(policies[0])
        policy = parsed.get('p','').lower()
        if policy not in ('none','quarantine','reject') or parsed.get('adkim','r') not in ('r','s') or parsed.get('aspf','r') not in ('r','s'):
            raise ValueError('Invalid policy or alignment tag')
        if parsed.get('sp',policy) not in ('none','quarantine','reject') or parsed.get('t','n') not in ('y','n'):
            raise ValueError('Invalid subdomain or testing tag')
        enforcing = policy in ('quarantine','reject') and parsed.get('t','n') != 'y'
        return {'state':'OBSERVED' if enforcing else 'REVIEW','enforcing':enforcing,'policy':policy,
                'detail':f'Direct policy p={policy}; testing mode t={parsed.get("t","n")}. Syntax checks are limited; alignment, inherited policies and receiver behavior were not tested.',
                'legacy_percentage':parsed.get('pct'), 'note':'The historical pct tag is shown as context, not treated as current policy enforcement.'}
    except ValueError as exc:
        return {'state':'REVIEW','enforcing':False,'detail':str(exc)}

def dkim_record(records):
    if len(records)!=1:
        return {'state':'UNKNOWN' if not records else 'REVIEW','detail':'No unique key record at this selector. This does not establish whether other selectors are configured.'}
    try:
        parsed = tags(records[0])
        if parsed.get('v','DKIM1').upper()!='DKIM1' or 'p' not in parsed:
            raise ValueError('No usable DKIM key tag')
        if not parsed['p'].strip():
            return {'state':'REVIEW','detail':'The public key is empty; this selector is revoked.'}
        raw = base64.b64decode(re.sub(r'\s+','',parsed['p']),validate=True)
        if not raw:
            raise ValueError('Empty key')
        return {'state':'OBSERVED','detail':'A nonempty base64 key was observed. Key strength, cryptographic validity and message signatures were not verified.','key_type':parsed.get('k','rsa'),'decoded_bytes':len(raw)}
    except (ValueError,TypeError) as exc:
        return {'state':'REVIEW','detail':'Malformed key record: '+str(exc)}

def selector_lookup(domain, selector):
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,62}[A-Za-z0-9])?',selector):
        raise ValueError('Use a selector such as selector1, with letters, numbers, dots, hyphens or underscores.')
    resolver = dns.resolver.Resolver()
    resolver.lifetime = 4
    name = selector+'._domainkey.'+domain
    try:
        answer = resolver.resolve(name,'TXT')
        records = [b''.join(r.strings).decode('utf-8',errors='replace') for r in answer]
        result = dkim_record(records)
        return {'selector':selector,'source':name,'observed_at':timestamp(),'records':records,**result}
    except (dns.resolver.NoAnswer,dns.resolver.NXDOMAIN):
        return {'selector':selector,'source':name,'observed_at':timestamp(),**dkim_record([])}
    except dns.exception.DNSException:
        return {'selector':selector,'source':name,'observed_at':timestamp(),'state':'UNKNOWN','detail':'The DNS query failed. No deduction was made.'}
