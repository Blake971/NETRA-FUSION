import whois
import time
from typing import Dict, Any
from utils.logger import log_module_start, log_module_complete, log_module_error, setup_logger


def scan_whois(domain: str) -> Dict[str, Any]:
    """
    Perform WHOIS lookup for a domain.
    
    Args:
        domain: Domain to query
    
    Returns:
        Standardized JSON response with WHOIS data
    """
    logger = setup_logger()
    start_time = time.time()
    
    log_module_start(logger, "WHOIS", domain)
    
    try:
        # Perform WHOIS lookup
        logger.info("WHOIS: Querying WHOIS server...")
        w = whois.whois(domain)
        
        # Check if we got any data
        if not w or not any([w.registrar, w.creation_date, w.name_servers]):
            execution_time = time.time() - start_time
            logger.warning(f"WHOIS: No data returned for {domain}")
            
            return {
                "module": "WHOIS",
                "status": "UNAVAILABLE",
                "severity": "INFO",
                "message": "WHOIS data unavailable - server returned no information",
                "execution_time": f"{execution_time:.2f}",
                "confidence": 0,
                "data": {
                    "status": "unavailable",
                    "reason": "WHOIS server returned no information"
                }
            }
        
        # Parse and normalize data
        logger.info("WHOIS: Parsing response data...")
        data = {
            "registrar": str(w.registrar) if w.registrar else None,
            "created": str(w.creation_date) if w.creation_date else None,
            "expires": str(w.expiration_date) if w.expiration_date else None,
            "updated": str(w.last_updated) if w.last_updated else None,
            "nameservers": w.name_servers if w.name_servers else [],
            "status": w.status if w.status else [],
            "country": w.country if hasattr(w, 'country') else None,
            "registrar_url": w.registrar_url if hasattr(w, 'registrar_url') else None
        }
        
        # Determine if we have partial or complete data
        has_essential_data = bool(data.get('registrar') or data.get('created') or data.get('nameservers'))
        
        execution_time = time.time() - start_time
        log_module_complete(logger, "WHOIS", domain, execution_time)
        
        if has_essential_data:
            return {
                "module": "WHOIS",
                "status": "SUCCESS",
                "severity": "INFO",
                "message": "WHOIS data retrieved successfully",
                "execution_time": f"{execution_time:.2f}",
                "confidence": 100,
                "data": data
            }
        else:
            return {
                "module": "WHOIS",
                "status": "PARTIAL",
                "severity": "INFO",
                "message": "WHOIS data incomplete - limited information available",
                "execution_time": f"{execution_time:.2f}",
                "confidence": 50,
                "data": data
            }
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_message = str(e)
        
        # Categorize error types
        if "timeout" in error_message.lower() or "timed out" in error_message.lower():
            error_type = "WHOIS server timeout"
            explanation = "The WHOIS server did not respond within the expected time. This may be due to network issues or server load."
        elif "no such domain" in error_message.lower() or "not found" in error_message.lower():
            error_type = "Domain not found"
            explanation = "The domain does not exist or is not registered."
        elif "rate limit" in error_message.lower() or "blocked" in error_message.lower():
            error_type = "WHOIS request blocked or rate limited"
            explanation = "The WHOIS server has blocked or rate-limited requests from this IP address."
        else:
            error_type = "WHOIS lookup error"
            explanation = "An unexpected error occurred while querying the WHOIS server."
        
        logger.error(f"WHOIS: {error_type} - {error_message}")
        log_module_error(logger, "WHOIS", domain, error_message)
        
        return {
            "module": "WHOIS",
            "status": "FAILED",
            "severity": "ERROR",
            "message": f"{error_type}",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 0,
            "data": {
                "status": "error",
                "reason": error_type,
                "explanation": explanation
            }
        }
