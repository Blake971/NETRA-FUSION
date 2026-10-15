"""Source-linked context and competing explanations for each scored observation."""
from fusion_email import dmarc_policy
from fusion_policy import sender_policy

def intelligence(case):
    results=case.get('results',{})
    web=results.get('web',{})
    dns=results.get('dns',{})
    dd=dns.get('data',{})
    registration=results.get('registration',{'status':'UNKNOWN','data':{},'source':'Not collected in this checkup'})
    reviews=[]
    for finding in case['assessment']['findings']:
        collector='dns' if finding['category'] in ('Email','DNS') else 'web'
        source=results.get(collector,{})
        alternatives = ('A parent-domain certificate-issuer policy may apply.' if finding['id']=='caa' else
                        'Mail alignment, receiver behavior and inherited policies can change practical protection.' if finding['category']=='Email' else
                        'The sampled root response may differ from other pages or from a response seen by another client.' if finding['category']=='Web' else
                        'The observed certificate or protocol can differ across hosts, routes or trust stores.')
        reviews.append({'id':finding['id'],'observation':finding['evidence'],'initial_question':finding['title'],
                        'alternative':alternatives,'conclusion':'Advisory review; no deduction.' if not finding['points'] else 'A gap was observed under this rule. Exploitability is not established.',
                        'source':source.get('source',collector),'observed_at':source.get('observed_at'),'collector':collector,'confidence':'Rule-supported observation, not a statistical probability'})
    for item in case['assessment']['challenged']:
        reviews.append({'id':'challenge-'+str(len(reviews)), 'initial_question':item['title'],'observation':item['reason'],
                        'alternative':'Another control or missing evidence changes the interpretation.','conclusion':'No unsupported deduction applied.','source':'Deterministic cross-check','observed_at':case.get('completed_at')})
    names={}
    for node in case['assessment']['graph']['nodes']:
        kind=node['kind']
        name='certificates' if kind=='certificate name' else 'dns' if kind in ('address','mail server') else None
        source=results.get(name,{})
        names[node['id']]={'source':source.get('source',node['source']),'observed_at':source.get('observed_at'), 'kind':kind,
                          'reachability':'Not tested' if kind!='domain' else 'Only root HTTPS checked when collection succeeded'}
    spf_known='TXT' in dd and 'TXT' not in dns.get('errors',{})
    dmarc_known='DMARC' in dd and 'DMARC' not in dns.get('errors',{})
    spf=sender_policy(dd.get('TXT',[])) if spf_known else (None,'No usable TXT observation.')
    return {'registration':registration,'transport':{'state':web.get('data',{}).get('tls_state','VALID' if web.get('status')=='SUCCESS' else 'UNKNOWN'),
                'details':web.get('data',{}),'source':web.get('source'),'observed_at':web.get('observed_at'),'error':web.get('error')},
            'email':{'spf':{'state':'UNKNOWN' if spf[0] is None else 'OBSERVED' if spf[0] else 'REVIEW','detail':spf[1]},
                     'dmarc':dmarc_policy(dd['DMARC']) if dmarc_known else {'state':'UNKNOWN','detail':'No usable direct DMARC observation.'}},
            'reviews':reviews,'assets':names}
