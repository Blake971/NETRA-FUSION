import ssl
import socket
import time
from datetime import datetime
from typing import Dict, Any
from utils.logger import log_module_start, log_module_complete, log_module_error, setup_logger


def scan_ssl(domain: str) -> Dict[str, Any]:
    """
    Analyze SSL certificate for a domain.
    
    Args:
        domain: Domain to analyze
    
    Returns:
        Standardized JSON response with SSL data
    """
    logger = setup_logger()
    start_time = time.time()
    
    log_module_start(logger, "SSL", domain)
    
    try:
        # Create SSL context
        logger.info("SSL: Creating SSL context...")
        context = ssl.create_default_context()
        
        # Connect to domain
        logger.info(f"SSL: Connecting to {domain}:443...")
        with socket.create_connection((domain, 443), timeout=10) as sock:
            logger.info("SSL: Connection established, initiating TLS handshake...")
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                logger.info("SSL: TLS handshake complete, retrieving certificate...")
                cert = ssock.getpeercert()
                logger.info(f"SSL: Certificate retrieved, protocol: {ssock.version()}")
                
                # Calculate days remaining
                expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                issue_date = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                days_remaining = (expiry_date - datetime.utcnow()).days
                logger.info(f"SSL: Certificate valid for {days_remaining} more days")
                
                # Extract issuer organization name
                issuer_name = None
                for rdns in cert['issuer']:
                    for rdn in rdns:
                        # Handle both tuple format and dict format
                        if isinstance(rdn, dict):
                            if rdn.get('organizationName'):
                                issuer_name = rdn['organizationName']
                                break
                            elif rdn.get('commonName'):
                                issuer_name = rdn['commonName']
                        elif isinstance(rdn, tuple) and len(rdn) > 0:
                            if isinstance(rdn[0], tuple) and len(rdn[0]) >= 2:
                                if rdn[0][0] == 'organizationName':
                                    issuer_name = rdn[0][1]
                                    break
                                elif rdn[0][0] == 'commonName':
                                    issuer_name = rdn[0][1]
                    if issuer_name:
                        break
                
                # Extract subject common name
                subject_cn = None
                for rdns in cert['subject']:
                    for rdn in rdns:
                        # Handle both tuple format and dict format
                        if isinstance(rdn, dict):
                            if rdn.get('commonName'):
                                subject_cn = rdn['commonName']
                                break
                        elif isinstance(rdn, tuple) and len(rdn) > 0:
                            if isinstance(rdn[0], tuple) and len(rdn[0]) >= 2:
                                if rdn[0][0] == 'commonName':
                                    subject_cn = rdn[0][1]
                                    break
                    if subject_cn:
                        break
                
                # Extract Subject Alternative Names (SANs)
                sans = []
                if 'subjectAltName' in cert:
                    san_data = cert['subjectAltName']
                    for san in san_data:
                        # SAN data comes as tuples like ('DNS', 'example.com')
                        if isinstance(san, tuple) and len(san) >= 2:
                            if san[0] == 'DNS':
                                sans.append(san[1])
                        elif isinstance(san, str) and san.startswith('DNS:'):
                            # Handle string format as fallback
                            sans.append(san[4:])
                
                # Verify hostname matches certificate
                hostname_verified = False
                if subject_cn:
                    # Check exact match or wildcard
                    if subject_cn == domain or (subject_cn.startswith('*.') and domain.endswith(subject_cn[2:])):
                        hostname_verified = True
                # Also check SANs
                if not hostname_verified and sans:
                    for san in sans:
                        if san == domain or (san.startswith('*.') and domain.endswith(san[2:])):
                            hostname_verified = True
                            break
                
                # Get signature algorithm
                signature_algorithm = cert.get('signatureAlgorithm', 'Unknown')
                
                data = {
                    "issuer_name": issuer_name or "Unknown",
                    "issuer_full": [dict(rdn) for rdn in cert['issuer']],
                    "subject_cn": subject_cn or "Unknown",
                    "subject_full": [dict(rdn) for rdn in cert['subject']],
                    "sans": sans,
                    "valid_from": cert['notBefore'],
                    "valid_until": cert['notAfter'],
                    "days_remaining": days_remaining,
                    "version": cert['version'],
                    "serial_number": cert['serialNumber'],
                    "protocol": ssock.version(),
                    "signature_algorithm": signature_algorithm,
                    "hostname_verified": hostname_verified,
                    "valid": days_remaining > 0
                }
        
        execution_time = time.time() - start_time
        log_module_complete(logger, "SSL", domain, execution_time)
        
        return {
            "module": "SSL",
            "status": "SUCCESS",
            "severity": "INFO",
            "message": "SSL data retrieved successfully",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 95,
            "data": data
        }
        
    except socket.timeout as e:
        execution_time = time.time() - start_time
        error_message = str(e)
        logger.error(f"SSL: Connection timeout - {error_message}")
        log_module_error(logger, "SSL", domain, error_message)
        
        return {
            "module": "SSL",
            "status": "FAILED",
            "severity": "ERROR",
            "message": f"Connection timeout: Could not connect to {domain}:443",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 0,
            "data": {
                "status": "error",
                "reason": "Connection timeout",
                "details": error_message
            }
        }
    except ssl.SSLCertVerificationError as e:
        execution_time = time.time() - start_time
        error_message = str(e)
        logger.error(f"SSL: Certificate verification failed - {error_message}")
        log_module_error(logger, "SSL", domain, error_message)
        
        return {
            "module": "SSL",
            "status": "FAILED",
            "severity": "ERROR",
            "message": f"Certificate verification failed: {error_message}",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 0,
            "data": {
                "status": "error",
                "reason": "Certificate verification failed",
                "details": error_message
            }
        }
    except ssl.SSLError as e:
        execution_time = time.time() - start_time
        error_message = str(e)
        logger.error(f"SSL: TLS handshake error - {error_message}")
        log_module_error(logger, "SSL", domain, error_message)
        
        return {
            "module": "SSL",
            "status": "FAILED",
            "severity": "ERROR",
            "message": f"TLS handshake error: {error_message}",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 0,
            "data": {
                "status": "error",
                "reason": "TLS handshake error",
                "details": error_message
            }
        }
    except socket.gaierror as e:
        execution_time = time.time() - start_time
        error_message = str(e)
        logger.error(f"SSL: DNS resolution failed - {error_message}")
        log_module_error(logger, "SSL", domain, error_message)
        
        return {
            "module": "SSL",
            "status": "FAILED",
            "severity": "ERROR",
            "message": f"DNS resolution failed: Could not resolve {domain}",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 0,
            "data": {
                "status": "error",
                "reason": "DNS resolution failed",
                "details": error_message
            }
        }
    except Exception as e:
        execution_time = time.time() - start_time
        error_message = str(e)
        logger.error(f"SSL: Unexpected error - {error_message}")
        log_module_error(logger, "SSL", domain, error_message)
        
        return {
            "module": "SSL",
            "status": "FAILED",
            "severity": "ERROR",
            "message": f"SSL analysis failed: {error_message}",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 0,
            "data": {
                "status": "error",
                "reason": "Unexpected error",
                "details": error_message
            }
        }
