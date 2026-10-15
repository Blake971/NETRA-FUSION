import unittest
import ssl
from unittest.mock import patch, MagicMock
import run_netra
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fusion_breach import build_breach_router, normalize_breaches
from fusion_research import queries
from fusion_hosting import attribution, ip_context, _cache
from fusion_engine import resolve_retry, collect
from fusion_transport import pinned_connection
from fusion_registration import registration_summary
from test_audience import fixture
import dns.resolver

class ExpansionTests(unittest.TestCase):
    def test_google_default_has_no_target_restriction(self):
        result=queries('example.com','documents','public research')
        self.assertNotIn('site:example.com',result[0]['query'])
        self.assertIn('filetype:docx',result[0]['query'])
        self.assertEqual(result[0]['scope_note'],'Across Google')

    def test_external_references_do_not_conflict_with_site_scope(self):
        for kind in ('social','papers','code'):
            result=queries('example.com',kind,'','website')[0]
            self.assertIn('"example.com"',result['query'])
            self.assertNotIn('site:example.com',result['query'])
            self.assertEqual(result['scope_note'],'External references to this domain')
        self.assertIn('site:example.com',queries('example.com','documents','','website')[0]['query'])

    def test_empty_topic_and_invalid_website(self):
        with self.assertRaises(ValueError):queries()
        with self.assertRaises(ValueError):queries('https://user:pass@example.com','all','','website')

    def test_dns_retries_only_transient_failure(self):
        resolver=MagicMock();resolver.resolve.side_effect=[dns.resolver.LifetimeTimeout, ['record']]
        self.assertEqual(resolve_retry(resolver,'example.com','TXT'),(['record'],True))
        resolver.resolve.side_effect=dns.resolver.NXDOMAIN
        with self.assertRaises(dns.resolver.NXDOMAIN):resolve_retry(resolver,'example.com','TXT')

    def test_another_ip_on_connection_failure_but_not_certificate_failure(self):
        raw=MagicMock()
        with patch('fusion_transport.socket.create_connection',side_effect=[TimeoutError(),raw]) as connect, patch('fusion_transport.ssl.create_default_context'):
            conn,addresses=pinned_connection('example.com',lambda _:['93.184.216.34','93.184.216.35'])
            self.assertEqual(connect.call_count,2);conn.close()
        with patch('fusion_transport.socket.create_connection',return_value=raw) as connect,patch('fusion_transport.ssl.create_default_context') as ctx:
            ctx.return_value.wrap_socket.side_effect=ssl.SSLCertVerificationError()
            with self.assertRaises(ssl.SSLCertVerificationError):pinned_connection('example.com',lambda _:['93.184.216.34','93.184.216.35'])
            self.assertEqual(connect.call_count,1)

    def test_transient_collector_retry_does_not_invent_data(self):
        with patch.dict('fusion_engine.COLLECTORS',{'test':MagicMock(side_effect=[TimeoutError(),{'status':'SUCCESS','data':{}}])}):
            self.assertEqual(collect('test','example.com')['attempts'],2)
        with patch.dict('fusion_engine.COLLECTORS',{'test':MagicMock(side_effect=TimeoutError())}):
            result=collect('test','example.com');self.assertEqual(result['status'],'UNKNOWN');self.assertEqual(result['data'],{})

    def test_cloudflare_not_origin_or_owner(self):
        case=fixture();case['results']['web']['data']['headers']['cf-ray']='abcdef123456-DEL'
        case['results']['web']['data']['body']='<script src="https://cdn.example/library.js"></script><a href="/legal">Legal</a>'
        result=attribution(case)
        self.assertTrue(result['cloudflare_observed']);self.assertEqual(result['edge_code'],'DEL')
        self.assertEqual(result['origin']['state'],'NOT_ESTABLISHED')
        self.assertEqual(result['organization']['state'],'NOT_DISCLOSED')
        self.assertIn('cdn.example',result['resource_hosts']);self.assertIn('https://northstar.example/legal',result['public_pages'])

    def test_nameservers_alone_do_not_prove_cloudflare_proxy(self):
        case=fixture();case['results']['dns']['data']['NS']=['a.ns.cloudflare.com']
        self.assertFalse(attribution(case)['cloudflare_observed'])

    def test_ip_metadata_validated_and_cached_with_provenance(self):
        _cache.clear()
        with patch('fusion_hosting.public_json',return_value=({'success':True,'ip':'8.8.8.8','country':'US','org':'Example network','asn':'AS15169'},'https://ipapi.co/8.8.8.8/json/')) as provider:
            first=ip_context('8.8.8.8',None);second=ip_context('8.8.8.8',None)
            self.assertEqual(provider.call_count,1);self.assertTrue(second['cached']);self.assertEqual(first['observed_at'],second['observed_at'])
        with self.assertRaises(ValueError):ip_context('127.0.0.1',None)
        with patch('fusion_hosting.public_json',return_value=({'success':True,'ip':'1.1.1.1'},'')):
            with self.assertRaises(ValueError):ip_context('8.8.4.4',None)

    def test_location_fallback_retains_provider_source(self):
        _cache.clear()
        with patch('fusion_hosting.public_json',side_effect=[TimeoutError(),({'success':True,'ip':'8.8.4.4','country':'US','connection':{'org':'Fallback network','asn':123}},'https://ipwho.is/8.8.4.4')]):
            result=ip_context('8.8.4.4',None)
            self.assertEqual(result['network'],'Fallback network');self.assertEqual(result['source'],'https://ipwho.is/8.8.4.4')
            self.assertEqual(result['provider_failures'][0]['provider'],'ipapi')

    def test_registrant_org_is_separate_from_registrar(self):
        row={'objectClassName':'domain','ldhName':'example.com','entities':[{'roles':['registrar'],'vcardArray':['vcard',[['fn',{},'text','Registration service']]]},{'roles':['registrant'],'vcardArray':['vcard',[['org',{},'text','Published organization'],['fn',{},'text','Person name']]]}]}
        result=registration_summary(row,'example.com');self.assertEqual(result['registrar'],'Registration service');self.assertEqual(result['registrant_organization'],'Published organization');self.assertNotIn('Person name',str(result))

