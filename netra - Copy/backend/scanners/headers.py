import httpx
import time
from typing import Dict, Any
from utils.logger import log_module_start, log_module_complete, log_module_error, setup_logger


def scan_headers(domain: str) -> Dict[str, Any]:
    """
    Analyze HTTP security headers for a domain.
    
    Args:
        domain: Domain to analyze
    
    Returns:
        Standardized JSON response with headers data
    """
    logger = setup_logger()
    start_time = time.time()
    
    log_module_start(logger, "Headers", domain)
    
    try:
        # Try HTTPS first
        logger.info("Headers: Attempting HTTPS connection...")
        url = f"https://{domain}"
        
        with httpx.Client(timeout=10, follow_redirects=True, max_redirects=5) as client:
            response = client.get(url)
            headers = dict(response.headers)
            logger.info(f"Headers: Got response with {len(headers)} headers after {len(response.history)} redirects")
            
            # Check security headers with FOUND/MISSING/UNKNOWN states
            def get_header_status(header_name):
                """Determine header status: FOUND, MISSING, or UNKNOWN"""
                # Case-insensitive search for header
                for key in headers.keys():
                    if key.lower() == header_name.lower():
                        return "FOUND", headers[key]
                return "MISSING", None
            
            # Check each security header
            hsts_status, hsts_value = get_header_status("strict-transport-security")
            csp_status, csp_value = get_header_status("content-security-policy")
            x_frame_options_status, x_frame_options_value = get_header_status("x-frame-options")
            x_content_type_options_status, x_content_type_options_value = get_header_status("x-content-type-options")
            referrer_policy_status, referrer_policy_value = get_header_status("referrer-policy")
            permissions_policy_status, permissions_policy_value = get_header_status("permissions-policy")
            
            # Check CSP for frame-ancestors directive
            csp_frame_ancestors_status = "UNKNOWN"
            csp_frame_ancestors_value = None
            if csp_status == "FOUND" and csp_value:
                if "frame-ancestors" in csp_value.lower():
                    csp_frame_ancestors_status = "FOUND"
                    # Extract frame-ancestors value
                    parts = csp_value.split(';')
                    for part in parts:
                        if "frame-ancestors" in part.lower():
                            csp_frame_ancestors_value = part.strip()
                            break
                else:
                    csp_frame_ancestors_status = "MISSING"
            
            data = {
                "hsts": {
                    "status": hsts_status,
                    "value": hsts_value
                },
                "csp": {
                    "status": csp_status,
                    "value": csp_value
                },
                "csp_frame_ancestors": {
                    "status": csp_frame_ancestors_status,
                    "value": csp_frame_ancestors_value
                },
                "x_frame_options": {
                    "status": x_frame_options_status,
                    "value": x_frame_options_value
                },
                "x_content_type_options": {
                    "status": x_content_type_options_status,
                    "value": x_content_type_options_value
                },
                "referrer_policy": {
                    "status": referrer_policy_status,
                    "value": referrer_policy_value
                },
                "permissions_policy": {
                    "status": permissions_policy_status,
                    "value": permissions_policy_value
                },
                "all_headers": headers,
                "redirects": len(response.history),
                "final_url": str(response.url),
                "status_code": response.status_code
            }
        
        execution_time = time.time() - start_time
        log_module_complete(logger, "Headers", domain, execution_time)
        
        return {
            "module": "HEADERS",
            "status": "SUCCESS",
            "severity": "INFO",
            "message": "Headers data retrieved successfully",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 90,
            "data": data
        }
        
    except httpx.ConnectError as e:
        # HTTPS failed, try HTTP
        logger.warning(f"Headers: HTTPS connection failed, trying HTTP...")
        try:
            url = f"http://{domain}"
            with httpx.Client(timeout=10, follow_redirects=True, max_redirects=5) as client:
                response = client.get(url)
                headers = dict(response.headers)
                logger.info(f"Headers: Got HTTP response with {len(headers)} headers after {len(response.history)} redirects")
                
            # Check security headers with FOUND/MISSING/UNKNOWN states
            def get_header_status(header_name):
                """Determine header status: FOUND, MISSING, or UNKNOWN"""
                # Case-insensitive search for header
                for key in headers.keys():
                    if key.lower() == header_name.lower():
                        return "FOUND", headers[key]
                return "MISSING", None
            
            # Check each security header
            hsts_status, hsts_value = get_header_status("strict-transport-security")
            csp_status, csp_value = get_header_status("content-security-policy")
            x_frame_options_status, x_frame_options_value = get_header_status("x-frame-options")
            x_content_type_options_status, x_content_type_options_value = get_header_status("x-content-type-options")
            referrer_policy_status, referrer_policy_value = get_header_status("referrer-policy")
            permissions_policy_status, permissions_policy_value = get_header_status("permissions-policy")
            
            # Check CSP for frame-ancestors directive
            csp_frame_ancestors_status = "UNKNOWN"
            csp_frame_ancestors_value = None
            if csp_status == "FOUND" and csp_value:
                if "frame-ancestors" in csp_value.lower():
                    csp_frame_ancestors_status = "FOUND"
                    # Extract frame-ancestors value
                    parts = csp_value.split(';')
                    for part in parts:
                        if "frame-ancestors" in part.lower():
                            csp_frame_ancestors_value = part.strip()
                            break
                else:
                    csp_frame_ancestors_status = "MISSING"
            
            data = {
                "hsts": {
                    "status": hsts_status,
                    "value": hsts_value
                },
                "csp": {
                    "status": csp_status,
                    "value": csp_value
                },
                "csp_frame_ancestors": {
                    "status": csp_frame_ancestors_status,
                    "value": csp_frame_ancestors_value
                },
                "x_frame_options": {
                    "status": x_frame_options_status,
                    "value": x_frame_options_value
                },
                "x_content_type_options": {
                    "status": x_content_type_options_status,
                    "value": x_content_type_options_value
                },
                "referrer_policy": {
                    "status": referrer_policy_status,
                    "value": referrer_policy_value
                },
                "permissions_policy": {
                    "status": permissions_policy_status,
                    "value": permissions_policy_value
                },
                "all_headers": headers,
                "redirects": len(response.history),
                "final_url": str(response.url),
                "status_code": response.status_code,
                "note": "HTTP only - HTTPS not available"
            }
            
            execution_time = time.time() - start_time
            log_module_complete(logger, "Headers", domain, execution_time)
            
            return {
                "module": "HEADERS",
                "status": "PARTIAL",
                "severity": "INFO",
                "message": "Headers retrieved via HTTP (HTTPS not available)",
                "execution_time": f"{execution_time:.2f}",
                "confidence": 70,
                "data": data
            }
        except Exception as http_error:
            execution_time = time.time() - start_time
            error_message = str(http_error)
            logger.error(f"Headers: Both HTTPS and HTTP failed - {error_message}")
            log_module_error(logger, "Headers", domain, error_message)
            
            return {
                "module": "HEADERS",
                "status": "FAILED",
                "severity": "ERROR",
                "message": f"Connection failed: {error_message}",
                "execution_time": f"{execution_time:.2f}",
                "confidence": 0,
                "data": {
                    "status": "error",
                    "reason": "Connection failed",
                    "details": error_message
                }
            }
    except Exception as e:
        execution_time = time.time() - start_time
        error_message = str(e)
        
        # Categorize error types
        if "timeout" in error_message.lower() or "timed out" in error_message.lower():
            error_type = "Connection timeout"
        elif "redirect" in error_message.lower():
            error_type = "Redirect loop or too many redirects"
        elif "ssl" in error_message.lower() or "certificate" in error_message.lower():
            error_type = "SSL certificate error"
        else:
            error_type = "Headers analysis error"
        
        logger.error(f"Headers: {error_type} - {error_message}")
        log_module_error(logger, "Headers", domain, error_message)
        
        return {
            "module": "HEADERS",
            "status": "FAILED",
            "severity": "ERROR",
            "message": f"{error_type}: {error_message}",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 0,
            "data": {
                "status": "error",
                "reason": error_type,
                "details": error_message
            }
        }
