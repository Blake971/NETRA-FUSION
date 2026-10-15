import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { getScanHistory, deleteScan } from '../services/api'

export default function ScanHistory() {
  const navigate = useNavigate()
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      setLoading(true)
      const response = await getScanHistory()
      setScans(response.data?.scans || [])
    } catch (err) {
      setError('Failed to load scan history')
      console.error('History error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (scanId) => {
    if (!confirm('Delete this scan?')) return
    try {
      await deleteScan(scanId)
      setScans(prev => prev.filter(s => s.scan_id !== scanId))
    } catch (err) {
      console.error('Delete error:', err)
    }
  }

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
      case 'low': return 'bg-emerald-500/10 border-emerald-500/30'
      case 'medium': return 'bg-amber-500/10 border-amber-500/30'
      case 'high': return 'bg-orange-500/10 border-orange-500/30'
      case 'critical': return 'bg-red-500/10 border-red-500/30'
      default: return 'bg-slate-500/10 border-slate-500/30'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900">
        <Navbar />
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500 mx-auto mb-4"></div>
            <p className="text-slate-400">Loading scan history...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">Scan History</h1>
            <p className="text-slate-400 mt-1">{scans.length} scan{scans.length !== 1 ? 's' : ''} recorded</p>
          </div>
          <button
            onClick={() => navigate('/')}
            className="bg-cyan-500 hover:bg-cyan-600 text-white px-6 py-2 rounded-lg font-semibold transition"
          >
            New Scan
          </button>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {scans.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">🔍</div>
            <h2 className="text-2xl font-semibold mb-2">No Scans Yet</h2>
            <p className="text-slate-400 mb-6">Start your first security assessment to see results here.</p>
            <button
              onClick={() => navigate('/')}
              className="bg-cyan-500 hover:bg-cyan-600 text-white px-8 py-3 rounded-lg font-semibold transition"
            >
              Run First Scan
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {scans.map(scan => (
              <div
                key={scan.scan_id}
                className={`border rounded-lg p-5 hover:border-cyan-500/50 transition cursor-pointer ${getRiskBg(scan.risk_level)}`}
                onClick={() => navigate(`/scan?domain=${scan.domain}`)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold">{scan.domain}</h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${getRiskColor(scan.risk_level)} bg-slate-800`}>
                        {scan.risk_level?.toUpperCase() || 'N/A'}
                      </span>
                    </div>
                    <p className="text-sm text-slate-400 mt-1">
                      {scan.created_at ? new Date(scan.created_at).toLocaleString() : 'Unknown date'}
                      {' · '}
                      {scan.execution_time ? `${scan.execution_time}s` : 'N/A'}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className={`text-2xl font-bold ${getRiskColor(scan.risk_level)}`}>
                        {scan.risk_score || 'N/A'}
                      </p>
                      <p className="text-xs text-slate-500">/100</p>
                    </div>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDelete(scan.scan_id) }}
                      className="text-slate-500 hover:text-red-400 transition p-2"
                      title="Delete scan"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
