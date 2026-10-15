# NETRA
# API Specification

Version: 2.0

---

# 1. API Overview

All APIs follow REST principles.

Base URL: `http://localhost:8000` (development)

Response Format: JSON

Authentication: None (current version)

Rate Limiting: Future feature

---

# 2. Standard Response Format

## Success Response

```json
{
  "success": true,
  "data": {}
}
```

## Error Response

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE"
}
```

## HTTP Status Codes

- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

---

# 3. Endpoints

## 3.1 Health Check

### GET /health

**Purpose**: Check if the API is running

**Authentication**: None

**Request**: None

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "2.0",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

**Errors**: None

---

## 3.2 Start Scan

### POST /scan

**Purpose**: Start a new domain security scan

**Authentication**: None

**Request Body**:
```json
{
  "domain": "example.com",
  "options": {
    "include_subdomains": true,
    "include_email_security": true,
    "include_ct_logs": true
  }
}
```

**Validation**:
- domain: Required, string, valid domain format (RFC compliant)
- options: Optional, object

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "scan_id": "uuid-string",
    "domain": "example.com",
    "status": "in_progress",
    "estimated_time": 10
  }
}
```

**Response** (400 Bad Request):
```json
{
  "success": false,
  "message": "Invalid domain format",
  "error_code": "INVALID_DOMAIN"
}
```

**Errors**:
- INVALID_DOMAIN: Domain format is invalid
- SCAN_IN_PROGRESS: A scan is already in progress for this domain

---

## 3.3 Get Scan Status

### GET /scan/{scan_id}

**Purpose**: Get the status of a running or completed scan

**Authentication**: None

**Parameters**:
- scan_id (path): UUID of the scan

**Response** (200 OK - In Progress):
```json
{
  "success": true,
  "data": {
    "scan_id": "uuid-string",
    "domain": "example.com",
    "status": "in_progress",
    "progress": 60,
    "current_module": "SSL",
    "modules": {
      "whois": {
        "status": "completed",
        "execution_time": 1.2
      },
      "dns": {
        "status": "completed",
        "execution_time": 0.8
      },
      "ssl": {
        "status": "running",
        "execution_time": null
      },
      "headers": {
        "status": "pending",
        "execution_time": null
      }
    }
  }
}
```

**Response** (200 OK - Completed):
```json
{
  "success": true,
  "data": {
    "scan_id": "uuid-string",
    "domain": "example.com",
    "status": "completed",
    "progress": 100,
    "execution_time": 8.5,
    "risk_score": 65,
    "risk_level": "medium",
    "modules": {
      "whois": {
        "status": "completed",
        "execution_time": 1.2,
        "data": {
          "registrar": "GoDaddy.com, LLC",
          "created": "2020-01-15",
          "expires": "2025-01-15"
        }
      },
      "dns": {
        "status": "completed",
        "execution_time": 0.8,
        "data": {
          "a_records": ["93.184.216.34"],
          "mx_records": ["mail.example.com"]
        }
      },
      "ssl": {
        "status": "completed",
        "execution_time": 1.5,
        "data": {
          "issuer": "Let's Encrypt",
          "valid": true,
          "expires": "2024-06-15"
        }
      },
      "headers": {
        "status": "completed",
        "execution_time": 0.5,
        "data": {
          "hsts": true,
          "csp": false,
          "x_frame_options": true
        }
      }
    },
    "ai_summary": {
      "executive_summary": "The domain has a moderate security posture...",
      "recommendations": [
        "Implement Content Security Policy",
        "Configure DMARC for email security"
      ]
    }
  }
}
```

**Response** (404 Not Found):
```json
{
  "success": false,
  "message": "Scan not found",
  "error_code": "SCAN_NOT_FOUND"
}
```

**Errors**:
- SCAN_NOT_FOUND: Scan ID does not exist

---

## 3.4 Get Scan History

### GET /history

**Purpose**: Get list of all completed scans

**Authentication**: None

