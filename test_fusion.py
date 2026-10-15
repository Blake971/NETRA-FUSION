"""Offline regression tests: python -m unittest test_fusion -v."""
import asyncio
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import run_netra
import fusion_api
from fusion_engine import analyze, demo_results, evidence_digest, normalize_domain, public_addresses
from fastapi.testclient import TestClient

class EvidenceTests(unittest.TestCase):
    def test_unknown_never_looks_secure(self):
        result = analyze('example.com', {})
        self.assertIsNone(result['score'])
        self.assertEqual(result['coverage'], 0)
        self.assertEqual(result['findings'], [])

    def test_score_matches_evidence(self):
        result = analyze('northstar.example', demo_results())
        self.assertEqual(result['score'], 100 - sum(f['points'] for f in result['findings']))
        self.assertEqual(result['coverage'], 100)
        self.assertNotIn('framing', [f['id'] for f in result['findings']])
        self.assertTrue(result['challenged'])

    def test_partial_dns_does_not_penalize_timeout(self):
        data = demo_results()
        data['dns']['status'] = 'PARTIAL'
        data['dns']['errors'] = {'DMARC': 'Timeout'}
        result = analyze('northstar.example', data)
        self.assertNotIn('dmarc', [f['id'] for f in result['findings']])
        self.assertLess(result['coverage'], 100)

    def test_error_response_is_not_missing_headers(self):
        data = demo_results()
        data['web']['data']['status_code'] = 403
        result = analyze('northstar.example', data)
        self.assertFalse(any(f['category'] == 'Web' for f in result['findings']))

    def test_invalid_framing_controls_do_not_pass(self):
        data = demo_results()
        data['web']['data']['headers'] = {'x-frame-options': 'garbage', 'content-security-policy': 'frame-ancestors *'}
        self.assertIn('framing', [f['id'] for f in analyze('example.com', data)['findings']])

    def test_caa_absence_is_advisory_due_to_inheritance(self):
        result = analyze('northstar.example', demo_results())
        self.assertEqual(next(f['points'] for f in result['findings'] if f['id'] == 'caa'), 0)

    def test_digest_detects_evidence_changes(self):
        data = demo_results()
        changed = copy.deepcopy(data)
        changed['web']['data']['protocol'] = 'TLSv1.2'
        self.assertNotEqual(evidence_digest(data), evidence_digest(changed))
        self.assertEqual(evidence_digest(data), evidence_digest(copy.deepcopy(data)))

    def test_domain_validation(self):
        self.assertEqual(normalize_domain('HTTPS://Example.COM/path'), 'example.com')
        for value in ['127.0.0.1', 'localhost', 'x.internal', 'https://user:pass@example.com', 'https://example.com:8080', 'a;whoami.com']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_domain(value)

    def test_private_dns_addresses_blocked(self):
        with patch('fusion_engine.dns.resolver.Resolver') as resolver:
            resolver.return_value.resolve.return_value = ['127.0.0.1']
            with self.assertRaises(ValueError):
                public_addresses('example.com')

    def test_permissions_policy_absence_detected(self):
        data = demo_results()
        self.assertIn('permissions_policy', [f['id'] for f in analyze('example.com', data)['findings']])

    def test_permissions_policy_present_passes(self):
        data = demo_results()
        data['web']['data']['headers']['permissions-policy'] = 'geolocation=()'
        self.assertNotIn('permissions_policy', [f['id'] for f in analyze('example.com', data)['findings']])

    def test_referrer_policy_absence_detected(self):
        data = demo_results()
        self.assertIn('referrer_policy', [f['id'] for f in analyze('example.com', data)['findings']])

    def test_referrer_policy_present_passes(self):
        data = demo_results()
        data['web']['data']['headers']['referrer-policy'] = 'strict-origin-when-cross-origin'
        self.assertNotIn('referrer_policy', [f['id'] for f in analyze('example.com', data)['findings']])

    def test_wildcard_cors_detected(self):
        data = demo_results()
        data['web']['data']['headers']['access-control-allow-origin'] = '*'
        self.assertIn('cors', [f['id'] for f in analyze('example.com', data)['findings']])

    def test_specific_cors_passes(self):
        data = demo_results()
        data['web']['data']['headers']['access-control-allow-origin'] = 'https://trusted.example.com'
        self.assertNotIn('cors', [f['id'] for f in analyze('example.com', data)['findings']])

    def test_certificate_expiry_tiered_scoring(self):
        data = demo_results()
        data['web']['data']['days_remaining'] = 5
        result = analyze('example.com', data)
        expiry_finding = next(f for f in result['findings'] if f['id'] == 'tls_expiry')
        self.assertEqual(expiry_finding['points'], 15)
        data['web']['data']['days_remaining'] = 10
        result = analyze('example.com', data)
        expiry_finding = next(f for f in result['findings'] if f['id'] == 'tls_expiry')
        self.assertEqual(expiry_finding['points'], 10)
        data['web']['data']['days_remaining'] = 20
        result = analyze('example.com', data)
        expiry_finding = next(f for f in result['findings'] if f['id'] == 'tls_expiry')
        self.assertEqual(expiry_finding['points'], 5)

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=run_netra.ROOT)
        self.db = patch.object(fusion_api, 'DB', Path(self.temp.name) / 'test.db')
        self.db.start()
        self.client = TestClient(fusion_api.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.db.stop()
        self.temp.cleanup()

    def test_demo_full_lifecycle(self):
        response = self.client.post('/api/cases', json={'demo': True})
        self.assertEqual(response.status_code, 202)
        identifier = response.json()['id']
        # Synchronize with the background tasks rather than sleeping.
        self.client.portal.call(self.wait_jobs)
        case = self.client.get('/api/cases/' + identifier).json()
        self.assertEqual(case['status'], 'COMPLETED')
        self.assertTrue(case['demo'])
        self.assertEqual(case['evidence_sha256'], evidence_digest(case['results']))
        self.assertEqual(self.client.get('/api/cases').json()[0]['id'], identifier)
        self.assertEqual(self.client.get('/api/cases/' + identifier + '/export').json(), case)

    def test_clear_history_removes_saved_cases(self):
        identifier = self.client.post('/api/cases', json={'demo': True}).json()['id']
        self.client.portal.call(self.wait_jobs)
        result = self.client.delete('/api/cases')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()['deleted'], 1)
        self.assertEqual(self.client.get('/api/cases').json(), [])
        self.assertEqual(self.client.get('/api/cases/' + identifier).status_code, 404)

    def test_hibp_requires_consent_and_key(self):
        self.assertEqual(self.client.post('/api/email-check', json={'email': 'user@example.com'}).status_code, 422)
        with patch.dict('os.environ', {'HIBP_API_KEY': ''}):
            self.assertEqual(self.client.post('/api/email-check', json={'email': 'user@example.com', 'consent': True}).status_code, 503)

    async def wait_jobs(self):
        await asyncio.gather(*list(fusion_api.TASKS))

    def test_missing_case_and_invalid_target(self):
        self.assertEqual(self.client.get('/api/cases/missing').status_code, 404)
        self.assertEqual(self.client.post('/api/cases', json={'domain': 'localhost'}).status_code, 422)

    def test_ai_unavailable_preserves_evidence(self):
        identifier = self.client.post('/api/cases', json={'demo': True}).json()['id']
        self.client.portal.call(self.wait_jobs)
        original = self.client.get('/api/cases/' + identifier).json()
        with patch.object(fusion_api, 'explain', side_effect=ValueError('AI not configured')):
            self.assertEqual(self.client.post('/api/cases/' + identifier + '/explain').status_code, 503)
        self.assertEqual(self.client.get('/api/cases/' + identifier).json(), original)

    def test_ai_explanation_cached_without_changing_score(self):
        identifier = self.client.post('/api/cases', json={'demo': True}).json()['id']
        self.client.portal.call(self.wait_jobs)
        original = self.client.get('/api/cases/' + identifier).json()
        with patch.object(fusion_api, 'explain', return_value={'mode': 'mock', 'text': 'Review TLS expiry', 'model': 'fixture'}) as explain:
            result = self.client.post('/api/cases/' + identifier + '/explain').json()
            self.client.post('/api/cases/' + identifier + '/explain')
            explain.assert_called_once()
        self.assertEqual(result['assessment'], original['assessment'])
        self.assertEqual(result['evidence_sha256'], original['evidence_sha256'])

    def test_untrusted_host_rejected(self):
        self.assertEqual(self.client.get('/api/health', headers={'host': 'attacker.example'}).status_code, 400)

    def test_live_private_target_fails_without_collecting(self):
        with patch.object(fusion_api, 'public_addresses', side_effect=ValueError('Non-public target')), patch.object(fusion_api, 'collect') as collect:
            identifier = self.client.post('/api/cases', json={'domain': 'example.com'}).json()['id']
            self.client.portal.call(self.wait_jobs)
            self.assertEqual(self.client.get('/api/cases/' + identifier).json()['status'], 'FAILED')
            collect.assert_not_called()

if __name__ == '__main__':
    unittest.main()
