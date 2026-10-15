import re
from typing import Optional


def validate_domain(domain: str) -> tuple[bool, Optional[str]]:
    """
    Validate domain name format.
    
    Args:
        domain: Domain string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not domain:
        return False, "Domain is required"
    
    # Remove protocol if present
    domain = domain.replace("http://", "").replace("https://", "").split("/")[0]
    
    # Remove port if present
    domain = domain.split(":")[0]
    
    # Remove www. prefix for validation
    domain = domain.replace("www.", "")
    
    # Improved domain regex that supports multi-level TLDs (e.g., .gov.in, .co.uk, .bank.in)
    # Allows subdomains and international TLDs
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](\.[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9])+$'
    
    if not re.match(pattern, domain):
        return False, "Invalid domain format"
    
    return True, None


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Validate email format.
    
    Args:
        email: Email string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, None
