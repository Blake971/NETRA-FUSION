# NETRA
# Development Guide

Version: 2.0

---

# 1. Development Philosophy

Build vertically, not horizontally.

Complete one feature end-to-end before starting the next.

This ensures:
- Working code at every step
- Easier debugging
- Faster feedback
- Better understanding of dependencies

---

# 2. Development Environment Setup

## 2.1 Prerequisites

- Python 3.12+
- Node.js 18+
- Git
- Code editor (VS Code recommended)

## 2.2 Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy python-whois dnspython requests httpx reportlab python-dotenv

# Create .env file
cp .env.example .env
# Add your API keys to .env

# Run development server
uvicorn main:app --reload --port 8000
```

## 2.3 Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 2.4 VS Code Extensions

- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- GitLens

---

# 3. Development Milestones

## Milestone 1: Foundation (Week 1)

### Tasks
- [ ] Set up project structure
- [ ] Initialize Git repository
- [ ] Create backend folder structure
- [ ] Create frontend folder structure
- [ ] Set up FastAPI with health endpoint
- [ ] Set up React with routing
- [ ] Configure environment variables
- [ ] Set up database connection

### Deliverables
- Running FastAPI server
- Running React frontend
- Health check endpoint working
- Database initialized

### Success Criteria
- `GET /health` returns 200
- Frontend loads at localhost:3000
- Database file created

---

## Milestone 2: Core Scanners (Week 2-3)

### Tasks
- [ ] Implement WHOIS scanner
- [ ] Implement DNS scanner
- [ ] Implement SSL scanner
- [ ] Implement Headers scanner
- [ ] Create scan controller
- [ ] Implement scan endpoint
- [ ] Add input validation
- [ ] Add error handling

### Deliverables
- Working WHOIS module
- Working DNS module
- Working SSL module
- Working Headers module
- POST /scan endpoint functional

### Success Criteria
- Can scan a domain and get WHOIS, DNS, SSL, Headers results
- All modules return proper JSON format
- Error handling works for failed scans

---

## Milestone 3: Additional Scanners (Week 4)

### Tasks
- [ ] Implement Certificate Transparency scanner
- [ ] Implement IP Intelligence scanner
- [ ] Implement Email Security scanner
- [ ] Implement Google Dork Assistant
- [ ] Implement Digital Footprint scanner
- [ ] Add all scanners to scan controller

### Deliverables
- All 12 scanner modules working
- Complete scan functionality

### Success Criteria
- Full domain scan returns results from all modules
- Each module works independently

---

## Milestone 4: Risk Engine (Week 5)

### Tasks
- [ ] Implement risk calculation logic
- [ ] Define all scoring rules
- [ ] Implement risk level determination
- [ ] Add findings generation
- [ ] Add priority recommendations
- [ ] Write unit tests for risk engine

### Deliverables
- Working risk engine
- Accurate risk scoring
- Detailed findings output

### Success Criteria
- Risk score calculated correctly
- Risk level determined accurately
- Findings match detected issues

---

## Milestone 5: AI Integration (Week 6)

### Tasks
- [ ] Set up Gemini API integration
- [ ] Implement system prompt
- [ ] Implement executive summary prompt
- [ ] Implement technical summary prompt
- [ ] Implement recommendations prompt
- [ ] Add error handling and fallbacks
- [ ] Implement response caching

### Deliverables
- AI summary generation working
- Fallback mechanisms in place
- Caching implemented

### Success Criteria
- AI generates summaries for scan results
- Fallback works when AI fails
- Responses are cached appropriately

---

## Milestone 6: Database Integration (Week 7)

### Tasks
- [ ] Create database schema
- [ ] Implement scan storage
- [ ] Implement scan history retrieval
- [ ] Implement statistics calculation
- [ ] Add data retention logic
- [ ] Write database tests

### Deliverables
- Scans saved to database
- History endpoint working
- Statistics endpoint working

### Success Criteria
- Scan results persist after restart
- Can retrieve scan history
- Statistics calculated correctly

---

## Milestone 7: PDF Reports (Week 8)

### Tasks
- [ ] Implement PDF generator
- [ ] Design report template
- [ ] Add report sections
- [ ] Implement charts
- [ ] Add report generation endpoint
- [ ] Add report download endpoint

### Deliverables
- Professional PDF reports
- Report generation endpoint
- Report download functionality

### Success Criteria
- PDF generates correctly
- Report includes all sections
- Download works in browser

---

## Milestone 8: Frontend Pages (Week 9-10)

### Tasks
- [ ] Build Landing Page
- [ ] Build Dashboard
- [ ] Build Domain Scan page
- [ ] Build Scan History page
- [ ] Build Reports page
- [ ] Build Digital Footprint page
- [ ] Build Google Dork page
- [ ] Build Settings page

### Deliverables
- All frontend pages complete
- Navigation working
- Responsive design

### Success Criteria
- All pages load correctly
- Navigation works between pages
- Design is responsive

---

## Milestone 9: Integration (Week 11)

### Tasks
- [ ] Connect frontend to backend APIs
- [ ] Implement loading states
- [ ] Implement error states
- [ ] Add real-time scan progress
- [ ] Add data refresh logic
- [ ] Test end-to-end flows

### Deliverables
- Fully integrated application
- Real-time progress updates
- Error handling throughout

### Success Criteria
- Can scan a domain from frontend
- Progress updates in real-time
- Errors handled gracefully

---

## Milestone 10: Polish (Week 12)

### Tasks
- [ ] Add animations
- [ ] Improve error messages
- [ ] Add accessibility features
- [ ] Optimize performance
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Fix bugs
- [ ] Update documentation

### Deliverables
- Polished application
- Test coverage
- Updated documentation

### Success Criteria
- Application feels smooth
- Tests pass
- Documentation is current

---

## Milestone 11: Deployment (Week 13)

### Tasks
- [ ] Prepare frontend for deployment
- [ ] Prepare backend for deployment
- [ ] Deploy to Vercel (frontend)
- [ ] Deploy to Render (backend)
- [ ] Configure environment variables
- [ ] Test deployed application
- [ ] Set up monitoring

### Deliverables
- Deployed application
- Monitoring configured
- Production-ready

### Success Criteria
- Application accessible online
- All features work in production
- Monitoring active

---

# 4. Development Workflow

## 4.1 Daily Workflow

1. Pull latest changes
2. Create feature branch
3. Implement feature
4. Write tests
5. Run tests
6. Commit changes
7. Push to remote
8. Create pull request
9. Review and merge

## 4.2 Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Code style
- refactor: Refactoring
- test: Tests
- chore: Maintenance

Examples:
```
feat(backend): Add WHOIS scanner module

