# NETRA
# AI Specification

Version: 2.0

---

# 1. AI Overview

**AI Provider**: Google Gemini API

**Purpose**: Explain security findings in human-readable language

**Role**: Assistant, NOT analyst

**Key Principle**: AI never performs security analysis. AI only explains findings.

---

# 2. AI Responsibilities

## What AI DOES

- Summarize scan results
- Explain technical findings in simple language
- Generate recommendations
- Create executive summaries
- Provide business context
- Translate technical terms

## What AI DOES NOT DO

- Calculate risk scores
- Identify vulnerabilities
- Perform security analysis
- Make security determinations
- Access external systems
- Execute code

---

# 3. Configuration

## 3.1 API Configuration

**API Key**: Stored in environment variable `GEMINI_API_KEY`

**Model**: gemini-pro

**Temperature**: 0.7 (balanced creativity and reliability)

**Max Tokens**: 2048

**Timeout**: 30 seconds

**Retry**: 3 attempts with exponential backoff

## 3.2 Safety Settings

```python
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]
```

---

# 4. Prompts

## 4.1 System Prompt

```
You are NETRA, an AI assistant for a cybersecurity platform. Your role is to explain security scan results in clear, simple language.

You must:
- Explain technical findings in non-technical terms
- Provide actionable recommendations
- Prioritize issues by severity
- Use clear, concise language
- Avoid jargon when possible
- Never calculate risk scores (that's done by our risk engine)
- Never perform security analysis
- Only explain the data provided to you

Your audience includes:
- Students
- Small business owners
- Website administrators
- Non-technical users

Tone: Professional, helpful, educational, not alarmist.
```

## 4.2 Executive Summary Prompt

**Input**: All scan results (WHOIS, DNS, SSL, Headers, Email, Risk Score)

**Prompt Template**:
```
Generate an executive summary for the following domain security scan:

Domain: {domain}
Risk Score: {risk_score} / 100
Risk Level: {risk_level}

WHOIS Data:
{whois_json}

DNS Data:
{dns_json}

SSL Data:
{ssl_json}

Headers Data:
{headers_json}

Email Security Data:
{email_json}

IP Data:
{ip_json}

Generate a 3-4 sentence executive summary that:
1. States the overall security posture
2. Highlights the most critical issues
3. Provides a general recommendation

Keep it concise and non-technical.
```

**Expected Output**:
```json
{
  "executive_summary": "example.com has a moderate security posture with several areas requiring attention. The SSL certificate is valid and properly configured, but email security is missing SPF and DMARC records. Priority should be given to implementing email authentication to prevent spoofing attacks."
}
```

## 4.3 Technical Summary Prompt

**Input**: All scan results

**Prompt Template**:
```
Generate a technical summary for the following domain security scan:

Domain: {domain}
Risk Score: {risk_score} / 100

Module Results:
WHOIS: {whois_summary}
DNS: {dns_summary}
SSL: {ssl_summary}
Headers: {headers_summary}
Email: {email_summary}
IP: {ip_summary}

Provide a technical summary that:
1. Lists all findings by module
2. Explains what each finding means
3. Identifies configuration issues
4. Notes any anomalies

Use technical terminology appropriately.
```

**Expected Output**:
```json
{
  "technical_summary": {
    "whois": "Domain registered with GoDaddy, expires in 180 days. Nameservers are properly configured.",
    "dns": "A records resolve correctly. MX records present for mail delivery. SPF record is missing.",
    "ssl": "Certificate issued by Let's Encrypt, valid for 89 days. TLS 1.3 supported.",
    "headers": "HSTS is configured with max-age of 31536000. Content Security Policy is missing.",
    "email": "SPF record not found. DMARC record not found. DKIM configuration unknown.",
    "ip": "Hosted on AWS (us-east-1). Reverse DNS configured."
  }
}
```

## 4.4 Business Summary Prompt

**Input**: All scan results

**Prompt Template**:
```
Generate a business impact summary for the following domain security scan:

Domain: {domain}
Risk Score: {risk_score} / 100
Risk Level: {risk_level}

Key Findings:
{critical_findings}

Explain the business impact of these findings:
1. What are the risks to the business?
2. How could this affect customers?
3. What are the compliance implications?
4. What is the potential financial impact?

Focus on business consequences, not technical details.
```

**Expected Output**:
```json
{
  "business_summary": {
    "customer_trust": "Missing email security could lead to phishing attacks that damage customer trust.",
    "compliance": "Lack of proper security headers may not meet GDPR requirements for data protection.",
    "reputation": "Expired SSL certificates would cause browser warnings, damaging brand reputation.",
    "financial": "Security incidents could result in regulatory fines and customer loss."
  }
}
```

## 4.5 Recommendations Prompt

**Input**: All scan results, prioritized by risk engine

**Prompt Template**:
```
Generate prioritized recommendations based on the following security scan:

Domain: {domain}
Risk Score: {risk_score} / 100

Findings by Priority:
{prioritized_findings}

For each finding, provide:
1. A clear recommendation
2. Why it matters
3. How to fix it (brief)
4. Estimated difficulty (Easy/Medium/Hard)
5. Priority level (Critical/High/Medium/Low)

Format as a numbered list.
```

**Expected Output**:
```json
{
  "recommendations": [
    {
      "id": 1,
      "issue": "Missing SPF Record",
      "recommendation": "Add an SPF record to your DNS configuration",
      "why": "Prevents email spoofing and improves email deliverability",
      "how": "Add TXT record: v=spf1 include:_spf.google.com ~all",
      "difficulty": "Easy",
      "priority": "High"
    },
    {
      "id": 2,
      "issue": "Missing Content Security Policy",
      "recommendation": "Implement a Content Security Policy header",
      "why": "Prevents XSS attacks and data injection",
      "how": "Add header: Content-Security-Policy: default-src 'self'",
      "difficulty": "Medium",
      "priority": "High"
    }
  ]
}
```

