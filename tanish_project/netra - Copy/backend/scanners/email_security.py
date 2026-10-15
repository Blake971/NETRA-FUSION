import dns.resolver
import time
import re
from typing import Dict, Any, List
from utils.logger import log_module_start, log_module_complete, log_module_error, setup_logger


def scan_email_security(domain: str, timeout: float = 3.0) -> Dict[str, Any]:
    """
    Check email authentication records: SPF, DKIM, and DMARC.

    Reads DNS TXT records and parses each authentication protocol.

    Args:
        domain: Domain to check
        timeout: DNS query timeout in seconds

    Returns:
        Standardized JSON response with email security data
    """
    logger = setup_logger()
    start_time = time.time()

    log_module_start(logger, "EMAIL_SECURITY", domain)

    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = timeout

    # Run SPF, DMARC and DKIM checks in parallel (DKIM fans out internally too)
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as executor:
        spf_future = executor.submit(_check_spf, resolver, domain, logger)
        dmarc_future = executor.submit(_check_dmarc, resolver, domain, logger)
        dkim_future = executor.submit(_check_dkim, resolver, domain, logger)

    results = {
        "spf": spf_future.result(),
        "dmarc": dmarc_future.result(),
        "dkim": dkim_future.result(),
    }

    # Overall status
    all_present = all(r["present"] for r in results.values())
    none_present = not any(r["present"] for r in results.values())

    execution_time = time.time() - start_time
    log_module_complete(logger, "EMAIL_SECURITY", domain, execution_time)

    if all_present:
        status = "SUCCESS"
        message = "All email authentication records (SPF, DMARC, DKIM) are configured"
    elif none_present:
        status = "WARNING"
        message = "No email authentication records found"
    else:
        status = "PARTIAL"
        present = [k.upper() for k, v in results.items() if v["present"]]
        missing = [k.upper() for k, v in results.items() if not v["present"]]
        message = f"Present: {', '.join(present)} | Missing: {', '.join(missing)}"

    return {
        "module": "EMAIL_SECURITY",
        "status": status,
        "severity": "INFO" if all_present else "WARNING",
        "message": message,
        "execution_time": f"{execution_time:.2f}",
        "confidence": 95,
        "data": results
    }


# ── SPF ──────────────────────────────────────────────────────────────────────

def _check_spf(resolver: dns.resolver.Resolver, domain: str, logger) -> Dict[str, Any]:
    """Check SPF TXT record."""
    try:
        answers = resolver.resolve(domain, "TXT")
        for rdata in answers:
            txt = str(rdata).strip('"')
            if txt.lower().startswith("v=spf1"):
                logger.info(f"EMAIL: SPF record found for {domain}")
                return {
                    "present": True,
                    "record": txt,
                    "status": _evaluate_spf(txt),
                    "explanation": _explain_spf(txt)
                }
        logger.info(f"EMAIL: No SPF record found for {domain}")
        return {"present": False, "record": None, "status": "MISSING",
                "explanation": "No SPF record found - email spoofing protection is missing"}
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return {"present": False, "record": None, "status": "MISSING",
                "explanation": "No SPF record found"}
    except Exception as e:
        logger.warning(f"EMAIL: SPF check failed - {e}")
        return {"present": False, "record": None, "status": "ERROR",
                "explanation": f"SPF check failed: {str(e)}"}


def _evaluate_spf(record: str) -> str:
    """Evaluate SPF record quality."""
    record_lower = record.lower()
    if "~all" in record_lower:
        return "SOFT_FAIL"
    if "-all" in record_lower:
        return "HARD_FAIL"
    if "+all" in record_lower:
        return "PERMIT_ALL"
    if "all" not in record_lower:
        return "NO_ALL_MECHANISM"
    return "CONFIGURED"


def _explain_spf(record: str) -> str:
    """Generate plain-English SPF explanation."""
    record_lower = record.lower()
    if "-all" in record_lower:
        return "SPF is configured with a strict policy (-all). Servers not listed will be rejected."
    if "~all" in record_lower:
        return "SPF is configured with a soft policy (~all). Unauthorized servers are marked but may still be accepted."
    if "+all" in record_lower:
        return "SPF allows all servers to send email for this domain - this is insecure."
    return "SPF record is present."


