"""
Normalization and Interpretation Layer for NETRA

This module provides functions to normalize raw technical data into
human-readable formats with three layers:
1. Simple View - For non-technical users
2. Explanation - What the information means
3. Technical Details - Raw/structured information for technical users
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import socket
import re


def normalize_infrastructure_intelligence(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize raw DNS/IP data into a structured infrastructure intelligence model.
    
    Args:
        raw_data: Raw data from DNS scanner with ip_info or infrastructure_intelligence
    
    Returns:
        Normalized infrastructure intelligence with simple_summary and technical_details
    """
    # Extract data from either old or new structure
    if raw_data.get('infrastructure_intelligence'):
        infra = raw_data['infrastructure_intelligence']
        ip_info = raw_data.get('ip_info')  # For backward compatibility
    elif raw_data.get('ip_info'):
        infra = None
        ip_info = raw_data['ip_info']
    else:
        return {
            'simple_summary': None,
            'explanation': 'Infrastructure information unavailable',
            'technical_details': raw_data,
            'confidence': 'UNKNOWN',
            'source': 'UNKNOWN'
        }
    
    # Use the new structure if available, otherwise build from ip_info
    if infra:
        ip_address = infra.get('ip_address')
        ip_ownership = infra.get('ip_ownership', {})
        geographic = infra.get('geographic_estimate', {})
        confidence_info = infra.get('confidence', {})
    else:
        ip_address = ip_info.get('ip')
        ip_ownership = {
            'isp': ip_info.get('isp'),
            'organization': ip_info.get('org'),
            'asn': ip_info.get('asn'),
            'asn_organization': ip_info.get('asn_organization'),
            'network': ip_info.get('network')
        }
        geographic = {
            'country': ip_info.get('country'),
            'country_code': ip_info.get('country_code'),
            'city': ip_info.get('city'),
            'region': ip_info.get('region'),
            'region_code': ip_info.get('region_code'),
            'latitude': ip_info.get('lat'),
            'longitude': ip_info.get('lon'),
            'accuracy_radius': ip_info.get('accuracy_radius')
        }
        confidence_info = {
            'score': ip_info.get('confidence'),
            'level': ip_info.get('confidence_level'),
            'source': ip_info.get('sources', ['unknown'])[0] if ip_info.get('sources') else 'unknown',
            'note': ip_info.get('accuracy_note')
        }
    
    # Build simple summary
    simple_summary = {
        'ip_address': ip_address,
        'hosting_provider': ip_ownership.get('isp') or ip_ownership.get('organization'),
        'organization': ip_ownership.get('organization') or ip_ownership.get('asn_organization'),
        'location': format_location(geographic),
        'network': ip_ownership.get('network'),
        'asn': ip_ownership.get('asn'),
        'confidence': confidence_info.get('level', 'UNKNOWN')
    }
    
    # Build explanation
    explanation = build_infrastructure_explanation(
        ip_address,
        ip_ownership,
        geographic,
        confidence_info
    )
    
    # Build technical details
    technical_details = {
        'ip': ip_address,
        'country': geographic.get('country'),
        'country_code': geographic.get('country_code'),
        'region': geographic.get('region'),
        'region_code': geographic.get('region_code'),
        'city': geographic.get('city'),
        'postal_code': geographic.get('postal_code'),
        'latitude': geographic.get('latitude'),
        'longitude': geographic.get('longitude'),
        'accuracy_radius_km': geographic.get('accuracy_radius'),
        'isp': ip_ownership.get('isp'),
        'organization': ip_ownership.get('organization'),
        'asn': ip_ownership.get('asn'),
        'asn_organization': ip_ownership.get('asn_organization'),
        'network': ip_ownership.get('network'),
        'confidence_score': confidence_info.get('score'),
        'confidence_level': confidence_info.get('level'),
        'source': confidence_info.get('source'),
        'accuracy_note': confidence_info.get('note')
    }
    
    return {
        'simple_summary': simple_summary,
        'explanation': explanation,
        'technical_details': technical_details,
        'confidence': confidence_info.get('level', 'UNKNOWN'),
        'source': confidence_info.get('source', 'UNKNOWN')
    }


