import requests
import time
from typing import Dict, Any, List, Optional
from utils.logger import log_module_start, log_module_complete, log_module_error, setup_logger


def scan_digital_footprint(domain: str) -> Dict[str, Any]:
    """
    Aggregate publicly available information about a domain's digital footprint.

    Uses free, public APIs only. No authentication required.

    The HTTPS homepage is fetched once and shared across the web-presence,
    technology and social checks to avoid redundant network calls. Independent
    lookups (homepage, HTTP redirect, MX records) run in parallel.

    Args:
        domain: Domain to analyze

    Returns:
        Standardized JSON response with digital footprint data
    """
    logger = setup_logger()
    start_time = time.time()

    log_module_start(logger, "DIGITAL_FOOTPRINT", domain)

    # Run the three independent network operations in parallel
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as executor:
        homepage_future = executor.submit(_fetch_homepage, domain, logger)
        redirect_future = executor.submit(_check_http_redirect, domain, logger)
        email_future = executor.submit(_check_email_exposure, domain, logger)

    homepage = homepage_future.result()
    redirect_info = redirect_future.result()
    email_exposure = email_future.result()

    footprint = {
        "web_presence": _analyze_web_presence(homepage, redirect_info),
        "technology_stack": _detect_technology(homepage, logger),
        "social_presence": _check_social_presence(homepage, logger),
        "email_exposure": email_exposure,
    }

    # Calculate visibility score (0-100)
    visibility_score = _calculate_visibility_score(footprint)

    execution_time = time.time() - start_time
    log_module_complete(logger, "DIGITAL_FOOTPRINT", domain, execution_time)

    return {
        "module": "DIGITAL_FOOTPRINT",
        "status": "SUCCESS",
        "severity": "INFO",
        "message": f"Digital footprint analysis complete for {domain}",
        "execution_time": f"{execution_time:.2f}",
        "confidence": 75,
        "data": {
            "domain": domain,
            "visibility_score": visibility_score,
            "visibility_level": (
                "HIGH" if visibility_score >= 70 else
                "MODERATE" if visibility_score >= 40 else "LOW"
            ),
            "footprint": footprint,
            "disclaimer": "This analysis uses only publicly available information."
        }
    }


# ── Helpers ──────────────────────────────────────────────────────────────────

def _fetch_homepage(domain: str, logger) -> Dict[str, Any]:
    """
    Fetch the HTTPS homepage once and capture everything downstream checks need.

    Returns a dict with: ok, status_code, final_url, headers, body (lowercased,
    first 20k chars).
    """
    result = {
        "ok": False,
        "status_code": None,
        "final_url": None,
        "headers": {},
        "body": "",
    }

    try:
        resp = requests.get(f"https://{domain}", timeout=8, allow_redirects=True)
        result["ok"] = resp.status_code < 500
        result["status_code"] = resp.status_code
        result["final_url"] = str(resp.url)
        result["headers"] = {k.lower(): v for k, v in resp.headers.items()}
        result["body"] = resp.text[:20000].lower()
    except Exception as e:
        logger.warning(f"FOOTPRINT: Homepage fetch failed - {e}")

    return result


def _check_http_redirect(domain: str, logger) -> Dict[str, Any]:
    """Check whether plain HTTP redirects to HTTPS / www."""
    info = {
        "http_redirects_to_https": False,
        "www_redirect": False,
    }

    try:
        http_resp = requests.get(f"http://{domain}", timeout=6, allow_redirects=False)
        if http_resp.status_code in (301, 302):
            location = http_resp.headers.get("Location", "")
            if location.startswith("https"):
                info["http_redirects_to_https"] = True
            if "www" in location and domain not in location:
                info["www_redirect"] = True
    except Exception as e:
        logger.warning(f"FOOTPRINT: HTTP redirect check failed - {e}")

    return info


def _analyze_web_presence(homepage: Dict[str, Any], redirect_info: Dict[str, Any]) -> Dict[str, Any]:
    """Build the web-presence summary from the shared homepage + redirect data."""
    presence = {
        "has_website": homepage.get("ok", False),
        "http_redirects_to_https": redirect_info.get("http_redirects_to_https", False),
        "www_redirect": redirect_info.get("www_redirect", False),
    }
    if homepage.get("final_url"):
        presence["final_url"] = homepage["final_url"]
    if homepage.get("status_code") is not None:
        presence["status_code"] = homepage["status_code"]
    return presence


