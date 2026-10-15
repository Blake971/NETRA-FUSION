# NETRA Fusion - Code Snippets for Presentation

## KEY CODE EXAMPLES TO SHOW

### 1. Main Component Structure (Fusion.jsx)
```jsx
export default function Fusion() {
  const [view, setView] = useState('Website checkup')
  const [domain, setDomain] = useState('')
  const [current, setCurrent] = useState(null)
  const [history, setHistory] = useState([])
  const [light, setLight] = useState(false)
  
  // State management for UI
  const assessment = current?.assessment
  const running = current && ['QUEUED', 'RUNNING'].includes(current.status)
  
  return (
    <div className={'fusion ' + (light ? 'light' : '')}>
      <aside className="sidebar">...</aside>
      <main>...</main>
    </div>
  )
}
```

**Talking Point:** "This is our main component using React hooks for state management."

---

### 2. Dark/Light Mode Toggle
```jsx
<button className="nav" onClick={() => setLight(!light)}>
  ◐ <span>{light ? 'Dark' : 'Light'} appearance</span>
</button>
```

**CSS Variables:**
```css
.fusion {
  --bg: #0c1117;
  --panel: #121a22;
  --border: #25303a;
  --text: #e5eeef;
  --mint: #53dfb7;
}

.fusion.light {
  --bg: #f8fafc;
  --panel: #ffffff;
  --border: #e2e8f0;
  --text: #1e293b;
  --mint: #0d9488;
}
```

**Talking Point:** "We use CSS custom properties for seamless theme switching."

---

### 3. API Integration
```jsx
async function api(path, options) {
  const response = await fetch('/api' + path, options)
  const body = await response.json()
  if (!response.ok) throw new Error(body.detail)
  return body
}

// Usage
async function start(demo = false) {
  setCurrent(await api('/cases', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ domain, demo })
  }))
}
```

**Talking Point:** "Clean API wrapper with error handling."

---

### 4. Real-Time Progress Updates
```jsx
useEffect(() => {
  if (!running) return
  const timer = setInterval(() => {
    api('/cases/' + current.id)
      .then(c => {
        setCurrent(c)
        if (c.status === 'COMPLETED') refresh()
      })
  }, 1000)
  return () => clearInterval(timer)
}, [current?.id, running])
```

**Talking Point:** "Polling every second to show real-time progress."

---

### 5. Interactive Asset Graph (SVG)
```jsx
function Graph({ graph }) {
  const [selected, select] = useState(null)
  const nodes = graph.nodes.slice(1, 15)
  
  return (
    <svg viewBox="0 0 800 420">
      {nodes.map((n, i) => {
        const angle = i * Math.PI * 2 / nodes.length
        const x = 400 + Math.cos(angle) * 270
        const y = 210 + Math.sin(angle) * 150
        return (
          <g key={n.id} onClick={() => select(n)}>
            <line x1="400" y1="210" x2={x} y2={y} />
            <circle cx={x} cy={y} r="17" />
            <text>{n.id}</text>
          </g>
        )
      })}
    </svg>
  )
}
```

**Talking Point:** "Custom SVG visualization for asset relationships."

---

### 6. Remediation Planner with Score Projection
```jsx
const projected = assessment?.score == null ? null 
  : Math.min(100, assessment.score + 
      assessment.findings
        .filter(f => planned.includes(f.id))
        .reduce((s, f) => s + f.points, 0))

return (
  <article className="panel finding">
    <label>
      <input 
        type="checkbox" 
        checked={planned.includes(f.id)}
        onChange={e => {
          setPlanned(e.target.checked 
            ? [...planned, f.id] 
            : planned.filter(x => x !== f.id))
        }}
      />
      <h2>{f.title}</h2>
      <span>+{f.points} pts</span>
    </label>
  </article>
)
```

**Talking Point:** "Dynamic score calculation as users select fixes."

---

### 7. Three-Level Explanation System
```jsx
const [level, setLevel] = useState('Explanation')

<div className="segments">
  {['Summary', 'Explanation', 'Technical'].map(l => (
    <button 
      className={level === l ? 'selected' : ''}
      onClick={() => setLevel(l)}
    >
      {l}
    </button>
  ))}
</div>

<p>
  {level === 'Summary' ? f.remediation 
   : level === 'Explanation' ? f.explanation 
   : JSON.stringify(f, null, 2)}
</p>
```

