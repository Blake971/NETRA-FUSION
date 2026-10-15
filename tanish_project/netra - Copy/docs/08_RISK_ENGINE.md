# NETRA
# Risk Engine Specification

> **Archived design specification.** This additive risk model is not the current Fusion score. Fusion starts at 100 and subtracts observed deductions; higher is better. See the [current guide](../../USER_GUIDE.md) and `backend/fusion_engine.py` for active behavior.

Version: 2.0

---

# 1. Risk Engine Overview

**Purpose**: Calculate a security risk score based on scan findings

**Type**: Deterministic algorithm (NO AI)

**Input**: Scan results from all modules

**Output**: Risk score (0-100), risk level, findings, recommendations

**Principle**: Risk calculation is based on predefined rules, not AI analysis

---

# 2. Risk Score Calculation

## 2.1 Score Range

- 0-25: Low Risk
- 26-50: Low-Medium Risk
- 51-75: Medium Risk
- 76-90: High Risk
- 91-100: Critical Risk

## 2.2 Base Score

Starting score: 0

Points are added for each security issue found.

Maximum possible score: 100

---

# 3. Scoring Rules

## 3.1 SSL Certificate Rules

### Rule ID: R001
**Condition**: SSL certificate is missing or invalid
**Severity**: Critical
**Weight**: +40
**Description**: No valid SSL certificate found
**Recommendation**: Install a valid SSL certificate immediately

### Rule ID: R002
**Condition**: SSL certificate is expired
**Severity**: Critical
**Weight**: +35
**Description**: SSL certificate has expired
**Recommendation**: Renew SSL certificate immediately

### Rule ID: R003
**Condition**: SSL certificate expiring within 7 days
**Severity**: High
**Weight**: +25
**Description**: SSL certificate expires soon
**Recommendation**: Renew SSL certificate within 7 days

### Rule ID: R004
**Condition**: SSL certificate expiring within 30 days
**Severity**: Medium
**Weight**: +15
**Description**: SSL certificate expiring soon
**Recommendation**: Plan SSL certificate renewal

### Rule ID: R005
**Condition**: Weak SSL/TLS protocol (SSLv2, SSLv3, TLS 1.0, TLS 1.1)
**Severity**: High
**Weight**: +20
**Description**: Using deprecated SSL/TLS protocol
**Recommendation**: Upgrade to TLS 1.2 or higher

### Rule ID: R006
**Condition**: Self-signed certificate
**Severity**: Medium
**Weight**: +15
**Description**: SSL certificate is self-signed
**Recommendation**: Use certificate from trusted CA

---

## 3.2 Security Headers Rules

### Rule ID: R007
**Condition**: Missing HSTS header
**Severity**: Medium
**Weight**: +15
**Description**: HTTP Strict Transport Security not configured
**Recommendation**: Implement HSTS header with max-age of at least 31536000

### Rule ID: R008
**Condition**: Missing Content Security Policy
**Severity**: High
**Weight**: +20
**Description**: Content Security Policy not configured
**Recommendation**: Implement Content Security Policy header

### Rule ID: R009
**Condition**: Missing X-Frame-Options
**Severity**: Medium
**Weight**: +10
**Description**: X-Frame-Options header not configured
**Recommendation**: Implement X-Frame-Options header

### Rule ID: R010
**Condition**: Missing X-Content-Type-Options
**Severity**: Low
**Weight**: +5
**Description**: X-Content-Type-Options header not configured
**Recommendation**: Implement X-Content-Type-Options: nosniff

### Rule ID: R011
**Condition**: Missing Referrer-Policy
**Severity**: Low
**Weight**: +5
**Description**: Referrer-Policy header not configured
**Recommendation**: Implement Referrer-Policy header

### Rule ID: R012
**Condition**: Missing Permissions-Policy
**Severity**: Low
**Weight**: +5
**Description**: Permissions-Policy header not configured
**Recommendation**: Implement Permissions-Policy header

---

## 3.3 DNS Configuration Rules

### Rule ID: R013
**Condition**: DNS resolution fails
**Severity**: Critical
**Weight**: +50
**Description**: Domain does not resolve
**Recommendation**: Check DNS configuration

### Rule ID: R014
**Condition**: No MX records found
**Severity**: Low
**Weight**: +5
**Description**: No mail exchange records configured
**Recommendation**: Configure MX records if email is needed

### Rule ID: R015
**Condition**: Missing SPF record
**Severity**: High
**Weight**: +15
**Description**: Sender Policy Framework not configured
**Recommendation**: Add SPF record to prevent email spoofing

### Rule ID: R016
**Condition**: Missing DMARC record
**Severity**: High
**Weight**: +15
**Description**: DMARC not configured
**Recommendation**: Add DMARC record for email authentication

