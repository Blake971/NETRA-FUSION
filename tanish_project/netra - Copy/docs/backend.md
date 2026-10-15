# NETRA
# Backend Architecture Specification

Version: 2.0

---

# 1. Overview

The backend is the heart of NETRA.

Responsibilities:

• Receive requests from the frontend

• Validate user input

• Execute scanner modules

• Collect results

• Normalize data

• Calculate risk score

• Generate AI summaries

• Store scan history

• Return structured JSON

The backend must remain modular, scalable, and independent of the frontend.

---

# 2. Backend Technology

Language

Python 3.12+

Framework

FastAPI

Server

Uvicorn

Communication

REST API

Response Format

JSON

---

# 3. Why FastAPI?

Reasons:

• Extremely fast

• Automatic Swagger Documentation

• Async support

• Excellent Python integration

• Easy validation

• Easy deployment

FastAPI acts as the central controller.

It does NOT perform scanning.

It simply coordinates the scanner modules.

---

# 4. Backend Folder Structure

backend/

│

├── main.py

│

├── config/

│       settings.py

│

├── routes/

│       scan.py

│       report.py

│       history.py

│       health.py

│

├── scanners/

│       whois.py

│       dns.py

│       ssl.py

│       headers.py

│       ctlogs.py

│       ip_info.py

│       email_security.py

│       dork_assistant.py

│       footprint.py

│

├── risk/

│       risk_engine.py

│

├── ai/

│       gemini.py

│

├── reports/

│       pdf_generator.py

│

├── database/

│       database.py

│       models.py

│

├── utils/

│       validator.py

│       formatter.py

│       logger.py

│

└── tests/

---

# 5. Backend Workflow

User

↓

React

↓

POST /scan

↓

FastAPI

↓

Validation

↓

Scanner Controller

↓

Run Modules

↓

Normalize Results

↓

Risk Engine

↓

Gemini

↓

Database

↓

JSON Response

---

# 6. Main Entry Point

main.py

Responsibilities

• Start FastAPI

• Load environment variables

• Configure CORS

• Register routes

• Initialize database

• Register middleware

No business logic should exist inside main.py

---

# 7. Route Layer

Routes only receive requests.

Example

POST /scan

↓

Validate request

↓

Call Scan Controller

↓

Return JSON

Routes NEVER perform scanning.

---

# 8. Scan Controller

This is the brain of the backend.

Responsibilities

• Receive validated domain

• Call scanner modules

• Collect responses

• Handle failures

• Continue execution even if one module fails

Pseudo Flow

Receive Domain

↓

WHOIS

↓

DNS

↓

SSL

↓

Headers

↓

CT Logs

↓

Email Security

↓

IP

↓

Merge Results

↓

Risk Engine

↓

Gemini

↓

Return

---

# 9. Scanner Modules

Every scanner is independent.

Each module has one responsibility only.

Example

whois.py

Only performs WHOIS lookup.

Nothing else.

dns.py

Only performs DNS lookup.

Nothing else.

This follows the Single Responsibility Principle.

---

# 10. Scanner Communication

Each scanner communicates with different Internet services.

WHOIS

↓

WHOIS Servers

DNS

↓

DNS Resolvers

SSL

↓

Website

Headers

↓

Website

CT Logs

↓

Public CT Servers

IP

↓

Public IP Service

Email Security

↓

DNS TXT Records

Every module returns JSON.

---

# 11. JSON Contract

Every module MUST return

{
    "module": "",
    "status": "",
    "severity": "",
    "message": "",
    "data": {}
}

Example

{
    "module":"WHOIS",

    "status":"SUCCESS",

    "severity":"INFO",

    "message":"WHOIS Retrieved",

    "data":{
        ...
    }
}

This format must never change.

---

# 12. Validation Layer

validator.py

Responsibilities

Check

• Empty input

• Invalid domain

• Invalid email

• Invalid URL

Return meaningful errors.

Never allow bad input to reach scanner modules.

---

# 13. Data Normalization

Different modules return different formats.

Normalization converts everything into one standard structure.

Purpose

Simplify frontend development.

Simplify AI.

Simplify report generation.

---

# 14. Error Handling

If WHOIS fails

↓

Continue DNS

If DNS fails

↓

Continue SSL

NETRA should NEVER stop because one module failed.

Instead

Return

Status

↓

FAILED

↓

Reason

↓

Continue remaining modules

---

# 15. Logging

Every module logs

Start Time

End Time

Errors

Execution Time

Example

SSL Started

SSL Completed

Time: 0.84 sec

---

# 16. Risk Engine

Risk Engine receives

WHOIS

DNS

SSL

Headers

Email

CT Logs

↓

Calculates Score

↓

Returns

{
"score":82,

"severity":"LOW"

}

Risk Engine is deterministic.

No AI.

---

# 17. AI Module

Gemini receives

Raw JSON

↓

Summary Prompt

↓

Recommendations

↓

Executive Summary

Gemini never performs security analysis.

Gemini explains.

---

# 18. Database Layer

Responsibilities

Store

User

Scan

Timestamp

JSON

Risk Score

AI Summary

Report Path

Backend should never directly write SQL inside routes.

Database layer handles all persistence.

---

# 19. API Standards

All APIs return

Success

{
"success":true,

"data":{}
}

Failure

{
"success":false,

"message":"..."
}

Consistent response format everywhere.

---

# 20. API Endpoints

GET

/health

POST

/scan

GET

/history

GET

/report/{id}

POST

/generate-report

POST

/dork

POST

/footprint

Future

POST

/compare

---

# 21. Async Processing

Scanner modules should be capable of running asynchronously.

Instead of

WHOIS

↓

DNS

↓

SSL

↓

Headers

Use

WHOIS

DNS

SSL

Headers

↓

Run Together

↓

Merge Results

This improves performance.

---

# 22. Performance Goals

Health API

<100 ms

WHOIS

<2 sec

DNS

<1 sec

SSL

<2 sec

Complete Scan

<10 sec

AI

<5 sec

---

# 23. Backend Rules

Never duplicate logic.

Never expose secrets.

Never trust user input.

Never crash.

Always log errors.

Always return JSON.

Always validate.

Keep modules independent.

Keep functions small.

---

# 24. Future Scalability

Current

FastAPI

↓

SQLite

Future

FastAPI

↓

PostgreSQL

↓

Redis

↓

Docker

↓

Kubernetes

Architecture should allow scaling without rewriting modules.

---

# 25. Backend Development Order

1.

Health API

↓

2.

WHOIS

↓

3.

DNS

↓

4.

SSL

↓

5.

Headers

↓

6.

CT Logs

↓

7.

Email Security

↓

8.

IP Info

↓

9.

Risk Engine

↓

10.

Gemini

↓

11.

Database

↓

12.

PDF

---

END OF BACKEND SPECIFICATION
