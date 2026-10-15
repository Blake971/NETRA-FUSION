import { useState } from 'react'
import Navbar from '../components/Navbar'
import { getGoogleDorks, getPersonDorks } from '../services/api'

export default function GoogleDork() {
  const [mode, setMode] = useState('domain') // 'domain' | 'person'
  const [domain, setDomain] = useState('')
  const [person, setPerson] = useState({ name: '', username: '', location: '', employer: '' })
  const [queries, setQueries] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [copiedIdx, setCopiedIdx] = useState(null)
  const [copiedAll, setCopiedAll] = useState(false)
  const [activeCategory, setActiveCategory] = useState('All')

  const updatePerson = (field) => (e) => setPerson({ ...person, [field]: e.target.value })

  const switchMode = (newMode) => {
    setMode(newMode)
    setQueries([])
    setError(null)
    setActiveCategory('All')
  }

  const handleGenerate = async (e) => {
    e.preventDefault()

    if (mode === 'domain' && !domain.trim()) return
    if (mode === 'person' && !person.name.trim()) {
      setError('Please enter a person name.')
      return
    }

    try {
      setLoading(true)
      setError(null)
      // Both endpoints return the axios body: { success, data: <module_result> },
      // and <module_result> is { module, status, ..., data: { queries } }, so the
      // queries live at response.data.data.queries (two levels, not three).
      const response = mode === 'domain'
        ? await getGoogleDorks(domain)
        : await getPersonDorks(person)
      setQueries(response.data?.data?.queries || [])
    } catch (err) {
      setError('Failed to generate queries. Check your input and try again.')
      console.error('Dork error:', err)
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text, idx) => {
    navigator.clipboard.writeText(text)
    setCopiedIdx(idx)
    setTimeout(() => setCopiedIdx(null), 2000)
  }

  const copyAllToClipboard = () => {
    // Copy every currently-visible query (respects the active category filter),
    // one per line, so they can be pasted into a text file or search tool.
    const text = filtered.map(q => q.query).join('\n')
    navigator.clipboard.writeText(text)
    setCopiedAll(true)
    setTimeout(() => setCopiedAll(false), 2000)
  }

  const categories = ['All', ...new Set(queries.map(q => q.category))]
  const filtered = activeCategory === 'All' ? queries : queries.filter(q => q.category === activeCategory)

  return (
    <div className="min-h-screen bg-slate-900">
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Google Dork Assistant</h1>
          <p className="text-slate-400 mt-1">
            Generate OSINT reconnaissance queries. Queries are generated only — never executed automatically.
          </p>
        </div>

        {/* Mode toggle */}
        <div className="flex gap-2 mb-6">
          <button
            type="button"
            onClick={() => switchMode('domain')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              mode === 'domain'
                ? 'bg-cyan-500 text-white'
                : 'bg-slate-800 text-slate-400 border border-slate-700 hover:border-slate-600'
            }`}
          >
            Domain
          </button>
          <button
            type="button"
            onClick={() => switchMode('person')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              mode === 'person'
                ? 'bg-cyan-500 text-white'
                : 'bg-slate-800 text-slate-400 border border-slate-700 hover:border-slate-600'
            }`}
          >
            Person / Username
          </button>
        </div>

        {/* Input */}
        <form onSubmit={handleGenerate} className="mb-8">
          {mode === 'domain' ? (
            <div className="flex gap-4">
              <input
                type="text"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="Enter domain (e.g., example.com)"
                className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition"
              />
              <button
                type="submit"
                disabled={loading}
                className="bg-cyan-500 hover:bg-cyan-600 disabled:opacity-50 text-white px-8 py-3 rounded-lg font-semibold transition"
              >
                {loading ? 'Generating...' : 'Generate'}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Full name *</label>
                  <input
                    type="text"
                    value={person.name}
                    onChange={updatePerson('name')}
                    placeholder="e.g., John Smith"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Username / handle</label>
                  <input
                    type="text"
                    value={person.username}
                    onChange={updatePerson('username')}
                    placeholder="e.g., johnsmith99"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Location</label>
                  <input
                    type="text"
                    value={person.location}
                    onChange={updatePerson('location')}
                    placeholder="e.g., San Francisco"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Employer</label>
                  <input
                    type="text"
                    value={person.employer}
                    onChange={updatePerson('employer')}
                    placeholder="e.g., Acme Corp"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition"
                  />
                </div>
              </div>
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-cyan-500 hover:bg-cyan-600 disabled:opacity-50 text-white px-8 py-3 rounded-lg font-semibold transition"
                >
                  {loading ? 'Generating...' : 'Generate Queries'}
                </button>
              </div>
            </div>
          )}
        </form>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {/* Category filter */}
        {queries.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-6">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-3 py-1 rounded-full text-sm transition ${
                  activeCategory === cat
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                    : 'bg-slate-800 text-slate-400 border border-slate-700 hover:border-slate-600'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        )}

        {/* Results header */}
        {filtered.length > 0 && (
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-slate-400">
              Showing {filtered.length} {filtered.length === 1 ? 'query' : 'queries'}
              {activeCategory !== 'All' && ` in “${activeCategory}”`}
            </p>
            <button
              type="button"
              onClick={copyAllToClipboard}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm bg-slate-800 border border-slate-700 text-slate-300 hover:border-cyan-500/40 hover:text-cyan-400 transition"
            >
              {copiedAll ? (
                <>
                  <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Copied!
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copy All
                </>
              )}
            </button>
          </div>
        )}

        {/* Results */}
        {filtered.length > 0 ? (
          <div className="space-y-3">
            {filtered.map((q, idx) => (
              <div key={idx} className="bg-slate-800 border border-slate-700 rounded-lg p-5 hover:border-cyan-500/30 transition">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs px-2 py-0.5 rounded-full bg-slate-700 text-slate-300">
                        {q.category}
                      </span>
                    </div>
                    <code className="block bg-slate-900 rounded px-3 py-2 text-cyan-400 text-sm font-mono mb-2 break-all">
                      {q.query}
                    </code>
                    <p className="text-sm text-slate-300 font-medium">{q.description}</p>
                    <p className="text-xs text-slate-500 mt-1">{q.purpose}</p>
                  </div>
                  <button
                    onClick={() => copyToClipboard(q.query, idx)}
                    className="shrink-0 text-slate-400 hover:text-cyan-400 transition p-2"
                    title="Copy query"
                  >
                    {copiedIdx === idx ? (
                      <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : !loading && (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">🔎</div>
            <h2 className="text-xl font-semibold mb-2">
              {mode === 'domain' ? 'Enter a Domain' : 'Enter a Person Name'}
            </h2>
            <p className="text-slate-400">
              {mode === 'domain'
                ? 'Generate Google Dork queries for OSINT reconnaissance.'
                : 'Generate queries to find public social profiles and online footprint.'}
            </p>
          </div>
        )}

        {/* Disclaimer */}
        <div className="mt-8 bg-amber-500/10 border border-amber-500/30 rounded-lg p-4">
          <p className="text-sm text-amber-400">
            <strong>Disclaimer:</strong> These queries are generated for educational and defensive security purposes only. 
            Always use responsibly and in compliance with applicable laws and terms of service.
          </p>
        </div>
      </div>
    </div>
  )
}
