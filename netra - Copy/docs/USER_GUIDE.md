# NETRA User Guide

**AI-Powered Digital Footprint & Security Assessment Platform**

---

## Table of Contents

1. [What is NETRA?](#what-is-netra)
2. [How to Use NETRA](#how-to-use-netra)
3. [Understanding Your Results](#understanding-your-results)
4. [Security Checks Explained](#security-checks-explained)
5. [FAQ](#faq)
6. [Troubleshooting](#troubleshooting)

---

## What is NETRA?

NETRA is a web-based security assessment tool that helps you check the security posture of any website. It analyzes publicly available information about a domain and provides you with:

- **Security Score** - An overall risk rating (0-100)
- **Detailed Findings** - Specific security issues detected
- **Recommendations** - Actionable steps to improve security
- **AI-Powered Explanations** - Simple language explanations of technical findings

### Key Features

✅ **Fast** - Results in seconds  
✅ **Easy** - No technical knowledge required  
✅ **Safe** - Passive analysis only, no active attacks  
✅ **Free** - No registration required  
✅ **Comprehensive** - Checks multiple security aspects  

---

## How to Use NETRA

### Step 1: Open NETRA

Navigate to the NETRA website in your browser.

### Step 2: Enter a Domain

In the search box on the homepage, type any website domain. Examples:
- `example.com`
- `google.com`
- `your-website.com`

### Step 3: Click "Scan Now"

Click the blue "Scan Now" button to start the analysis.

### Step 4: Wait for Results

The scan typically takes 10-30 seconds. You'll see a loading indicator while NETRA analyzes the domain.

### Step 5: Review Your Results

Once complete, you'll see:
- Overall security score
- Risk level (Low, Medium, High, Critical)
- Detailed findings by category
- Recommendations for improvement

---

## Understanding Your Results

### Security Score

NETRA calculates a security score from 0 to 100:

- **0-25 (Low Risk)**: Good security posture
- **26-50 (Low-Medium Risk)**: Acceptable with some improvements needed
- **51-75 (Medium Risk)**: Moderate security, several improvements recommended
- **76-90 (High Risk)**: High-risk issues found, address soon
- **91-100 (Critical Risk)**: Critical issues, immediate action required

### Risk Level

The risk level gives you a quick assessment:
- 🟢 **Low** - Your website is secure
- 🟡 **Medium** - Some improvements needed
- 🟠 **High** - Important security issues
- 🔴 **Critical** - Urgent action required

### Findings

Each finding includes:
- **What was found** - Description of the issue
- **Why it matters** - Explanation of the security impact
- **How to fix it** - Specific steps to resolve
- **Priority** - How urgent the fix is

---

## Security Checks Explained

### 1. WHOIS Analysis 🔍

**What it checks:**
- Domain registration information
- Registrar details
- Domain expiration date
- Registration status

**Why it matters:**
- Ensures your domain is properly registered
- Alerts you to upcoming expiration
- Verifies domain ownership

**Common issues:**
- Domain expiring soon - Renew your registration
- Invalid registrar info - Update with your registrar

---

### 2. DNS Configuration 🌐

**What it checks:**
- A records (domain to IP mapping)
- MX records (email servers)
- NS records (name servers)
- TXT records (text information)

**Why it matters:**
- Ensures your website is accessible
- Verifies email delivery works
- Confirms DNS is properly configured

**Common issues:**
- Missing MX records - Configure email servers
- Incorrect A records - Update with your hosting provider

---

### 3. SSL Certificate 🔒

**What it checks:**
- SSL/TLS certificate validity
- Certificate expiration date
- Encryption protocol (TLS version)
- Certificate issuer

**Why it matters:**
- Protects data in transit
- Prevents man-in-the-middle attacks
- Required for HTTPS

**Common issues:**
- Expired certificate - Renew immediately
- Weak encryption - Upgrade to TLS 1.2+

---

### 4. Security Headers 🛡️

**What it checks:**
- HSTS (HTTP Strict Transport Security)
- CSP (Content Security Policy)
- X-Frame-Options
- X-Content-Type-Options

**Why it matters:**
- Protects against XSS attacks
- Prevents clickjacking
- Enforces HTTPS

**Common issues:**
- Missing HSTS - Add to your web server config
- Missing CSP - Implement content security policy

---

### 5. Email Security 📧

**What it checks:**
- SPF (Sender Policy Framework)
- DKIM (DomainKeys Identified Mail)
- DMARC (Domain-based Message Authentication)

**Why it matters:**
- Prevents email spoofing
- Improves email deliverability
- Protects your brand reputation

**Common issues:**
- Missing SPF - Add SPF record to DNS
- Missing DMARC - Configure DMARC policy

---

### 6. AI-Powered Reports 🤖

**What it provides:**
- Simple language explanations
- Executive summaries
- Business impact analysis
- Prioritized recommendatons

**Why it matters:**
- Makes technical findings understandable
- Helps non-technical users
- Provides actionable insights

---

## FAQ

### Is NETRA safe to use?

Yes, NETRA is completely safe. It only analyzes publicly available information and performs no active attacks on your website. It's a passive security assessment tool.

### Do I need to be technical to use NETRA?

Not at all. NETRA is designed for everyone. Simply enter a domain and get easy-to-understand results with clear recommendations.

### How long does a scan take?

Most scans complete within 10-30 seconds, depending on the domain and network conditions.

### What happens with my scan data?

Your scan results are stored securely and are only used to provide you with the security assessment. We do not share your data with third parties.

### Can I scan any website?

Yes, you can scan any publicly accessible website. However, you should only scan websites you own or have permission to assess.

### What if I find security issues?

NETRA provides specific recommendations for each issue found. Follow the "How to fix" instructions in your results, or consult with a security professional for assistance.

### Is NETRA free?

Yes, NETRA is free to use. No registration or payment is required.

### Can I download my results?

Yes, you can download a detailed PDF report of your security assessment.

---

## Troubleshooting

### Scan failed to complete

**Possible causes:**
- The website is down
- Network connectivity issues
- The domain doesn't exist

**Solution:**
- Check if the website is accessible in your browser
- Try again after a few minutes
- Verify the domain name is correct

### Results seem incorrect

**Possible causes:**
- DNS propagation delay
- CDN caching
- Temporary server issues

**Solution:**
- Wait a few minutes and rescan
- Clear your browser cache
- Contact support if issues persist

### Can't access NETRA

**Possible causes:**
- Server maintenance
- Network issues
- Browser compatibility

**Solution:**
- Check your internet connection
- Try a different browser
- Check if the service is operational

---

## Getting Help

If you need additional help:

1. Check this user guide
2. Review the FAQ section
3. Contact support through the website

---

## Security Best Practices

Based on NETRA assessments, here are general security best practices:

1. **Keep SSL certificates current** - Renew before expiration
2. **Implement security headers** - Add HSTS, CSP, and others
3. **Configure email security** - Set up SPF, DKIM, and DMARC
4. **Monitor DNS regularly** - Ensure records are correct
5. **Keep software updated** - Apply security patches promptly
6. **Use strong passwords** - For all accounts and services
7. **Enable two-factor authentication** - Wherever possible

---

## Disclaimer

NETRA is provided for educational and informational purposes only. Security assessments are based on publicly available information at the time of scanning. Always consult with a qualified security professional for comprehensive security audits.

---

**Last Updated:** August 2024  
**Version:** 2.0
