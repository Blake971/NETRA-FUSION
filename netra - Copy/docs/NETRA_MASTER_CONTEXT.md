# NETRA
# Master Context for AI Development

Version: 2.0

---

# Quick Reference for AI Agents

**Read this before making any changes to NETRA.**

---

# 1. Project Overview

NETRA is an AI-powered cybersecurity platform that performs passive security assessments using publicly available information.

**Key Principle**: NETRA is NOT a penetration testing tool. It only analyzes publicly exposed information.

**Tech Stack**:
- Backend: Python + FastAPI
- Frontend: React + Tailwind CSS
- AI: Google Gemini API
- Database: SQLite

---

# 2. Architecture Rules

## Critical Rules (NEVER VIOLATE)

1. **Frontend never talks directly to scanner modules**
   - Frontend → FastAPI → Scanner Modules
   - No direct API calls from React to external services

2. **AI never performs security analysis**
   - AI only explains findings
   - Risk calculation is deterministic (no AI)

3. **Every module must return standardized JSON**
   ```json
   {
     "module": "",
     "status": "",
     "severity": "",
     "message": "",
     "data": {}
   }
   ```

4. **Modules are independent**
   - One responsibility per module
   - No module depends on another
   - Scanner modules don't talk to database

5. **Never crash on module failure**
   - If WHOIS fails, continue with DNS
   - Return error status, don't terminate scan

---

# 3. Folder Structure

```
Netra/
├── docs/                    # All documentation
│   ├── 01_PROJECT_OVERVIEW.md
│   ├── 02_ARCHITECTURE.md
│   ├── 03_MODULES.md
│   ├── 04_FRONTEND.md
│   ├── 05_API_SPEC.md
│   ├── 06_DATABASE.md
│   ├── 07_AI_SPEC.md
│   ├── 08_RISK_ENGINE.md
│   ├── 09_DEVELOPMENT.md
│   └── NETRA_MASTER_CONTEXT.md (this file)
├── backend/
│   ├── main.py
│   ├── config/
│   ├── routes/
│   ├── scanners/
│   ├── risk/
│   ├── ai/
│   ├── reports/
│   ├── database/
│   ├── utils/
│   └── tests/
└── frontend/
    └── src/
```

---

# 4. Module Specifications

## Scanner Modules (12 total)

1. **WHOIS** - Domain registration info
2. **DNS** - DNS configuration
3. **SSL** - HTTPS certificate analysis
4. **Headers** - Security headers inspection
5. **Certificate Transparency** - Public certificate logs
6. **IP Intelligence** - Hosting information
7. **Email Security** - SPF/DKIM/DMARC
8. **Risk Engine** - Score calculation (deterministic)
9. **Gemini AI** - Explain findings (no analysis)
10. **PDF Generator** - Report generation
11. **Google Dork Assistant** - Query generation
12. **Digital Footprint** - Public information aggregation

## Module Rules

- Maximum 300 lines per module
- Split helpers into utils
- Document every public function
- Handle every exception
- Log execution time
- Never expose secrets

---

# 5. API Endpoints

- `GET /health` - Health check
- `POST /scan` - Start new scan
- `GET /scan/{id}` - Get scan status/results
- `GET /history` - Get scan history
- `GET /report/{id}` - Download PDF report
- `POST /generate-report` - Generate PDF
- `POST /dork` - Generate Google dork queries
- `POST /footprint` - Digital footprint search
- `DELETE /scan/{id}` - Delete scan
- `GET /stats` - Get statistics

All APIs return:
```json
{
  "success": true/false,
  "data": {} or "message": "..."
}
```

---

# 6. Database Schema

## Main Table: scans

- id (UUID, PK)
- domain
- status (pending/in_progress/completed/failed)
- risk_score (0-100)
- risk_level (low/medium/high/critical)
- whois_json, dns_json, ssl_json, headers_json, etc.
- ai_summary
- report_path
- created_at, completed_at

## Secondary Table: reports

- id (UUID, PK)
- scan_id (FK)
- file_path
- generated_at

---

# 7. Risk Engine Rules

**Deterministic scoring (NO AI)**

Critical Issues:
- Missing SSL: +40
- Expired SSL: +35
- SSL expiring <7 days: +25
- Missing CSP: +20
- Domain expired: +50
- DNS failure: +50