### Rule ID: R017
**Condition**: SPF record is misconfigured
**Severity**: Medium
**Weight**: +10
**Description**: SPF record syntax error or too permissive
**Recommendation**: Review and fix SPF record configuration

### Rule ID: R018
**Condition**: DMARC policy is set to none
**Severity**: Medium
**Weight**: +10
**Description**: DMARC policy is not enforcing
**Recommendation**: Change DMARC policy to quarantine or reject

---

## 3.4 WHOIS Rules

### Rule ID: R019
**Condition**: Domain expiring within 30 days
**Severity**: High
**Weight**: +20
**Description**: Domain registration expiring soon
**Recommendation**: Renew domain registration immediately

### Rule ID: R020
**Condition**: Domain expired
**Severity**: Critical
**Weight**: +50
**Description**: Domain registration has expired
**Recommendation**: Renew domain registration immediately

### Rule ID: R021
**Condition**: Domain status shows clientHold or serverHold
**Severity**: Critical
**Weight**: +45
**Description**: Domain is on hold
**Recommendation**: Contact registrar to resolve hold status

---

## 3.5 IP Intelligence Rules

### Rule ID: R022
**Condition**: IP is from high-risk country
**Severity**: Medium
**Weight**: +10
**Description**: IP address from country with high cybercrime rate
**Recommendation**: Review hosting location and consider CDN

### Rule ID: R023
**Condition**: IP is listed in spam database
**Severity**: High
**Weight**: +25
**Description**: IP address is blacklisted
**Recommendation**: Investigate and request delisting

### Rule ID: R024
**Condition**: No reverse DNS configured
**Severity**: Low
**Weight**: +5
**Description**: Reverse DNS not configured
**Recommendation**: Configure reverse DNS for better email deliverability

---

## 3.6 Certificate Transparency Rules

### Rule ID: R025
**Condition**: No certificates found in CT logs
**Severity**: Low
**Weight**: +5
**Description**: No certificates in transparency logs
**Recommendation**: Ensure certificates are logged

### Rule ID: R026
**Condition**: Multiple certificates issued for same domain
**Severity**: Medium
**Weight**: +10
**Description**: Many certificates issued recently
**Recommendation**: Review certificate issuance history

### Rule ID: R027
**Condition**: Wildcard certificate detected
**Severity**: Low
**Weight**: +5
**Description**: Wildcard certificate in use
**Recommendation**: Ensure wildcard certificate is properly secured

---

# 4. Risk Level Determination

## 4.1 Level Calculation

Based on total score:

```python
def determine_risk_level(score: int) -> str:
    if score <= 25:
        return "low"
    elif score <= 50:
        return "low_medium"
    elif score <= 75:
        return "medium"
    elif score <= 90:
        return "high"
    else:
        return "critical"
```

## 4.2 Level Descriptions

**Low (0-25)**: Good security posture. Minor improvements possible.

**Low-Medium (26-50)**: Acceptable security with some improvements needed.

**Medium (51-75)**: Moderate security posture. Several improvements recommended.

**High (76-90)**: High-risk security issues found. Address as soon as possible.

**Critical (91-100)**: Critical security issues detected. Immediate action required.

---

# 5. Findings Structure

## 5.1 Finding Object

```json
{
  "rule_id": "R001",
  "severity": "critical",
  "weight": 40,
  "description": "SSL certificate is missing",
  "recommendation": "Install a valid SSL certificate immediately",
  "category": "ssl"
}
```

## 5.2 Categories

- ssl: SSL/TLS issues
- headers: HTTP security headers
- dns: DNS configuration
- whois: Domain registration
- email: Email security
- ip: IP intelligence
- ct: Certificate transparency

---

# 6. Implementation

## 6.1 Risk Engine Function

```python
def calculate_risk(scan_results: dict) -> dict:
    """
    Calculate risk score based on scan results.
    
    Args:
        scan_results: Dictionary containing results from all modules
    
    Returns:
        Dictionary with risk score, level, and findings
    """
    score = 0
    findings = []
    
    # SSL checks
    score, findings = check_ssl(scan_results.get('ssl'), score, findings)
    
    # Header checks
    score, findings = check_headers(scan_results.get('headers'), score, findings)
    
    # DNS checks
    score, findings = check_dns(scan_results.get('dns'), score, findings)
    
    # WHOIS checks
    score, findings = check_whois(scan_results.get('whois'), score, findings)
    
    # Email checks
    score, findings = check_email(scan_results.get('email'), score, findings)
    
    # IP checks
    score, findings = check_ip(scan_results.get('ip'), score, findings)
    
    # CT logs checks
    score, findings = check_ctlogs(scan_results.get('ctlogs'), score, findings)
    
    # Cap score at 100
    score = min(score, 100)
    
    # Determine risk level
    risk_level = determine_risk_level(score)
    
    return {
        "score": score,
        "level": risk_level,
        "findings": findings,
        "total_issues": len(findings)
    }
```

