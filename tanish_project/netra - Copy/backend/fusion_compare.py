"""Conservative comparisons: missing evidence must never masquerade as a fix."""
def compare(before, after):
    """Compare like-for-like check states and mark noncomparable measurements."""
    if before['domain'] != after['domain'] or before['demo'] != after['demo']:
        raise ValueError('Choose two assessments of the same domain and the same demo/live mode.')
    if before['created_at'] > after['created_at']:
        raise ValueError('The baseline must be older than the current assessment.')
    old, new = before['assessment'], after['assessment']
    a = {c['id']: c for c in old['checks']}
    b = {c['id']: c for c in new['checks']}
    changes = []
    for key in sorted(a.keys() | b.keys()):
        x, y = a.get(key), b.get(key)
        old_state, new_state = x['state'] if x else 'NOT_CHECKED', y['state'] if y else 'NOT_CHECKED'
        if old_state == new_state:
            continue
        label = 'Needs another check' if old_state in ('UNKNOWN', 'NOT_CHECKED') or new_state in ('UNKNOWN', 'NOT_CHECKED') else 'Observed improvement' if new_state == 'PASS' else 'Newly observed gap'
        changes.append({'id': key, 'title': (y or x)['title'], 'before': old_state, 'after': new_state, 'meaning': label})
    comparable = (old.get('methodology') == new.get('methodology') and a.keys() == b.keys() and
                  all(a[k]['weight'] == b[k]['weight'] and a[k]['state'] != 'UNKNOWN' and b[k]['state'] != 'UNKNOWN' for k in a) and
                  old['score'] is not None and new['score'] is not None)
    asset_changes = []
    for collector, fields in [('dns', ('A','AAAA','MX','NS')), ('certificates', ('names',))]:
        x, y = before.get('results',{}).get(collector,{}), after.get('results',{}).get(collector,{})
        for field in fields:
            usable = all(r.get('status') in ('SUCCESS','PARTIAL') and field in r.get('data',{}) and field not in r.get('errors',{}) for r in (x,y))
            if not usable:
                asset_changes.append({'type':field,'meaning':'Comparison unavailable','detail':'One sample is missing this source. No disappearance inferred.'})
                continue
            old_values, new_values = set(x['data'][field]), set(y['data'][field])
            for meaning, values in [('Newly observed',new_values-old_values),('Not observed in newer sample',old_values-new_values)]:
                for value in sorted(values):
                    asset_changes.append({'type':field,'meaning':meaning,'detail':value,'source':y.get('source'), 'observed_at':y.get('observed_at')})
    followup = []
    for key, action in before.get('actions',{}).items():
        state = b.get(key,{}).get('state','UNKNOWN')
        followup.append({'title':a.get(key,{}).get('title',key),'owner':action.get('owner'), 'planned_status':action.get('status'), 'observed_state':state,
                         'meaning':'Expected control observed in the newer checkup' if state=='PASS' else 'Gap still observed' if state=='GAP' else 'Unable to verify; another check is needed'})
    return {'before_id': before['id'], 'after_id': after['id'], 'changes': changes, 'asset_changes':asset_changes, 'action_followup':followup, 'comparable': comparable,
            'score_change': new['score'] - old['score'] if comparable else None,
            'explanation': 'Same rules and fully observed checks; compare the recorded results in context.' if comparable else 'Score changes are hidden because rules or evidence coverage differ. A missing observation is not a verified fix.'}