Medium Issues:
- Missing HSTS: +15
- Missing SPF: +15
- Missing DMARC: +15
- SSL expiring <30 days: +15

Risk Levels:
- 0-25: Low
- 26-50: Low-Medium
- 51-75: Medium
- 76-90: High
- 91-100: Critical

---

# 8. AI Configuration

**Provider**: Google Gemini API

**Role**: Explain findings, NOT analyze

**Prompts**:
- Executive summary
- Technical summary
- Business summary
- Recommendations
- Warnings

**Settings**:
- Model: gemini-pro
- Temperature: 0.7
- Max tokens: 2048
- Timeout: 30 seconds

**Fallback**: Use template-based summaries if AI fails

---

# 9. Development Workflow

**Build Vertically**:
1. Complete one module end-to-end
2. Test thoroughly
3. Commit
4. Then start next module

**Example**:
WHOIS → Backend → Frontend → Dashboard → Testing → Commit → DNS

---

# 10. Coding Standards

## Python (Backend)
- Use type hints
- Docstrings for public functions
- PEP 8 formatting
- Handle all exceptions
- Log errors

## React (Frontend)
- Functional components
- Hooks for state
- PropTypes or TypeScript
- Semantic HTML
- Accessible

## General
- Small functions (<50 lines)
- Clear variable names
- No code duplication
- Comment complex logic

---

# 11. Security Principles

- Validate all input
- Never expose secrets (use .env)
- Never trust user input
- Implement CORS properly
- Use HTTPS in production
- Parameterized queries (SQLAlchemy handles this)

---

# 12. Project Rules (CRITICAL)

## NEVER DO:
- Never redesign architecture without discussion
- Never rename folders without updating references
- Never delete existing APIs without deprecation
- Never break JSON schema
- Never remove comments
- Never add features not in specifications
- Never make breaking changes without approval

## ALWAYS DO:
- Always follow existing coding style
- Always keep modules independent
- Always return standardized JSON
- Always handle errors gracefully
- Always write tests for new features
- Always update documentation
- Always ask before making architectural changes

---

# 13. When Implementing Features

**Step 1**: Read relevant documentation
- 01_PROJECT_OVERVIEW.md - Overall context
- 03_MODULES.md - Module specifications
- 05_API_SPEC.md - API endpoints
- 08_RISK_ENGINE.md - If modifying risk logic

**Step 2**: Follow existing patterns
- Look at similar existing modules
- Copy JSON structure
- Follow error handling patterns

**Step 3**: Implement
- Write code
- Add tests
- Update documentation

**Step 4**: Verify
- Run tests
- Check JSON output
- Verify API response

---

# 14. Common Pitfalls to Avoid

❌ **Don't**: Make frontend call external APIs directly
✅ **Do**: Frontend calls FastAPI, FastAPI calls external APIs

❌ **Don't**: Use AI to calculate risk scores
✅ **Do**: Use deterministic risk engine rules

❌ **Don't**: Stop scan if one module fails
✅ **Do**: Continue with remaining modules, log error

❌ **Don't**: Hardcode API keys
✅ **Do**: Use environment variables

❌ **Don't**: Modify JSON schema without updating all references
✅ **Do**: Update schema, then update all code that uses it

---

# 15. Testing

**Unit Tests**: Test individual functions
**Integration Tests**: Test module interactions
**E2E Tests**: Test complete user flows

**Coverage Goal**: 80% for critical paths

---

# 16. Documentation Updates

When you make changes:
1. Update relevant spec document
2. Update this master context if architecture changes
3. Update API spec if endpoints change
4. Update module spec if modules change

---

# 17. Quick Command Reference

## Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

## Frontend
```bash
cd frontend
npm install
npm start
```

## Database
```bash
# SQLite location: backend/database/netra.db
# Backup: cp backend/database/netra.db backup.db
```

---

# 18. If Something Is Unclear

1. Read the detailed specification documents
2. Look at existing similar code
3. Ask for clarification before making assumptions
4. Propose the change and get approval

**Better to ask than to break the architecture.**

---

END OF MASTER CONTEXT

**Remember: This is a production-grade project. Follow the specifications exactly.**
