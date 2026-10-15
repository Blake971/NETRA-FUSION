from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from sqlalchemy.sql import func
from database.database import Base


class Scan(Base):
    """Scan model for storing domain scan results."""
    
    __tablename__ = "scans"
    
    id = Column(String, primary_key=True)
    domain = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")
    risk_score = Column(Integer, nullable=True)
    risk_level = Column(String, nullable=True)
    execution_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Module results as JSON
    whois_json = Column(JSON, nullable=True)
    dns_json = Column(JSON, nullable=True)
    ssl_json = Column(JSON, nullable=True)
    headers_json = Column(JSON, nullable=True)
    ctlogs_json = Column(JSON, nullable=True)
    ip_json = Column(JSON, nullable=True)
    email_json = Column(JSON, nullable=True)
    
    # AI summary
    ai_summary = Column(JSON, nullable=True)
    
    # Report path
    report_path = Column(String, nullable=True)