## 6.2 SSL Check Example

```python
def check_ssl(ssl_data: dict, score: int, findings: list) -> tuple:
    if not ssl_data:
        score += 40
        findings.append({
            "rule_id": "R001",
            "severity": "critical",
            "weight": 40,
            "description": "SSL certificate is missing",
            "recommendation": "Install a valid SSL certificate immediately",
            "category": "ssl"
        })
        return score, findings
    
    if ssl_data.get('valid') == False:
        score += 35
        findings.append({
            "rule_id": "R002",
            "severity": "critical",
            "weight": 35,
            "description": "SSL certificate has expired",
            "recommendation": "Renew SSL certificate immediately",
            "category": "ssl"
        })
    
    days_remaining = ssl_data.get('days_remaining', 0)
    if days_remaining <= 7:
        score += 25
        findings.append({
            "rule_id": "R003",
            "severity": "high",
            "weight": 25,
            "description": f"SSL certificate expires in {days_remaining} days",
            "recommendation": "Renew SSL certificate within 7 days",
            "category": "ssl"
        })
    elif days_remaining <= 30:
        score += 15
        findings.append({
            "rule_id": "R004",
            "severity": "medium",
            "weight": 15,
            "description": f"SSL certificate expires in {days_remaining} days",
            "recommendation": "Plan SSL certificate renewal",
            "category": "ssl"
        })
    
    return score, findings
```

---

# 7. Priority Recommendations

## 7.1 Priority Calculation

Findings are prioritized by:

1. Severity (Critical > High > Medium > Low)
2. Weight (Higher weight = higher priority)
3. Category (SSL and Headers typically higher priority)

## 7.2 Priority Output

```json
{
  "recommendations": [
    {
      "priority": "critical",
      "rule_id": "R001",
      "action": "Install SSL certificate",
      "reason": "No valid SSL certificate found"
    },
    {
      "priority": "high",
      "rule_id": "R007",
      "action": "Implement HSTS",
      "reason": "Missing HTTP Strict Transport Security"
    }
  ]
}
```

---

# 8. Testing

## 8.1 Unit Tests

```python
def test_risk_calculation():
    scan_data = {
        "ssl": {"valid": False},
        "headers": {"hsts": False, "csp": False},
        "dns": {"spf": None, "dmarc": None}
    }
    
    result = calculate_risk(scan_data)
    
    assert result["score"] > 0
    assert len(result["findings"]) > 0
    assert result["level"] in ["low", "low_medium", "medium", "high", "critical"]
```

## 8.2 Rule Tests

```python
def test_ssl_missing():
    result = check_ssl(None, 0, [])
    assert result[0] == 40
    assert len(result[1]) == 1
    assert result[1][0]["rule_id"] == "R001"
```

## 8.3 Edge Cases

```python
def test_empty_scan():
    result = calculate_risk({})
    assert result["score"] == 0
    assert result["level"] == "low"
    assert len(result["findings"]) == 0

def test_max_score():
    # Create scan with all critical issues
    scan_data = create_critical_scan()
    result = calculate_risk(scan_data)
    assert result["score"] <= 100
```

---

# 9. Configuration

## 9.1 Rule Weights Configuration

Rules and weights can be configured in:

```
backend/risk/config.json
```

```json
{
  "rules": {
    "R001": {
      "weight": 40,
      "severity": "critical",
      "enabled": true
    },
    "R002": {
      "weight": 35,
      "severity": "critical",
      "enabled": true
    }
  }
}
```

## 9.2 Custom Rules

New rules can be added by:

1. Adding rule definition to config
2. Implementing check function
3. Adding to main calculation function

---

# 10. Performance

## 10.1 Performance Goals

- Risk calculation: < 100ms
- Single rule check: < 10ms
- Total findings generation: < 50ms

## 10.2 Optimization

- Cache rule configurations
- Use early termination for critical scores
- Parallel rule checks where possible

---

# 11. Future Enhancements

## 11.1 Dynamic Weights

Future: Adjust weights based on:

- Industry standards
- Threat intelligence
- Historical data

## 11.2 Machine Learning (Future)

Future: Use ML to predict risk based on:

- Historical scan patterns
- Industry benchmarks
- Threat landscape changes

Note: This would be separate from the deterministic risk engine and used for additional insights only.

---

END OF RISK ENGINE SPECIFICATION
