"""Small policy checks with deliberately limited claims.

HSTS: https://www.rfc-editor.org/rfc/rfc6797
SPF: https://www.rfc-editor.org/rfc/rfc7208
"""
import re

def positive_hsts(value):
    """Check for one numeric, positive max-age directive, not mere header presence."""
    directives = [x.strip() for x in value.split(';') if x.strip()]
    ages = [x for x in directives if x.split('=', 1)[0].strip().lower() == 'max-age']
    if len(ages) != 1:
        return False
    match = re.fullmatch(r'max-age\s*=\s*(?:"([0-9]+)"|([0-9]+))', ages[0], re.I)
    return bool(match and int(match.group(1) or match.group(2)) > 0)

def sender_policy(records):
    """Check selection and obvious broad authorization, not full SPF evaluation."""
    policies = [x for x in records if re.match(r'^v=spf1(?:\s|$)', x, re.I)]
    if len(policies) != 1:
        return False, 'Expected one SPF record; observed ' + str(len(policies)) + '.'
    tokens = policies[0].lower().split()[1:]
    # An unqualified all mechanism is equivalent to +all. Earlier mechanisms
    # can still reject some senders, so do not claim that literally all mail passes.
    if any(token in ('all', '+all') for token in tokens):
        return False, 'SPF contains an all/+all mechanism that can authorize otherwise unmatched senders.'
    return True, 'One SPF record observed. Sender authorization, DNS lookup limits, and delivery were not evaluated.'
