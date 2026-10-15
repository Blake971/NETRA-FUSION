import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import './fusion.css'
import './light-mode.css'
import './ai.css'
import './recon-animations.css'
import Portfolio from './Portfolio.jsx'
import './portfolio.css'
import Audience from './Audience.jsx'
import {Discovery, Compare} from './Discovery.jsx'

const views = ['Website checkup', 'Overview', 'Evidence room', 'Public footprint', 'Asset graph', 'Google Dorks', 'Remediation', 'Compare checkups', 'Assessment history', 'Portfolio']

const animations = {
  fadeIn: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 }
  },
  slideIn: {
    initial: { x: -20, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: 20, opacity: 0 }
  },
  scaleIn: {
    initial: { scale: 0.95, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 0.95, opacity: 0 }
  }
}
async function api(path, options) {
  const response = await fetch('/api' + path, options)
  const contentType = response.headers.get('content-type')
  let body
  try {
    if (contentType && contentType.includes('application/json')) {
      body = await response.json()
    } else {
      const text = await response.text()
      body = { detail: text }
    }
  } catch (e) {
    body = { detail: 'Unable to parse response' }
  }
  if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : 'Unable to process this request.')
  return body
}
function download(data, name) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }))
  const a = document.createElement('a'); a.href = url; a.download = name; a.click(); URL.revokeObjectURL(url)
}
function ReconNetwork() {
  const nodes = [[72, 44], [144, 93], [238, 39], [322, 93], [407, 48], [468, 102]]
  return <div className="recon-network" role="img" aria-label="NETRA reconnaissance network visual">
    <svg viewBox="0 0 540 140" aria-hidden="true">
      <path className="recon-link" d="M72 44L144 93L238 39L322 93L407 48L468 102" />
      <path className="recon-link recon-link-secondary" d="M72 44L238 39L407 48M144 93L322 93L468 102" />
      {nodes.map(([x, y], index) => <g className="recon-node" style={{ '--node-delay': `${index * 0.12}s` }} key={`${x}-${y}`}>
        <circle cx={x} cy={y} r="5" />
        <circle className="recon-node-ring" cx={x} cy={y} r="12" />
      </g>)}
      <circle className="recon-core" cx="270" cy="69" r="18" />
      <circle className="recon-core-dot" cx="270" cy="69" r="5" />
    </svg>
    <span className="recon-label">PUBLIC SIGNALS / CORRELATION READY</span>
  </div>
}
function Graph({ graph }) {
  const [selected, select] = useState(null)
  const nodes = graph.nodes.slice(1, 15)
  return <div className="graph-wrap"><svg viewBox="0 0 800 420" role="img" aria-label="Domain relationships from DNS and certificate transparency">
    <defs><radialGradient id="halo"><stop stopColor="#26ddba" stopOpacity=".14"/><stop offset="1" stopColor="#26ddba" stopOpacity="0"/></radialGradient></defs>
    <circle cx="400" cy="210" r="185" fill="url(#halo)"/>
    {[90, 160].map(r => <circle key={r} cx="400" cy="210" r={r} fill="none" stroke="#233239" strokeDasharray="4 8"/>)}
    {nodes.map((n, i) => { const angle = i * Math.PI * 2 / nodes.length; const x = 400 + Math.cos(angle) * 270; const y = 210 + Math.sin(angle) * 150; return <g key={n.id} tabIndex="0" role="button" aria-label={n.id} onClick={() => select(n)} onKeyDown={e => e.key === 'Enter' && select(n)}><line x1="400" y1="210" x2={x} y2={y} stroke="#31534f"/><circle cx={x} cy={y} r="17" fill="#142a29" stroke={n.kind === 'address' ? '#7a9eff' : '#39d8b5'}/><text x={x} y={y + 35} textAnchor="middle" fill="#aabbbd" fontSize="11">{n.id.length > 32 ? n.id.slice(0, 29) + '…' : n.id}</text><text x={x} y={y + 4} textAnchor="middle" fill="#52dcc0" fontSize="12">{n.kind === 'address' ? 'IP' : '◇'}</text></g> })}
    <circle cx="400" cy="210" r="38" fill="#163d34" stroke="#53ecc4"/><text x="400" y="216" textAnchor="middle" fill="#61efcb" fontSize="25">◎</text><text x="400" y="269" textAnchor="middle" fill="#edf6f4" fontSize="13">{graph.nodes[0].id}</text>
  </svg><p>{selected ? `${selected.id} · ${selected.kind} · ${selected.source}` : 'Select an asset to inspect its source. Certificate names are historical observations.'}</p>{graph.nodes.length > 15 && <p>Showing 15 of {graph.nodes.length} assets. The complete inventory is in the evidence export.</p>}</div>
}