class EmailTests(unittest.TestCase):
    def setUp(self):
        app=FastAPI();app.include_router(build_breach_router());self.client=TestClient(app)
    def tearDown(self):self.client.close()
    def send(self):return self.client.post('/api/email-check',json={'email':'owner@example.com','consent':True})
    def test_demo_no_provider_and_no_submitted_email_returned(self):
        with patch('fusion_breach.provider_lookup') as provider:
            result=self.client.post('/api/email-check',json={'demo':True,'email':'private@example.com'})
            self.assertTrue(result.json()['demo']);provider.assert_not_called();self.assertNotIn('private@example.com',result.text)
            self.assertEqual(result.headers['cache-control'],'no-store')
    def test_requires_consent_and_credentials(self):
        self.assertEqual(self.client.post('/api/email-check',json={'email':'owner@example.com'}).status_code,422)
        with patch.dict('os.environ',{'HIBP_API_KEY':''}):self.assertEqual(self.send().status_code,503)
    def test_404_is_limited_no_known_match(self):
        with patch.dict('os.environ',{'HIBP_API_KEY':'fixture'}),patch('fusion_breach.provider_lookup',return_value=(404,None,'6')):
            result=self.send();self.assertEqual(result.json()['state'],'NO_KNOWN_MATCH');self.assertIn('does not prove safety',result.json()['detail'])
    def test_provider_errors_are_not_safe_results(self):
        for code in (401,403,429,500):
            app=FastAPI();app.include_router(build_breach_router())
            with TestClient(app) as client,patch.dict('os.environ',{'HIBP_API_KEY':'fixture'}),patch('fusion_breach.provider_lookup',return_value=(code,None,'6')):
                result=client.post('/api/email-check',json={'email':'owner@example.com','consent':True})
                self.assertIn(result.status_code,(429,503));self.assertNotIn('NO_KNOWN_MATCH',result.text)
    def test_matching_incidents_and_rate_limit(self):
        row={'Name':'Example','Title':'Example incident','Domain':'example.com','BreachDate':'2020-01-01','DataClasses':['Email addresses'],'IsVerified':False,'Description':'<script>bad</script>'}
        with patch.dict('os.environ',{'HIBP_API_KEY':'fixture'}),patch('fusion_breach.provider_lookup',return_value=(200,[row],'6')):
            result=self.send();self.assertEqual(result.json()['state'],'MATCHES');self.assertNotIn('<script>',result.text);self.assertNotIn('owner@example.com',result.text)
            self.assertEqual(self.send().status_code,429)
