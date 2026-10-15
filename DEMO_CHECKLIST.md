# NETRA Fusion - Demo Checklist

## 🎯 DEMO PREPARATION

### Before the Presentation
- [ ] Start the backend server: `python run_netra.py`
- [ ] Open browser to: http://127.0.0.1:8001
- [ ] Test the "Try demo" button works
- [ ] Verify all 9 views load correctly
- [ ] Test dark/light mode toggle
- [ ] Check asset graph is interactive
- [ ] Verify remediation planner works
- [ ] Test export functionality

---

## 🎯 DEMO FLOW (5 minutes)

### 1. Landing Page (30 seconds)
- Show clean welcome screen
- Point out "Enter a domain" input
- Highlight "Try demo" button
- Mention: "User-friendly starting point"

### 2. Run Demo Assessment (1 minute)
- Click "Try demo" button
- Show progress bar filling
- Point out real-time updates
- Read progress messages (e.g., "Collecting DNS records")
- Say: "Users see exactly what's happening"

### 3. Overview Dashboard (45 seconds)
- Show security score (e.g., 67/100)
- Point out evidence coverage percentage
- Show configuration gaps count
- Highlight asset graph preview
- Mention: "At-a-glance security posture"

### 4. Navigate All Views (1 minute)
- Click through sidebar navigation
- Briefly mention each view:
  - "Evidence Room - detailed findings"
  - "Public Footprint - raw evidence"
  - "Asset Graph - infrastructure visualization"
  - "Remediation - fix planning"
  - "Compare Checkups - side-by-side comparison"
  - "Assessment History - saved scans"
  - "Portfolio - batch management"

### 5. Asset Graph Deep Dive (45 seconds)
- Click "Asset Graph" in sidebar
- Show the circular visualization
- Click on a node to show details
- Point out different node types (IP, certificate, mail server)
- Say: "Visual representation of domain relationships"

### 6. Evidence Room (45 seconds)
- Click "Evidence Room"
- Show search/filter toolbar
- Type in search box to filter
- Change severity filter (ALL → HIGH)
- Toggle explanation levels (Summary → Explanation → Technical)
- Say: "Three-level explanation for different audiences"

### 7. Remediation Planner (45 seconds)
- Click "Remediation"
- Show list of security issues
- Check 2-3 checkboxes
- Watch projected score update in real-time
- Say: "What-if score projection"
- Click "Export selected action plan"
- Show JSON download

### 8. Theme Toggle (15 seconds)
- Click moon icon in sidebar
- Show light mode
- Click again for dark mode
- Say: "Dark mode reduces eye strain, light mode for bright environments"

### 9. Export Evidence (15 seconds)
- Click "Export evidence" button
- Show JSON file download
- Say: "Exportable evidence bundle for sharing"

---

## 🎯 KEY TALKING POINTS DURING DEMO

### When Showing Landing Page
- "Clean, modern interface"
- "Users can enter any domain or try demo"
- "No login required for local workspace"

### When Running Assessment
- "Real-time progress updates every second"
- "Shows current step and percentage"
- "Transparent assessment process"

### When Showing Overview
- "Security score based on 12 deterministic checks"
- "Evidence coverage shows what was observed"
- "Configuration gaps backed by evidence"

### When Showing Asset Graph
- "Custom SVG visualization"
- "Interactive nodes you can click"
- "Shows DNS, IPs, certificates, mail servers"
- "Helps understand infrastructure"

### When Showing Evidence Room
- "Search and filter findings"
- "Three explanation levels"
- "Summary for non-technical, Technical for experts"

### When Showing Remediation
- "Select fixes to see score impact"
- "Projected score updates in real-time"
- "Export action plan as JSON"

### When Toggling Theme
- "Dark mode for eye strain"
- "Light mode for bright environments"
- "CSS custom properties for seamless switching"

### When Exporting
- "Export evidence as JSON"
- "Includes raw data and SHA-256 digest"
- "Shareable with team"

---

## 🎯 WHAT TO EMPHASIZE

### User Experience
- ✅ Intuitive navigation
- ✅ Real-time feedback
- ✅ Clear visual hierarchy
- ✅ Responsive design

### Technical Excellence
- ✅ Modern React hooks
- ✅ Efficient state management
- ✅ Clean API integration
- ✅ Optimized performance

### Design Quality
- ✅ Professional dark mode
- ✅ Consistent styling
- ✅ Accessible interface
- ✅ Print-friendly

### Innovation
- ✅ Interactive asset graph
- ✅ Three-level explanations
- ✅ Score projection
- ✅ Real-time updates

---

## 🎯 COMMON QUESTIONS TO PREPARE FOR

**Q: How long does an assessment take?**
A: Typically 10-30 seconds depending on domain.

**Q: Can I assess my own domain?**
A: Yes, enter any public domain.

**Q: What's the difference between demo and live?**
A: Demo uses synthetic data, live assesses real domains.

**Q: Is my data private?**
A: Yes, all data stored locally in SQLite.

**Q: Can I compare assessments?**
A: Yes, use "Compare Checkups" view.

**Q: Can I export results?**
A: Yes, export as JSON with full evidence.

**Q: Does it work on mobile?**
A: Yes, fully responsive design.

**Q: Can I customize the views?**
A: Navigation is fixed, but you can filter and search.

---

## 🎯 BACKUP PLAN

### If Demo Fails
1. **Have screenshots ready** - Show images of the app
2. **Describe features verbally** - Use the presentation guide
3. **Focus on code** - Show code snippets instead
4. **Discuss design decisions** - Talk about the process

### If Server Won't Start
1. **Check backend is running** - `python run_netra.py`
2. **Check port 8001 is available** - No other app using it
3. **Check dependencies installed** - `pip install -r requirements.txt`
4. **Check Python version** - Need Python 3.10+

### If Browser Won't Load
1. **Try different browser** - Chrome, Firefox, Edge
2. **Clear cache** - Ctrl+Shift+Delete
3. **Check URL** - http://127.0.0.1:8001
4. **Check console** - F12 for errors

---

## 🎯 QUICK REMINDERS

### Before Starting
- [ ] Server is running
- [ ] Browser is open
- [ ] Demo works
- [ ] All views load
- [ ] Theme toggle works

### During Demo
- [ ] Speak clearly and confidently
- [ ] Point to features with mouse
- [ ] Explain what you're doing
- [ ] Keep pace steady
- [ ] Don't rush

### After Demo
- [ ] Summarize key features
- [ ] Mention future enhancements
- [ ] Open for questions
- [ ] Thank the audience

---

## 🎯 SUCCESS METRICS

### You Know You're Ready When:
- ✅ You can explain the 9 views without notes
- ✅ You can run the demo without hesitation
- ✅ You can answer technical questions
- ✅ You can explain design decisions
- ✅ You feel confident

---

**You've got this! Good luck tomorrow! 🚀**
