"""
Scan History and Report Download Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from database.database import get_db
from models.scan import Scan
from utils.logger import setup_logger
from reports.pdf_generator import generate_pdf_report
import os

router = APIRouter()
logger = setup_logger()


@router.get("/scans")
async def get_scan_history(db: Session = Depends(get_db)):
    """Get all past scans ordered by most recent."""
    try:
        scans = db.query(Scan).order_by(Scan.created_at.desc()).all()
        return {
            "success": True,
            "data": {
                "total": len(scans),
                "scans": [
                    {
                        "scan_id": s.id,
                        "domain": s.domain,
                        "status": s.status,
                        "risk_score": s.risk_score,
                        "risk_level": s.risk_level,
                        "execution_time": s.execution_time,
                        "created_at": s.created_at.isoformat() if s.created_at else None,
                    }
                    for s in scans
                ]
            }
        }
    except Exception as e:
        logger.error(f"History: Failed to retrieve scans - {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve scan history")


@router.get("/scans/{scan_id}")
async def get_scan_results(scan_id: str, db: Session = Depends(get_db)):
    """Get full results for a specific scan."""
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")

        return {
            "success": True,
            "data": {
                "scan_id": scan.id,
                "domain": scan.domain,
                "status": scan.status,
                "risk_score": scan.risk_score,
                "risk_level": scan.risk_level,
                "execution_time": scan.execution_time,
                "created_at": scan.created_at.isoformat() if scan.created_at else None,
                "results": {
                    "whois": scan.whois_json,
                    "dns": scan.dns_json,
                    "ssl": scan.ssl_json,
                    "headers": scan.headers_json,
                    "ct_logs": scan.ctlogs_json,
                    "ip_intelligence": scan.ip_json,
                    "email_security": scan.email_json,
                },
                "ai_summary": scan.ai_summary,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"History: Failed to retrieve scan {scan_id} - {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve scan results")


@router.get("/scans/{scan_id}/report")
async def download_report(scan_id: str, db: Session = Depends(get_db)):
    """Download PDF report for a scan."""
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")

        # If report already exists, return it
        if scan.report_path and os.path.exists(scan.report_path):
            return FileResponse(
                scan.report_path,
                media_type="application/pdf",
                filename=f"netra_{scan.domain}_report.pdf"
            )

        # Generate new report
        scan_data = {
            "domain": scan.domain,
            "risk_score": scan.risk_score,
            "risk_level": scan.risk_level,
            "execution_time": scan.execution_time,
            "risk_summary": "",
            "risk_deductions": [],
            "results": {
                "whois": scan.whois_json,
                "dns": scan.dns_json,
                "ssl": scan.ssl_json,
                "headers": scan.headers_json,
            },
            "ai_summary": scan.ai_summary,
        }

        result = generate_pdf_report(scan_data)

        if result["status"] == "SUCCESS":
            # Save report path
            scan.report_path = result["file_path"]
            db.commit()

            return FileResponse(
                result["file_path"],
                media_type="application/pdf",
                filename=result["filename"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report: Failed to generate report for scan {scan_id} - {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")


@router.delete("/scans/{scan_id}")
async def delete_scan(scan_id: str, db: Session = Depends(get_db)):
    """Delete a scan and its associated report."""
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")

        # Delete report file if exists
        if scan.report_path and os.path.exists(scan.report_path):
            os.remove(scan.report_path)

        db.delete(scan)
        db.commit()

        return {"success": True, "message": "Scan deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"History: Failed to delete scan {scan_id} - {e}")
        raise HTTPException(status_code=500, detail="Failed to delete scan")
