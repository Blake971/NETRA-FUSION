from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from scanners.whois import scan_whois
from scanners.dns import scan_dns
from scanners.ssl import scan_ssl
from scanners.headers import scan_headers
from scanners.ct_logs import scan_ct_logs
from scanners.email_security import scan_email_security
from scanners.google_dork import scan_google_dorks
from scanners.digital_footprint import scan_digital_footprint
from utils.validator import validate_domain
from utils.logger import setup_logger
from utils.risk_engine import calculate_risk_score
from ai.gemini import generate_ai_summary
from database.database import SessionLocal
from models.scan import Scan
from utils.normalization import (
    normalize_infrastructure_intelligence,
    normalize_whois,
    normalize_dns,
    normalize_ssl,
    normalize_headers
)

router = APIRouter()
logger = setup_logger()


class ScanRequest(BaseModel):
    domain: str
    options: Optional[dict] = None


class ScanResponse(BaseModel):
    success: bool
    data: dict


def validate_consistency(risk_assessment, normalized_results):
    """Validate risk deductions against normalized results to catch contradictions."""
    try:
        deductions = risk_assessment.get('deductions', [])
        if not deductions:
            return

        header_summary = (
            normalized_results
            .get('headers', {})
            .get('simple_summary', {})
        )

        keyword_to_key = {
            'HSTS': 'hsts',
            'CSP': 'csp',
        }

        filtered_deductions = []
        removed_any = False

        for deduction in deductions:
            finding = str(deduction.get('finding', ''))
            evidence = str(deduction.get('evidence', ''))
            combined = f"{finding} {evidence}".upper()

            dominated = False
            for keyword, summary_key in keyword_to_key.items():
                if keyword in combined:
                    status = str(header_summary.get(summary_key, '')).upper()
                    if status == 'FOUND':
                        logger.warning(
                            f"Consistency contradiction detected: deduction "
                            f"claims missing {keyword} but normalized result "
                            f"shows {summary_key}={status}. Removing deduction."
                        )
                        dominated = True
                        removed_any = True
                        break

            if not dominated:
                filtered_deductions.append(deduction)

        if removed_any:
            new_score = 100
            for d in filtered_deductions:
                new_score -= d.get('points', 0)
            new_score = max(0, min(100, new_score))

            risk_assessment['deductions'] = filtered_deductions
            risk_assessment['score'] = new_score

            if new_score >= 80:
                risk_assessment['level'] = 'LOW'
                risk_assessment['color'] = 'green'
            elif new_score >= 50:
                risk_assessment['level'] = 'MEDIUM'
                risk_assessment['color'] = 'yellow'
            else:
                risk_assessment['level'] = 'HIGH'
                risk_assessment['color'] = 'red'

            logger.warning(
                f"Risk score recalculated to {new_score} after removing "
                f"contradictory deductions."
            )

    except Exception as e:
        logger.error(f"Consistency validation failed (non-fatal): {e}")


async def run_scanner(scanner_func, domain, scanner_name, executor, **kwargs):
    """Run a scanner in a thread pool to avoid blocking."""
    loop = asyncio.get_event_loop()
    try:
        bound_func = partial(scanner_func, domain, **kwargs)
        result = await loop.run_in_executor(executor, bound_func)
        return result
    except Exception as e:
        logger.error(f"{scanner_name} scanner error: {str(e)}")
        return {
            "module": scanner_name.upper(),
            "status": "FAILED",
            "severity": "ERROR",
            "message": str(e),
            "execution_time": "0.00",
            "data": {}
        }


def save_scan_to_db(scan_id, domain, results, risk_assessment, ai_summary, execution_time):
    """Persist scan results to the database."""
    try:
        db = SessionLocal()
        scan = Scan(
            id=scan_id,
            domain=domain,
            status="completed",
            risk_score=risk_assessment.get('score'),
            risk_level=risk_assessment.get('level'),
            execution_time=float(execution_time),
            completed_at=datetime.utcnow(),
            whois_json=results.get("whois"),
            dns_json=results.get("dns"),
            ssl_json=results.get("ssl"),
            headers_json=results.get("headers"),
            ctlogs_json=results.get("ct_logs"),
            ip_json=results.get("dns", {}).get("data", {}).get("infrastructure_intelligence") if results.get("dns", {}).get("data") else None,
            email_json=results.get("email_security"),
            ai_summary=ai_summary,
        )
        db.add(scan)
        db.commit()
        logger.info(f"Scan {scan_id} saved to database")
        db.close()
    except Exception as e:
        logger.error(f"Failed to save scan to database: {e}")


