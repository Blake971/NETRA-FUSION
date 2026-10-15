import React, {useEffect, useState} from 'react'

export default function Portfolio({api, open}) {
  const [text, setText] = useState(''), [rows, setRows] = useState([]), [message, setMessage] = useState(''), [busy, setBusy] = useState(false)
  useEffect(() => {
    let mounted = true
    const refresh = () => api('/cases').then(data => {if (mounted) setRows(data)}).catch(e => {if (mounted) setMessage(e.message)})
    refresh(); const timer = setInterval(refresh, 3000)
    return () => {mounted = false; clearInterval(timer)}
  }, [])
  async function queue() {
    const domains = [...new Set(text.split(/[\n,]+/).map(d => d.trim()).filter(d => d && d.toLowerCase() !== 'domain'))]
    if (!domains.length || domains.length > 10) {setMessage('Enter between 1 and 10 domains.'); return}
    setBusy(true); const errors = []; let count = 0
    for (const domain of domains) {
      try {await api('/cases', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({domain})}); count++}
      catch(e) {errors.push(domain + ': ' + e.message)}
    }
    setMessage(`${count} assessments queued. ${errors.join(' ')}`); setBusy(false)
  }
  const latest = [...new Map(rows.filter(r => !r.demo).slice().reverse().map(r => [r.domain, r])).values()].reverse()
  const complete = latest.filter(r => r.status === 'COMPLETED' && r.coverage === 100 && r.score != null)
  return <><section className="panel portfolio"><div><div className="eyebrow">MULTI-DOMAIN WORKSPACE</div><h2>One organization. A connected view.</h2><p>Queue up to 10 public domains. Three assessments run at a time; results are saved individually.</p><textarea aria-label="Portfolio domains" rows="5" placeholder={'example.com\nexample.org'} value={text} onChange={e => setText(e.target.value)}/><div className="portfolio-actions"><label className="secondary">Import domain list<input aria-label="Import domain list" type="file" accept=".txt,.csv" onChange={async e => {const f = e.target.files[0]; if (f) {if (f.size > 10000) {setMessage('Use a list smaller than 10 KB.'); return} setText(await f.text())}}}/></label><button className="primary" disabled={busy} onClick={queue}>{busy ? 'Queueing…' : 'Queue portfolio →'}</button></div><small>Import a plain text list or a single-column CSV with an optional “domain” header.</small>{message && <p role="status">{message}</p>}</div><div className="portfolio-stat"><strong>{latest.length}</strong><span>distinct live domains</span><strong>{complete.length ? Math.round(complete.reduce((s,r) => s + r.score, 0) / complete.length) : '—'}</strong><span>average of {complete.length} fully observed assessments</span><p>Local portfolio metric. Not an industry benchmark.</p></div></section><section className="panel"><div className="panel-head"><h2>Latest assessment per domain</h2><span>Updates every 3 seconds</span></div><div className="table-scroll"><table><thead><tr><th>Domain</th><th>Status</th><th>Score</th><th>Coverage</th></tr></thead><tbody>{latest.map(r => <tr key={r.id}><td><button className="text-button" onClick={() => open(r.id)}>{r.domain} ↗</button></td><td>{r.status}</td><td>{r.score ?? '—'}</td><td>{r.coverage == null ? '—' : r.coverage + '%'}</td></tr>)}</tbody></table></div>{!latest.length && <p className="empty">No live domains assessed yet.</p>}</section></>
}
