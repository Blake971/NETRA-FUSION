# NETRA
# Module Specification

Version: 2.0

This document defines every module in NETRA.

Every module must follow the same architecture.

Every module must:

• Receive validated input

• Perform only one task

• Return standardized JSON

• Handle errors internally

• Never crash the application

• Never communicate directly with React

Only FastAPI communicates with modules.

---

# Standard Module Architecture

Every module follows:

Input → Validation → Data Collection → Data Parsing → Normalization → JSON Response

---

# JSON Format

```json
{
    "module": "",
    "status": "",
    "severity": "",
    "message": "",
    "execution_time": "",
    "data": {}
}
```

---

# MODULE 1: WHOIS

## Purpose

Retrieve domain registration information.

## Input

- Domain (Example: google.com)

## Protocol

WHOIS Protocol → WHOIS Server → Response

## Data Collected

- Registrar
- Creation Date
- Expiry Date
- Updated Date
- Name Servers
- Domain Status
- Registrar URL
- Country (if available)

## Workflow

Receive Domain → Validate Domain → WHOIS Request → Receive Response → Parse → Normalize → Return JSON

## Failure Cases

- Domain does not exist
- WHOIS timeout
- WHOIS blocked
- Invalid response

## Output Example

```json
{
    "registrar": "GoDaddy.com, LLC",
    "created": "2020-01-15",
    "expires": "2025-01-15",
    "nameservers": ["ns1.example.com", "ns2.example.com"],
    "status": "clientTransferProhibited"
}
```

## Difficulty

Easy

---

# MODULE 2: DNS

## Purpose

Retrieve DNS configuration.

## Input

- Domain

## Protocol

DNS

## Data

- A Record
- AAAA
- MX
- TXT
- NS
- SOA
- CNAME

## Workflow

Domain → DNS Resolver → Receive Records → Normalize → Return JSON

## Checks

- DNS Exists
- Mail Server
- TXT Records
- Email Security Records

## Failure Cases

- Timeout
- NXDOMAIN
- Resolver Failure

## Difficulty

Easy

---

# MODULE 3: SSL

## Purpose

Analyze HTTPS certificate.

## Input

- Domain

## Protocol

HTTPS (Port 443)

## Collect

- Issuer
- Subject
- Issued Date
- Expiry Date
- Algorithm
- TLS Version

## Workflow

Socket → SSL Handshake → Certificate → Parse → JSON

## Checks

- Expired
- Weak Algorithm
- Self Signed
- Days Remaining

## Failure Cases

- SSL Missing
- Handshake Failure
- Connection Timeout

## Difficulty

Easy

---

# MODULE 4: Security Headers

## Purpose

Inspect HTTP security headers.

## Request

HTTPS GET

## Headers

- HSTS
- Content Security Policy
- X Frame Options
- Referrer Policy
- Permissions Policy
- X Content Type Options

## Checks

- Header Exists
- Header Missing
- Header Misconfigured

## Workflow

Request → Read Headers → Compare → Return

## Difficulty

Easy

---

# MODULE 5: Certificate Transparency

## Purpose

Retrieve publicly logged certificates.

## Source

Public CT Servers

## Collect

- Certificate
- Subdomains
- Issue Date
- Expiry

## Workflow

Domain → CT Query → Certificates → Extract Subdomains → Return

## Checks

- Wildcard
- Duplicate
- Expired Certificates

## Difficulty

Medium

---

# MODULE 6: IP Intelligence

## Purpose

Retrieve hosting information.

## Collect

- IP
- Country
- City
- ASN
- ISP
- Organization
- Reverse DNS

## Workflow

Resolve Domain → IP → Public IP Information → Return

## Difficulty

Easy

---

# MODULE 7: Email Security

## Purpose

Check email authentication.

## Read

DNS TXT Records

## Find

- SPF
- DKIM
- DMARC

## Checks

- Present
- Missing
- Malformed

## Output

- SPF Status
- DKIM Status
- DMARC Status

## Difficulty

Medium

---

# MODULE 8: Risk Engine

## Purpose

Calculate security score.

## Rule

NO AI. Deterministic rules only.

## Scoring Rules

- Missing SSL: +40
- Missing CSP: +15
- Missing HSTS: +15
- Missing SPF: +15
- Expired Domain: +20
- No DMARC: +15

## Return

- Risk Score
- Risk Level
- Findings
- Recommendation Priority

## Difficulty

Medium

---

# MODULE 9: Gemini AI

## Purpose

Explain findings.

## Input

- WHOIS
- DNS
- SSL
- Headers
- Email
- Risk

## Gemini Generates

- Executive Summary
- Technical Summary
- Business Summary
- Recommendations
- Warnings

## Gemini NEVER

- Calculate Risk
- Identify Vulnerabilities
- Perform Analysis

## Difficulty

Easy

---

# MODULE 10: PDF Generator

## Purpose

Generate report.

## Sections

- Cover
- Executive Summary
- Risk Score
- WHOIS
- DNS
- SSL
- Headers
- Email
- Recommendations
- Charts
- Footer

## Output

PDF

## Difficulty

Easy

---

# MODULE 11: Google Dork Assistant

## Purpose

Generate search queries.

## Rules

- Never scrape Google
- Never automate searches

## Generate

- site:{domain}
- filetype:pdf
- inurl:login
- intitle:index of
- site:github.com
- site:pastebin.com

## Return

- Query
- Description
- Purpose

## Difficulty

Easy

---

# MODULE 12: Digital Footprint

## Purpose

Aggregate publicly available information.

## Input

- Name
- Email
- Domain

## Collect

- Public Websites
- GitHub
- News
- Public Profiles
- Public Repositories
- Public Mentions

## Future

- Image Search
- Academic Papers

## Return

- Summary
- Visibility
- Exposure Score

## Difficulty

Hard

---

# Execution Flow

User → Validation → WHOIS → DNS → SSL → Headers → CT Logs → IP → Email → Merge → Risk → Gemini → Database → Frontend → PDF

---

# Module Rules

Every module must be:

- Independent
- Reusable
- Testable
- Returns JSON
- No frontend logic
- No database logic
- No AI inside scanners
- One responsibility only

---

# Coding Rules

- Maximum 300 lines per module
- Split helpers into utils
- Document every public function
- Handle every exception
- Log execution time
- Never expose secrets
- Never terminate scan because one module failed

---

END OF MODULE SPECIFICATION