def format_location(geographic: Dict[str, Any]) -> str:
    """Format location data into a human-readable string."""
    city = geographic.get('city')
    region = geographic.get('region')
    country = geographic.get('country')
    
    parts = []
    if city:
        parts.append(city)
    if region and region != city:
        parts.append(region)
    if country:
        parts.append(country)
    
    return ', '.join(parts) if parts else 'Unknown'


def build_infrastructure_explanation(
    ip_address: str,
    ip_ownership: Dict[str, Any],
    geographic: Dict[str, Any],
    confidence_info: Dict[str, Any]
) -> str:
    """Build plain-English explanation for infrastructure intelligence."""
    explanations = []
    
    # Location explanation
    location = format_location(geographic)
    if location != 'Unknown':
        explanations.append(
            f"This website appears to be running on infrastructure located in {location}. "
            f"This is the estimated location of the network endpoint and may represent a cloud provider "
            f"or data center rather than the physical location of the website owner."
        )
    
    # Hosting provider explanation
    hosting = ip_ownership.get('isp') or ip_ownership.get('organization')
    if hosting:
        explanations.append(
            f"The IP address is associated with {hosting}."
        )
    
    # ASN explanation
    asn = ip_ownership.get('asn')
    if asn:
        asn_org = ip_ownership.get('asn_organization')
        if asn_org:
            explanations.append(
                f"The network is operated by {asn_org} (ASN: {asn}). "
                f"An ASN identifies the network organization responsible for this group of Internet addresses."
            )
    
    # Confidence explanation
    confidence = confidence_info.get('level', 'UNKNOWN')
    source = confidence_info.get('source', 'unknown')
    if confidence == 'HIGH':
        explanations.append(
            f"Location confidence is High based on {source} data."
        )
    elif confidence == 'MODERATE':
        explanations.append(
            f"Location confidence is Moderate. Different data sources may provide slightly different estimates."
        )
    elif confidence == 'LOW':
        explanations.append(
            f"Location confidence is Low. The exact location could not be reliably determined."
        )
    
    return ' '.join(explanations)


def interpret_asn(asn: Optional[str], asn_organization: Optional[str] = None) -> Dict[str, Any]:
    """
    Interpret ASN information with plain-English explanation.
    
    Args:
        asn: Autonomous System Number (e.g., "AS16509")
        asn_organization: Organization name
    
    Returns:
        Dictionary with simple, explanation, and technical details
    """
    if not asn:
        return {
            'simple': 'ASN information unavailable',
            'explanation': 'Autonomous System information could not be determined for this IP.',
            'technical': {'asn': None, 'organization': None}
        }
    
    simple = f"{asn}"
    if asn_organization:
        simple += f" ({asn_organization})"
    
    explanation = (
        f"An ASN (Autonomous System Number) identifies the network organization responsible for "
        f"this group of Internet addresses. {asn} is operated by {asn_organization or 'an unknown organization'}."
    )
    
    return {
        'simple': simple,
        'explanation': explanation,
        'technical': {
            'asn': asn,
            'organization': asn_organization
        }
    }


def interpret_cidr(cidr: Optional[str], net_range: Optional[str] = None) -> Dict[str, Any]:
    """
    Interpret CIDR network block with plain-English explanation.
    
    Args:
        cidr: CIDR notation (e.g., "3.108.0.0/14")
        net_range: Human-readable range (e.g., "3.108.0.0 - 3.111.255.255")
    
    Returns:
        Dictionary with simple, explanation, and technical details
    """
    if not cidr and not net_range:
        return {
            'simple': 'Network range unavailable',
            'explanation': 'Network range information could not be determined.',
            'technical': {'cidr': None, 'net_range': None}
        }
    
    simple = cidr or net_range or 'Unknown'
    
    explanation = (
        "This identifies the larger group of IP addresses that this server belongs to. "
        "Servers in the same network block typically share the same hosting provider or infrastructure."
    )
    
    if net_range:
        explanation += f" The range {net_range} includes this IP address."
    
    return {
        'simple': simple,
        'explanation': explanation,
        'technical': {
            'cidr': cidr,
            'net_range': net_range
        }
    }


