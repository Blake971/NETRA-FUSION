# NETRA
# System Architecture

Version: 2.0

---

# 1. System Architecture Overview

```
User
↓
React Frontend
↓
FastAPI Backend
↓
Scan Controller
↓
Scanner Modules
  ├── WHOIS
  ├── DNS
  ├── SSL
  ├── Headers
  ├── Certificate Transparency
  └── IP Intelligence
  └── Email Security
↓
Risk Engine
↓
Gemini AI
↓
Dashboard
↓
PDF Report
```

---

# 2. Backend Architecture

## 2.1 Backend Technology

- **Language**: Python 3.12+
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Communication**: REST API
- **Response Format**: JSON

## 2.2 Why FastAPI?

- Extremely fast
- Automatic Swagger Documentation
- Async support
- Excellent Python integration
- Easy validation
- Easy deployment

FastAPI acts as the central controller. It does NOT perform scanning. It simply coordinates the scanner modules.

## 2.3 Backend Folder Structure

```
backend/
├── main.py
├── config/
│   └── settings.py
├── routes/
│   ├── scan.py
│   ├── report.py
│   ├── history.py
│   └── health.py
├── scanners/
│   ├── whois.py
│   ├── dns.py
│   ├── ssl.py
│   ├── headers.py
│   ├── ctlogs.py
│   ├── ip_info.py
│   ├── email_security.py
│   ├── dork_assistant.py
│   └── footprint.py
├── risk/
│   └── risk_engine.py
├── ai/
│   └── gemini.py
├── reports/
│   └── pdf_generator.py
├── database/
│   ├── database.py
│   └── models.py
├── utils/
│   ├── validator.py
│   ├── formatter.py
│   └── logger.py
└── tests/
```

## 2.4 Backend Workflow

```
User → React → POST /scan → FastAPI → Validation → Scanner Controller → Run Modules → Normalize Results → Risk Engine → Gemini → Database → JSON Response
```

## 2.5 Main Entry Point (main.py)

Responsibilities:

- Start FastAPI
- Load environment variables
- Configure CORS
- Register routes
- Initialize database
- Register middleware

No business logic should exist inside main.py.

## 2.6 Route Layer

Routes only receive requests.

Example: POST /scan → Validate request → Call Scan Controller → Return JSON

Routes NEVER perform scanning.

## 2.7 Scan Controller

This is the brain of the backend.

Responsibilities:

- Receive validated domain
- Call scanner modules
- Collect responses
- Handle failures
- Continue execution even if one module fails

## 2.8 Scanner Modules

Every scanner is independent. Each module has one responsibility only.

Example:
- whois.py - Only performs WHOIS lookup
- dns.py - Only performs DNS lookup

This follows the Single Responsibility Principle.

## 2.9 Scanner Communication

Each scanner communicates with different Internet services:

- WHOIS → WHOIS Servers
- DNS → DNS Resolvers
- SSL → Website
- Headers → Website
- CT Logs → Public CT Servers
- IP → Public IP Service
- Email Security → DNS TXT Records

Every module returns JSON.

## 2.10 Validation Layer (validator.py)

Responsibilities:

- Check empty input
- Check invalid domain
- Check invalid email
- Check invalid URL

Return meaningful errors. Never allow bad input to reach scanner modules.

## 2.11 Data Normalization

Different modules return different formats. Normalization converts everything into one standard structure.

Purpose:

- Simplify frontend development
- Simplify AI
- Simplify report generation

## 2.12 Error Handling

If WHOIS fails → Continue DNS

If DNS fails → Continue SSL

NETRA should NEVER stop because one module failed.

Instead, return Status: FAILED + Reason → Continue remaining modules.

## 2.13 Logging

Every module logs:

- Start Time
- End Time
- Errors
- Execution Time

Example: SSL Started → SSL Completed → Time: 0.84 sec

## 2.14 Risk Engine

Risk Engine receives WHOIS, DNS, SSL, Headers, Email, CT Logs → Calculates Score → Returns {"score":82, "severity":"LOW"}

Risk Engine is deterministic. No AI.

## 2.15 AI Module

Gemini receives Raw JSON → Summary Prompt → Recommendations → Executive Summary

Gemini never performs security analysis. Gemini explains.

## 2.16 Database Layer

Responsibilities:

- Store User
- Store Scan
- Store Timestamp
- Store JSON
- Store Risk Score
- Store AI Summary
- Store Report Path

Backend should never directly write SQL inside routes. Database layer handles all persistence.

## 2.17 API Standards

All APIs return:

Success:
```json
{
  "success": true,
  "data": {}
}
```

Failure:
```json
{
  "success": false,
  "message": "..."
}
```

Consistent response format everywhere.

## 2.18 API Endpoints

- GET /health
- POST /scan
- GET /history
- GET /report/{id}
- POST /generate-report
- POST /dork
- POST /footprint

Future: POST /compare

## 2.19 Async Processing

Scanner modules should be capable of running asynchronously.

Instead of: WHOIS → DNS → SSL → Headers

Use: WHOIS, DNS, SSL, Headers (Run Together) → Merge Results

This improves performance.

## 2.20 Performance Goals

- Health API: <100 ms
- WHOIS: <2 sec
- DNS: <1 sec
- SSL: <2 sec
- Complete Scan: <10 sec
- AI: <5 sec

## 2.21 Backend Rules

- Never duplicate logic
- Never expose secrets
- Never trust user input
- Never crash
- Always log errors
- Always return JSON
- Always validate
- Keep modules independent
- Keep functions small

## 2.22 Future Scalability

Current: FastAPI → SQLite

Future: FastAPI → PostgreSQL → Redis → Docker → Kubernetes

Architecture should allow scaling without rewriting modules.

---

# 3. Frontend Architecture

## 3.1 Frontend Technology

- React
- Tailwind CSS
- React Router
- Axios
- Recharts

## 3.2 Frontend Principles

- Component-based architecture
- State management with React hooks
- API communication through Axios
- Responsive design
- Dark theme default

## 3.3 Frontend Folder Structure

```
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── utils/
│   ├── services/
│   └── styles/
├── public/
└── package.json
```

## 3.4 Frontend Rules

- Never communicate directly with scanner modules
- Only communicate with FastAPI backend
- Handle loading states
- Handle error states
- Validate user input before sending to backend

---

# 4. Communication Flow

## 4.1 Request Flow

```
User Input → React Component → Validation → Axios Request → FastAPI Route → Validation → Scanner Controller → Scanner Modules → JSON Response
```

## 4.2 Response Flow

```
Scanner Modules → JSON → Scan Controller → Normalize → Risk Engine → Gemini AI → Database → FastAPI Response → React Component → UI Update
```

---

# 5. Data Flow

## 5.1 Scan Data Flow

```
Domain → WHOIS (JSON) → DNS (JSON) → SSL (JSON) → Headers (JSON) → CT Logs (JSON) → Email (JSON) → IP (JSON) → Merge → Risk Engine → Score → Gemini → Summary → Database
```

## 5.2 Report Data Flow

```
Database → Retrieve Scan → PDF Generator → PDF File → Download
```

---

# 6. Security Architecture

## 6.1 Input Validation

- Client-side validation (React)
- Server-side validation (FastAPI)
- Type checking with Pydantic

## 6.2 API Security

- CORS configuration
- Rate limiting (future)
- API key management
- Environment variables for secrets

## 6.3 Data Security

- No sensitive data in logs
- Encrypted secrets in .env
- HTTPS in production
- SQL injection prevention (ORM)

---

END OF ARCHITECTURE