**Talking Point:** "Toggle between complexity levels for different audiences."

---

### 8. Responsive Design (CSS)
```css
/* Desktop */
.sidebar { width: 235px; }

/* Tablet */
@media(max-width: 1150px) {
  .sidebar { width: 200px; }
  .metrics { grid-template-columns: repeat(2, 1fr); }
}

/* Mobile */
@media(max-width: 750px) {
  .sidebar { 
    position: static; 
    width: 100%; 
  }
  .nav { 
    display: flex; 
    overflow: auto; 
  }
}
```

**Talking Point:** "Mobile-first responsive design with three breakpoints."

---

### 9. Package.json Dependencies
```json
{
  "dependencies": {
    "axios": "^1.6.2",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^7.18.4",
    "recharts": "^2.10.3"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^6.1.1",
    "tailwindcss": "^3.3.6",
    "vite": "^8.3.0",
    "@playwright/test": "^1.63.0"
  }
}
```

**Talking Point:** "Modern React ecosystem with Vite and Tailwind."

---

### 10. Print Styles
```css
@media print {
  .sidebar, .topbar, .scan-bar {
    display: none !important;
  }
  .fusion, .panel, .metric {
    background: white !important;
    color: black !important;
  }
  .panel {
    break-inside: avoid;
  }
}
```

**Talking Point:** "Print-friendly styles for report exports."

---

## 🎯 VISUAL ELEMENTS TO SHOW

### Before/During/After
1. **Landing Page** - Clean welcome screen
2. **Progress Bar** - Real-time updates
3. **Completed Assessment** - Full results
4. **Asset Graph** - Interactive visualization
5. **Remediation Planner** - Score projection
6. **Dark vs Light Mode** - Theme comparison

### Key Screenshots to Prepare
- Landing page with "Try demo" button
- Progress bar during assessment
- Overview dashboard with metrics
- Asset graph with selected node
- Evidence room with filters
- Remediation planner with selected fixes
- Dark mode vs light mode comparison

---

## 🎯 DEMO SCRIPT

**Step 1: Introduction**
"Let me show you the application..."

**Step 2: Landing Page**
"This is the landing page. Users can enter a domain or try the demo."

**Step 3: Run Assessment**
"I'll click 'Try demo' to show the progress..."

**Step 4: Progress Updates**
"Notice the progress bar updating in real-time as it collects evidence."

**Step 5: Navigate Views**
"Now I'll navigate through the 9 views..."

**Step 6: Overview**
"The Overview shows the security score, coverage, and key metrics."

**Step 7: Asset Graph**
"The Asset Graph visualizes domain relationships. Click any node to see details."

**Step 8: Evidence Room**
"The Evidence Room shows all findings with search and filters."

**Step 9: Remediation**
"In Remediation, I can select fixes and see the projected score change."

**Step 10: Theme Toggle**
"I can toggle between dark and light mode..."

**Step 11: Export**
"Finally, I can export the evidence as JSON."

---

## 🎯 TECHNICAL QUESTIONS & ANSWERS

**Q: Why React?**
A: Industry standard, great ecosystem, component-based architecture, excellent state management with hooks.

**Q: Why Vite over Create React App?**
A: Much faster development experience, instant hot module replacement, optimized production builds, modern tooling.

**Q: Why Tailwind CSS?**
A: Rapid development, consistent design system, small bundle size, easy customization.

**Q: How do you handle state?**
A: React hooks (useState, useEffect) for component state, session storage for persistence.

**Q: How does the app communicate with backend?**
A: RESTful API with Axios wrapper, error handling, loading states.

**Q: How do you ensure accessibility?**
A: ARIA labels, keyboard navigation, semantic HTML, focus management, print styles.

**Q: How do you handle performance?**
A: Efficient re-renders, debounced search, optimized graph rendering, Vite's HMR.

**Q: What was the biggest challenge?**
A: Complex data visualization - solved with custom SVG graph with interactive nodes.

---

**You're ready! Good luck tomorrow! 🚀**