# ── DMARC ────────────────────────────────────────────────────────────────────

def _check_dmarc(resolver: dns.resolver.Resolver, domain: str, logger) -> Dict[str, Any]:
    """Check DMARC TXT record at _dmarc.domain."""
    dmarc_domain = f"_dmarc.{domain}"
    try:
        answers = resolver.resolve(dmarc_domain, "TXT")
        for rdata in answers:
            txt = str(rdata).strip('"')
            if txt.lower().startswith("v=dmarc1"):
                logger.info(f"EMAIL: DMARC record found for {domain}")
                return {
                    "present": True,
                    "record": txt,
                    "policy": _extract_dmarc_policy(txt),
                    "explanation": _explain_dmarc(txt)
                }
        logger.info(f"EMAIL: No DMARC record found for {domain}")
        return {"present": False, "record": None, "policy": "MISSING",
                "explanation": "No DMARC record found"}
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return {"present": False, "record": None, "policy": "MISSING",
                "explanation": "No DMARC record found"}
    except Exception as e:
        logger.warning(f"EMAIL: DMARC check failed - {e}")
        return {"present": False, "record": None, "policy": "ERROR",
                "explanation": f"DMARC check failed: {str(e)}"}


def _extract_dmarc_policy(record: str) -> str:
    """Extract DMARC policy (p=) from record."""
    match = re.search(r'\bp=(\w+)', record, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return "UNKNOWN"


def _explain_dmarc(record: str) -> str:
    """Generate plain-English DMARC explanation."""
    policy = _extract_dmarc_policy(record)
    if policy == "REJECT":
        return "DMARC is configured with a strict reject policy. Emails failing authentication will be rejected."
    if policy == "QUARANTINE":
        return "DMARC is configured with a quarantine policy. Suspicious emails will be marked as spam."
    if policy == "NONE":
        return "DMARC is present but set to monitoring mode (p=none). No enforcement is active."
    return "DMARC record is present."


# ── DKIM ─────────────────────────────────────────────────────────────────────

# Common DKIM selectors to check (kept short for performance)
COMMON_SELECTORS = [
    "default", "google", "dkim", "mail", "smtp", "s1", "s2",
    "selector1", "selector2", "k1", "mandrill", "protonmail",
    "zoho", "amazonses", "sendgrid", "mailgun"
]


def _check_dkim(resolver: dns.resolver.Resolver, domain: str, logger) -> Dict[str, Any]:
    """Check DKIM TXT records across common selectors (parallelised)."""
    found_selectors: List[Dict[str, str]] = []

    def probe(selector: str):
        """Probe a single DKIM selector. Returns a dict or None."""
        dkim_domain = f"{selector}._domainkey.{domain}"
        try:
            answers = resolver.resolve(dkim_domain, "TXT")
            for rdata in answers:
                txt = str(rdata).strip('"')
                if "v=dkim1" in txt.lower() or "p=" in txt:
                    return {
                        "selector": selector,
                        "record": txt[:200]  # Truncate long records
                    }
        except Exception:
            return None
        return None

    # Query all selectors in parallel to avoid 16 x timeout delays
    from concurrent.futures import ThreadPoolExecutor, as_completed
    try:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(probe, s) for s in COMMON_SELECTORS]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    found_selectors.append(result)
                    logger.info(f"EMAIL: DKIM found - selector: {result['selector']}")
    except Exception as e:
        logger.warning(f"EMAIL: DKIM parallel check failed - {e}")

    if found_selectors:
        return {
            "present": True,
            "selectors_found": len(found_selectors),
            "selectors": found_selectors,
            "explanation": f"DKIM is configured with {len(found_selectors)} selector(s): {', '.join(s['selector'] for s in found_selectors)}"
        }

    logger.info(f"EMAIL: No DKIM records found for {domain}")
    return {
        "present": False,
        "selectors_found": 0,
        "selectors": [],
        "explanation": "No DKIM records found with common selectors. DKIM may use a custom selector."
    }