**Query Parameters**:
- limit (optional): Number of results (default: 20, max: 100)
- offset (optional): Pagination offset (default: 0)
- sort_by (optional): Field to sort by (default: created_at)
- order (optional): Sort order (asc/desc, default: desc)

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "total": 45,
    "limit": 20,
    "offset": 0,
    "scans": [
      {
        "scan_id": "uuid-string",
        "domain": "example.com",
        "risk_score": 65,
        "risk_level": "medium",
        "created_at": "2024-01-15T10:30:00Z",
        "status": "completed"
      },
      {
        "scan_id": "uuid-string-2",
        "domain": "test.com",
        "risk_score": 25,
        "risk_level": "low",
        "created_at": "2024-01-14T15:20:00Z",
        "status": "completed"
      }
    ]
  }
}
```

**Errors**: None

---

## 3.5 Get Report

### GET /report/{scan_id}

**Purpose**: Get the PDF report for a completed scan

**Authentication**: None

**Parameters**:
- scan_id (path): UUID of the scan

**Response** (200 OK):
- Returns PDF file as binary data
- Content-Type: application/pdf
- Content-Disposition: attachment; filename="netra_report_example.com.pdf"

**Response** (404 Not Found):
```json
{
  "success": false,
  "message": "Report not found",
  "error_code": "REPORT_NOT_FOUND"
}
```

**Response** (400 Bad Request):
```json
{
  "success": false,
  "message": "Scan not completed yet",
  "error_code": "SCAN_NOT_COMPLETED"
}
```

**Errors**:
- REPORT_NOT_FOUND: Report does not exist
- SCAN_NOT_COMPLETED: Scan is still in progress

---

## 3.6 Generate Report

### POST /generate-report

**Purpose**: Generate a PDF report for a completed scan

**Authentication**: None

**Request Body**:
```json
{
  "scan_id": "uuid-string",
  "options": {
    "include_ai_summary": true,
    "include_recommendations": true,
    "include_charts": true
  }
}
```

**Validation**:
- scan_id: Required, string, valid UUID
- options: Optional, object

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "report_id": "uuid-string",
    "scan_id": "uuid-string",
    "status": "generating",
    "estimated_time": 5
  }
}
```

**Response** (400 Bad Request):
```json
{
  "success": false,
  "message": "Scan not completed yet",
  "error_code": "SCAN_NOT_COMPLETED"
}
```

**Errors**:
- SCAN_NOT_COMPLETED: Scan is still in progress
- REPORT_ALREADY_EXISTS: Report already generated for this scan

---

## 3.7 Google Dork Queries

### POST /dork

**Purpose**: Generate Google dork search queries for a domain

**Authentication**: None

**Request Body**:
```json
{
  "domain": "example.com",
  "query_types": [
    "file_search",
    "login_pages",
    "directory_listings",
    "github",
    "pastebin"
  ]
}
```

**Validation**:
- domain: Required, string, valid domain format
- query_types: Optional, array of strings

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "domain": "example.com",
    "queries": [
      {
        "query": "site:example.com filetype:pdf",
        "description": "Find PDF files on the domain",
        "purpose": "Document discovery"
      },
      {
        "query": "site:example.com inurl:login",
        "description": "Find login pages",
        "purpose": "Authentication endpoint discovery"
      },
      {
        "query": "site:example.com intitle:\"index of\"",
        "description": "Find directory listings",
        "purpose": "Exposed directory discovery"
      },
      {
        "query": "site:github.com example.com",
        "description": "Find GitHub repositories",
        "purpose": "Source code discovery"
      },
      {
        "query": "site:pastebin.com example.com",
        "description": "Find pastes on Pastebin",
        "purpose": "Leaked information discovery"
      }
    ]
  }
}
```

**Response** (400 Bad Request):
```json
{
  "success": false,
  "message": "Invalid domain format",
  "error_code": "INVALID_DOMAIN"
}
```

**Errors**:
- INVALID_DOMAIN: Domain format is invalid

---

## 3.8 Digital Footprint

### POST /footprint

**Purpose**: Search for digital footprint of a person or organization

**Authentication**: None

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "domain": "example.com"
}
```

