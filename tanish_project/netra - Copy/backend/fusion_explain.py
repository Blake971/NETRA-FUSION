"""Plain-language interpretation of recorded evidence, never a second risk engine."""
from html import escape

# title, analogy, impact, owner, next step, technical term
GUIDE = {
    'hsts': ('Keep visits on an encrypted connection', 'A sign that tells returning browsers to use the protected entrance.', 'Without this instruction, browsers may attempt an unencrypted connection before reaching HTTPS.', 'Website administrator', 'Ask your website administrator to enable a valid HTTPS-only browser policy after testing it.', 'HSTS'),
    'csp': ('Set rules for what the page may load', 'A guest list for scripts and other content on a page.', 'A content policy can limit the damage of injected content. A missing policy does not prove an attack is possible.', 'Web developer', 'Ask the developer to inventory needed content, test a report-only policy, and then enforce it.', 'Content Security Policy / CSP'),
    'framing': ('Control who may embed the website', 'A rule about who may place your page inside their own window.', 'Unrestricted embedding may help someone trick visitors into clicking disguised controls.', 'Web developer', 'Ask the developer to restrict embedding to approved sites.', 'X-Frame-Options / CSP frame-ancestors'),
    'nosniff': ('Tell browsers how to handle files', 'A clear label on a package, so the browser does not guess its contents.', 'Browser guessing can cause some files to be handled in unexpected ways.', 'Website administrator', 'Ask the administrator to send correct file types and the nosniff instruction.', 'X-Content-Type-Options'),
    'tls_expiry': ('Keep the website certificate current', 'A website identity document with an expiry date.', 'If renewal is missed, visitors may see warnings and trusted connections may fail.', 'Hosting or website administrator', 'Check the renewal date, enable automatic renewal, and add an expiry reminder.', 'TLS certificate expiry'),
    'tls_protocol': ('Use a modern encrypted connection', 'An updated lock for information travelling between browser and website.', 'Older connection protocols may provide weaker protection. One handshake cannot test every supported option.', 'Hosting provider', 'Ask the host to review TLS settings and support modern protocols.', 'TLS protocol'),
    'spf': ('Publish an authorized email-sender list', 'A public list of mail services allowed to send for your domain.', 'A missing or obviously unusable sender policy weakens one part of email authentication; this is not a delivered-email test.', 'Email administrator', 'Ask the email administrator to review legitimate senders and publish one suitable SPF record.', 'SPF'),
    'dmarc': ('Tell mail providers how to handle impersonation', 'Instructions for what to do when a message fails identity checks.', 'A missing or monitoring-only policy does not request quarantine or rejection of failing messages. Receiver behavior and delivery are not tested.', 'Email administrator', 'Review sender alignment and reports, then move carefully toward quarantine or rejection.', 'DMARC'),
    'caa': ('Review who may issue website certificates', 'A public list of certificate issuers you permit.', 'The domain may inherit a policy from its parent. An absent local record alone is not enough to deduct points.', 'Domain administrator', 'Check the parent-domain policy before deciding whether a local CAA record is needed.', 'CAA'),
}

GLOSSARY = [
    {'term': 'OSINT', 'meaning': 'Open-source intelligence: learning from publicly available information.', 'example': 'NETRA reads public website and domain records.'},
    {'term': 'Domain', 'meaning': 'The readable name people use to reach a website.', 'example': 'example.com'},
    {'term': 'DNS', 'meaning': 'The internet directory that connects names to services.', 'example': 'It can tell us which computers serve a website or receive its email.'},
    {'term': 'IP address', 'meaning': 'A network address used to reach a computer or service.', 'example': 'One address can be shared by many websites; it does not identify a person.'},
    {'term': 'TLS / HTTPS', 'meaning': 'Protection for information travelling between a browser and a website.', 'example': 'An encrypted connection does not prove that the website itself is trustworthy.'},
    {'term': 'Certificate transparency', 'meaning': 'Public logs of issued website certificates.', 'example': 'A historical name in a log might no longer have a working website.'},
    {'term': 'Evidence coverage', 'meaning': 'How many of NETRA’s configured checks had enough information to reach a result.', 'example': '100% means all configured checks were observed, not that the whole website was audited.'},
    {'term': 'Security score', 'meaning': '100 minus deductions for the specific observed checks. Higher is better.', 'example': '70/100 is not a 70% chance of safety or a 30% chance of being hacked.'},
    {'term': 'Unknown', 'meaning': 'NETRA could not collect enough evidence to answer this check.', 'example': 'A timeout is a measurement gap, not proof that the site is unsafe.'},
    {'term': 'Public footprint', 'meaning': 'Website information visible in the sources that were checked.', 'example': 'A public document or social link can be intentional and is not automatically a leak.'},
    {'term': 'Evidence review', 'meaning': 'Rules check whether a finding is supported and whether another observed control changes it.', 'example': 'An existing page-embedding policy can remove a duplicate warning.'},
]

