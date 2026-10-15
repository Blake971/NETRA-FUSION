"""
Gemini AI Integration for NETRA

Generates executive, technical, and business summaries from scan results.
Gemini NEVER calculates risk or identifies vulnerabilities - it only explains.
"""

import time
import json
from typing import Dict, Any, Optional
from utils.logger import setup_logger

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from config.settings import settings


SYSTEM_PROMPT = """You are NETRA AI, a cybersecurity analyst assistant.

Your role:
- Explain security scan findings in clear, simple language.
- Provide actionable recommendations.
- Generate executive, technical, and business summaries.

Rules you MUST follow:
- NEVER calculate or change risk scores.
- NEVER identify vulnerabilities that were not already reported.
- NEVER perform your own security analysis.
- ONLY explain and summarize the data provided to you.
- Be accurate and concise.
- Use plain language for executive summaries, technical terms for technical summaries.
"""


def generate_ai_summary(scan_results: Dict[str, Any], risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AI-powered summaries for scan results using Gemini.

    Args:
        scan_results: Dictionary with raw results from all scanners
        risk_assessment: Dictionary with risk score and deductions

    Returns:
        Dictionary with executive_summary, technical_summary, business_summary,
        recommendations, and warnings
    """
    logger = setup_logger()

    if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_api_key_here":
        logger.warning("AI: Gemini API key not configured, returning fallback summaries")
        return _fallback_summary(risk_assessment)

    if genai is None:
        logger.warning("AI: google-generativeai package not installed, returning fallback summaries")
        return _fallback_summary(risk_assessment)

    start_time = time.time()

    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Build context from scan results
        context = _build_context(scan_results, risk_assessment)

        # Generate summaries with a single prompt
        prompt = _build_prompt(context, risk_assessment)

        logger.info("AI: Sending request to Gemini API")
        response = model.generate_content(prompt)
        ai_text = response.text

        logger.info(f"AI: Gemini responded with {len(ai_text)} characters")

        # Parse the response
        summaries = _parse_response(ai_text)

        execution_time = time.time() - start_time
        logger.info(f"AI: Summary generation completed in {execution_time:.2f}s")

        return {
            "status": "SUCCESS",
            "executive_summary": summaries.get("executive_summary", ""),
            "technical_summary": summaries.get("technical_summary", ""),
            "business_summary": summaries.get("business_summary", ""),
            "recommendations": summaries.get("recommendations", []),
            "warnings": summaries.get("warnings", []),
            "execution_time": f"{execution_time:.2f}",
            "model": "gemini-2.0-flash"
        }

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"AI: Gemini API error - {str(e)}")

        return {
            "status": "FALLBACK",
            "executive_summary": _fallback_summary(risk_assessment)["executive_summary"],
            "technical_summary": _fallback_summary(risk_assessment)["technical_summary"],
            "business_summary": _fallback_summary(risk_assessment)["business_summary"],
            "recommendations": _fallback_summary(risk_assessment)["recommendations"],
            "warnings": _fallback_summary(risk_assessment)["warnings"],
            "execution_time": f"{execution_time:.2f}",
            "model": "fallback",
            "error": str(e)
        }


def _build_context(scan_results: Dict[str, Any], risk_assessment: Dict[str, Any]) -> str:
    """Build a condensed context string from scan results for the AI prompt."""
    parts = []

    # Risk
    parts.append(f"Risk Score: {risk_assessment.get('score', 'N/A')}/100 ({risk_assessment.get('level', 'N/A')})")

    # Deductions
    deductions = risk_assessment.get("deductions", [])
    if deductions:
        parts.append("Findings:")
        for d in deductions:
            parts.append(f"  - {d.get('finding', '')} (Severity: {d.get('severity', '')})")

    # WHOIS
    whois = scan_results.get("whois", {})
    if whois.get("status") == "SUCCESS":
        wd = whois.get("data", {})
        parts.append(f"WHOIS: Registrar={wd.get('registrar')}, Created={wd.get('created')}, Expires={wd.get('expires')}")

    # DNS
    dns = scan_results.get("dns", {})
    if dns.get("status") == "SUCCESS":
        dd = dns.get("data", {})
        parts.append(f"DNS: A records={len(dd.get('a_records', []))}, MX records={len(dd.get('mx_records', []))}, NS records={len(dd.get('ns_records', []))}")

    # SSL
    ssl = scan_results.get("ssl", {})
    if ssl.get("status") == "SUCCESS":
        sd = ssl.get("data", {})
        parts.append(f"SSL: Issuer={sd.get('issuer_name')}, Days remaining={sd.get('days_remaining')}, Protocol={sd.get('protocol')}, Valid={sd.get('valid')}")

    # Headers
    headers = scan_results.get("headers", {})
    if headers.get("status") in ("SUCCESS", "PARTIAL"):
        hd = headers.get("data", {})
        header_statuses = []
        for h in ["hsts", "csp", "x_frame_options", "x_content_type_options"]:
            hdata = hd.get(h, {})
            if isinstance(hdata, dict):
                header_statuses.append(f"{h}={hdata.get('status', 'UNKNOWN')}")
        parts.append(f"Headers: {', '.join(header_statuses)}")

    # Email
    email = scan_results.get("email_security", {})
    if email.get("data"):
        ed = email["data"]
        parts.append(f"Email Security: SPF={'Present' if ed.get('spf', {}).get('present') else 'Missing'}, DMARC={'Present' if ed.get('dmarc', {}).get('present') else 'Missing'}, DKIM={'Present' if ed.get('dkim', {}).get('present') else 'Missing'}")

    # CT Logs
    ct = scan_results.get("ct_logs", {})
    if ct.get("status") == "SUCCESS":
        ctd = ct.get("data", {})
        parts.append(f"CT Logs: {ctd.get('total_certificates', 0)} certificates, {ctd.get('unique_subdomains', 0)} subdomains found")

    return "\n".join(parts)


def _build_prompt(context: str, risk_assessment: Dict[str, Any]) -> str:
    """Build the full prompt for Gemini."""
    return f"""Based on the following security scan data, generate three summaries and recommendations.

SCAN DATA:
{context}

Respond in EXACTLY this JSON format (no markdown, no code fences, just raw JSON):
{{
  "executive_summary": "A 2-3 sentence summary for non-technical stakeholders. Plain language only.",
  "technical_summary": "A 3-5 sentence summary for security professionals. Use technical terms.",
  "business_summary": "A 2-3 sentence summary focused on business impact and compliance.",
  "recommendations": ["Prioritized list of specific actions to improve security"],
  "warnings": ["Any urgent warnings that need immediate attention"]
}}
"""


def _parse_response(ai_text: str) -> Dict[str, Any]:
    """Parse Gemini's response into structured data."""
    # Clean up response - remove markdown code fences if present
    cleaned = ai_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first and last lines (code fences)
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # If JSON parsing fails, treat the whole response as executive summary
        return {
            "executive_summary": cleaned,
            "technical_summary": "",
            "business_summary": "",
            "recommendations": [],
            "warnings": []
        }


def _fallback_summary(risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
    """Generate fallback summaries when AI is unavailable."""
    score = risk_assessment.get("score", 0)
    level = risk_assessment.get("level", "UNKNOWN")
    deductions = risk_assessment.get("deductions", [])

    if score >= 80:
        exec_summary = "The domain demonstrates a reasonable security posture. Most critical configurations are in place."
        tech_summary = f"Security score: {score}/100 ({level}). The domain passes most passive security checks."
        biz_summary = "The domain meets basic security expectations. Continue monitoring for changes."
    elif score >= 60:
        exec_summary = "The domain has some security configurations but improvements are recommended."
        tech_summary = f"Security score: {score}/100 ({level}). Several security controls are missing or misconfigured."
        biz_summary = "The domain has moderate security gaps that could expose the organization to risk."
    elif score >= 40:
        exec_summary = "The domain has significant security concerns that should be addressed."
        tech_summary = f"Security score: {score}/100 ({level}). Multiple critical security controls are missing."
        biz_summary = "The domain has notable security deficiencies that increase organizational risk."
    else:
        exec_summary = "The domain has critical security issues requiring immediate attention."
        tech_summary = f"Security score: {score}/100 ({level}). Fundamental security controls are absent."
        biz_summary = "The domain presents significant security risk to the organization."

    recommendations = []
    warnings = []
    for d in deductions:
        rec = d.get("recommendation")
        if rec:
            recommendations.append(rec)
        if d.get("severity") in ("CRITICAL", "HIGH"):
            warnings.append(d.get("finding", "Security issue detected"))

    if not recommendations:
        recommendations.append("Continue monitoring your domain's security posture regularly.")

    return {
        "status": "FALLBACK",
        "executive_summary": exec_summary,
        "technical_summary": tech_summary,
        "business_summary": biz_summary,
        "recommendations": recommendations,
        "warnings": warnings,
        "execution_time": "0.00",
        "model": "fallback"
    }
