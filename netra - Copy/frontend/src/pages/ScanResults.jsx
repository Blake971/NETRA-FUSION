 import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { startScan } from '../services/api'
import Navbar from '../components/Navbar'

export default function ScanResults() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const domain = searchParams.get('domain')
  
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [results, setResults] = useState(null)
  const [expandedSections, setExpandedSections] = useState({})

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  useEffect(() => {
    if (!domain) {
      navigate('/')
      return
    }

    const performScan = async () => {
      try {
        setLoading(true)
        setError(null)
        const response = await startScan(domain)
        setResults(response)
      } catch (err) {
        setError('Failed to scan domain. Please try again.')
        console.error('Scan error:', err)
      } finally {
        setLoading(false)
      }
    }

    performScan()
  }, [domain, navigate])

  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'low': return 'text-emerald-500'
      case 'medium': return 'text-amber-500'
      case 'high': return 'text-orange-500'
      case 'critical': return 'text-red-500'
      default: return 'text-slate-400'
    }
  }

  const getRiskBg = (level) => {
    switch (level?.toLowerCase()) {
      case 'low': return 'bg-emerald-500/20 border-emerald-500'
      case 'medium': return 'bg-amber-500/20 border-amber-500'
      case 'high': return 'bg-orange-500/20 border-orange-500'
      case 'critical': return 'bg-red-500/20 border-red-500'
      default: return 'bg-slate-500/20 border-slate-500'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-cyan-500 mx-auto mb-4"></div>
          <h2 className="text-2xl font-semibold mb-2">Scanning {domain}...</h2>
          <p className="text-slate-400">Analyzing security configuration</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-semibold mb-2 text-red-500">Scan Failed</h2>
          <p className="text-slate-400 mb-4">{error}</p>
          <div className="text-left bg-slate-800 rounded-lg p-4 mb-6 text-sm text-slate-300">
            <p className="font-medium mb-2">Common reasons:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Domain doesn't exist or has DNS issues</li>
              <li>Website is down or not responding</li>
              <li>No SSL certificate (HTTP-only site)</li>
              <li>Network timeout or firewall blocking</li>
              <li>Invalid domain format</li>
            </ul>
          </div>
          <button
            onClick={() => navigate('/')}
            className="bg-cyan-500 hover:bg-cyan-600 text-white px-6 py-2 rounded-lg transition"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Navbar */}
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Security Assessment for {domain}</h1>
          <p className="text-slate-400">Netra passive assessment completed</p>
        </div>

        {/* Risk Score Card */}
        <div className={`border rounded-lg p-6 mb-8 bg-slate-800 border-slate-700`}>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">Security Score</h2>
              <p className={`text-4xl font-bold ${getRiskColor(results?.data?.risk_level)}`}>
                {results?.data?.risk_score || 'N/A'}/100
              </p>
              <p className={`text-lg font-semibold mt-2 ${getRiskColor(results?.data?.risk_level)}`}>
                {results?.data?.risk_level?.toUpperCase() || 'UNKNOWN'} RISK
              </p>
            </div>
            <div className="text-right">
              <p className="text-lg font-semibold mb-1">Execution Time</p>
              <p className="text-2xl font-bold text-cyan-500">
                {results?.data?.execution_time || 'N/A'}s
              </p>
            </div>
          </div>
          <p className="text-sm mt-4 text-slate-300">
            {results?.data?.risk_summary || 'Scan completed'}
          </p>
          
          {/* Score Breakdown */}
          {results?.data?.score_breakdown && (
            <div className="mt-4 pt-4 border-t border-slate-700">
              <p className="text-sm font-medium mb-2 text-slate-400">Score Breakdown</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">SSL:</span>
                  <span className={results.data.score_breakdown.ssl < 0 ? 'text-red-400' : 'text-emerald-400'}>
                    {results.data.score_breakdown.ssl >= 0 ? '+' : ''}{results.data.score_breakdown.ssl}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Headers:</span>
                  <span className={results.data.score_breakdown.headers < 0 ? 'text-red-400' : 'text-emerald-400'}>
                    {results.data.score_breakdown.headers >= 0 ? '+' : ''}{results.data.score_breakdown.headers}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">DNS:</span>
                  <span className={results.data.score_breakdown.dns < 0 ? 'text-red-400' : 'text-emerald-400'}>
                    {results.data.score_breakdown.dns >= 0 ? '+' : ''}{results.data.score_breakdown.dns}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">WHOIS:</span>
                  <span className={results.data.score_breakdown.whois < 0 ? 'text-red-400' : 'text-emerald-400'}>
                    {results.data.score_breakdown.whois >= 0 ? '+' : ''}{results.data.score_breakdown.whois}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Risk Issues */}
        {results?.data?.risk_deductions && results.data.risk_deductions.length > 0 && (
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-8">
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <span className="text-2xl">⚠️</span> Security Findings
            </h3>
            <div className="space-y-3">
              {results.data.risk_deductions.map((deduction, idx) => (
                <div key={idx} className="border-l-4 border-red-500 pl-4 py-2">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <p className="font-medium text-red-400">{deduction.finding}</p>
                      <p className="text-sm text-slate-400 mt-1">{deduction.explanation}</p>
                      {deduction.evidence && (
                        <p className="text-xs text-slate-500 mt-1">Evidence: {deduction.evidence}</p>
                      )}
                      {deduction.recommendation && (
                        <p className="text-xs text-cyan-400 mt-1">Recommendation: {deduction.recommendation}</p>
                      )}
                    </div>
                    <span className={`text-xs px-2 py-1 rounded ml-4 ${
                      deduction.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-500' :
                      deduction.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-500' :
                      deduction.severity === 'MEDIUM' ? 'bg-amber-500/20 text-amber-500' :
                      'bg-emerald-500/20 text-emerald-500'
                    }`}>
                      {deduction.severity}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {/* Infrastructure Intelligence Card */}
          {results?.data?.normalized?.infrastructure_intelligence && (
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">🌍</span>
                <h3 className="text-lg font-semibold">Where is this website running?</h3>
              </div>
              
              {/* Simple Summary */}
              {results.data.normalized.infrastructure_intelligence.simple_summary && (
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span className="text-slate-400">IP Address</span>
                    <span className="font-medium">{results.data.normalized.infrastructure_intelligence.simple_summary.ip_address}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Hosting Provider</span>
                    <span className="font-medium">{results.data.normalized.infrastructure_intelligence.simple_summary.hosting_provider}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Location</span>
                    <span className="font-medium">{results.data.normalized.infrastructure_intelligence.simple_summary.location}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Organization</span>
                    <span className="font-medium text-sm">{results.data.normalized.infrastructure_intelligence.simple_summary.organization}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">ASN</span>
                    <span className="font-medium">{results.data.normalized.infrastructure_intelligence.simple_summary.asn}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Confidence</span>
                    <span className={`font-medium ${
                      results.data.normalized.infrastructure_intelligence.confidence === 'HIGH' ? 'text-emerald-500' :
                      results.data.normalized.infrastructure_intelligence.confidence === 'MODERATE' ? 'text-cyan-500' :
                      'text-amber-500'
                    }`}>
                      {results.data.normalized.infrastructure_intelligence.confidence}
                    </span>
                  </div>
                </div>
              )}
              
              {/* Explanation */}
              {results.data.normalized.infrastructure_intelligence.explanation && (
                <p className="text-xs text-slate-400 mb-3">
                  {results.data.normalized.infrastructure_intelligence.explanation}
                </p>
              )}
              
              {/* Technical Details Accordion */}
              <button
                onClick={() => toggleSection('infrastructure')}
                className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
              >
                {expandedSections.infrastructure ? '▼' : '▶'} View Technical Details
              </button>
              
              {expandedSections.infrastructure && results.data.normalized.infrastructure_intelligence.technical_details && (
                <div className="mt-3 pt-3 border-t border-slate-700 text-xs space-y-1">
                  {Object.entries(results.data.normalized.infrastructure_intelligence.technical_details).map(([key, value]) => (
                    value && (
                      <div key={key} className="flex justify-between">
                        <span className="text-slate-500">{key}:</span>
                        <span className="text-slate-300">{String(value)}</span>
                      </div>
                    )
                  ))}
                </div>
              )}
              
              <p className="text-xs text-slate-500 mt-3">
                Source: {results.data.normalized.infrastructure_intelligence.source}
              </p>
            </div>
          )}

          {/* Domain Registration Card */}
          {results?.data?.normalized?.whois && (
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">📅</span>
                <h3 className="text-lg font-semibold">Domain Registration</h3>
              </div>
              
              {/* Simple Summary */}
              {results.data.normalized.whois.simple_summary && (
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Registration Date</span>
                    <span className="font-medium">{results.data.normalized.whois.simple_summary.registration_date}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Domain Age</span>
                    <span className="font-medium">{results.data.normalized.whois.simple_summary.domain_age}</span>
                  </div>
                  {results.data.normalized.whois.simple_summary.registrar && (
                    <div className="flex justify-between">
                      <span className="text-slate-400">Registrar</span>
                      <span className="font-medium text-sm">{results.data.normalized.whois.simple_summary.registrar}</span>
                    </div>
                  )}
                  {results.data.normalized.whois.simple_summary.expiry_date && (
                    <div className="flex justify-between">
                      <span className="text-slate-400">Expiry Date</span>
                      <span className="font-medium">{results.data.normalized.whois.simple_summary.expiry_date}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-slate-400">Status</span>
                    <span className="font-medium">{results.data.normalized.whois.simple_summary.status}</span>
                  </div>
                </div>
              )}
              
              {/* Explanation */}
              {results.data.normalized.whois.explanation && (
                <p className="text-xs text-slate-400 mb-3">
                  {results.data.normalized.whois.explanation}
                </p>
              )}
              
              {/* Technical Details Accordion */}
              <button
                onClick={() => toggleSection('whois')}
                className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
              >
                {expandedSections.whois ? '▼' : '▶'} View Technical Details
              </button>
              
              {expandedSections.whois && results.data.normalized.whois.technical_details && (
                <div className="mt-3 pt-3 border-t border-slate-700 text-xs space-y-1">
                  {Object.entries(results.data.normalized.whois.technical_details).map(([key, value]) => (
                    value && (
                      <div key={key} className="flex justify-between">
                        <span className="text-slate-500">{key}:</span>
                        <span className="text-slate-300">{Array.isArray(value) ? value.join(', ') : String(value)}</span>
                      </div>
                    )
                  ))}
                </div>
              )}
            </div>
          )}

          {/* SSL Configuration Card */}
          {results?.data?.normalized?.ssl && (
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">🔒</span>
                <h3 className="text-lg font-semibold">Connection Security</h3>
              </div>
              
              {/* Simple Summary */}
              {results.data.normalized.ssl.simple_summary && (
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Status</span>
                    <span className={`font-medium ${results.data.normalized.ssl.simple_summary.status === 'Secure' ? 'text-emerald-500' : 'text-red-500'}`}>
                      {results.data.normalized.ssl.simple_summary.status}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Protocol</span>
                    <span className="font-medium">{results.data.normalized.ssl.simple_summary.protocol}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Certificate Valid For</span>
                    <span className={`font-medium ${results.data.normalized.ssl.simple_summary.days_remaining < 30 ? 'text-red-500' : 'text-emerald-500'}`}>
                      {results.data.normalized.ssl.simple_summary.days_remaining} days
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Issuer</span>
                    <span className="font-medium text-sm">{results.data.normalized.ssl.simple_summary.issuer}</span>
                  </div>
                </div>
              )}
              
              {/* Explanation */}
              {results.data.normalized.ssl.explanation && (
                <p className="text-xs text-slate-400 mb-3">
                  {results.data.normalized.ssl.explanation}
                </p>
              )}
              
              {/* Technical Details Accordion */}
              <button
                onClick={() => toggleSection('ssl')}
                className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
              >
                {expandedSections.ssl ? '▼' : '▶'} View Technical Details
              </button>
              
              {expandedSections.ssl && results.data.normalized.ssl.technical_details && (
                <div className="mt-3 pt-3 border-t border-slate-700 text-xs space-y-1">
                  {Object.entries(results.data.normalized.ssl.technical_details).map(([key, value]) => (
                    value && (
                      <div key={key} className="flex justify-between">
                        <span className="text-slate-500">{key}:</span>
                        <span className="text-slate-300">{Array.isArray(value) ? value.join(', ') : String(value)}</span>
                      </div>
                    )
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* AI Summary */}
        {results?.data?.ai_summary && results.data.ai_summary.status !== 'FALLBACK' && (
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-8">
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <span className="text-2xl">🤖</span> AI Analysis
            </h3>
            {results.data.ai_summary.executive_summary && (
              <div className="mb-4">
                <p className="text-sm font-medium text-cyan-400 mb-1">Executive Summary</p>
                <p className="text-slate-300 text-sm">{results.data.ai_summary.executive_summary}</p>
              </div>
            )}
            {results.data.ai_summary.technical_summary && (
              <div className="mb-4">
                <p className="text-sm font-medium text-cyan-400 mb-1">Technical Summary</p>
                <p className="text-slate-300 text-sm">{results.data.ai_summary.technical_summary}</p>
              </div>
            )}
            {results.data.ai_summary.recommendations?.length > 0 && (
              <div>
                <p className="text-sm font-medium text-cyan-400 mb-2">Recommendations</p>
                <ul className="list-disc list-inside space-y-1">
                  {results.data.ai_summary.recommendations.map((rec, idx) => (
                    <li key={idx} className="text-sm text-slate-300">{rec}</li>
                  ))}
                </ul>
              </div>
            )}
            <p className="text-xs text-slate-500 mt-4">
              Powered by {results.data.ai_summary.model === 'fallback' ? 'NETRA Fallback' : 'Gemini AI'}
            </p>
          </div>
        )}

        {/* Detailed Results */}
        <h2 className="text-2xl font-bold mb-6">Detailed Analysis</h2>
        
        {/* Results Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* DNS Results */}
          {results?.data?.normalized?.dns && (
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <span className="text-2xl">🌐</span> DNS Configuration
              </h3>
              
              {/* Simple Summary */}
              {results.data.normalized.dns.simple_summary && (
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Website Address</span>
                    <span className="font-medium">{results.data.normalized.dns.simple_summary.website_address}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Email Configured</span>
                    <span className={`font-medium ${results.data.normalized.dns.simple_summary.has_email ? 'text-emerald-500' : 'text-slate-500'}`}>
                      {results.data.normalized.dns.simple_summary.has_email ? '✓ Yes' : '✗ No'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">DNS Servers</span>
                    <span className={`font-medium ${results.data.normalized.dns.simple_summary.has_dns_servers ? 'text-emerald-500' : 'text-slate-500'}`}>
                      {results.data.normalized.dns.simple_summary.has_dns_servers ? '✓ Yes' : '✗ No'}
                    </span>
                  </div>
                </div>
              )}
              
              {/* Explanation */}
              {results.data.normalized.dns.explanation && (
                <p className="text-sm text-slate-400 mb-4">
                  {results.data.normalized.dns.explanation}
                </p>
              )}
              
              {/* Technical Details Accordion */}
              <button
                onClick={() => toggleSection('dns')}
                className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
              >
                {expandedSections.dns ? '▼' : '▶'} View Technical Details
              </button>
              
              {expandedSections.dns && results.data.normalized.dns.technical_details && (
                <div className="mt-3 pt-3 border-t border-slate-700 text-xs space-y-2">
                  {results.data.normalized.dns.technical_details.a_records && (
                    <div>
                      <p className="text-slate-500 font-medium">A Records:</p>
                      <div className="text-slate-300">
                        {results.data.normalized.dns.technical_details.a_records.map((r, i) => (
                          <p key={i}>{r}</p>
                        ))}
                      </div>
                    </div>
                  )}
                  {results.data.normalized.dns.technical_details.mx_records && (
                    <div>
                      <p className="text-slate-500 font-medium">MX Records:</p>
                      <div className="text-slate-300">
                        {results.data.normalized.dns.technical_details.mx_records.map((r, i) => (
                          <p key={i}>{typeof r === 'object' ? r.exchange : r}</p>
                        ))}
                      </div>
                    </div>
                  )}
                  {results.data.normalized.dns.technical_details.ns_records && (
                    <div>
                      <p className="text-slate-500 font-medium">NS Records:</p>
                      <div className="text-slate-300">
                        {results.data.normalized.dns.technical_details.ns_records.map((r, i) => (
                          <p key={i}>{r}</p>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Security Headers Results */}
          {results?.data?.normalized?.headers && (
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <span className="text-2xl">🛡️</span> Security Headers
              </h3>
              
              {/* Simple Summary */}
              {results.data.normalized.headers.simple_summary && (
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">HSTS (HTTPS Enforcement)</span>
                    <span className={`font-medium ${
                      results.data.normalized.headers.simple_summary.hsts === 'FOUND' ? 'text-emerald-500' :
                      results.data.normalized.headers.simple_summary.hsts === 'MISSING' ? 'text-red-500' :
                      'text-slate-500'
                    }`}>
                      {results.data.normalized.headers.simple_summary.hsts === 'FOUND' ? '✓ Present' :
                       results.data.normalized.headers.simple_summary.hsts === 'MISSING' ? '✗ Missing' : '? Unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">CSP (Content Protection)</span>
                    <span className={`font-medium ${
                      results.data.normalized.headers.simple_summary.csp === 'FOUND' ? 'text-emerald-500' :
                      results.data.normalized.headers.simple_summary.csp === 'MISSING' ? 'text-red-500' :
                      'text-slate-500'
                    }`}>
                      {results.data.normalized.headers.simple_summary.csp === 'FOUND' ? '✓ Present' :
                       results.data.normalized.headers.simple_summary.csp === 'MISSING' ? '✗ Missing' : '? Unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">X-Frame-Options</span>
                    <span className={`font-medium ${
                      results.data.normalized.headers.simple_summary.x_frame_options === 'FOUND' ? 'text-emerald-500' :
                      results.data.normalized.headers.simple_summary.x_frame_options === 'MISSING' ? 'text-amber-500' :
                      'text-slate-500'
                    }`}>
                      {results.data.normalized.headers.simple_summary.x_frame_options === 'FOUND' ? '✓ Present' :
                       results.data.normalized.headers.simple_summary.x_frame_options === 'MISSING' ? '✗ Missing' : '? Unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">X-Content-Type-Options</span>
                    <span className={`font-medium ${
                      results.data.normalized.headers.simple_summary.x_content_type_options === 'FOUND' ? 'text-emerald-500' :
                      results.data.normalized.headers.simple_summary.x_content_type_options === 'MISSING' ? 'text-amber-500' :
                      'text-slate-500'
                    }`}>
                      {results.data.normalized.headers.simple_summary.x_content_type_options === 'FOUND' ? '✓ Present' :
                       results.data.normalized.headers.simple_summary.x_content_type_options === 'MISSING' ? '✗ Missing' : '? Unknown'}
                    </span>
                  </div>
                </div>
              )}
              
              {/* Explanation */}
              {results.data.normalized.headers.explanation && (
                <p className="text-sm text-slate-400 mb-4">
                  {results.data.normalized.headers.explanation}
                </p>
              )}
              
              {/* Technical Details Accordion */}
              <button
                onClick={() => toggleSection('headers')}
                className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
              >
                {expandedSections.headers ? '▼' : '▶'} View Technical Details
              </button>
              
              {expandedSections.headers && results.data.normalized.headers.technical_details && (
                <div className="mt-3 pt-3 border-t border-slate-700 text-xs space-y-1">
                  {Object.entries(results.data.normalized.headers.technical_details).map(([key, value]) => (
                    value && (
                      <div key={key} className="flex justify-between">
                        <span className="text-slate-500">{key}:</span>
                        <span className="text-slate-300">{typeof value === 'object' ? JSON.stringify(value) : String(value)}</span>
                      </div>
                    )
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Email Security & CT Logs */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          {/* Email Security */}
          {results?.data?.results?.email_security && (
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <span className="text-2xl">📧</span> Email Security
              </h3>
              {(() => {
                const email = results.data.results.email_security
                const data = email.data || {}
                return (
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">SPF</span>
                      <span className={`font-medium ${data.spf?.present ? 'text-emerald-500' : 'text-red-500'}`}>
                        {data.spf?.present ? '✓ Configured' : '✗ Missing'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">DMARC</span>
                      <span className={`font-medium ${data.dmarc?.present ? 'text-emerald-500' : 'text-red-500'}`}>
                        {data.dmarc?.present ? `✓ ${data.dmarc.policy || 'Configured'}` : '✗ Missing'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">DKIM</span>
                      <span className={`font-medium ${data.dkim?.present ? 'text-emerald-500' : 'text-amber-500'}`}>
                        {data.dkim?.present ? `✓ ${data.dkim.selectors_found || 0} selector(s)` : '? Not detected'}
                      </span>
                    </div>
                    {email.message && (
                      <p className="text-xs text-slate-400 pt-2 border-t border-slate-700">{email.message}</p>
                    )}
                  </div>
                )
              })()}
            </div>
          )}

          {/* Certificate Transparency */}
          {results?.data?.results?.ct_logs && results.data.results.ct_logs.status === 'SUCCESS' && (
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <span className="text-2xl">📜</span> Certificate Transparency
              </h3>
              {(() => {
                const ct = results.data.results.ct_logs.data || {}
                return (
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Certificates Found</span>
                      <span className="font-medium">{ct.total_certificates || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Subdomains Discovered</span>
                      <span className="font-medium">{ct.unique_subdomains || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Wildcard Certificates</span>
                      <span className="font-medium">{ct.wildcard_certificates || 0}</span>
                    </div>
                    {ct.subdomains?.length > 0 && (
                      <div className="pt-2 border-t border-slate-700">
                        <p className="text-xs text-slate-500 mb-2">Top subdomains:</p>
                        <div className="flex flex-wrap gap-1">
                          {ct.subdomains.slice(0, 8).map((sub, i) => (
                            <span key={i} className="text-xs bg-slate-700 px-2 py-0.5 rounded text-slate-300">{sub}</span>
                          ))}
                          {ct.subdomains.length > 8 && (
                            <span className="text-xs text-slate-500">+{ct.subdomains.length - 8} more</span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })()}
            </div>
          )}
        </div>

        {/* Scan Another */}
        <div className="mt-8 text-center">
          <button
            onClick={() => navigate('/')}
            className="bg-cyan-500 hover:bg-cyan-600 text-white px-8 py-3 rounded-lg font-semibold transition"
          >
            Scan Another Domain
          </button>
        </div>
      </div>
    </div>
  )
}