def _detect_technology(homepage: Dict[str, Any], logger) -> Dict[str, Any]:
    """Detect technology stack from the already-fetched homepage headers/body."""
    tech = {
        "server": None,
        "x_powered_by": None,
        "cms_detected": False,
        "cms_hints": []
    }

    if not homepage.get("ok"):
        return tech

    headers = homepage.get("headers", {})
    tech["server"] = headers.get("server")
    tech["x_powered_by"] = headers.get("x-powered-by")

    # Check for CMS hints in headers and body
    body_snippet = homepage.get("body", "")[:5000]
    cms_signals = {
        "WordPress": ["wp-content", "wp-includes", "wordpress"],
        "Drupal": ["drupal", "sites/default"],
        "Joomla": ["joomla", "/media/jui"],
        "Shopify": ["shopify", "cdn.shopify"],
        "Wix": ["wix.com", "static.wixstatic"],
        "Squarespace": ["squarespace", "static1.squarespace"],
    }

    powered_by = (tech["x_powered_by"] or "").lower()
    for cms, keywords in cms_signals.items():
        for kw in keywords:
            if kw in body_snippet or (powered_by and kw in powered_by):
                tech["cms_detected"] = True
                if cms not in tech["cms_hints"]:
                    tech["cms_hints"].append(cms)
                break

    return tech


def _check_social_presence(homepage: Dict[str, Any], logger) -> Dict[str, Any]:
    """Check for social media links using the already-fetched homepage body."""
    social = {
        "known_platforms": [],
        "notes": "Social media presence is estimated from public DNS and web data."
    }

    if not homepage.get("ok"):
        return social

    body = homepage.get("body", "")[:10000]

    platform_urls = {
        "Twitter/X": "twitter.com",
        "Facebook": "facebook.com",
        "LinkedIn": "linkedin.com",
        "Instagram": "instagram.com",
        "YouTube": "youtube.com",
        "GitHub": "github.com",
    }

    for platform, url_hint in platform_urls.items():
        if url_hint in body:
            social["known_platforms"].append(platform)

    return social


def _check_email_exposure(domain: str, logger) -> Dict[str, Any]:
    """Check for email-related exposure signals."""
    exposure = {
        "has_mx_records": False,
        "email_provider": None,
    }

    # Check MX records to identify email provider
    try:
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.timeout = 3
        resolver.lifetime = 3

        try:
            mx_records = resolver.resolve(domain, "MX")
            exposure["has_mx_records"] = True

            mx_hosts = [str(r.exchange).lower() for r in mx_records]
            mx_string = " ".join(mx_hosts)

            if "google" in mx_string or "googlemail" in mx_string:
                exposure["email_provider"] = "Google Workspace"
            elif "outlook" in mx_string or "microsoft" in mx_string:
                exposure["email_provider"] = "Microsoft 365"
            elif "zoho" in mx_string:
                exposure["email_provider"] = "Zoho Mail"
            elif "protonmail" in mx_string or "proton" in mx_string:
                exposure["email_provider"] = "ProtonMail"
            else:
                exposure["email_provider"] = "Custom/Other"
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
    except Exception as e:
        logger.warning(f"FOOTPRINT: Email exposure check failed - {e}")

    return exposure


def _calculate_visibility_score(footprint: Dict[str, Any]) -> int:
    """Calculate a 0-100 visibility score based on footprint data."""
    score = 0

    # Web presence (up to 30 points)
    web = footprint.get("web_presence", {})
    if web.get("has_website"):
        score += 20
    if web.get("http_redirects_to_https"):
        score += 10

    # Technology exposure (up to 20 points)
    tech = footprint.get("technology_stack", {})
    if tech.get("server"):
        score += 5
    if tech.get("x_powered_by"):
        score += 5
    if tech.get("cms_detected"):
        score += 10

    # Social presence (up to 30 points)
    social = footprint.get("social_presence", {})
    platforms = social.get("known_platforms", [])
    score += min(30, len(platforms) * 6)

    # Email exposure (up to 20 points)
    email = footprint.get("email_exposure", {})
    if email.get("has_mx_records"):
        score += 10
    if email.get("email_provider"):
        score += 10

    return min(100, score)