function DorkLauncher({ mode, setMode, term, setTerm, username, setUsername, location, setLocation, employer, setEmployer, onGenerate, links }) {
  return <section className="panel dork-person-panel"><div className="panel-head"><h2>Person / organization search</h2><span>Manual public-web queries</span></div><p className="method">Generate public search links for authorized OSINT research. NETRA does not inspect private accounts or execute searches automatically.</p><div className="dork-search-mode"><label htmlFor="launcher-dork-mode"><strong>Search type:</strong></label><select id="launcher-dork-mode" value={mode} onChange={e => setMode(e.target.value)}><option value="person">Person / username</option><option value="organization">Organization</option></select><label htmlFor="launcher-dork-term"><strong>Name:</strong></label><input id="launcher-dork-term" value={term} onChange={e => setTerm(e.target.value)} placeholder={mode === 'person' ? 'Enter a name' : 'Enter an organization name'} />{mode === 'person' && <><label htmlFor="launcher-dork-username"><strong>Username (optional):</strong></label><input id="launcher-dork-username" value={username} onChange={e => setUsername(e.target.value)} placeholder="Enter a username/handle" /><label htmlFor="launcher-dork-location"><strong>Location (optional):</strong></label><input id="launcher-dork-location" value={location} onChange={e => setLocation(e.target.value)} placeholder="Enter a city or region" /><label htmlFor="launcher-dork-employer"><strong>Employer (optional):</strong></label><input id="launcher-dork-employer" value={employer} onChange={e => setEmployer(e.target.value)} placeholder="Enter a company or organization" /></>}<button className="secondary" type="button" onClick={() => onGenerate(mode, term, username, location, employer)}>Generate queries</button></div>{links.length > 0 && <div className="dork-generated-links">{links.map(link => <a key={link.url} className="secondary" href={link.url} target="_blank" rel="noreferrer"><strong>{link.title}</strong><span aria-hidden="true">↗</span><small>{link.query}</small></a>)}</div>}</section>
}
function GeneratedQueries({ links }) {
  return <section className="panel generated-query-panel"><div className="panel-head"><h2>Generated query links</h2><span>{links.length} queries ready</span></div><div className="dork-generated-links">{links.map(link => <a key={link.url} className="secondary" href={link.url} target="_blank" rel="noreferrer"><strong>{link.title}</strong><span aria-hidden="true">↗</span><small>{link.query}</small></a>)}</div></section>
}

