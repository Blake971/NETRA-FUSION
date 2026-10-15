import React, {useState} from 'react'

function ActionItem({card, saved, current, api, update}) {
  const [owner, setOwner] = useState(saved?.owner || card.owner), [status, setStatus] = useState(saved?.status || 'To do')
  const [notes, setNotes] = useState(saved?.notes || ''), [message, setMessage] = useState(''), [busy, setBusy] = useState(false)
  async function save(e) {
    e.preventDefault(); setBusy(true); setMessage('')
    try {const result = await api(`/cases/${current.id}/actions/${card.id}`, {method:'PATCH', headers:{'Content-Type':'application/json'}, body:JSON.stringify({owner,status,notes})}); update(result); setMessage('Saved to this checkup.')}
    catch(e) {setMessage(e.message)} finally {setBusy(false)}
  }
  return <form className="panel action-item" onSubmit={save}><div className="action-heading"><span className="plain-state gap">{card.advisory ? 'Review suggested' : 'Needs attention'}</span><h3>{card.title}</h3></div><p>{card.action}</p><div className="action-fields"><label>Person or team to ask<input aria-label={`Owner for ${card.id}`} maxLength="80" value={owner} onChange={e => {setOwner(e.target.value); setMessage('')}}/></label><label>Progress<select aria-label={`Progress for ${card.id}`} value={status} onChange={e => {setStatus(e.target.value); setMessage('')}}>{['To do','In progress','Ready to recheck'].map(s => <option key={s}>{s}</option>)}</select></label></div><label>Notes <span className="muted">(optional)</span><textarea aria-label={`Notes for ${card.id}`} placeholder="Add a reminder or a question for your administrator" maxLength="1000" rows="2" value={notes} onChange={e => {setNotes(e.target.value); setMessage('')}}/></label><div className="action-save"><button className="secondary" disabled={busy}>{busy ? 'Saving…' : 'Save action'}</button><span role="status">{message}</span></div></form>
}

export default function ActionPlan({current, api, update, recheck}) {
  const cards = current.audience?.cards.filter(c => c.state === 'GAP') || []
  const actions = current.actions || {}
  const ready = cards.filter(c => actions[c.id]?.status === 'Ready to recheck').length
  function exportPlan() {
    const content = [`NETRA action plan: ${current.domain}`, current.demo ? 'Fictional demonstration data' : 'Based on recorded public observations', 'Task progress is self-reported. It does not change the measured score.', '', ...cards.map(c => `${c.title}\nAsk: ${actions[c.id]?.owner || c.owner}\nProgress: ${actions[c.id]?.status || 'To do'}\nNext step: ${c.action}\nNotes: ${actions[c.id]?.notes || 'None'}\n`)].join('\n')
    const url = URL.createObjectURL(new Blob([content],{type:'text/plain;charset=utf-8'})); const a = document.createElement('a'); a.href=url; a.download='netra-action-plan.txt'; a.click(); URL.revokeObjectURL(url)
  }
  return <div className="audience"><section className="panel discovery-intro"><div className="eyebrow">SMALL STEPS. CLEAR OWNERSHIP.</div><h2>Know what to ask, and who to ask.</h2><p>Save a person or team for each improvement. These are your planning notes; changing a task’s progress does not change the measured result.</p><div className="plan-summary"><strong>{ready} of {cards.length}</strong><span>marked ready for another check</span></div><div className="hero-actions"><button className="primary" onClick={recheck}>{current.demo ? 'Check the improved example' : 'Check this website again'}</button><button className="secondary" onClick={exportPlan}>↓ Download action checklist</button></div></section>{cards.map(c => <ActionItem key={current.id+c.id} card={c} saved={actions[c.id]} current={current} api={api} update={update}/>)}{!cards.length && <div className="panel empty">No observed gaps to plan for. Review unanswered checks and continue normal website maintenance.</div>}</div>
}