def interpret_reverse_dns(reverse_dns: Optional[str]) -> Dict[str, Any]:
    """
    Interpret reverse DNS with plain-English explanation.
    
    Args:
        reverse_dns: Reverse DNS hostname
    
    Returns:
        Dictionary with simple, explanation, and technical details
    """
    if not reverse_dns:
        return {
            'simple': 'Reverse DNS unavailable',
            'explanation': 'No reverse DNS record was found for this IP address.',
            'technical': {'reverse_dns': None}
        }
    
    simple = reverse_dns
    
    explanation = (
        "This is the hostname associated with the server's IP address. "
        "Reverse DNS can provide clues about the hosting infrastructure."
    )
    
    # Add infrastructure inference if hostname suggests cloud provider
    if 'amazonaws.com' in reverse_dns.lower() or 'aws' in reverse_dns.lower():
        explanation += " This hostname suggests the IP is associated with Amazon EC2 infrastructure."
    elif 'googleusercontent.com' in reverse_dns.lower():
        explanation += " This hostname suggests the IP is associated with Google Cloud infrastructure."
    elif 'azure.com' in reverse_dns.lower() or 'microsoft.com' in reverse_dns.lower():
        explanation += " This hostname suggests the IP is associated with Microsoft Azure infrastructure."
    elif 'digitalocean.com' in reverse_dns.lower():
        explanation += " This hostname suggests the IP is associated with DigitalOcean infrastructure."
    
    return {
        'simple': simple,
        'explanation': explanation,
        'technical': {
            'reverse_dns': reverse_dns
        }
    }


def interpret_connection_type(connection_type: Optional[str], hostname: Optional[str] = None) -> Dict[str, Any]:
    """
    Interpret connection type with plain-English explanation.
    
    Args:
        connection_type: Raw connection type from provider
        hostname: Reverse DNS hostname for inference
    
    Returns:
        Dictionary with simple, explanation, and technical details
    """
    # Normalize connection type
    normalized = 'Unknown'
    
    if connection_type:
        ct_lower = connection_type.lower()
        if 'residential' in ct_lower:
            normalized = 'Residential'
        elif 'business' in ct_lower or 'commercial' in ct_lower:
            normalized = 'Business'
        elif 'corporate' in ct_lower or 'enterprise' in ct_lower:
            normalized = 'Corporate'
        elif 'data center' in ct_lower or 'datacenter' in ct_lower or 'dc' in ct_lower:
            normalized = 'Data Center'
        elif 'cloud' in ct_lower:
            normalized = 'Cloud'
        elif 'mobile' in ct_lower or 'cellular' in ct_lower:
            normalized = 'Mobile'
        elif 'isp' in ct_lower:
            normalized = 'ISP'
    
    # Infer from hostname if connection type unknown
    if normalized == 'Unknown' and hostname:
        hostname_lower = hostname.lower()
        if 'amazonaws.com' in hostname_lower or 'aws' in hostname_lower:
            normalized = 'Cloud / Data Center'
        elif 'googleusercontent.com' in hostname_lower:
            normalized = 'Cloud / Data Center'
        elif 'azure.com' in hostname_lower or 'microsoft.com' in hostname_lower:
            normalized = 'Cloud / Data Center'
        elif 'digitalocean.com' in hostname_lower:
            normalized = 'Cloud / Data Center'
    
    explanation = {
        'Residential': 'This connection appears to be from a residential internet service.',
        'Business': 'This connection appears to be from a business internet service.',
        'Corporate': 'This connection appears to be from a corporate network.',
        'Data Center': 'This connection appears to be from a data center or hosting facility.',
        'Cloud': 'This connection appears to be from a cloud computing service.',
        'Mobile': 'This connection appears to be from a mobile network.',
        'ISP': 'This connection appears to be from a standard internet service provider.',
        'Cloud / Data Center': 'This connection appears to be from cloud infrastructure or a data center.',
        'Unknown': 'The connection type could not be determined from available information.'
    }
    
    return {
        'simple': normalized,
        'explanation': explanation.get(normalized, explanation['Unknown']),
        'technical': {
            'connection_type': connection_type,
            'inferred_from_hostname': hostname if normalized != 'Unknown' and connection_type is None else None
        }
    }


