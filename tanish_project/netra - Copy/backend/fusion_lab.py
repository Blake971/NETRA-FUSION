"""Offline, independently labeled evidence-fixture benchmark; not internet accuracy."""
import copy
import hashlib
import json
from fusion_transport import timestamp

def benchmark(analyze):
    base={'web':{'status':'SUCCESS','data':{'status_code':200,'tls_state':'VALID','days_remaining':180,'protocol':'TLSv1.3','headers':{'strict-transport-security':'max-age=86400','content-security-policy':"default-src 'self'; frame-ancestors 'self'",'x-content-type-options':'nosniff'}}},
          'dns':{'status':'SUCCESS','data':{'TXT':['v=spf1 -all'],'DMARC':['v=DMARC1; p=reject'],'CAA':['0 issue "ca.example"']}},'certificates':{'status':'SUCCESS','data':{'names':[]}}}
    specs=[('Expected controls','baseline','hsts','PASS'),('Missing HTTPS policy','missing_hsts','hsts','GAP'),('Disabled HTTPS policy','zero_hsts','hsts','GAP'),
           ('Quoted HTTPS duration','quoted_hsts','hsts','PASS'),('Duplicate HTTPS duration','duplicate_hsts','hsts','GAP'),
           ('CSP replaces framing header','baseline','framing','PASS'),('Missing framing controls','missing_csp','framing','GAP'),
           ('Missing content policy','missing_csp','csp','GAP'),('Missing file handling rule','missing_nosniff','nosniff','GAP'),
           ('Certificate renewal soon','renewal','tls_expiry','GAP'),('Expired certificate','expired','tls_expiry','GAP'),
           ('HTTP blocked, TLS retained','http_blocked','hsts','UNKNOWN'),('DNS timeout','dns_timeout','spf','UNKNOWN'),
           ('Two SPF records','spf_duplicate','spf','GAP'),('Broad SPF authorization','spf_broad','spf','GAP'),
           ('Monitoring-only email policy','dmarc_monitor','dmarc','GAP'),('Duplicate DMARC tags','dmarc_duplicate','dmarc','GAP'),
           ('DMARC testing mode','dmarc_test','dmarc','GAP')]
    rows=[]; corpus=[]; counts={'true_positive':0,'false_positive':0,'false_negative':0,'true_negative':0,'unknown_outputs':0}
    for name,variant,check,expected in specs:
        data=copy.deepcopy(base); headers=data['web']['data']['headers']; dns=data['dns']['data']
        if variant=='missing_hsts': headers.pop('strict-transport-security')
        if variant=='zero_hsts': headers['strict-transport-security']='max-age=0'
        if variant=='quoted_hsts': headers['strict-transport-security']='max-age="86400"'
        if variant=='duplicate_hsts': headers['strict-transport-security']='max-age=86400; max-age=0'
        if variant=='missing_csp': headers.pop('content-security-policy')
        if variant=='missing_nosniff': headers.pop('x-content-type-options')
        if variant=='renewal': data['web']['data']['days_remaining']=8
        if variant=='expired': data['web']={'status':'PARTIAL','data':{'tls_state':'EXPIRED'}}
        if variant=='http_blocked': data['web']['data']['status_code']=403
        if variant=='dns_timeout': data['dns']={'status':'UNKNOWN','data':{}}
        if variant=='spf_duplicate': dns['TXT']=['v=spf1 -all','v=spf1 ~all']
        if variant=='spf_broad': dns['TXT']=['v=spf1 +all']
        if variant=='dmarc_monitor': dns['DMARC']=['v=DMARC1; p=none']
        if variant=='dmarc_duplicate': dns['DMARC']=['v=DMARC1; p=reject; p=none']
        if variant=='dmarc_test': dns['DMARC']=['v=DMARC1; p=reject; t=y']
        actual=next(c['state'] for c in analyze('fixture.example',data)['checks'] if c['id']==check)
        rows.append({'scenario':name,'check':check,'expected':expected,'actual':actual,'matched':actual==expected})
        corpus.append({'input':data,'check':check,'expected':expected})
        if actual=='UNKNOWN': counts['unknown_outputs']+=1
        if expected=='GAP': counts['true_positive' if actual=='GAP' else 'false_negative']+=1
        elif expected=='PASS':
            if actual=='GAP': counts['false_positive']+=1
            elif actual=='PASS': counts['true_negative']+=1
    tp,fp,fn=counts['true_positive'],counts['false_positive'],counts['false_negative']
    return {'ran_at':timestamp(),'corpus_version':'1.0','cases':rows,'total':len(rows),'matched':sum(r['matched'] for r in rows),'counts':counts,
            'precision':round(tp/(tp+fp),3) if tp+fp else None,'recall':round(tp/(tp+fn),3) if tp+fn else None,
            'corpus_sha256':hashlib.sha256(json.dumps(corpus,sort_keys=True).encode()).hexdigest(),
            'scope':'Offline evidence-fixture benchmark of selected rules. Inputs are controlled synthetic observations, not live websites. These metrics do not estimate real-world detection accuracy; network collection and full policy semantics are outside this benchmark.'}