Implement WHOIS lookup using python-whois library.
Returns standardized JSON with registrar information.

Closes #12
```

## 4.3 Branch Naming

- feature/feature-name
- fix/bug-description
- docs/documentation-update
- test/test-addition

Examples:
- feature/whois-scanner
- fix/ssl-validation
- docs/api-specification

---

# 5. Testing Strategy

## 5.1 Unit Tests

Test individual functions and modules.

```python
# Example unit test
def test_whois_scanner():
    result = whois_scanner("example.com")
    assert result["module"] == "WHOIS"
    assert result["status"] in ["SUCCESS", "FAILED"]
    assert "data" in result
```

## 5.2 Integration Tests

Test module interactions.

```python
# Example integration test
def test_scan_flow():
    result = run_scan("example.com")
    assert result["status"] == "completed"
    assert "whois" in result
    assert "dns" in result
```

## 5.3 End-to-End Tests

Test complete user flows.

```python
# Example E2E test
def test_complete_scan_flow():
    # Start scan
    response = client.post("/scan", json={"domain": "example.com"})
    scan_id = response.json()["data"]["scan_id"]
    
    # Wait for completion
    wait_for_scan(scan_id)
    
    # Get results
    result = client.get(f"/scan/{scan_id}")
    assert result.json()["data"]["status"] == "completed"