## 4.6 Warnings Prompt

**Input**: Critical findings

**Prompt Template**:
```
Generate urgent warnings for the following critical security issues:

Domain: {domain}

Critical Issues:
{critical_issues}

Generate warnings that:
1. Are clear and actionable
2. Explain the immediate risk
3. Recommend immediate action
4. Use urgent but not alarmist language

Only include truly critical issues that require immediate attention.
```

**Expected Output**:
```json
{
  "warnings": [
    {
      "issue": "SSL Certificate Expiring Soon",
      "message": "Your SSL certificate expires in 7 days. This will cause browser warnings and security errors.",
      "action": "Renew the certificate immediately to prevent service disruption."
    },
    {
      "issue": "Domain Expiring Soon",
      "message": "Your domain registration expires in 30 days. Failure to renew will result in service loss.",
      "action": "Renew domain registration immediately."
    }
  ]
}
```

---

# 5. Input Data Structure

## 5.1 Complete Scan Input

```json
{
  "domain": "example.com",
  "risk_score": 65,
  "risk_level": "medium",
  "whois": {
    "registrar": "GoDaddy.com, LLC",
    "created": "2020-01-15",
    "expires": "2025-01-15",
    "status": "clientTransferProhibited"
  },
  "dns": {
    "a_records": ["93.184.216.34"],
    "mx_records": ["mail.example.com"],
    "ns_records": ["ns1.example.com"],
    "spf": null,
    "dmarc": null
  },
  "ssl": {
    "valid": true,
    "issuer": "Let's Encrypt",
    "expires": "2024-06-15",
    "days_remaining": 89,
    "protocol": "TLS 1.3"
  },
  "headers": {
    "hsts": true,
    "csp": false,
    "x_frame_options": true,
    "x_content_type_options": true
  },
  "email": {
    "spf": "missing",
    "dkim": "unknown",
    "dmarc": "missing"
  },
  "ip": {
    "ip": "93.184.216.34",
    "country": "United States",
    "isp": "Example ISP",
    "asn": "AS15169"
  }
}
```

---

# 6. Output Structure

## 6.1 Complete AI Response

```json
{
  "executive_summary": "string",
  "technical_summary": {
    "whois": "string",
    "dns": "string",
    "ssl": "string",
    "headers": "string",
    "email": "string",
    "ip": "string"
  },
  "business_summary": {
    "customer_trust": "string",
    "compliance": "string",
    "reputation": "string",
    "financial": "string"
  },
  "recommendations": [
    {
      "id": 1,
      "issue": "string",
      "recommendation": "string",
      "why": "string",
      "how": "string",
      "difficulty": "Easy|Medium|Hard",
      "priority": "Critical|High|Medium|Low"
    }
  ],
  "warnings": [
    {
      "issue": "string",
      "message": "string",
      "action": "string"
    }
  ]
}
```

---

# 7. Error Handling

## 7.1 API Errors

**Timeout**:
- Retry 3 times with exponential backoff
- Return cached summary if available
- Fall back to template-based summary

**Rate Limit**:
- Implement exponential backoff
- Queue requests if rate limit exceeded
- Return error message to user

**Invalid Response**:
- Validate response structure
- Log error details
- Return fallback summary

## 7.2 Fallback Strategy

If AI fails, use template-based summaries:

```python
def generate_fallback_summary(scan_data):
    risk_level = scan_data["risk_level"]
    
    if risk_level == "critical":
        return "Critical security issues detected. Immediate action required."
    elif risk_level == "high":
        return "High-risk security issues found. Address as soon as possible."
    elif risk_level == "medium":
        return "Moderate security posture. Several improvements recommended."
    else:
        return "Good security posture. Minor improvements possible."
```

---

# 8. Performance

## 8.1 Caching

- Cache AI responses for 24 hours
- Use domain + risk_score as cache key
- Invalidate cache when new scan is performed

## 8.2 Async Processing

- Run AI generation asynchronously
- Don't block scan completion
- Return scan results immediately
- AI summary available via separate endpoint

---

# 9. Cost Management

## 9.1 Token Estimation

- Executive summary: ~200 tokens
- Technical summary: ~300 tokens
- Business summary: ~250 tokens
- Recommendations: ~400 tokens
- Warnings: ~150 tokens
- Total per scan: ~1300 tokens

## 9.2 Cost Control

- Implement daily token limit
- Cache responses to reduce API calls
- Use smaller model for simple summaries
- Batch requests when possible

---

# 10. Testing

## 10.1 Unit Tests

```python
def test_ai_summary_generation():
    scan_data = load_test_scan_data()
    summary = generate_ai_summary(scan_data)
    
    assert "executive_summary" in summary
    assert "recommendations" in summary
    assert len(summary["recommendations"]) > 0
```

## 10.2 Integration Tests

```python
def test_ai_integration():
    response = gemini.generate_content(prompt)
    
    assert response.text is not None
    assert len(response.text) > 0
```

## 10.3 Mock Testing

```python
def test_with_mock_ai():
    with patch('ai.gemini.generate_content') as mock:
        mock.return_value = Mock(text="Mocked response")
        result = generate_ai_summary(test_data)
        assert result == "Mocked response"
```

---

# 11. Monitoring

## 11.1 Metrics to Track

- API call success rate
- Average response time
- Token usage per scan
- Error rate by error type
- Cache hit rate

## 11.2 Alerts

- Alert if success rate < 95%
- Alert if response time > 10 seconds
- Alert if token usage exceeds budget

---

END OF AI SPECIFICATION
