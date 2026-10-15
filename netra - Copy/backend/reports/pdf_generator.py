"""
PDF Report Generator for NETRA

Generates professional PDF security reports using ReportLab.
"""

import os
import time
from datetime import datetime
from typing import Dict, Any
from utils.logger import setup_logger

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_pdf_report(
    scan_data: Dict[str, Any],
    output_dir: str = "reports"
) -> Dict[str, Any]:
    """
    Generate a professional PDF security report.

    Args:
        scan_data: Complete scan data including results, normalized data, and risk assessment
        output_dir: Directory to save the PDF

    Returns:
        Dictionary with status and file path
    """
    logger = setup_logger()

    if not REPORTLAB_AVAILABLE:
        logger.error("PDF: ReportLab is not installed. Run: pip install reportlab")
        return {
            "status": "FAILED",
            "message": "ReportLab is not installed. Install with: pip install reportlab",
            "file_path": None
        }

    start_time = time.time()

    try:
        os.makedirs(output_dir, exist_ok=True)

        domain = scan_data.get("domain", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"netra_{domain}_{timestamp}.pdf"
        filepath = os.path.join(output_dir, filename)

        logger.info(f"PDF: Generating report for {domain}")

        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm
        )

        styles = getSampleStyleSheet()

        # Custom styles
        styles.add(ParagraphStyle(
            name='NetraTitle',
            parent=styles['Title'],
            fontSize=28,
            textColor=colors.HexColor('#06b6d4'),
            spaceAfter=6,
            alignment=TA_CENTER
        ))
        styles.add(ParagraphStyle(
            name='NetraSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#0891b2'),
            spaceBefore=16,
            spaceAfter=8
        ))
        styles.add(ParagraphStyle(
            name='SubHeader',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#0e7490'),
            spaceBefore=10,
            spaceAfter=6
        ))
        # 'BodyText' already exists in the default stylesheet, so customise it
        # in place instead of calling styles.add() (which raises on duplicates).
        body_style = styles['BodyText']
        body_style.fontSize = 10
        body_style.leading = 14
        body_style.spaceAfter = 6
        styles.add(ParagraphStyle(
            name='SmallText',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER
        ))

        elements = []

        # ── Cover Section ─────────────────────────────────────────────
        elements.append(Spacer(1, 2 * inch))
        elements.append(Paragraph("NETRA", styles['NetraTitle']))
        elements.append(Paragraph("Security Assessment Report", styles['NetraSubtitle']))
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(HRFlowable(width="60%", color=colors.HexColor('#06b6d4'), thickness=2))
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(f"<b>Domain:</b> {domain}", styles['BodyText']))
        elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}", styles['BodyText']))

        risk_score = scan_data.get("risk_score", "N/A")
        risk_level = scan_data.get("risk_level", "N/A")
        elements.append(Paragraph(f"<b>Security Score:</b> {risk_score}/100 ({risk_level})", styles['BodyText']))
        elements.append(Paragraph(f"<b>Execution Time:</b> {scan_data.get('execution_time', 'N/A')}s", styles['BodyText']))

        elements.append(Spacer(1, 1 * inch))
        elements.append(Paragraph(
            "CONFIDENTIAL - This report is generated for informational purposes only.",
            styles['SmallText']
        ))
        elements.append(PageBreak())

        # ── Executive Summary ─────────────────────────────────────────
        ai = scan_data.get("ai_summary", {})
        if ai and ai.get("executive_summary"):
            elements.append(Paragraph("Executive Summary", styles['SectionHeader']))
            elements.append(Paragraph(ai["executive_summary"], styles['BodyText']))
            elements.append(Spacer(1, 0.2 * inch))

        # ── Risk Score ────────────────────────────────────────────────
        elements.append(Paragraph("Risk Assessment", styles['SectionHeader']))

        risk_color = {
            "LOW": "#10b981", "MEDIUM": "#f59e0b",
            "HIGH": "#f97316", "CRITICAL": "#ef4444"
        }.get(risk_level, "#64748b")

        risk_table_data = [
            ["Score", "Level", "Summary"],
            [str(risk_score), risk_level, scan_data.get("risk_summary", "N/A")]
        ]
        risk_table = Table(risk_table_data, colWidths=[1.5 * inch, 1.5 * inch, 4.5 * inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#334155')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8fafc')),
        ]))
        elements.append(risk_table)
        elements.append(Spacer(1, 0.2 * inch))

        # ── Findings ──────────────────────────────────────────────────
        deductions = scan_data.get("risk_deductions", [])
        if deductions:
            elements.append(Paragraph("Security Findings", styles['SectionHeader']))
            for d in deductions:
                finding_text = f"<b>{d.get('finding', '')}</b> [{d.get('severity', '')}]"
                elements.append(Paragraph(finding_text, styles['BodyText']))
                if d.get("explanation"):
                    elements.append(Paragraph(d["explanation"], styles['BodyText']))
                if d.get("recommendation"):
                    elements.append(Paragraph(f"<i>Recommendation: {d['recommendation']}</i>", styles['BodyText']))
                elements.append(Spacer(1, 0.1 * inch))

        # ── Module Results ────────────────────────────────────────────
        results = scan_data.get("results", {})

        # WHOIS
        whois = results.get("whois", {})
        if whois.get("status") == "SUCCESS":
            elements.append(Paragraph("WHOIS Information", styles['SectionHeader']))
            wd = whois.get("data", {})
            whois_table_data = [
                ["Field", "Value"],
                ["Registrar", str(wd.get("registrar", "N/A"))],
                ["Created", str(wd.get("created", "N/A"))],
                ["Expires", str(wd.get("expires", "N/A"))],
                ["Nameservers", ", ".join(wd.get("nameservers", [])[:3])],
            ]
            whois_table = Table(whois_table_data, colWidths=[2 * inch, 5.5 * inch])
            whois_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#334155')),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            elements.append(whois_table)
            elements.append(Spacer(1, 0.2 * inch))

        # SSL
        ssl = results.get("ssl", {})
        if ssl.get("status") == "SUCCESS":
            elements.append(Paragraph("SSL Certificate", styles['SectionHeader']))
            sd = ssl.get("data", {})
            ssl_table_data = [
                ["Field", "Value"],
                ["Issuer", str(sd.get("issuer_name", "N/A"))],
                ["Protocol", str(sd.get("protocol", "N/A"))],
                ["Days Remaining", str(sd.get("days_remaining", "N/A"))],
                ["Valid", str(sd.get("valid", "N/A"))],
            ]
            ssl_table = Table(ssl_table_data, colWidths=[2 * inch, 5.5 * inch])
            ssl_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#334155')),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            elements.append(ssl_table)
            elements.append(Spacer(1, 0.2 * inch))

        # ── Recommendations ───────────────────────────────────────────
        if ai and ai.get("recommendations"):
            elements.append(Paragraph("Recommendations", styles['SectionHeader']))
            for i, rec in enumerate(ai["recommendations"], 1):
                elements.append(Paragraph(f"{i}. {rec}", styles['BodyText']))

        # ── Footer ────────────────────────────────────────────────────
        elements.append(Spacer(1, 1 * inch))
        elements.append(HRFlowable(width="100%", color=colors.HexColor('#cbd5e1'), thickness=0.5))
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(
            f"Generated by NETRA v2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')} | Passive security assessment only",
            styles['SmallText']
        ))

        # Build PDF
        doc.build(elements)

        execution_time = time.time() - start_time
        logger.info(f"PDF: Report generated at {filepath} in {execution_time:.2f}s")

        return {
            "status": "SUCCESS",
            "message": "PDF report generated successfully",
            "file_path": filepath,
            "filename": filename,
            "execution_time": f"{execution_time:.2f}"
        }

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"PDF: Report generation failed - {str(e)}")

        return {
            "status": "FAILED",
            "message": f"PDF generation failed: {str(e)}",
            "file_path": None,
            "execution_time": f"{execution_time:.2f}"
        }