def normalize_whois(raw_whois: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize WHOIS data into human-readable format.
    
    Args:
        raw_whois: Raw WHOIS data from scanner
    
    Returns:
        Normalized WHOIS with simple_summary and technical_details
    """
    if not raw_whois or raw_whois.get('status') in ['FAILED', 'UNAVAILABLE']:
        return {
            'simple_summary': None,
            'explanation': raw_whois.get('data', {}).get('explanation', 'Domain registration information unavailable'),
            'technical_details': raw_whois,
            'confidence': 'UNKNOWN'
        }
    
    data = raw_whois.get('data', {})
    
    # Calculate domain age
    created = data.get('created')
    age_years = None
    if created:
        try:
            created_date = datetime.strptime(created, '%Y-%m-%d')
            age_days = (datetime.now() - created_date).days
            age_years = age_days // 365
        except:
            pass
    
    # Calculate days until expiry
    expires = data.get('expires')
    days_until_expiry = None
    if expires:
        try:
            expires_date = datetime.strptime(expires, '%Y-%m-%d')
            days_until_expiry = (expires_date - datetime.now()).days
        except:
            pass
    
    # Build simple summary
    simple_summary = {
        'registration_date': format_date(created),
        'domain_age': f"{age_years} years" if age_years is not None else "Unknown",
        'registrar': data.get('registrar'),
        'expiry_date': format_date(expires),
        'status': data.get('status', ['Unknown'])[0] if isinstance(data.get('status'), list) else data.get('status', 'Unknown'),
        'name_servers': data.get('nameservers', [])[:3]  # Show first 3
    }
    
    # Build explanation
    explanation_parts = []
    
    if age_years is not None:
        if age_years < 1:
            explanation_parts.append(f"This domain was recently registered (less than 1 year ago).")
        elif age_years < 5:
            explanation_parts.append(f"This domain was registered approximately {age_years} years ago.")
        else:
            explanation_parts.append(f"This domain has been registered for {age_years} years.")
    
    if data.get('registrar'):
        explanation_parts.append(f"It is registered through {data['registrar']}.")
    
    if days_until_expiry is not None:
        if days_until_expiry < 30:
            explanation_parts.append(f"The domain registration expires in {days_until_expiry} days (renewal needed soon).")
        elif days_until_expiry < 90:
            explanation_parts.append(f"The domain registration expires in {days_until_expiry} days.")
    
    if not explanation_parts:
        explanation_parts.append("Domain registration information is available but some details may be hidden due to privacy policies.")
    
    explanation = ' '.join(explanation_parts)
    
    # Build technical details
    technical_details = {
        'registrar': data.get('registrar'),
        'created': data.get('created'),
        'expires': data.get('expires'),
        'updated': data.get('updated'),
        'name_servers': data.get('nameservers'),
        'status': data.get('status'),
        'country': data.get('country'),
        'registrar_url': data.get('registrar_url')
    }
    
    return {
        'simple_summary': simple_summary,
        'explanation': explanation,
        'technical_details': technical_details,
        'confidence': 'HIGH' if raw_whois.get('status') == 'SUCCESS' else 'UNKNOWN'
    }


def format_date(date_input: Optional[str]) -> str:
    """Format date string or datetime object for display."""
    if not date_input:
        return 'Unknown'
    
    # Handle list of datetime objects
    if isinstance(date_input, list):
        if len(date_input) > 0:
            date_input = date_input[0]
        else:
            return 'Unknown'
    
    # Handle datetime object
    if hasattr(date_input, 'strftime'):
        try:
            return date_input.strftime('%B %d, %Y')
        except:
            return str(date_input)
    
    # Handle string
    if isinstance(date_input, str):
        try:
            date_obj = datetime.strptime(date_input, '%Y-%m-%d')
            return date_obj.strftime('%B %d, %Y')
        except:
            return date_input
    
    return str(date_input)


def normalize_dns(raw_dns: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize DNS data into human-readable format.
    
    Args:
        raw_dns: Raw DNS data from scanner
    
    Returns:
        Normalized DNS with simple_summary and technical_details
    """
    if not raw_dns or raw_dns.get('status') != 'SUCCESS':
        return {
            'simple_summary': None,
            'explanation': 'DNS information unavailable',
            'technical_details': raw_dns,
            'confidence': 'UNKNOWN'
        }
    
    data = raw_dns.get('data', {})
    
    # Build simple summary
    simple_summary = {
        'website_address': data.get('a_records', ['Unknown'])[0] if data.get('a_records') else 'Unknown',
        'has_email': len(data.get('mx_records', [])) > 0,
        'has_dns_servers': len(data.get('ns_records', [])) > 0
    }
    
    # Build explanation
    explanation_parts = []
    
    if data.get('a_records'):
        ip = data['a_records'][0]
        explanation_parts.append(
            f"The A record points to IP address {ip}. "
            "This tells browsers which server to contact when they access this domain."
        )
    
    if data.get('mx_records'):
        explanation_parts.append(
            f"MX records are configured ({len(data['mx_records'])} servers), "
            "which means this domain can receive email."
        )
    
    if data.get('ns_records'):
        explanation_parts.append(
            f"NS records are configured ({len(data['ns_records'])} servers), "
            "which specify the DNS servers for this domain."
        )
    
    explanation = ' '.join(explanation_parts) if explanation_parts else 'DNS records are configured for this domain.'
    
    # Build technical details
    technical_details = {
        'a_records': data.get('a_records'),
        'mx_records': data.get('mx_records'),
        'ns_records': data.get('ns_records'),
        'txt_records': data.get('txt_records'),
        'aaaa_records': data.get('aaaa_records')
    }
    
    return {
        'simple_summary': simple_summary,
        'explanation': explanation,
        'technical_details': technical_details,
        'confidence': 'HIGH'
    }


def normalize_ssl(raw_ssl: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize SSL data into human-readable format.
    
    Args:
        raw_ssl: Raw SSL data from scanner
    
    Returns:
        Normalized SSL with simple_summary and technical_details
    """
    if not raw_ssl or raw_ssl.get('status') != 'SUCCESS':
        return {
            'simple_summary': None,
            'explanation': 'SSL information unavailable',
            'technical_details': raw_ssl,
            'confidence': 'UNKNOWN'
        }
    
    data = raw_ssl.get('data', {})
    
    # Build simple summary
    is_valid = data.get('valid', False)
    days_remaining = data.get('days_remaining', 0)
    protocol = data.get('protocol', 'Unknown')
    
    simple_summary = {
        'status': 'Secure' if is_valid else 'Not Secure',
        'protocol': protocol,
        'days_remaining': days_remaining,
        'issuer': data.get('issuer_name', 'Unknown')
    }
    
    # Build explanation
    if is_valid:
        explanation = (
            f"Netra successfully verified the HTTPS certificate during this scan. "
            f"The connection uses {protocol}, which encrypts information exchanged between visitors and the website."
        )
        if days_remaining < 30:
            explanation += f" The certificate expires in {days_remaining} days and should be renewed soon."
        else:
            explanation += f" The certificate is valid for {days_remaining} more days."
    else:
        explanation = (
            "The SSL certificate could not be verified or is invalid. "
            "This means the connection may not be secure."
        )
    
    # Build technical details
    technical_details = {
        'issuer_name': data.get('issuer_name'),
        'issuer_full': data.get('issuer_full'),
        'subject_cn': data.get('subject_cn'),
        'subject_full': data.get('subject_full'),
        'sans': data.get('sans'),
        'valid_from': data.get('valid_from'),
        'valid_until': data.get('valid_until'),
        'days_remaining': days_remaining,
        'protocol': protocol,
        'signature_algorithm': data.get('signature_algorithm'),
        'hostname_verified': data.get('hostname_verified'),
        'serial_number': data.get('serial_number'),
        'version': data.get('version')
    }
    
    return {
        'simple_summary': simple_summary,
        'explanation': explanation,
        'technical_details': technical_details,
        'confidence': 'HIGH' if is_valid else 'LOW'
    }


def normalize_headers(raw_headers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize security headers data into human-readable format.
    
    Args:
        raw_headers: Raw headers data from scanner
    
    Returns:
        Normalized headers with simple_summary and technical_details
    """
    if not raw_headers or raw_headers.get('status') not in ['SUCCESS', 'PARTIAL']:
        return {
            'simple_summary': None,
            'explanation': 'Security header information unavailable',
            'technical_details': raw_headers,
            'confidence': 'UNKNOWN'
        }
    
    data = raw_headers.get('data', {})
    
    # Count critical headers
    critical_headers = ['hsts', 'csp']
    present_count = 0
    header_status = {}
    
    for header in critical_headers:
        header_info = data.get(header)
        if isinstance(header_info, dict):
            status = header_info.get('status')
            if status == 'FOUND':
                present_count += 1
            header_status[header] = status
        elif header_info:  # Backward compatibility
            present_count += 1
            header_status[header] = 'FOUND'
        else:
            header_status[header] = 'MISSING'
    
    # Build simple summary
    simple_summary = {
        'critical_headers_present': present_count,
        'critical_headers_total': len(critical_headers),
        'hsts': header_status.get('hsts', 'UNKNOWN'),
        'csp': header_status.get('csp', 'UNKNOWN'),
        'x_frame_options': data.get('x_frame_options', {}).get('status', 'UNKNOWN') if isinstance(data.get('x_frame_options'), dict) else ('FOUND' if data.get('x_frame_options') else 'MISSING'),
        'x_content_type_options': data.get('x_content_type_options', {}).get('status', 'UNKNOWN') if isinstance(data.get('x_content_type_options'), dict) else ('FOUND' if data.get('x_content_type_options') else 'MISSING')
    }
    
    # Build explanation
    explanation_parts = []
    
    if present_count == len(critical_headers):
        explanation_parts.append("Critical security headers (HSTS and CSP) are present.")
    else:
        missing = [h for h, s in header_status.items() if s == 'MISSING']
        if missing:
            missing_upper = [m.upper() if isinstance(m, str) else str(m) for m in missing]
            explanation_parts.append(f"Critical security headers are missing: {', '.join(missing_upper)}.")
    
    explanation_parts.append(
        "Security headers provide additional protection against common web attacks "
        "by controlling browser behavior."
    )
    
    explanation = ' '.join(explanation_parts)
    
    # Build technical details
    technical_details = {
        'hsts': data.get('hsts'),
        'csp': data.get('csp'),
        'csp_frame_ancestors': data.get('csp_frame_ancestors'),
        'x_frame_options': data.get('x_frame_options'),
        'x_content_type_options': data.get('x_content_type_options'),
        'referrer_policy': data.get('referrer_policy'),
        'permissions_policy': data.get('permissions_policy'),
        'redirects': data.get('redirects'),
        'final_url': data.get('final_url'),
        'status_code': data.get('status_code')
    }
    
    return {
        'simple_summary': simple_summary,
        'explanation': explanation,
        'technical_details': technical_details,
        'confidence': 'HIGH' if raw_headers.get('status') == 'SUCCESS' else 'MODERATE'
    }
