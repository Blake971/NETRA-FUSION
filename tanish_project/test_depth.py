import sqlite3
from contextlib import closing
import ssl
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import test_fusion
from test_audience import fixture
from fusion_engine import analyze
from fusion_email import dkim_record, dmarc_policy
from fusion_lab import benchmark
from fusion_registration import registration_summary
from fusion_transport import capture_web, certificate_failure, public_json
from fusion_compare import compare

class DepthTests(unittest.TestCase):
    def test_controlled_benchmark(self):
        result=benchmark(analyze)
        self.assertEqual(result['matched'],18)
        self.assertEqual(result['counts']['false_positive'],0)
        self.assertEqual(result['counts']['false_negative'],0)

    def test_email_limits(self):
        self.assertEqual(dkim_record(['v=DKIM1; p='])['state'],'REVIEW')
        self.assertEqual(dkim_record([])['state'],'UNKNOWN')
        self.assertEqual(dkim_record(['p=%%%'])['state'],'REVIEW')
        self.assertIn('not verified',dkim_record(['p=YWJj'])['detail'])
        for record in ['v=DMARC1; p=reject; p=none','v=DMARC1; p=reject; t=y']:
            self.assertFalse(dmarc_policy([record])['enforcing'])

    def test_registration_identity(self):
        data={'objectClassName':'domain','ldhName':'EXAMPLE.COM','events':[{'eventAction':'expiration','eventDate':'2030-01-01T00:00:00Z'}]}
        result=registration_summary(data,'example.com')
        self.assertGreater(result['days_until_expiry'],0)
        self.assertIn('expiration',result['events'])
        with self.assertRaises(ValueError):registration_summary(data,'other.com')

    def test_tls_failure_categories(self):
        for message,state in [('certificate has expired','EXPIRED'),('Hostname mismatch','HOSTNAME_MISMATCH'),('certificate is not yet valid','NOT_YET_VALID'),('self signed certificate','TRUST_FAILED')]:
            exc=ssl.SSLCertVerificationError();exc.verify_message=message
            self.assertEqual(certificate_failure(exc)['tls_state'],state)
            with patch('fusion_transport.pinned_connection',side_effect=exc):
                result=capture_web('example.com',lambda _:[])
                self.assertEqual(result['status'],'PARTIAL')
                checks={c['id']:c['state'] for c in analyze('example.com',{'web':result})['checks']}
                self.assertEqual(checks['hsts'],'UNKNOWN')
                self.assertEqual(checks['tls_expiry'],'GAP' if state=='EXPIRED' else 'UNKNOWN')

    def test_http_failure_retains_tls(self):
        conn=MagicMock();conn.sock.getpeercert.return_value={'notAfter':'Jan  1 00:00:00 2030 GMT'};conn.sock.version.return_value='TLSv1.3';conn.request.side_effect=OSError()
        with patch('fusion_transport.pinned_connection',return_value=(conn,['93.184.216.34'])):
            result=capture_web('example.com',lambda _:[])
        checks={c['id']:c['state'] for c in analyze('example.com',{'web':result})['checks']}
        self.assertEqual(checks['hsts'],'UNKNOWN');self.assertEqual(checks['tls_protocol'],'PASS');conn.close.assert_called_once()

    def test_redirect_revalidates_host(self):
        conn=MagicMock();conn.getresponse.return_value.status=302;conn.getresponse.return_value.getheader.return_value='https://127.0.0.1/private'
        with patch('fusion_transport.pinned_connection',side_effect=[(conn,[]),ValueError('private host')]) as mocked:
            with self.assertRaises(ValueError):public_json('https://registry.example/data',lambda _:[])
            self.assertEqual(mocked.call_args.args[0],'127.0.0.1')

    def test_asset_missing_source_and_action_recheck(self):
        before,after=fixture(),fixture(True)
        before['actions']={'hsts':{'status':'Ready to recheck','owner':'Team'}}
        after['results']['certificates']={'status':'UNKNOWN','data':{}}
        result=compare(before,after)
        self.assertEqual(result['action_followup'][0]['observed_state'],'PASS')
        self.assertTrue(any(r['meaning']=='Comparison unavailable' for r in result['asset_changes']))
        self.assertFalse(any(r['type']=='names' and r['meaning']=='Not observed in newer sample' for r in result['asset_changes']))

class ResearchApiTests(unittest.TestCase):
    setUp=test_fusion.ApiTests.setUp
    tearDown=test_fusion.ApiTests.tearDown
    wait_jobs=test_fusion.ApiTests.wait_jobs

    def create(self):
        identifier=self.client.post('/api/cases',json={'demo':True}).json()['id']
        self.client.portal.call(self.wait_jobs)
        return '/api/cases/'+identifier

    def test_notebook_lifecycle_and_backup(self):
        base=self.create();original=self.client.get(base).json()
        lead={'title':'Public report','url':'https://example.com/report.pdf','notes':'Review publication','status':'To review'}
        saved=self.client.post(base+'/research',json=lead)
        self.assertEqual(saved.status_code,201,saved.text);item=saved.json()
        self.assertEqual(self.client.post(base+'/research',json=lead).status_code,409)
        self.assertEqual(self.client.post(base+'/research',json=lead|{'url':'javascript:alert(1)'}).status_code,422)
        result=self.client.patch(base+'/research/'+item['id'],json=lead|{'status':'Follow up'})
        self.assertEqual(result.json()['status'],'Follow up')
        other=self.create();self.assertEqual(self.client.delete(other+'/research/'+item['id']).status_code,404)
        after=self.client.get(base).json();self.assertEqual(original['assessment'],after['assessment']);self.assertEqual(len(after['research']),1)
        backup=self.client.get('/api/backup');self.assertEqual(backup.status_code,200)
        path=Path(self.temp.name)/'restore.sqlite3';path.write_bytes(backup.content)
        with closing(sqlite3.connect(path)) as restored:
            self.assertEqual(restored.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertEqual(restored.execute('SELECT count(*) FROM research').fetchone()[0],1)
        self.assertEqual(self.client.delete(base+'/research/'+item['id']).status_code,200)
        self.assertEqual(self.client.get(base+'/research').json()['items'],[])

    def test_queries_and_lab(self):
        base=self.create()
        result=self.client.post(base+'/research/queries',json={'scope':'website','keyword':'" OR site:other.com'}).json()
        self.assertEqual(len(result['queries']),13)
        self.assertTrue(all('northstar.example' in q['query'] for q in result['queries']))
        self.assertTrue(all('site:other.com' not in q['query'] for q in result['queries']))
        self.assertEqual(self.client.post(base+'/research/queries',json={'purpose':'bad'}).status_code,422)
        self.assertEqual(self.client.get('/api/lab').json()['matched'],18)
        self.assertEqual(self.client.post(base+'/dkim',json={'selector':'selector1'}).status_code,409)

    def test_supplemental_key_persists_without_score_change(self):
        base=self.create();case=self.client.get(base).json();case['demo']=False;case['domain']='example.com';test_fusion.fusion_api.save(case)
        result={'selector':'selector1','state':'UNKNOWN','detail':'No record','source':'selector1._domainkey.example.com'}
        with patch('fusion_local.selector_lookup',return_value=result):
            self.assertEqual(self.client.post(base+'/dkim',json={'selector':'selector1'}).status_code,200)
        updated=self.client.get(base).json();self.assertEqual(updated['supplemental'],[result]);self.assertEqual(updated['assessment'],case['assessment'])
