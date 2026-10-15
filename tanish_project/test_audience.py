"""Regression coverage for interpretation, planning, and honest comparisons."""
import copy
import unittest
import test_fusion
from fusion_engine import analyze, demo_results, evidence_digest
from fusion_explain import interpret, audience_report
from fusion_footprint import footprint
from fusion_compare import compare
from fusion_policy import positive_hsts, sender_policy

def fixture(improved=False):
    results = demo_results(improved)
    return {'id': 'after' if improved else 'before', 'domain':'northstar.example', 'demo':True,
            'created_at': '2026-09-18T10:01:00+00:00' if improved else '2026-09-18T10:00:00+00:00',
            'assessment':analyze('northstar.example', results), 'results':results, 'evidence_sha256':evidence_digest(results)}

class InterpretationTests(unittest.TestCase):
    def test_counts_distinguish_advice_from_scored_findings(self):
        result = interpret(fixture())
        self.assertEqual(result['counts'], {'pass':4, 'attention':4, 'advisory':1, 'unknown':0})
        self.assertIn('Higher is better', result['score_note'])
        self.assertIn('fictional', result['summary'])

    def test_unknown_is_not_reported_as_safe(self):
        case = fixture()
        case['assessment'] = analyze(case['domain'], {})
        result = interpret(case)
        self.assertEqual(result['counts']['unknown'], 9)
        self.assertEqual(result['title'], 'We need more information')

    def test_safe_html_handout(self):
        case = fixture()
        case['domain'] = '<script>alert(1)</script>'
        html = audience_report(case)
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertIn('FICTIONAL DEMO DATA', html)

    def test_footprint_uses_real_anchors_and_host_boundaries(self):
        case = fixture()
        case['results']['web']['data']['body'] = '<p>github.com</p><a href="https://github.com.attacker.example/x">bad</a><a href="javascript:alert(1)">bad</a><a href="https://github.com/team?token=private">ok</a><a href="/report.pdf#page=2">doc</a>'
        result = footprint(case)
        self.assertEqual(len(result['links']), 2)
        self.assertTrue(all('private' not in link['url'] for link in result['links']))
        self.assertEqual(result['queries'][0]['query'], 'site:northstar.example')

    def test_comparison_detects_real_state_changes(self):
        result = compare(fixture(), fixture(True))
        self.assertTrue(result['comparable'])
        self.assertEqual(result['score_change'],45)
        self.assertEqual(len(result['changes']),5)

    def test_lost_evidence_never_becomes_verified_improvement(self):
        before, after = fixture(), fixture(True)
        after['assessment']['checks'][0]['state'] = 'UNKNOWN'
        result = compare(before, after)
        self.assertFalse(result['comparable'])
        self.assertIsNone(result['score_change'])
        self.assertEqual(next(c['meaning'] for c in result['changes'] if c['id']=='hsts'), 'Needs another check')

    def test_mixed_rules_and_targets_are_not_comparable(self):
        before, after = fixture(), fixture(True)
        after['assessment']['methodology'] = 'different version'
        self.assertFalse(compare(before, after)['comparable'])
        after['domain'] = 'different.example'
        with self.assertRaises(ValueError):
            compare(before, after)

    def test_disabled_or_malformed_hsts_not_passed(self):
        for value in ['', 'max-age=0', 'max-age=no', 'max-age=10;max-age=20']:
            self.assertFalse(positive_hsts(value))
        self.assertTrue(positive_hsts('max-age="86400"; includeSubDomains'))

    def test_spf_duplicate_and_broad_records_flagged(self):
        for records in [[], ['v=spf1 -all','v=spf1 ~all'], ['v=spf1 +all'], ['v=spf1 all']]:
            self.assertFalse(sender_policy(records)[0])
        self.assertTrue(sender_policy(['v=spf1 -all'])[0])

class AudienceApiTests(unittest.TestCase):
    setUp = test_fusion.ApiTests.setUp
    tearDown = test_fusion.ApiTests.tearDown
    wait_jobs = test_fusion.ApiTests.wait_jobs

    def test_actions_persist_without_altering_evidence(self):
        identifier = self.client.post('/api/cases', json={'demo':True}).json()['id']
        self.client.portal.call(self.wait_jobs)
        before = self.client.get('/api/cases/' + identifier).json()
        endpoint = '/api/cases/' + identifier + '/actions/hsts'
        response = self.client.patch(endpoint, json={'owner':'Website team','status':'In progress','notes':'Ask about staging.'})
        self.assertEqual(response.status_code,200)
        after = self.client.get('/api/cases/' + identifier).json()
        self.assertEqual(after['actions']['hsts']['owner'],'Website team')
        self.assertEqual(after['assessment'],before['assessment'])
        self.assertEqual(after['evidence_sha256'],before['evidence_sha256'])
        self.assertEqual(self.client.patch(endpoint, json={'status':'Verified safe'}).status_code,422)

    def test_report_and_comparison_endpoints(self):
        before = self.client.post('/api/cases', json={'demo':True}).json()['id']
        self.client.portal.call(self.wait_jobs)
        after = self.client.post('/api/cases', json={'demo':True,'demo_profile':'improved'}).json()['id']
        self.client.portal.call(self.wait_jobs)
        result = self.client.get(f'/api/cases/{after}/compare/{before}').json()
        self.assertEqual(result['score_change'],45)
        report = self.client.get(f'/api/cases/{after}/report')
        self.assertEqual(report.status_code,200)
        self.assertIn('attachment',report.headers['content-disposition'])
        self.assertIn('Higher is better',report.text)

if __name__ == '__main__':
    unittest.main()
