import requests
import time
from typing import Dict, Any, List, Set
from utils.logger import log_module_start, log_module_complete, log_module_error, setup_logger


# crt.sh rejects many clients that do not send a browser-like User-Agent
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def _query_crtsh(domain: str, logger) -> List[Dict[str, Any]]:
    """Query crt.sh for certificate entries. Raises on non-200 responses."""
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    logger.info(f"CT: Querying crt.sh for {domain}")
    response = requests.get(url, headers=_HEADERS, timeout=20)
    if response.status_code != 200:
        raise Exception(f"crt.sh returned status {response.status_code}")
    data = response.json()
    return data if isinstance(data, list) else []


def _query_certspotter(domain: str, logger) -> List[Dict[str, Any]]:
    """
    Fallback CT source. CertSpotter's issuances API is free for light use.
    Returns entries normalised into crt.sh-compatible dicts.
    """
    url = (
        "https://api.certspotter.com/v1/issuances"
        f"?domain={domain}&include_subdomains=true&expand=dns_names"
    )
    logger.info(f"CT: Querying certspotter fallback for {domain}")
    response = requests.get(url, headers=_HEADERS, timeout=20)
    if response.status_code != 200:
        raise Exception(f"certspotter returned status {response.status_code}")
    raw = response.json()
    if not isinstance(raw, list):
        return []

    entries: List[Dict[str, Any]] = []
    for item in raw:
        dns_names = item.get("dns_names", []) or []
        cert_meta = item.get("cert_meta", {}) or {}
        entries.append({
            "name_value": "\n".join(dns_names),
            "common_name": dns_names[0] if dns_names else "",
            "issuer_name": item.get("issuer", {}).get("name", "") if isinstance(item.get("issuer"), dict) else "",
            "not_before": cert_meta.get("notBefore", ""),
            "not_after": cert_meta.get("notAfter", ""),
            "serial_number": "",
            "entry_timestamp": "",
        })
    return entries


def _fetch_ct_entries(domain: str, logger) -> tuple[List[Dict[str, Any]], str]:
    """
    Try crt.sh first (with one retry), then fall back to CertSpotter.

    Returns:
        Tuple of (entries, source_name)
    """
    last_error = ""

    # crt.sh attempt (with a single retry, since it is often transiently 404/503)
    for attempt in range(2):
        try:
            entries = _query_crtsh(domain, logger)
            if entries:
                return entries, "crt.sh"
            # Empty but valid response is still a success
            logger.info("CT: crt.sh returned no entries")
            return entries, "crt.sh"
        except Exception as e:
            last_error = str(e)
            logger.warning(f"CT: crt.sh attempt {attempt + 1} failed - {last_error}")
            if attempt == 0:
                time.sleep(1)  # Brief pause before retry

    # CertSpotter fallback
    try:
        entries = _query_certspotter(domain, logger)
        return entries, "certspotter"
    except Exception as e:
        logger.error(f"CT: certspotter fallback also failed - {e}")
        raise Exception(f"All CT log providers failed (crt.sh: {last_error}; certspotter: {e})")


def scan_ct_logs(domain: str) -> Dict[str, Any]:
    """
    Query Certificate Transparency logs to find publicly logged certificates
    and discover subdomains.

    Uses crt.sh (free, no API key required) with a CertSpotter fallback.

    Args:
        domain: Domain to query

    Returns:
        Standardized JSON response with CT log data
    """
    logger = setup_logger()
    start_time = time.time()

    log_module_start(logger, "CT_LOGS", domain)

    try:
        entries, source = _fetch_ct_entries(domain, logger)
        logger.info(f"CT: Received {len(entries)} certificate entries from {source}")

        # Extract unique subdomains and certificate details
        subdomains: Set[str] = set()
        certificates: List[Dict[str, Any]] = []
        seen_names: Set[str] = set()

        for entry in entries:
            # Extract subdomains from name_value
            name_value = entry.get("name_value", "")
            for name in name_value.split("\n"):
                name = name.strip().lower()
                if name and name.endswith(domain):
                    subdomains.add(name)

            # Collect certificate details (limit to recent 50)
            common_name = entry.get("common_name", "")
            issuer = entry.get("issuer_name", "")
            not_before = entry.get("not_before", "")
            not_after = entry.get("not_after", "")
            serial = entry.get("serial_number", "")
            entry_ts = entry.get("entry_timestamp", "")

            cert_key = f"{common_name}:{serial}"
            if cert_key not in seen_names and len(certificates) < 50:
                seen_names.add(cert_key)
                certificates.append({
                    "common_name": common_name,
                    "issuer": issuer,
                    "not_before": not_before,
                    "not_after": not_after,
                    "serial_number": serial,
                    "entry_timestamp": entry_ts
                })

        # Sort subdomains
        sorted_subdomains = sorted(subdomains)

        # Check for wildcard certificates
        wildcard_count = sum(1 for s in sorted_subdomains if s.startswith("*."))

        data = {
            "total_certificates": len(entries),
            "unique_subdomains": len(sorted_subdomains),
            "subdomains": sorted_subdomains[:100],  # Limit to 100
            "wildcard_certificates": wildcard_count,
            "certificates": certificates,
            "source": source
        }

        execution_time = time.time() - start_time
        log_module_complete(logger, "CT_LOGS", domain, execution_time)

        return {
            "module": "CT_LOGS",
            "status": "SUCCESS",
            "severity": "INFO",
            "message": f"Found {len(entries)} certificates and {len(sorted_subdomains)} subdomains",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 90,
            "data": data
        }

    except requests.exceptions.Timeout:
        execution_time = time.time() - start_time
        logger.error(f"CT: CT log query timed out for {domain}")
        log_module_error(logger, "CT_LOGS", domain, "Request timed out")

        return {
            "module": "CT_LOGS",
            "status": "FAILED",
            "severity": "ERROR",
            "message": "Certificate Transparency query timed out",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 0,
            "data": {"status": "error", "reason": "Request timed out"}
        }

    except Exception as e:
        execution_time = time.time() - start_time
        error_message = str(e)
        logger.error(f"CT: Unexpected error - {error_message}")
        log_module_error(logger, "CT_LOGS", domain, error_message)

        return {
            "module": "CT_LOGS",
            "status": "FAILED",
            "severity": "ERROR",
            "message": f"CT log query failed: {error_message}",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 0,
            "data": {"status": "error", "reason": error_message}
        }
