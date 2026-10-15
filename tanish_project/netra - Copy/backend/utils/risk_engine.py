"""
Risk Scoring Engine for NETRA
Calculates overall security risk score based on scan results
"""

from typing import Dict, Any
from utils.logger import setup_logger


def calculate_risk_score(scan_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate overall risk score based on scan results.
    
    Args:
        scan_results: Dictionary containing results from all scanners
    
    Returns:
        Dictionary with risk score, level, and breakdown
    """
    logger = setup_logger()
    
    # Initialize scores
    total_score = 100
    deductions = []
    
    # SSL Risk Assessment (30 points max)
    ssl_result = scan_results.get('ssl', {})
    # Only evaluate SSL if scan succeeded - scanner errors should not affect risk score
    if ssl_result.get('status') in ['SUCCESS', 'PARTIAL']:
        ssl_data = ssl_result.get('data', {})
        
        # Check if SSL is valid
        if not ssl_data.get('valid', True):
            total_score -= 25
            deductions.append({
                'finding': 'Invalid SSL certificate',
                'status': 'DETECTED',
                'severity': 'HIGH',
                'evidence': f"Certificate validity: {ssl_data.get('valid')}",
                'explanation': 'SSL certificate is invalid - data is not encrypted securely',
                'recommendation': 'Install a valid SSL certificate from a trusted certificate authority',
                'score_impact': -25,
                'confidence': ssl_result.get('confidence', 95),
                'category': 'SSL Certificate'
            })
        
        # Check SSL expiration
        days_remaining = ssl_data.get('days_remaining', 365)
        if days_remaining < 7:
            total_score -= 20
            deductions.append({
                'finding': 'SSL certificate expiring very soon',
                'status': 'DETECTED',
                'severity': 'CRITICAL',
                'evidence': f"Days remaining: {days_remaining}",
                'explanation': f'SSL certificate expires in {days_remaining} days - renew immediately',
                'recommendation': 'Renew the SSL certificate immediately to avoid service disruption',
                'score_impact': -20,
                'confidence': ssl_result.get('confidence', 95),
                'category': 'SSL Certificate'
            })
        elif days_remaining < 30:
            total_score -= 10
            deductions.append({
                'finding': 'SSL certificate expiring soon',
                'status': 'DETECTED',
                'severity': 'MEDIUM',
                'evidence': f"Days remaining: {days_remaining}",
                'explanation': f'SSL certificate expires in {days_remaining} days - plan to renew soon',
                'recommendation': 'Plan to renew the SSL certificate within the next 30 days',
                'score_impact': -10,
                'confidence': ssl_result.get('confidence', 95),
                'category': 'SSL Certificate'
            })
        
        # Check protocol version
        protocol = ssl_data.get('protocol', '')
        if 'SSLv2' in protocol or 'SSLv3' in protocol:
            total_score -= 15
            deductions.append({
                'finding': 'Outdated SSL protocol in use',
                'status': 'DETECTED',
                'severity': 'HIGH',
                'evidence': f"Protocol: {protocol}",
                'explanation': 'Using outdated SSL protocol - upgrade to TLS 1.2 or higher',
                'recommendation': 'Configure the server to use TLS 1.2 or higher',
                'score_impact': -15,
                'confidence': ssl_result.get('confidence', 95),
                'category': 'SSL Certificate'
            })
    # If status is FAILED, PARTIAL, or UNKNOWN, do not deduct points - this is a scanner error
    
    # Security Headers Risk Assessment (25 points max)
    headers_result = scan_results.get('headers', {})
    # Only evaluate headers if scan succeeded - scanner errors should not affect risk score
    if headers_result.get('status') in ['SUCCESS', 'PARTIAL']:
        headers_data = headers_result.get('data', {})
        
        # Check critical headers - only deduct points for CRITICAL missing headers (HSTS, CSP)
        # Missing headers are informational, not security vulnerabilities
        critical_headers = {
            'hsts': 'HSTS (HTTPS Enforcement)',
            'csp': 'CSP (Content Security Policy)'
        }
        
        missing_critical_headers = []
        for key, name in critical_headers.items():
            # Handle new header structure with status/value
            if isinstance(headers_data.get(key), dict):
                header_info = headers_data.get(key, {})
                if header_info.get('status') == 'MISSING':
                    missing_critical_headers.append(name)
                    total_score -= 5
            elif not headers_data.get(key):
                # Backward compatibility for old boolean structure
                missing_critical_headers.append(name)
                total_score -= 5
        
        if missing_critical_headers:
            deductions.append({
                'finding': f'Missing {len(missing_critical_headers)} critical security headers',
                'status': 'DETECTED',
                'severity': 'MEDIUM' if len(missing_critical_headers) == 1 else 'HIGH',
                'evidence': f"Missing headers: {', '.join(missing_critical_headers)}",
                'explanation': f'Missing critical security headers: {", ".join(missing_critical_headers)} - these provide important security protections',
                'recommendation': 'Implement HSTS and CSP headers to enhance security',
                'score_impact': -5 * len(missing_critical_headers),
                'confidence': headers_result.get('confidence', 90),
                'category': 'Security Headers'
            })
    # If status is FAILED, PARTIAL, or UNKNOWN, do not deduct points - this is a scanner error
    
    # DNS Risk Assessment (20 points max)
    dns_result = scan_results.get('dns', {})
    # Only evaluate DNS if scan succeeded - scanner errors should not affect risk score
    if dns_result.get('status') in ['SUCCESS', 'PARTIAL']:
        dns_data = dns_result.get('data', {})
        
        # Check for DNS records
        if not dns_data.get('a_records'):
            total_score -= 10
            deductions.append({
                'finding': 'No A records found',
                'status': 'DETECTED',
                'severity': 'HIGH',
                'evidence': f"A records count: {len(dns_data.get('a_records', []))}",
                'explanation': 'No IP address records found - website may not be accessible',
                'recommendation': 'Configure A records to point to valid IP addresses',
                'score_impact': -10,
                'confidence': dns_result.get('confidence', 100),
                'category': 'DNS Configuration'
            })
        
        # MX records are optional - do not deduct points for missing MX records
        # Many domains intentionally do not receive email
    # If status is FAILED, PARTIAL, or UNKNOWN, do not deduct points - this is a scanner error
    
    # WHOIS Risk Assessment (15 points max)
    whois_result = scan_results.get('whois', {})
    # Only evaluate WHOIS if scan succeeded - scanner errors should not affect risk score
    if whois_result.get('status') == 'SUCCESS':
        whois_data = whois_result.get('data', {})
        
        # Check domain age
        if whois_data.get('created'):
            try:
                from datetime import datetime
                created_date = datetime.strptime(whois_data['created'], '%Y-%m-%d')
                domain_age = (datetime.now() - created_date).days
                
                if domain_age < 30:
                    total_score -= 10
                    deductions.append({
                        'finding': 'Newly registered domain',
                        'status': 'DETECTED',
                        'severity': 'MEDIUM',
                        'evidence': f"Domain age: {domain_age} days",
                        'explanation': f'Domain is only {domain_age} days old - new domains are often used for scams',
                        'recommendation': 'Exercise caution with this domain as it was recently registered',
                        'score_impact': -10,
                        'confidence': whois_result.get('confidence', 100),
                        'category': 'Domain Registration'
                    })
                elif domain_age < 90:
                    total_score -= 5
                    deductions.append({
                        'finding': 'Recently registered domain',
                        'status': 'DETECTED',
                        'severity': 'LOW',
                        'evidence': f"Domain age: {domain_age} days",
                        'explanation': f'Domain is {domain_age} days old - exercise caution with newer domains',
                        'recommendation': 'Verify the legitimacy of this recently registered domain',
                        'score_impact': -5,
                        'confidence': whois_result.get('confidence', 100),
                        'category': 'Domain Registration'
                    })
            except:
                pass
        
        # Check domain expiration
        if whois_data.get('expires'):
            try:
                from datetime import datetime
                expires_date = datetime.strptime(whois_data['expires'], '%Y-%m-%d')
                days_until_expiry = (expires_date - datetime.now()).days
                
                if days_until_expiry < 30:
                    total_score -= 10
                    deductions.append({
                        'finding': 'Domain expiring soon',
                        'status': 'DETECTED',
                        'severity': 'HIGH',
                        'evidence': f"Days until expiry: {days_until_expiry}",
                        'explanation': f'Domain expires in {days_until_expiry} days - renew to avoid losing it',
                        'recommendation': 'Renew the domain registration to avoid service disruption',
                        'score_impact': -10,
                        'confidence': whois_result.get('confidence', 100),
                        'category': 'Domain Registration'
                    })
            except:
                pass
    # If status is FAILED, PARTIAL, or UNKNOWN, do not deduct points - this is a scanner error
    
    # Ensure score doesn't go below 0
    total_score = max(0, total_score)
    
    # Determine risk level
    if total_score >= 80:
        risk_level = 'LOW'
        risk_color = 'emerald'
    elif total_score >= 60:
        risk_level = 'MEDIUM'
        risk_color = 'amber'
    elif total_score >= 40:
        risk_level = 'HIGH'
        risk_color = 'orange'
    else:
        risk_level = 'CRITICAL'
        risk_color = 'red'
    
    logger.info(f"Risk score calculated: {total_score}/100 ({risk_level})")
    
    # Calculate score breakdown by category
    score_breakdown = {
        'ssl': 0,
        'headers': 0,
        'dns': 0,
        'whois': 0
    }
    
    for deduction in deductions:
        category = deduction.get('category', '').lower()
        if 'ssl' in category:
            score_breakdown['ssl'] += deduction.get('score_impact', 0)
        elif 'header' in category:
            score_breakdown['headers'] += deduction.get('score_impact', 0)
        elif 'dns' in category:
            score_breakdown['dns'] += deduction.get('score_impact', 0)
        elif 'domain' in category or 'whois' in category:
            score_breakdown['whois'] += deduction.get('score_impact', 0)
    
    return {
        'score': total_score,
        'level': risk_level,
        'color': risk_color,
        'deductions': deductions,
        'score_breakdown': score_breakdown,
        'summary': generate_risk_summary(total_score, risk_level, deductions)
    }


def generate_risk_summary(score: int, level: str, deductions: list) -> str:
    """Generate a user-friendly summary of the risk assessment."""
    
    if score >= 80:
        return "Netra did not detect significant security issues during this passive assessment."
    elif score >= 60:
        return "Netra observed some security configurations that could be improved."
    elif score >= 40:
        return "Netra detected moderate security concerns during this scan."
    else:
        return "Netra detected critical security issues during this assessment."