def interpret(case):
    """Explain stored check states without changing scores or claiming extra observations."""
    a = case['assessment']
    findings = {f['id']: f for f in a['findings']}
    cards = []
    for check in a['checks']:
        title, analogy, impact, owner, action, term = GUIDE.get(check['id'], (check['title'], '', 'Review the recorded evidence.', 'Website administrator', 'Review this check with the administrator.', check['id']))
        f = findings.get(check['id'])
        state = check['state']
        advisory = state == 'GAP' and check['weight'] == 0
        label = 'Could not check' if state == 'UNKNOWN' else 'Observed control' if state == 'PASS' else 'Review suggested' if advisory else 'Needs attention'
        cards.append({'id': check['id'], 'category': check['category'], 'title': title, 'analogy': analogy, 'impact': impact,
                      'owner': owner, 'action': action, 'term': term, 'state': state, 'label': label,
                      'advisory': advisory, 'points': f['points'] if f else 0, 'evidence': f['evidence'] if f else None})
    attention = sorted([c for c in cards if c['state'] == 'GAP' and not c['advisory']], key=lambda c: -c['points'])
    unknown = sum(c['state'] == 'UNKNOWN' for c in cards)
    passed = sum(c['state'] == 'PASS' for c in cards)
    advisory = sum(c['advisory'] for c in cards)
    title = 'We need more information' if a['score'] is None else 'Some protections need attention' if attention else 'No scored gaps in the observed checks'
    summary = f"We checked public information about {case['domain']}. {passed} checks found an expected control, {len(attention)} need attention, {advisory} are advisory, and {unknown} could not be answered."
    limits = 'This is an outside checkup of selected public signals. It does not inspect private accounts, test attacks, or guarantee that a website is safe.'
    if case['demo']:
        summary = 'This is a fictional demonstration, not a live website result. ' + summary
    first = attention[0] if attention else None
    speech = f"NETRA helps us understand a website’s public security signals without needing to read technical records. {summary} " + (f"Our first practical step is: {first['action']} " if first else 'We should review any unanswered checks before drawing wider conclusions. ') + limits
    return {'title': title, 'summary': summary, 'cards': cards, 'priorities': attention[:3], 'counts': {'pass': passed, 'attention': len(attention), 'advisory': advisory, 'unknown': unknown},
            'score_note': 'Higher is better. This score is a checklist result, not a percentage chance of safety.',
            'coverage_note': f"{len(cards) - unknown} of {len(cards)} configured checks had usable evidence. Unknown checks do not remove points.",
            'limits': limits, 'speech': speech, 'glossary': GLOSSARY}

def audience_report(case):
    """Return a self-contained, escaped HTML handout with no external dependencies."""
    a = interpret(case)
    e = lambda value: escape(str(value))
    cards = ''.join(f"<article><h2>{e(c['title'])}</h2><b>{e(c['label'])}</b><p>{e(c['analogy'])}</p><p><strong>Why it matters:</strong> {e(c['impact'])}</p>" +
                    (f"<p><strong>Next step:</strong> {e(c['action'])} <strong>Who:</strong> {e(c['owner'])}</p>" if c['state'] == 'GAP' else '') +
                    (f"<details><summary>Evidence</summary><p>{e(c['evidence'])}</p></details>" if c['evidence'] else '') + '</article>' for c in a['cards'])
    score = case['assessment']['score']
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>NETRA checkup — {e(case['domain'])}</title>
<style>body{{font:16px/1.65 system-ui,sans-serif;max-width:900px;margin:40px auto;padding:0 24px;color:#183b36}}h1{{font-size:36px}}article{{padding:18px 0;border-bottom:1px solid #ccd9d5;break-inside:avoid}}.hero{{background:#edf8f2;padding:28px;border-radius:14px}}small{{color:#48635e}}@media print{{body{{margin:0;max-width:none}}details{{display:block}}}}</style>
<header><small>NETRA FUSION · WEBSITE CHECKUP</small><h1>{e(case['domain'])}</h1><p>{'FICTIONAL DEMO DATA' if case['demo'] else 'LIVE PUBLIC OBSERVATIONS'} · {e(case.get('completed_at', ''))}</p></header>
<section class="hero"><h2>{e(a['title'])}</h2><p>{e(a['summary'])}</p><strong>Score: {e(score if score is not None else 'Unknown')}/100</strong><p>{e(a['score_note'])}</p><p>{e(a['coverage_note'])}</p></section>
<h2>How to explain this to your audience</h2><p>{e(a['speech'])}</p>{cards}<h2>What this report can tell us</h2><p>{e(a['limits'])}</p><p>Use your browser’s Print command to save this handout as a PDF.</p><small>Assessment {e(case['id'])}<br>Evidence SHA-256: {e(case['evidence_sha256'])}</small></html>"""
