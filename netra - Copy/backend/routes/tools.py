"""
Google Dork and Digital Footprint Routes
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from scanners.google_dork import scan_google_dorks, scan_person_dorks
from scanners.digital_footprint import scan_digital_footprint
from utils.validator import validate_domain
from utils.logger import setup_logger

router = APIRouter()
logger = setup_logger()


class PersonDorkRequest(BaseModel):
    """Request body for person/username OSINT dork generation."""
    name: str
    username: Optional[str] = None
    location: Optional[str] = None
    employer: Optional[str] = None


@router.post("/google-dork")
async def google_dork(domain: str):
    """Generate Google Dork queries for a domain."""
    is_valid, error = validate_domain(domain)
    if not is_valid:
        return {"success": False, "message": error}

    result = scan_google_dorks(domain)
    return {"success": True, "data": result}


@router.post("/digital-footprint")
async def digital_footprint(domain: str):
    """Analyze digital footprint for a domain."""
    is_valid, error = validate_domain(domain)
    if not is_valid:
        return {"success": False, "message": error}

    result = scan_digital_footprint(domain)
    return {"success": True, "data": result}


@router.post("/person-dork")
async def person_dork(request: PersonDorkRequest):
    """
    Generate Google Dork queries to find a person's public social profiles
    from their name (plus optional username, location, and employer).

    Generates query strings only - never executes searches or scrapes data.
    """
    name = (request.name or "").strip()
    if not name:
        return {"success": False, "message": "A person name is required"}

    if len(name) > 120:
        return {"success": False, "message": "Name is too long (max 120 characters)"}

    result = scan_person_dorks(
        name=name,
        username=(request.username or "").strip(),
        location=(request.location or "").strip(),
        employer=(request.employer or "").strip(),
    )
    return {"success": True, "data": result}
