import React from 'react'
export const labels = {'Hosting':'Hosting and ownership','Email exposure':'Email exposure','Workspace guide':'Workspace guide','Accuracy lab':'Accuracy lab','Research':'Google search assistant','Evidence review':'Evidence review','Website checkup':'Website checkup','Action plan':'My action plan','Public footprint':'Public information','Compare checkups':'Compare results','Assessment history':'Past checkups','Portfolio':'Multiple websites','Overview':'Technical overview','Evidence room':'Recorded evidence','Asset graph':'Connection map','Remediation':'Technical fixes'}
const simple=['Website checkup','Action plan','Public footprint','Hosting','Research','Email exposure','Compare checkups','Assessment history','Portfolio','Workspace guide','Accuracy lab']
const advanced=['Evidence review','Overview','Evidence room','Asset graph','Remediation']
export default function Navigation({view,setView,hasResult}) {
 const button=v=><button key={v} aria-label={labels[v]} aria-current={view===v?'page':undefined} className={view===v?'nav active':'nav'} onClick={()=>setView(v)} disabled={!hasResult&&!['Website checkup','Assessment history','Portfolio','Workspace guide','Accuracy lab','Research','Email exposure'].includes(v)}><span aria-hidden="true">◇</span>{labels[v]}</button>
 return <nav className="simple-navigation"><div className="everyday-nav">{simple.map(button)}</div><details className="advanced-nav" open={advanced.includes(view)||undefined}><summary>Advanced details</summary>{advanced.map(button)}</details></nav>
}