**Validation**:
- At least one field is required
- name: Optional, string
- email: Optional, string, valid email format
- domain: Optional, string, valid domain format

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "exposure_score": 75,
    "visibility_level": "high",
    "findings": {
      "public_websites": [
        "example.com",
        "blog.example.com"
      ],
      "github_repositories": [
        "github.com/johndoe/project1",
        "github.com/johndoe/project2"
      ],
      "news_mentions": [
        "TechNews - Interview with John Doe"
      ],
      "public_profiles": [
        "linkedin.com/in/johndoe",
        "twitter.com/johndoe"
      ],
      "social_media": [
        "facebook.com/johndoe",
        "instagram.com/johndoe"
      ]
    },
    "summary": "High digital footprint with multiple public profiles and repositories"
  }
}
```

**Response** (400 Bad Request):
```json
{
  "success": false,
  "message": "At least one search parameter is required",
  "error_code": "NO_SEARCH_PARAMS"
}
```

**Errors**:
- NO_SEARCH_PARAMS: No search parameters provided
- INVALID_EMAIL: Email format is invalid
- INVALID_DOMAIN: Domain format is invalid

---

## 3.9 Delete Scan

### DELETE /scan/{scan_id}

**Purpose**: Delete a scan from history

**Authentication**: None

**Parameters**:
- scan_id (path): UUID of the scan

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "message": "Scan deleted successfully",
    "scan_id": "uuid-string"
  }
}
```

**Response** (404 Not Found):
```json
{
  "success": false,
  "message": "Scan not found",
  "error_code": "SCAN_NOT_FOUND"
}
```

**Errors**:
- SCAN_NOT_FOUND: Scan ID does not exist

---

## 3.10 Get Statistics

### GET /stats

**Purpose**: Get overall statistics about scans

**Authentication**: None

**Query Parameters**: None

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "total_scans": 150,
    "high_risk_count": 25,
    "medium_risk_count": 60,
    "low_risk_count": 65,
    "average_risk_score": 45,
    "scans_this_week": 12,
    "scans_this_month": 45,
    "most_scanned_domains": [
      "example.com",
      "test.com",
      "demo.com"
    ]
  }
}
```

**Errors**: None

---

# 4. Error Codes

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| INVALID_DOMAIN | Domain format is invalid | 400 |
| INVALID_EMAIL | Email format is invalid | 400 |
| SCAN_NOT_FOUND | Scan ID does not exist | 404 |
| REPORT_NOT_FOUND | Report does not exist | 404 |
| SCAN_NOT_COMPLETED | Scan is still in progress | 400 |
| REPORT_ALREADY_EXISTS | Report already generated | 400 |
| SCAN_IN_PROGRESS | Scan already in progress | 400 |
| NO_SEARCH_PARAMS | No search parameters provided | 400 |
| INTERNAL_ERROR | Internal server error | 500 |
| TIMEOUT | Request timeout | 500 |

---

# 5. Rate Limiting (Future)

Current: No rate limiting

Future Implementation:

- 100 requests per minute per IP
- 1000 requests per hour per IP
- Response headers:
  - X-RateLimit-Limit: 100
  - X-RateLimit-Remaining: 95
  - X-RateLimit-Reset: 1642230000

Rate Limit Exceeded Response (429):
```json
{
  "success": false,
  "message": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

---

# 6. CORS Configuration

**Allowed Origins**: 
- http://localhost:3000 (development)
- https://netra.vercel.app (production)

**Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS

**Allowed Headers**: Content-Type, Authorization

**Max Age**: 3600 seconds

---

# 7. API Versioning

Current Version: v2.0

Version in URL: Not used (current version)

Future: `/api/v2/scan` for versioned endpoints

---

# 8. Webhooks (Future)

Future Implementation:

- POST /webhooks
- GET /webhooks
- DELETE /webhooks/{id}

Events:
- scan.completed
- scan.failed
- report.generated

---

END OF API SPECIFICATION