export default function Fusion() {
  const [view, setView] = useState('Website checkup'), [domain, setDomain] = useState(''), [current, setCurrent] = useState(null)
  const [history, setHistory] = useState([]), [error, setError] = useState(''), [busy, setBusy] = useState(false), [clearingHistory, setClearingHistory] = useState(false)
  const [filter, setFilter] = useState('ALL'), [query, setQuery] = useState(''), [level, setLevel] = useState('Explanation')
  const [planned, setPlanned] = useState([]), [light, setLight] = useState(false)
  const [aiAvailable, setAiAvailable] = useState(false), [aiBusy, setAiBusy] = useState(false)
  const [searchMode, setSearchMode] = useState('domain'), [emailConsent, setEmailConsent] = useState(false), [emailBusy, setEmailBusy] = useState(false), [emailResult, setEmailResult] = useState(null), [breachStats, setBreachStats] = useState(null)
  const [dorkMode, setDorkMode] = useState('domain'), [dorkSearchTerm, setDorkSearchTerm] = useState(''), [dorkUsername, setDorkUsername] = useState(''), [dorkLocation, setDorkLocation] = useState(''), [dorkEmployer, setDorkEmployer] = useState(''), [dorkLinks, setDorkLinks] = useState([])
  const assessment = current?.assessment
  const running = current && ['QUEUED', 'RUNNING'].includes(current.status)
  const refresh = () => api('/cases').then(setHistory).catch(e => setError(e.message))
  useEffect(() => { refresh(); api('/health').then(h => setAiAvailable(h.ai_available)).catch(() => {}); api('/breach-stats').then(s => setBreachStats(s)).catch(() => {}) }, [])
  useEffect(() => {
    if (!running) return
    const timer = setInterval(() => api('/cases/' + current.id).then(c => { setCurrent(c); if (c.status === 'COMPLETED' || c.status === 'FAILED') refresh() }).catch(e => setError(e.message)), 1000)
    return () => clearInterval(timer)
  }, [current?.id, running])
  useEffect(() => { setPlanned([]); if(current?.id) {try {sessionStorage.setItem('netra-case', current.id)} catch {}} }, [current?.id])
  useEffect(() => {try {const saved = sessionStorage.getItem('netra-case'); if(saved) open(saved)} catch {}}, [])
  async function start(demo = false, demo_profile = 'baseline') {
    setBusy(true); setError(''); setView('Website checkup')
    try { setCurrent(await api('/cases', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ domain, demo, demo_profile }) })) }
    catch (e) { setError(e.message) } finally { setBusy(false) }
  }
  async function open(id) { try { setCurrent(await api('/cases/' + id)); setView('Website checkup'); setError('') } catch(e) { setError(e.message) } }
  async function clearHistory() {
    if (!window.confirm('Clear all saved assessment history? This cannot be undone.')) return
    setClearingHistory(true); setError('')
    try {
      await api('/cases', { method: 'DELETE' })
      setHistory([])
      setCurrent(null)
      try { sessionStorage.removeItem('netra-case') } catch {}
    } catch (e) {
      setError(e.message)
    } finally {
      setClearingHistory(false)
    }
  }
  async function explainWithAI() {
    const id = current.id
    setAiBusy(true); setError('')
    try { const updated = await api('/cases/' + id + '/explain', {method: 'POST'}); setCurrent(c => c?.id === id ? updated : c) }
    catch(e) { setError(e.message) } finally { setAiBusy(false) }
  }
  async function generatePersonDorks(mode, searchTerm, username = '', location = '', employer = '') {
    console.log('generatePersonDorks called with:', { mode, searchTerm, username, location, employer })
    const normalizedTerm = searchTerm.trim()
    if (!normalizedTerm) {
      setError('Please enter a search term')
      return
    }
    setBusy(true)
    setError('')
    try {
      if (mode === 'person') {
        const result = await api('/person-dork', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: normalizedTerm,
            username: username.trim(),
            location: location.trim(),
            employer: employer.trim()
          })
        })
        if (result.status === 'SUCCESS' && result.data?.queries) {
          const queries = result.data.queries.map(q => ({
            title: q.description,
            query: q.query,
            url: `https://www.google.com/search?q=${encodeURIComponent(q.query)}`,
            category: q.category,
            purpose: q.purpose
          }))
          setDorkLinks(queries)
        } else {
          setError('Failed to generate person dork queries')
        }
      } else if (mode === 'organization') {
        // For organization, generate client-side queries (same as before)
        const subject = `"${normalizedTerm}"`
        const queries = [
          { title: 'Public pages', query: subject },
          { title: 'Public documents', query: `${subject} (filetype:pdf OR filetype:doc OR filetype:docx)` },
          { title: 'Public social profiles', query: `${subject} (site:linkedin.com/company OR site:github.com OR site:instagram.com OR site:x.com OR site:facebook.com)` },
          { title: 'Slides and presentations', query: `${subject} (filetype:ppt OR filetype:pptx OR filetype:pdf) presentation` },
          { title: 'Public spreadsheets', query: `${subject} (filetype:xls OR filetype:xlsx OR filetype:csv)` },
          { title: 'Code references', query: `${subject} site:github.com` },
          { title: 'Contact and about pages', query: `${subject} (inurl:contact OR inurl:about)` },
          { title: 'Privacy and legal pages', query: `${subject} (privacy OR terms OR imprint OR "legal notice")` },
          { title: 'Security reporting', query: `${subject} ("security.txt" OR "responsible disclosure")` },
          { title: 'Sign-in pages', query: `${subject} (inurl:login OR inurl:signin)` },
          { title: 'Directory listings', query: `${subject} intitle:"index of"` },
        ]
        setDorkLinks(queries.map(({ title, query }) => ({ title, query, url: `https://www.google.com/search?q=${encodeURIComponent(query)}` })))
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }
  function submitSearch() {
    setDorkLinks([])
    if (searchMode === 'domain') {
      start(false)
      return
    }
    if (searchMode === 'email') {
      setEmailBusy(true); setError(''); setEmailResult(null)
      api('/breach-check', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query: domain, search_type: 'email_address', consent: emailConsent }) })
        .then(setEmailResult)
        .catch(e => setError(e.message))
        .finally(() => setEmailBusy(false))
      return
    }
    if (searchMode === 'person-breach') {
      setEmailBusy(true); setError(''); setEmailResult(null)
      api('/breach-check', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query: domain, search_type: 'username', consent: true }) })
        .then(setEmailResult)
        .catch(e => setError(e.message))
        .finally(() => setEmailBusy(false))
      return
    }
    if (searchMode === 'organization-breach') {
      setEmailBusy(true); setError(''); setEmailResult(null)
      api('/breach-check', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query: domain, search_type: 'domain', consent: true }) })
        .then(setEmailResult)
        .catch(e => setError(e.message))
        .finally(() => setEmailBusy(false))
      return
    }
    if (searchMode === 'person-dork') {
      setView('Google Dorks')
      setDorkMode('person')
      setDorkSearchTerm(domain)
      setDorkUsername('')
      setDorkLocation('')
      setDorkEmployer('')
      return
    }
    if (searchMode === 'organization-dork') {
      setView('Google Dorks')
      setDorkMode('organization')
      setDorkSearchTerm(domain)
      return
    }
  }
  const findings = assessment?.findings.filter(f => (filter === 'ALL' || f.severity === filter) && `${f.title} ${f.category} ${f.evidence}`.toLowerCase().includes(query.toLowerCase())) || []
  const prior = history.find(h => h.domain === current?.domain && h.demo === current?.demo && h.status === 'COMPLETED' && h.created_at < current.created_at)
  const projected = assessment?.score == null ? null : Math.min(100, assessment.score + assessment.findings.filter(f => planned.includes(f.id)).reduce((s, f) => s + f.points, 0))
  return <div className={'fusion ' + (light ? 'light' : '') + (view === 'Google Dorks' ? ' dork-view' : '')}>
    <aside className="sidebar"><motion.a className="brand" href="#" onClick={e => {e.preventDefault(); setView('Overview')}} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}><span className="brand-symbol">◉</span> NETRA<span className="version">FUSION</span></motion.a><div className="workspace-label">INTELLIGENCE WORKSPACE</div><nav>{views.map((v, i) => <motion.button key={v} aria-label={v} className={view === v ? 'nav active' : 'nav'} onClick={() => setView(v)} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}><span>{['♡', '◫', '⌕', '◎', '⬡', '☷', '⇄', '◷', '▦'][i]}</span>{v}{v === 'Evidence room' && assessment && <b>{assessment.findings.length}</b>}</motion.button>)}</nav><div className="sidebar-bottom"><div className="fusion-note"><span className="live-dot"/> NETRA FUSION<p>Discover. Challenge. Explain.</p></div><motion.button className="nav" onClick={() => setLight(!light)} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>◐ <span>{light ? 'Dark' : 'Light'} appearance</span></motion.button><div className="profile"><span>NA</span><div>Security analyst<small>Local investigation workspace</small></div></div></div></aside>
    <main><header className="topbar"><span>Workspace <span className="slash">/</span> <strong>{view}</strong></span><div><span className="local-badge"><span className="live-dot"/> LOCAL WORKSPACE</span><button className="icon-button" title="Print current report" onClick={() => window.print()}>↗</button></div></header>
    <AnimatePresence mode='wait'><motion.div key={view} className="content" initial={animations.fadeIn.initial} animate={animations.fadeIn.animate} exit={animations.fadeIn.exit} transition={{ duration: 0.3 }}><div className="heading"><motion.div initial={animations.slideIn.initial} animate={animations.slideIn.animate} transition={{ delay: 0.1 }}><div className="eyebrow">EXTERNAL EXPOSURE INTELLIGENCE</div><h1>{view === 'Website checkup' ? 'Understand your website. Know your next step.' : view === 'Overview' ? 'See the surface. Understand the risk.' : view}</h1><p>An outside checkup that turns public information into clear explanations and practical next steps.</p></motion.div><button className="secondary" disabled={!assessment} onClick={() => download(current, `netra-${current.domain}-${current.id.slice(0,8)}.json`)}>↓ Export evidence</button></div>
    <form className="scan-bar" onSubmit={e => {e.preventDefault(); submitSearch()}}><span className="search-icon">⌕</span><select className="search-mode-select" aria-label="Search type" value={searchMode} onChange={e => {setSearchMode(e.target.value); setEmailResult(null); setError('')}}><option value="domain">Domain assessment</option><option value="email">Email breach check</option><option value="person-breach">Username breach check</option><option value="organization-breach">Domain breach check</option><option value="person-dork">Person dork search</option><option value="organization-dork">Organization dork search</option></select><input type={searchMode === 'email' ? 'email' : 'text'} aria-label={searchMode === 'domain' ? 'Public domain to assess' : searchMode === 'email' ? 'Email address to check' : searchMode === 'person-breach' ? 'Username to check' : searchMode === 'person-dork' ? 'Person name to search' : searchMode === 'organization-dork' ? 'Organization name to search' : 'Domain to check'} placeholder={searchMode === 'domain' ? 'Enter a public domain, e.g. example.com' : searchMode === 'email' ? 'Enter an email address' : searchMode === 'person-breach' ? 'Enter a username' : searchMode === 'person-dork' ? 'Enter a person name' : searchMode === 'organization-dork' ? 'Enter an organization name' : 'Enter a domain'} value={domain} onChange={e => setDomain(e.target.value)} required maxLength="300"/><span className="scan-type">{searchMode === 'domain' ? 'DOMAIN ASSESSMENT' : (searchMode === 'person-dork' || searchMode === 'organization-dork') ? 'GOOGLE DORK SEARCH' : 'BREACH EXPOSURE CHECK'}</span><button className="primary" disabled={busy || running || emailBusy}>↗ {busy || running || emailBusy ? 'Checking…' : searchMode === 'domain' ? 'Run assessment' : (searchMode === 'person-dork' || searchMode === 'organization-dork') ? 'Generate dorks' : 'Check breaches'}</button><button className="secondary" type="button" disabled={busy || running || emailBusy} onClick={() => start(true)}>▶ Try demo</button></form>
    {searchMode === 'email' && <label className="email-consent"><input type="checkbox" checked={emailConsent} onChange={e => setEmailConsent(e.target.checked)} /> I own this email address or have permission to check it with Leak-Lookup.</label>}
    {(searchMode === 'person-dork' || searchMode === 'organization-dork') && <p className="method">Generates Google search queries only - no data collection or API calls. Execute queries manually in a search engine.</p>}
    {view === 'Google Dorks' && dorkLinks.length > 0 && <GeneratedQueries links={dorkLinks}/>}
    {emailResult && <section className="panel email-result"><div className="panel-head"><h2>{emailResult.state === 'MATCHES' ? `${emailResult.breaches.length} known incident${emailResult.breaches.length === 1 ? '' : 's'} reported` : 'No known match returned'}</h2><span>Leak-Lookup · not stored</span></div><p>{emailResult.detail}</p>{emailResult.breaches?.map(breach => <article className="email-breach" key={breach.name}><strong>{breach.title}</strong><span>{breach.date} · {breach.domain || 'Reported incident'}</span><small>{breach.data_classes.join(', ')}</small></article>)}</section>}
    {breachStats && (searchMode === 'email' || searchMode === 'person-breach' || searchMode === 'organization-breach') && <div className="breach-stats"><small>Leak-Lookup API: {breachStats.requests}/{breachStats.limit} requests used today</small></div>}
    {view === 'Assessment history' && <div className="history-actions"><button className="secondary danger-action" type="button" disabled={clearingHistory || history.length === 0} onClick={clearHistory}>{clearingHistory ? 'Clearing history…' : 'Clear history'}</button></div>}
    {error && <div role="alert" className="error">{error}</div>}
    {running && <div className="panel progress" role="status"><strong>Collecting evidence for {current.domain}</strong><span>{current.progress}%</span><progress max="100" value={current.progress}/><p>{current.events.at(-1)?.message}</p></div>}
    {current?.status === 'FAILED' && <div className="error" role="alert">Assessment failed: {current.error}</div>}
    {view === 'Google Dorks' && <DorkLauncher mode={dorkMode === 'domain' ? 'person' : dorkMode} setMode={setDorkMode} term={dorkSearchTerm} setTerm={setDorkSearchTerm} username={dorkUsername} setUsername={setDorkUsername} location={dorkLocation} setLocation={setDorkLocation} employer={dorkEmployer} setEmployer={setDorkEmployer} onGenerate={generatePersonDorks} links={dorkLinks}/>}
    {view === 'Portfolio' ? <Portfolio api={api} open={open}/> : view === 'Assessment history' ? <section className="panel"><div className="panel-head"><h2>Saved assessments</h2><span>{history.length} records</span></div>{!history.length && <div className="empty">Your assessments will appear here. Start with the offline demo.</div>}<div className="table-scroll"><table><thead><tr><th>Domain</th><th>Collected</th><th>Mode</th><th>Status</th><th>Score</th><th>Coverage</th></tr></thead><tbody>{history.map(h => <tr key={h.id} onClick={() => open(h.id)}><td><button className="text-button" onClick={e => {e.stopPropagation(); open(h.id)}}>{h.domain} ↗</button></td><td>{new Date(h.created_at).toLocaleString()}</td><td>{h.demo ? 'Synthetic demo' : 'Live'}</td><td>{h.status}</td><td>{h.score ?? '—'}</td><td>{h.coverage == null ? '—' : h.coverage + '%'}</td></tr>)}</tbody></table></div></section> : !assessment ? <section className="welcome panel"><ReconNetwork/><div className="eyebrow">ONE WORKSPACE. EVERY SIGNAL IN CONTEXT.</div><h2>A website checkup, without the jargon.</h2><p>Enter a website address to understand its public-facing protections.<br/>Or try a fictional example and learn how to explain the results to anyone.</p><button className="primary" disabled={busy || running} onClick={() => start(true)}>Explore the competition demo →</button><div className="welcome-features"><span>◇ Evidence provenance</span><span>◎ Transparent scoring</span><span>☷ Actionable remediation</span></div></section> : <>
      <div className="case-line"><strong><span className="live-dot"/>{current.domain}</strong><span className={current.demo ? 'demo-badge' : 'local-badge'}>{current.demo ? 'SYNTHETIC DEMO · NO LIVE CLAIMS' : 'LIVE OBSERVATIONS'}</span><span>{new Date(current.completed_at).toLocaleString()}</span><span className="case-id">CASE {current.id.slice(0,8).toUpperCase()}</span></div>
      {view === 'Website checkup' && <Audience key={current.id} current={current} navigate={setView} startImproved={() => start(true, 'improved')}/>}
      {view === 'Public footprint' && <Discovery current={current}/>}
      {view === 'Compare checkups' && <Compare current={current} history={history} api={api}/>}
      {view === 'Overview' && <><div className="metrics"><div className="metric score-metric"><div><label>Security posture</label><strong>{assessment.score ?? '—'}<small>/100</small></strong><p>{assessment.coverage < 100 ? 'Provisional · incomplete coverage' : 'Observed configuration score'}</p></div><svg viewBox="0 0 70 70"><circle cx="35" cy="35" r="28" fill="none" stroke="#263a3d" strokeWidth="5"/><circle cx="35" cy="35" r="28" fill="none" stroke="#51e2b7" strokeWidth="5" strokeDasharray={`${(assessment.score || 0) * 1.76} 176`} transform="rotate(-90 35 35)"/><text x="35" y="41" textAnchor="middle" fill="#51e2b7" fontSize="18">◎</text></svg></div><div className="metric"><label>Evidence coverage <span>◉</span></label><strong>{assessment.coverage}<small>%</small></strong><p>{assessment.checks.filter(c => c.state !== 'UNKNOWN').length} of {assessment.checks.length} checks observed</p></div><div className="metric"><label>Configuration gaps <span>⚑</span></label><strong>{assessment.findings.length}<small className="amber">{assessment.findings.filter(f => f.severity === 'HIGH').length} high priority</small></strong><p>Each deduction backed by evidence</p></div><div className="metric"><label>Discovered assets <span>⬡</span></label><strong>{assessment.graph.nodes.length}</strong><p>DNS + historical certificate names</p></div></div>
      <div className="dashboard-grid"><section className="panel"><div className="panel-head"><h2>Exposure map</h2><button className="text-button" onClick={() => setView('Asset graph')}>Explore graph ↗</button></div><Graph graph={assessment.graph}/></section><section className="panel briefing"><div className="panel-head"><h2><span className="mint">✧</span> Analyst briefing</h2><span className="tiny-badge">RULE-BASED</span></div><p>{assessment.briefing.summary}</p><div className="divider"/><div className="eyebrow">RECOMMENDED NEXT MOVES</div>{assessment.findings.slice(0,3).map((f,i) => <button className="priority-item" key={f.id} onClick={() => setView('Remediation')}><span>0{i+1}</span><div><strong>{f.title}</strong><small>{f.category} · {f.points}-point deduction</small></div><span>↗</span></button>)}{!assessment.findings.length && <p>No observed gaps. Review coverage before drawing conclusions.</p>}<div className="briefing-footer">Synthesis from collected evidence. No model inference or exploit verification.</div></section></div>
      <div className="dashboard-grid bottom-grid"><section className="panel"><div className="panel-head"><h2>Risk by category</h2><span>Observed deductions</span></div><div className="categories">{assessment.categories.map(c => <div key={c.name}><div><strong>{c.name}</strong><span>{c.observed}/{c.total} checks · −{c.deductions} pts</span></div><div className="bar"><i style={{width: (c.deductions / 30 * 100) + '%'}}/></div></div>)}</div><p className="method">{assessment.methodology}</p></section><section className="panel"><div className="panel-head"><h2>Evidence review trail</h2><span className="mint">DETERMINISTIC CHALLENGE</span></div><div className="trail">{current.events.map((e,i) => <div key={i}><span>✓</span><div><strong>{e.stage}</strong><p>{e.message}</p></div></div>)}</div>{prior && <p className="method">Previous comparable score: {prior.score ?? 'unknown'} · change {assessment.score != null && prior.score != null ? assessment.score - prior.score : 'unavailable'} points. Check coverage before comparing.</p>}</section></div></>}
        {view === 'Asset graph' && <div className="asset-graph-view"><section className="panel"><div className="panel-head"><h2>Connected infrastructure</h2><span>{assessment.graph.nodes.length} observed assets</span></div><Graph graph={assessment.graph}/><div className="asset-list">{assessment.graph.nodes.map(n => <div key={n.id}><strong>{n.id}</strong><span>{n.kind}</span><small>{n.source}</small></div>)}</div><div className="panel-head"><h2>Technology signals</h2></div><div className="asset-list">{assessment.technologies.map((t,i) => <div key={i}><strong>{t.name}</strong><span>{t.evidence}</span><small>{t.confidence}</small></div>)}{!assessment.technologies.length && <p>No technology signals observed.</p>}</div></section>{current.results?.dns?.status === 'SUCCESS' && (() => {const dnsData = current.results.dns.data || {};const txtRecords = dnsData.TXT || [];const dmarcRecords = dnsData.DMARC || [];const spfRecord = txtRecords.find(r => r.toLowerCase().startsWith('v=spf1'));const dmarcRecord = dmarcRecords.find(r => r.toLowerCase().startsWith('v=dmarc1'));const dmarcPolicy = dmarcRecord ? (dmarcRecord.match(/p\s*=\s*(\w+)/i) || [])[1] : null;return <section className="panel"><div className="panel-head"><h2>Email Security & Spoofing Protection</h2><span>SPF · DMARC · DKIM</span></div><div className="eyebrow">EMAIL AUTHENTICATION CHECKS</div><p>Records that help prevent email spoofing and improve deliverability.</p><div className="email-security-grid"><div className="email-security-card"><div className="email-header"><strong>SPF (Sender Policy Framework)</strong><span className={spfRecord ? 'status-badge success' : 'status-badge failure'}>{spfRecord ? '✓ Configured' : '✗ Missing'}</span></div><p className="email-desc">Declares which mail servers are authorized to send email for this domain.</p>{spfRecord ? <div className="email-detail"><small>Record:</small><code>{spfRecord}</code></div> : <p className="email-warning">No SPF record found. Email spoofing is possible.</p>}</div><div className="email-security-card"><div className="email-header"><strong>DMARC (Domain-based Message Authentication)</strong><span className={dmarcRecord ? 'status-badge ' + (dmarcPolicy === 'reject' || dmarcPolicy === 'quarantine' ? 'success' : 'warning') : 'status-badge failure'}>{dmarcRecord ? `✓ ${dmarcPolicy || 'Configured'}` : '✗ Missing'}</span></div><p className="email-desc">Enforces SPF and DKIM policies with specific handling rules.</p>{dmarcRecord ? <><div className="email-detail"><small>Policy:</small><code>{dmarcRecord}</code></div><p className="email-status">{dmarcPolicy === 'reject' ? 'Strong: Rejects unauthenticated emails' : dmarcPolicy === 'quarantine' ? 'Medium: Quarantines suspicious emails' : 'Weak: Monitoring only'}</p></> : <p className="email-warning">No DMARC record found. Email spoofing protection is minimal.</p>}</div><div className="email-security-card"><div className="email-header"><strong>DKIM (DomainKeys Identified Mail)</strong><span className="status-badge unknown">? Not detected</span></div><p className="email-desc">Cryptographic signature that verifies email message integrity.</p><p className="email-info">DKIM selectors are domain-specific and require separate validation. This check shows only if configured records are present in DNS.</p></div></div></section>})()}{current.results?.geolocation?.status === 'SUCCESS' && <section className="panel"><div className="panel-head"><h2>IP Geolocation & Provider Intelligence</h2><span>{current.results.geolocation.data.successful_lookups}/{current.results.geolocation.data.total_ips} IPs located</span></div><div className="eyebrow">NETWORK INFRASTRUCTURE ANALYSIS</div><p>Geolocation and provider information for resolved IP addresses.</p><div className="geo-grid">{Object.entries(current.results.geolocation.data.ip_data).map(([ip, data]) => <div key={ip} className="geo-card"><div className="geo-header"><strong>{ip}</strong><span className="source-badge">{data.source}</span></div>{data.error ? <p className="error">{data.error}</p> : <><div className="geo-location"><span>📍</span><strong>{data.city}, {data.region}, {data.country_code}</strong></div><div className="geo-details"><div><label>ISP:</label><span>{data.isp || 'N/A'}</span></div><div><label>Organization:</label><span>{data.organization || 'N/A'}</span></div><div><label>ASN:</label><span>{data.asn || 'N/A'}</span></div><div><label>Timezone:</label><span>{data.timezone || 'N/A'}</span></div>{data.latitude && data.longitude && <div><label>Coordinates:</label><span>{data.latitude.toFixed(4)}, {data.longitude.toFixed(4)}</span></div>}</div></>}</div>)} </div><p className="method">Geolocation data provided by ipinfo.io and freeipapi.com. Accuracy may vary based on IP type (CDN, hosting, residential).</p></section>}</div>}
      {view === 'Google Dorks' && <motion.section className="panel" initial={animations.fadeIn.initial} animate={animations.fadeIn.animate} exit={animations.fadeIn.exit}><div className="panel-head"><h2>Google Dork Queries</h2><span>OSINT reconnaissance</span></div>{current.results?.google_dork?.status === 'SUCCESS' ? <><div className="eyebrow">DEFENSIVE SECURITY INTELLIGENCE</div><p>These Google Dork queries can help discover publicly indexed information about the domain. Use responsibly for authorized security research only.</p><div className="dork-disclaimer"><span>⚠️</span> These queries are for educational and defensive security purposes only. Execute them manually in a search engine.</div><div className="dork-search-mode"><label><strong>Search Mode:</strong></label><select value={dorkMode} onChange={e => setDorkMode(e.target.value)}><option value="domain">Domain Assessment</option><option value="person">Person Search (OSINT)</option><option value="organization">Organization Search</option></select>{dorkMode !== 'domain' && <><input type="text" placeholder={dorkMode === 'person' ? 'Enter person name' : 'Enter organization name'} value={dorkSearchTerm} onChange={e => setDorkSearchTerm(e.target.value)} /><button className="secondary" onClick={() => generatePersonDorks(dorkMode, dorkSearchTerm)}>Generate Queries</button></>}</div><div className="dork-categories">{Object.entries(current.results.google_dork.data.queries.reduce((acc, q) => { if (!acc[q.category]) acc[q.category] = []; acc[q.category].push(q); return acc; }, {})).map(([category, queries]) => <motion.div key={category} className="dork-category" initial={animations.scaleIn.initial} animate={animations.scaleIn.animate} transition={{ delay: 0.1 }}><h3>{category}</h3>{queries.map((q, i) => <motion.div key={i} className="dork-item" initial={animations.fadeIn.initial} animate={animations.fadeIn.animate} transition={{ delay: i * 0.05 }}><code>{q.query}</code><p>{q.description}</p><small>{q.purpose}</small><button className="text-button" onClick={() => window.open('https://www.google.com/search?q=' + encodeURIComponent(q.query), '_blank')}>Run in Google ↗</button></motion.div>)}</motion.div>)}</div></> : <div className="empty">Google Dork queries not available. This may indicate the scanner module is not installed or collection failed.</div>}</motion.section>}
      {view === 'Evidence room' && <><div className="toolbar"><input aria-label="Search findings" placeholder="Search findings or evidence…" value={query} onChange={e => setQuery(e.target.value)}/><select aria-label="Severity" value={filter} onChange={e => setFilter(e.target.value)}>{['ALL','HIGH','MEDIUM','LOW'].map(x => <option key={x}>{x}</option>)}</select><div className="segments">{['Summary','Explanation','Technical'].map(l => <button className={level === l ? 'selected' : ''} key={l} onClick={() => setLevel(l)}>{l}</button>)}</div></div>{findings.map(f => <article className="panel finding" key={f.id}><div><span className={'severity ' + f.severity.toLowerCase()}>{f.severity}</span><span className="muted">{f.category} · −{f.points} points</span></div><h2>{f.title}</h2><p>{level === 'Summary' ? f.remediation : f.explanation}</p>{level !== 'Summary' && <blockquote>{f.evidence}</blockquote>}{level === 'Technical' && <><pre>{JSON.stringify(f, null, 2)}</pre><small>{f.review}</small></>}</article>)}{!findings.length && <div className="panel empty">No findings match these filters.</div>}<section className="panel"><div className="panel-head"><h2>Skeptic review</h2><span>{assessment.challenged.length} observations</span></div><div className="asset-list">{assessment.challenged.map((c,i) => <div key={i}><strong>{c.title}</strong><p>{c.reason}</p></div>)}{!assessment.challenged.length && <p>No conflicting or unavailable evidence flagged by these rules.</p>}</div></section><details className="panel raw"><summary>Raw collector evidence & SHA-256 digest</summary><p className="digest">{current.evidence_sha256}</p><pre>{JSON.stringify(current.results, null, 2)}</pre></details></>}
      {view === 'Remediation' && <><section className="panel simulator"><div><div className="eyebrow">REMEDIATION PLANNER</div><h2>Turn findings into a focused action plan.</h2><p>Select fixes to model their score impact. Verify changes with a new assessment.</p></div><div><span>Projected score</span><strong>{projected ?? '—'}<small>/100</small></strong><span>What-if estimate · not a new measurement</span></div></section>{assessment.findings.map(f => <article className="panel finding" key={f.id}><label className="fix-title"><input type="checkbox" checked={planned.includes(f.id)} onChange={e => setPlanned(e.target.checked ? [...planned, f.id] : planned.filter(x => x !== f.id))}/><h2>{f.title}</h2><span className="mint">+{f.points} pts</span></label><p>{f.remediation}</p>{f.snippet && <><small>NGINX · review and stage before applying</small><pre>{f.snippet}</pre></>}<small>Evidence: {f.evidence}</small></article>)}<button className="secondary" onClick={() => download({domain: current.domain, assessment_id: current.id, projected_score: projected, fixes: assessment.findings.filter(f => planned.includes(f.id))}, 'netra-remediation-plan.json')}>↓ Export selected action plan</button></>}
      {view === 'Overview' && <section className="panel ai-panel"><div><h2>✧ Optional AI explanation</h2><p>{aiAvailable ? 'Generate a narrative by sending this domain and normalized findings to Gemini.' : 'Configure GEMINI_API_KEY and GEMINI_MODEL on the server to enable Gemini. The evidence briefing works offline.'}</p></div><button className="secondary" disabled={!aiAvailable || aiBusy || Boolean(current.ai_explanation)} onClick={explainWithAI}>{aiBusy ? 'Generating…' : current.ai_explanation ? 'Explanation saved' : 'Explain with Gemini'}</button>{current.ai_explanation && <div className="ai-output"><small>{current.ai_explanation.mode} · {current.ai_explanation.model}</small><p>{current.ai_explanation.text}</p></div>}</section>}
      {view === 'Google Dorks' && dorkLinks.length > 0 && (() => {
        // Check if links have categories (from backend person dork)
        const hasCategories = dorkLinks.some(link => link.category)
        if (hasCategories) {
          // Group by category
          const grouped = dorkLinks.reduce((acc, link) => {
            if (!acc[link.category]) acc[link.category] = []
            acc[link.category].push(link)
            return acc
          }, {})
          return <motion.section className="panel" initial={animations.fadeIn.initial} animate={animations.fadeIn.animate} exit={animations.fadeIn.exit}>
            <div className="panel-head"><h2>Generated Person Dork Queries</h2><span>{dorkLinks.length} queries ready</span></div>
            <div className="dork-disclaimer"><span>⚠️</span> These queries are for educational and defensive security purposes only. Execute them manually in a search engine.</div>
            <div className="dork-categories">
              {Object.entries(grouped).map(([category, queries]) => (
                <motion.div key={category} className="dork-category" initial={animations.scaleIn.initial} animate={animations.scaleIn.animate} transition={{ delay: 0.1 }}>
                  <h3>{category}</h3>
                  {queries.map((q, i) => (
                    <motion.div key={i} className="dork-item" initial={animations.fadeIn.initial} animate={animations.fadeIn.animate} transition={{ delay: i * 0.05 }}>
                      <code>{q.query}</code>
                      <p>{q.title}</p>
                      <small>{q.purpose}</small>
                      <a className="secondary" href={q.url} target="_blank" rel="noreferrer">Run in Google ↗</a>
                    </motion.div>
                  ))}
                </motion.div>
              ))}
            </div>
          </motion.section>
        } else {
          // Simple list (organization mode)
          return <section className="panel dork-person-panel"><div className="panel-head"><h2>Generated query links</h2><span>{dorkLinks.length} queries ready</span></div><div className="dork-generated-links">{dorkLinks.map(link => <a key={link.url} className="secondary" href={link.url} target="_blank" rel="noreferrer"><strong>{link.title}</strong><span aria-hidden="true">↗</span><small>{link.query}</small></a>)}</div></section>
        }
      })()}
      <footer><span>NETRA FUSION <b> / </b> Evidence before conclusions.</span><span>Public signals only · No exploit verification · No compliance certification</span></footer>
    </>}</motion.div></AnimatePresence></main>
  </div>
}