@router.post("/scan")
async def start_scan(request: ScanRequest) -> ScanResponse:
    """
    Start a new domain security scan with parallel execution of all modules.
    """
    # Validate domain
    is_valid, error = validate_domain(request.domain)
    if not is_valid:
        raise HTTPException(status_code=400, detail={"success": False, "message": error})

    # Generate scan ID
    scan_id = str(uuid.uuid4())
    domain = request.domain.lower()

    logger.info(f"Starting parallel scan {scan_id} for domain: {domain}")

    start_time = time.time()

    # Extract scan options
    options = request.options or {}
    dns_timeout = options.get('dns_timeout', 5.0)
    use_dns_cache = options.get('use_dns_cache', True)

    # Run all scanners in parallel. The digital-footprint HTTP lookups and the
    # Google Dork generator overlap with the slower WHOIS/DNS/geolocation calls,
    # so a single batch is faster than running them in sequential phases.
    with ThreadPoolExecutor(max_workers=8) as executor:
        tasks = [
            run_scanner(scan_whois, domain, "WHOIS", executor),
            run_scanner(scan_dns, domain, "DNS", executor, timeout=dns_timeout, use_cache=use_dns_cache),
            run_scanner(scan_ssl, domain, "SSL", executor),
            run_scanner(scan_headers, domain, "HEADERS", executor),
            run_scanner(scan_ct_logs, domain, "CT_LOGS", executor),
            run_scanner(scan_email_security, domain, "EMAIL_SECURITY", executor, timeout=dns_timeout),
            run_scanner(scan_google_dorks, domain, "GOOGLE_DORK", executor),
            run_scanner(scan_digital_footprint, domain, "DIGITAL_FOOTPRINT", executor),
        ]

        results_list = await asyncio.gather(*tasks)

    results = {
        "whois": results_list[0],
        "dns": results_list[1],
        "ssl": results_list[2],
        "headers": results_list[3],
        "ct_logs": results_list[4],
        "email_security": results_list[5],
        "google_dork": results_list[6],
        "digital_footprint": results_list[7],
    }

    # Normalize results
    normalized_results = {
        "whois": normalize_whois(results["whois"]),
        "dns": normalize_dns(results["dns"]),
        "ssl": normalize_ssl(results["ssl"]),
        "headers": normalize_headers(results["headers"])
    }

    # Normalize infrastructure intelligence from DNS
    if results["dns"].get("status") == "SUCCESS":
        dns_data = results["dns"].get("data", {})
        normalized_infrastructure = normalize_infrastructure_intelligence(dns_data)
        normalized_results["infrastructure_intelligence"] = normalized_infrastructure

    # Calculate risk score
    risk_assessment = calculate_risk_score(results)

    # Validate consistency
    validate_consistency(risk_assessment, normalized_results)

    # Generate AI summary
    ai_summary = generate_ai_summary(results, risk_assessment)

    total_time = time.time() - start_time

    logger.info(f"Parallel scan {scan_id} completed in {total_time:.2f}s")

    # Save to database (non-blocking)
    save_scan_to_db(scan_id, domain, results, risk_assessment, ai_summary, total_time)

    return ScanResponse(
        success=True,
        data={
            "scan_id": scan_id,
            "domain": domain,
            "status": "completed",
            "execution_time": f"{total_time:.2f}",
            "results": results,
            "normalized": normalized_results,
            "risk_score": risk_assessment['score'],
            "risk_level": risk_assessment['level'],
            "risk_color": risk_assessment['color'],
            "risk_summary": risk_assessment['summary'],
            "risk_deductions": risk_assessment['deductions'],
            "score_breakdown": risk_assessment.get('score_breakdown', {}),
            "ai_summary": ai_summary,
        }
    )


@router.get("/scan/{scan_id}")
async def get_scan(scan_id: str) -> ScanResponse:
    """Get scan results by ID from database."""
    try:
        db = SessionLocal()
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        db.close()

        if not scan:
            return ScanResponse(
                success=False,
                data={"message": "Scan not found", "scan_id": scan_id}
            )

        return ScanResponse(
            success=True,
            data={
                "scan_id": scan.id,
                "domain": scan.domain,
                "status": scan.status,
                "risk_score": scan.risk_score,
                "risk_level": scan.risk_level,
                "execution_time": scan.execution_time,
                "created_at": scan.created_at.isoformat() if scan.created_at else None,
                "ai_summary": scan.ai_summary,
            }
        )
    except Exception as e:
        logger.error(f"Failed to retrieve scan {scan_id}: {e}")
        return ScanResponse(
            success=False,
            data={"message": str(e), "scan_id": scan_id}
        )