```

## 5.4 Test Coverage Goal

- Unit tests: 80% coverage
- Integration tests: All critical paths
- E2E tests: Main user flows

---

# 6. Code Review Checklist

## 6.1 Functionality
- [ ] Code works as intended
- [ ] Edge cases handled
- [ ] Error handling implemented
- [ ] Tests pass

## 6.2 Code Quality
- [ ] Code is readable
- [ ] Functions are small
- [ ] No code duplication
- [ ] Follows style guide

## 6.3 Architecture
- [ ] Follows project architecture
- [ ] Modules are independent
- [ ] Proper separation of concerns
- [ ] No circular dependencies

## 6.4 Security
- [ ] Input validation
- [ ] No exposed secrets
- [ ] SQL injection prevention
- [ ] XSS prevention

## 6.5 Performance
- [ ] No unnecessary loops
- [ ] Efficient data structures
- [ ] Proper caching
- [ ] No memory leaks

---

# 7. Debugging Guide

## 7.1 Backend Debugging

```bash
# Enable debug mode
uvicorn main:app --reload --log-level debug

# Check logs
tail -f logs/app.log

# Test endpoint
curl http://localhost:8000/health
```

## 7.2 Frontend Debugging

```bash
# Check console for errors
# Use React DevTools
# Network tab for API calls
```

## 7.3 Common Issues

**Module fails silently**
- Check logs for errors
- Verify module returns JSON
- Check exception handling

**API returns 500**
- Check backend logs
- Verify database connection
- Check environment variables

**Frontend not updating**
- Check API response
- Verify state management
- Check for console errors

---

# 8. Performance Optimization

## 8.1 Backend Optimization

- Use async/await for I/O operations
- Implement response caching
- Use database indexes
- Optimize database queries
- Implement rate limiting

## 8.2 Frontend Optimization

- Code splitting
- Lazy loading
- Image optimization
- Minimize bundle size
- Use memoization

---

# 9. Security Best Practices

## 9.1 Backend Security

- Validate all input
- Use parameterized queries
- Never expose secrets
- Implement CORS properly
- Use HTTPS in production
- Rate limit API endpoints

## 9.2 Frontend Security

- Sanitize user input
- Use HTTPS only
- Implement CSP headers
- Validate on client and server
- Secure cookies

---

# 10. Deployment Checklist

## 10.1 Pre-Deployment

- [ ] All tests pass
- [ ] Environment variables set
- [ ] Database migrations run
- [ ] Assets optimized
- [ ] Documentation updated

## 10.2 Deployment

- [ ] Backup current version
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Run smoke tests
- [ ] Monitor for errors

## 10.3 Post-Deployment

- [ ] Verify all features work
- [ ] Check error logs
- [ ] Monitor performance
- [ ] Update documentation

---

# 11. Project Rules

## 11.1 Never Do

- Never redesign architecture without discussion
- Never rename folders without updating all references
- Never delete existing APIs without deprecation
- Never break JSON schema
- Never remove comments
- Never add features not in specifications
- Never make breaking changes without approval

## 11.2 Always Do

- Always follow existing coding style
- Always keep modules independent
- Always return standardized JSON
- Always handle errors gracefully
- Always write tests for new features
- Always update documentation
- Always ask before making architectural changes

---

# 12. Getting Help

## 12.1 Documentation

- Read project specifications first
- Check module documentation
- Review API specification

## 12.2 Debugging

- Check logs
- Use debugger
- Add print statements temporarily

## 12.3 Questions

- Ask specific questions
- Provide context
- Share error messages
- Show code snippet

---

END OF DEVELOPMENT GUIDE
