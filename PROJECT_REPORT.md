# NETRA Fusion - Comprehensive Project Report

## Executive Summary

NETRA Fusion is an evidence-first domain security assessment workspace that transforms scattered public security signals into traceable findings and prioritized action plans. The system implements a discover → challenge → report workflow, where every security deduction is backed by collected evidence, collection gaps remain visible, and optional AI explanations never alter the deterministic scores.

**Key Philosophy**: Evidence before conclusions. No unsupported claims, no AI-driven decisions, no exploit verification - only observable public signals analyzed through deterministic rules.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Security Checks](#security-checks)
5. [Data Flow](#data-flow)
6. [Technology Stack](#technology-stack)
7. [Deployment](#deployment)
8. [Security Considerations](#security-considerations)
9. [Limitations](#limitations)
10. [Future Enhancements](#future-enhancements)

---

## Project Overview

### Purpose

NETRA Fusion provides a local workspace for assessing domain security posture through public information collection. It is designed for:
- Security analysts needing quick domain posture assessments
- DevOps teams validating security configurations
- Security researchers analyzing public-facing infrastructure
- Educational purposes for understanding security headers and DNS records

### What It Does

1. **Collects Evidence**: Gathers public DNS records, HTTPS/TLS configuration, and certificate transparency data
2. **Analyzes Configuration**: Runs 12 deterministic security checks against collected evidence
3. **Scores Posture**: Calculates a 0-100 score based on observed configuration gaps
4. **Provides Context**: Shows evidence coverage, asset relationships, and technology signals
5. **Suggests Fixes**: Offers remediation guidance with what-if score projections
6. **Explains Findings**: Three-level explanation system (Summary, Explanation, Technical)
7. **Optional AI**: Gemini integration for narrative explanations (non-altering)

### What It Does NOT Do

- No exploit execution or penetration testing
- No compliance certification claims
- No breach probability estimation
- No complete inventory enumeration
- No attribution or threat intelligence
- No internal network scanning
- No authentication bypass testing

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                            │
│                    React/Vite Frontend                           │
│              http://127.0.0.1:8001 (Light/Dark Mode)             │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP/JSON API
┌────────────────────▼────────────────────────────────────────────┐
│                    FastAPI Backend                               │
│                  fusion_api.py                                   │
│  - REST API Endpoints                                            │
│  - Async Job Queue (max 12 concurrent)                          │
│  - SQLite Persistence (fusion.db)                               │
│  - TrustedHost Middleware                                        │
│  - Gemini AI Integration (Optional)                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                  Assessment Engine                               │
│                  fusion_engine.py                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Collectors (Evidence Gathering)                         │  │
│  │  - web_snapshot: HTTPS/TLS handshake + headers           │  │
│  │  - dns_snapshot: DNS records (A, AAAA, MX, NS, TXT, CAA)│  │
│  │  - ct_snapshot: Certificate transparency (crt.sh)         │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Analyzer (Security Checks)                               │  │
│  │  - 12 deterministic checks (Web, TLS, Email, DNS)        │  │
│  │  - Evidence-aware scoring (100 - deductions)               │  │
│  │  - Skeptic pattern (suppress unsupported findings)         │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Validators                                              │  │
│  │  - normalize_domain: Public domain validation             │  │
│  │  - public_addresses: IP address validation                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction

```
User Request
    ↓
normalize_domain() → Validates domain format
    ↓
public_addresses() → Resolves to public IPs only
    ↓
collect() → Runs 3 collectors in parallel
    ├─ web_snapshot() → HTTPS/TLS + headers
    ├─ dns_snapshot() → DNS records
    └─ ct_snapshot() → Certificate transparency
    ↓
analyze() → Runs 12 security checks
    ├─ Evidence validation
    ├─ Scoring calculation
    ├─ Skeptic cross-checks
    └─ Technology detection
    ↓
SQLite Storage → Persists assessment with SHA-256 digest
    ↓
Frontend Display → Interactive UI with multiple views
```

---

## Core Components

### 1. Entry Point: run_netra.py

**Purpose**: Application launcher and environment configuration

**Responsibilities**:
- Sets Python paths for dependencies
- Configures Gemini API credentials
- Starts uvicorn server on 127.0.0.1:8001
- Binds to loopback for local-only access

**Key Configuration**:
```python
os.environ['GEMINI_API_KEY'] = 'AIzaSyB0863MEzep5DkO3vQWEpnldswEJOECeew'
os.environ['GEMINI_MODEL'] = 'gemini-1.5-flash'
```

### 2. Backend API: fusion_api.py

**Purpose**: REST API server and job orchestration

**Key Endpoints**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check, AI availability |
| `/api/cases` | POST | Create new assessment |
| `/api/cases` | GET | List all assessments |
| `/api/cases/{id}` | GET | Retrieve specific assessment |
| `/api/cases/{id}/export` | GET | Export evidence bundle |
| `/api/cases/{id}/explain` | POST | Generate AI explanation |
| `/api/cases/{id}/compare/{baseline}` | GET | Compare two assessments |
| `/` | GET | Serve frontend |

**Job Queue System**:
- Async task management with `asyncio`
- Semaphore limits: 3 concurrent collectors, 12 total jobs
- Automatic cleanup on server restart
- Progress tracking with events log

**Persistence**:
- SQLite database (`fusion.db`)
- JSON document storage per case
- SHA-256 evidence digest for change detection
- Timestamps and provenance tracking

**Security**:
- TrustedHost middleware (localhost, 127.0.0.1)
- Domain validation before collection
- Public IP enforcement
- Host header rejection

### 3. Assessment Engine: fusion_engine.py

**Purpose**: Core security assessment logic

#### Collectors

**web_snapshot(domain)**
- Resolves public IP addresses
- Creates HTTPS connection with IP pinning
- Validates TLS certificate
- Extracts headers, status code, protocol version
- Calculates certificate expiry days
- Captures response body (limited to 131KB)
- Records redirects without following

**dns_snapshot(domain)**
- Queries recursive DNS resolver
- Collects: A, AAAA, MX, NS, TXT, CAA records
- Special handling for DMARC (_dmarc.domain)
- 3-second timeout per query
- Tracks partial results with error reporting

**ct_snapshot(domain)**
- Queries crt.sh certificate transparency log
- Searches for subdomain patterns (%.domain)
- Extracts historical certificate names
- Limits to 100 names, 2MB response
- Historical data warning (not proof of live service)

#### Analyzer

**analyze(domain, results)**

The analyzer runs 12 security checks:

1. **HSTS** (10 points): Checks for Strict-Transport-Security with positive max-age
2. **CSP** (10 points): Checks for Content-Security-Policy presence
3. **Framing** (5 points): Checks X-Frame-Options or CSP frame-ancestors
4. **NoSniff** (5 points): Checks X-Content-Type-Options: nosniff
5. **Permissions-Policy** (5 points): Checks for browser feature permissions control
6. **Referrer-Policy** (3 points): Checks for referrer information control
7. **CORS** (5 points): Detects wildcard Access-Control-Allow-Origin
8. **TLS Expiry** (5-15 points): Tiered scoring based on days remaining
9. **TLS Protocol** (15 points): Checks for TLS 1.2 or 1.3
10. **SPF** (10 points): Checks for sender policy framework record
11. **DMARC** (15 points): Checks for enforcement policy (p=reject/quarantine)
12. **CAA** (0 points): Advisory check for certificate authority restriction

**Skeptic Pattern**:
- Suppresses findings when evidence conflicts
- Example: Missing X-Frame-Options not flagged if CSP has frame-ancestors
- Tracks challenged findings in separate list
- Collection failures marked as UNKNOWN (no deduction)

**Scoring Algorithm**:
```
score = max(0, 100 - sum(finding_points))
coverage = (observed_checks / total_checks) * 100
```

- Unknown checks never deduct
- Incomplete coverage makes score provisional
- Maximum deductions: 103 points (with new checks)
- CAA is advisory (0 points)

**Technology Detection**:
- Headers: server, x-powered-by, x-aspnet-version
- HTML heuristics: 17 framework markers (WordPress, React, Vue, etc.)
- Clearly labeled as self-reported or heuristic

**Asset Graph**:
- Nodes: Domain, IPs, certificate names, mail servers
- Edges: Relationship types (DNS, CT observation)
- Visual representation in UI

### 4. Frontend: Fusion.jsx

**Purpose**: React-based user interface

**Key Features**:
- Single-page application with 9 views
- Dark/Light mode toggle
- Real-time progress updates
- Interactive asset graph visualization
- Three-level explanation system
- Remediation planner with what-if scoring
- Assessment history and comparison
- Portfolio management

**Views**:
1. **Website checkup**: Main assessment view with audience report
2. **Overview**: Dashboard with metrics and briefing
3. **Evidence room**: Detailed findings with filters
4. **Public footprint**: Raw evidence display
5. **Asset graph**: Interactive infrastructure visualization
6. **Remediation**: Fix selection and score projection
7. **Compare checkups**: Side-by-side assessment comparison
8. **Assessment history**: Saved assessments table
9. **Portfolio**: Batch domain management

**State Management**:
- Current assessment
- Assessment history
- View navigation
- Search/filter state
- Light/dark mode preference
- AI explanation status

---

## Security Checks

### Web Security Checks (7)

#### 1. HSTS (HTTPS Strict Transport Security)
- **Points**: 10
- **Evidence**: Strict-Transport-Security header
- **Check**: Positive max-age value present
- **Remediation**: `add_header Strict-Transport-Security "max-age=86400" always;`
- **Why**: Prevents protocol downgrade attacks

#### 2. CSP (Content Security Policy)
- **Points**: 10
- **Evidence**: Content-Security-Policy header
- **Check**: Header presence
- **Remediation**: `add_header Content-Security-Policy-Report-Only "default-src 'self'; object-src 'none'; base-uri 'self'" always;`
- **Why**: Reduces impact of content injection attacks

#### 3. Framing Protection
- **Points**: 5
- **Evidence**: X-Frame-Options or CSP frame-ancestors
- **Check**: DENY/SAMEORIGIN or valid frame-ancestors
- **Remediation**: `add_header Content-Security-Policy "frame-ancestors 'self'" always;`
- **Skeptic**: Suppresses if CSP frame-ancestors exists
- **Why**: Prevents clickjacking attacks

#### 4. NoSniff (Content Type Protection)
- **Points**: 5
- **Evidence**: X-Content-Type-Options header
- **Check**: Value equals "nosniff"
- **Remediation**: `add_header X-Content-Type-Options "nosniff" always;`
- **Why**: Prevents MIME-type sniffing attacks

#### 5. Permissions-Policy (NEW)
- **Points**: 5
- **Evidence**: Permissions-Policy or legacy Feature-Policy
- **Check**: Header presence
- **Remediation**: `add_header Permissions-Policy "geolocation=(), camera=(), microphone=()" always;`
- **Why**: Controls browser feature access (geolocation, camera, microphone)

#### 6. Referrer-Policy (NEW)
- **Points**: 3
- **Evidence**: Referrer-Policy header
- **Check**: Header presence
- **Remediation**: `add_header Referrer-Policy "strict-origin-when-cross-origin" always;`
- **Why**: Controls referrer information leakage

#### 7. CORS Configuration (NEW)
- **Points**: 5
- **Evidence**: Access-Control-Allow-Origin header
- **Check**: Wildcard (*) value
- **Remediation**: `add_header Access-Control-Allow-Origin "https://trusted.example.com" always;`
- **Why**: Prevents overly permissive cross-origin access

### TLS Security Checks (2)

#### 8. TLS Expiry
- **Points**: 5-15 (tiered)
- **Evidence**: Certificate notAfter field
- **Check**: Days remaining < 30
- **Tiered Scoring**:
  - < 7 days: 15 points (critical)
  - < 14 days: 10 points (warning)
  - < 30 days: 5 points (advisory)
- **Remediation**: Enable automatic certificate renewal
- **Why**: Prevents service interruption from expired certificates

#### 9. TLS Protocol
- **Points**: 15
- **Evidence**: Negotiated TLS version
- **Check**: Protocol is TLS 1.2 or 1.3
- **Remediation**: Configure TLS 1.2 or newer
- **Why**: Modern TLS protects transport confidentiality
- **Limitation**: Only checks one handshake, not all supported protocols

### Email Security Checks (2)

#### 10. SPF (Sender Policy Framework)
- **Points**: 10
- **Evidence**: DNS TXT record
- **Check**: Valid SPF record present
- **Remediation**: Publish reviewed SPF policy
- **Why**: Declares permitted mail senders
- **Limitation**: Does not evaluate full semantics

#### 11. DMARC (Domain-based Message Authentication)
- **Points**: 15
- **Evidence**: DMARC DNS record
- **Check**: Enforcement policy (p=reject or p=quarantine)
- **Remediation**: Move from p=none to p=quarantine/reject
- **Why**: Provides spoofing protection
- **Limitation**: Does not test alignment or delivery

### DNS Security Checks (1)

#### 12. CAA (Certificate Authority Authorization)
- **Points**: 0 (advisory)
- **Evidence**: CAA DNS record
- **Check**: Record presence
- **Remediation**: Check inherited policies before publishing
- **Why**: Restricts certificate issuance
- **Advisory**: Zero points because inherited parent policies may apply

---

## Data Flow

### Assessment Lifecycle

```
1. User Input
   ├─ Domain: example.com
   └─ Mode: Live or Demo

2. Validation
   ├─ normalize_domain(): Format validation
   ├─ public_addresses(): IP resolution
   └─ Error: 422 if invalid

3. Job Creation
   ├─ Generate UUID
   ├─ Status: QUEUED
   ├─ Store in SQLite
   └─ Return to client

4. Collection (Async)
   ├─ Status: RUNNING
   ├─ Progress: 10%
   ├─ web_snapshot(): HTTPS/TLS
   │  ├─ Progress: 33%
   │  └─ Event logged
   ├─ dns_snapshot(): DNS records
   │  ├─ Progress: 56%
   │  └─ Event logged
   ├─ ct_snapshot(): Certificate transparency
   │  ├─ Progress: 79%
   │  └─ Event logged
   └─ All collectors complete

5. Analysis
   ├─ Status: RUNNING
   ├─ Progress: 90%
   ├─ analyze(): 12 security checks
   ├─ Skeptic cross-checks
   ├─ Technology detection
   ├─ Asset graph generation
   └─ Scoring calculation

6. Completion
   ├─ Status: COMPLETED
   ├─ Progress: 100%
   ├─ evidence_sha256: SHA-256 digest
   ├─ Store in SQLite
   └─ Return to client

7. Display
   ├─ Frontend renders assessment
   ├─ User navigates views
   ├─ Optional: AI explanation
   └─ Optional: Remediation planning
```

### Evidence Digest

**Purpose**: Detect changes in collected evidence

**Algorithm**:
```python
def evidence_digest(results):
    json_str = json.dumps(results, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(json_str.encode()).hexdigest()
```

**Use Cases**:
- Verify evidence hasn't changed between assessments
- Detect tampering in exported bundles
- Compare assessment snapshots

---

## Technology Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Runtime | Python | 3.10+ | Application runtime |
| Web Framework | FastAPI | 0.104.1 | REST API server |
| ASGI Server | Uvicorn | 0.24.0 | Async server |
| Database | SQLite | Built-in | Persistence |
| DNS | dnspython | 2.4.2 | DNS queries |
| HTTP | httpx | 0.25.2 | HTTP client |
| TLS | pyOpenSSL | 24.0.0 | TLS handling |
| Validation | Pydantic | 2.0+ | Data validation |
| AI | google-generativeai | 0.5+ | Gemini integration |

### Frontend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | React | 18+ | UI framework |
| Build Tool | Vite | Latest | Build tooling |
| Styling | Tailwind CSS | Latest | Utility CSS |
| Charts | Victory | Latest | Graph visualization |
| HTTP Client | Axios | Latest | API calls |

### Development Tools

| Tool | Purpose |
|------|---------|
| unittest | Python testing |
| Playwright | Browser testing |
| npm | Node package manager |
| pip | Python package manager |

---

## Deployment

### Local Development

**Prerequisites**:
- Python 3.10+
- Node.js 24+
- Git

**Setup**:
```powershell
# Install Python dependencies
python -m pip install --target .runtime -r "netra - Copy/backend/fusion_requirements.txt"

# Install Node dependencies
cd "netra - Copy/frontend"
npm ci

# Build frontend
npm run build

# Run server
cd ../..
python run_netra.py
```

**Access**: http://127.0.0.1:8001

### Production Considerations

**Required Changes**:
1. **Authentication**: Add user authentication and authorization
2. **Database**: Migrate to PostgreSQL for concurrent access
3. **Queue**: Use Redis/Celery for durable job queue
4. **Deployment**: Containerize with Docker
5. **HTTPS**: Configure TLS termination
6. **Rate Limiting**: Add per-user rate limits
7. **Monitoring**: Add logging and metrics
8. **Backup**: Implement database backup strategy

**Security Hardening**:
- Remove TrustedHost restriction (or configure properly)
- Add API key authentication
- Implement CSRF protection
- Add input sanitization
- Configure CORS properly
- Enable security headers
- Regular dependency updates

---

## Security Considerations

### Local Security Boundaries

**Network Isolation**:
- Binds to 127.0.0.1 (loopback only)
- Rejects arbitrary Host headers
- No external network access except to target domain

**Target Validation**:
- Domain format validation
- Public IP enforcement (rejects private IPs)
- Port and credential rejection
- Internal domain rejection (.local, .internal, etc.)

**Collection Safety**:
- IP pinning for HTTPS connections
- Certificate validation preserved
- Redirects recorded, not followed
- Timeouts and size limits enforced
- Response body truncated to 131KB

**Job Limits**:
- Max 12 concurrent/pending jobs
- Max 3 parallel collectors per job
- Automatic cleanup on restart

### Data Privacy

**What is Collected**:
- Public DNS records
- HTTPS response headers
- Certificate transparency names
- Response body (first 131KB)

**What is NOT Collected**:
- Cookies
- Authentication tokens
- Internal network data
- User credentials
- Request bodies

**AI Privacy**:
- Only sends: domain, demo flag, score, coverage, normalized findings
- Excludes: raw response bodies, cookies, headers
- AI output cached and labeled separately
- Provider failure leaves deterministic report unchanged

### Evidence Export

**Included in Export**:
- Raw collector observations
- Review trail with timestamps
- Methodology documentation
- SHA-256 evidence digest
- Assessment metadata

**Warning**:
- May include public response headers
- May include HTML content
- Review before sharing
- Digest is not a digital signature

---

## Limitations

### Collection Limitations

**DNS**:
- Uses system recursive resolver
- 3-second timeout per query
- Does not check inherited CAA policies
- DMARC alignment not tested

**HTTPS/TLS**:
- Only checks root page (/)
- Single handshake (not all protocols)
- Does not enumerate cipher suites
- Expired/untrusted certs make collector UNKNOWN
- Does not follow redirects

**Certificate Transparency**:
- Historical data (may be inactive)
- Limited to 100 names
- 2MB response limit
- Not proof of live service

### Analysis Limitations

**Security Checks**:
- Header presence only (no semantic validation)
- SPF does not evaluate full semantics
- DMARC alignment not tested
- No exploit verification
- No compliance certification

**Scoring**:
- Configuration score, not breach probability
- Confidence values are heuristics, not probabilities
- Incomplete coverage makes score provisional
- No benchmark percentiles

**Technology Detection**:
- Self-reported headers (unverified)
- HTML heuristics (not version-specific)
- May have false positives/negatives

### General Limitations

- Single-user local workspace
- No multi-user support
- No scheduled assessments
- No subdomain discovery
- No vulnerability scanning
- No penetration testing
- No threat intelligence
- No compliance frameworks

---

## Future Enhancements

### Priority 1: Security & Reliability

1. **Certificate Failure Classification**
   - Separate cert validation from HTTP collection
   - Classify cert failures as distinct findings
   - Better visibility into certificate issues

2. **Policy-Semantic Validation**
   - Parse and validate CSP directives
   - Evaluate SPF mechanisms
   - Check DMARC alignment

3. **Enhanced TLS Detection**
   - Enumerate all supported TLS versions
   - Check cipher suite configuration
   - Test for weak protocols

### Priority 2: Feature Additions

4. **SARIF Scanner Integration**
   - Import Nuclei results
   - Import ZAP results
   - Multi-tool evidence correlation

5. **Subdomain Discovery**
   - Certificate Transparency enumeration
   - DNS brute force
   - Attack surface mapping

6. **Historical Trending**
   - Score changes over time
   - Visualizations
   - Security posture monitoring

7. **Multi-Tenant Support**
   - User authentication
   - Role-based access
   - Team workspaces

### Priority 3: Infrastructure

8. **Durable Queue**
   - Redis/Celery integration
   - Persistent job storage
   - Worker scaling

9. **Database Migration**
   - PostgreSQL support
   - Concurrent access
   - Better querying

10. **Rate Limiting**
    - Per-user limits
    - API key authentication
    - Abuse prevention

### Priority 4: AI & Automation

11. **Multi-Provider AI**
    - OpenAI support
    - Anthropic support
    - Local LLM support

12. **Automated Remediation**
    - Generate config files
    - nginx/Apache templates
    - Cloud config generation

13. **Scheduled Assessments**
    - Cron-like scheduling
    - Continuous monitoring
    - Alert integration

### Priority 5: User Experience

14. **Real-Time Updates**
    - WebSocket streaming
    - Live progress events
    - Better UX

15. **Custom Dashboards**
    - Portfolio statistics
    - Aggregate metrics
    - Executive views

16. **Mobile Optimization**
    - PWA support
    - Native app
    - On-the-go monitoring

---

## Conclusion

NETRA Fusion provides a principled, evidence-first approach to domain security assessment. By prioritizing observable evidence over assumptions, implementing deterministic cross-checks, and maintaining clear boundaries between collection and analysis, it offers a reliable tool for understanding public-facing security posture.

The system is designed as a local workspace for security professionals, not a replacement for comprehensive penetration testing or compliance audits. Its strength lies in transparency: every deduction can be traced to specific evidence, every gap is clearly visible, and optional AI explanations never alter the deterministic scores.

With the recent enhancements (12 security checks, improved technology detection, tiered certificate expiry scoring, and enhanced light mode UI), NETRA Fusion offers a more comprehensive assessment capability while maintaining its core philosophy of evidence before conclusions.

---

## Appendix

### File Structure

```
tanish_project/
├── run_netra.py                 # Application launcher
├── test_fusion.py               # Test suite (22 tests)
├── README.md                    # Project documentation
├── PROJECT_REPORT.md            # This report
├── .runtime.backup/             # Backup of bundled dependencies
└── netra - Copy/
    ├── backend/
    │   ├── fusion_api.py        # REST API server
    │   ├── fusion_engine.py     # Assessment engine
    │   ├── fusion_policy.py     # Policy validation helpers
    │   ├── fusion_ai.py         # Gemini integration
    │   ├── fusion_explain.py    # Explanation formatting
    │   ├── fusion_footprint.py  # Footprint analysis
    │   ├── fusion_compare.py    # Assessment comparison
    │   ├── fusion.db            # SQLite database
    │   └── fusion_requirements.txt
    └── frontend/
        ├── src/
        │   ├── Fusion.jsx       # Main React component
        │   ├── fusion.css       # Dark mode styles
        │   ├── light-mode.css   # Light mode styles
        │   ├── ai.css           # AI component styles
        │   ├── portfolio.css    # Portfolio styles
        │   ├── audience.css     # Audience report styles
        │   ├── index.css        # Global styles
        │   ├── Audience.jsx     # Audience report component
        │   ├── Discovery.jsx    # Evidence display
        │   ├── Portfolio.jsx    # Portfolio management
        │   └── components/
        │       └── Navbar.jsx   # Navigation
        ├── dist/                # Built frontend
        └── package.json
```

### Test Coverage

**EvidenceTests (14 tests)**:
- test_unknown_never_looks_secure
- test_score_matches_evidence
- test_partial_dns_does_not_penalize_timeout
- test_error_response_is_not_missing_headers
- test_invalid_framing_controls_do_not_pass
- test_caa_absence_is_advisory_due_to_inheritance
- test_digest_detects_evidence_changes
- test_domain_validation
- test_private_dns_addresses_blocked
- test_permissions_policy_absence_detected
- test_permissions_policy_present_passes
- test_referrer_policy_absence_detected
- test_referrer_policy_present_passes
- test_wildcard_cors_detected
- test_specific_cors_passes
- test_certificate_expiry_tiered_scoring

**ApiTests (6 tests)**:
- test_demo_full_lifecycle
- test_missing_case_and_invalid_target
- test_ai_unavailable_preserves_evidence
- test_ai_explanation_cached_without_changing_score
- test_untrusted_host_rejected
- test_live_private_target_fails_without_collecting

**Total**: 22 tests, all passing

### API Reference

**Health Check**
```
GET /api/health
Response: {status: "ok", version: "3.0", ai_available: boolean}
```

**Create Assessment**
```
POST /api/cases
Body: {domain: string, demo: boolean, demo_profile: "baseline"|"improved"}
Response: {id: uuid, domain: string, status: "QUEUED", ...}
```

**List Assessments**
```
GET /api/cases
Response: [{id, domain, demo, created_at, status, score, coverage}, ...]
```

**Get Assessment**
```
GET /api/cases/{id}
Response: Full assessment object with results and analysis
```

**Export Evidence**
```
GET /api/cases/{id}/export
Response: JSON evidence bundle with SHA-256 digest
```

**AI Explanation**
```
POST /api/cases/{id}/explain
Response: Assessment with ai_explanation field
```

**Compare Assessments**
```
GET /api/cases/{id}/compare/{baseline}
Response: Comparison object with score changes
```

---

**Report Generated**: October 6, 2026
**NETRA Fusion Version**: 3.0
**Security Checks**: 12
**Test Coverage**: 22/22 passing
