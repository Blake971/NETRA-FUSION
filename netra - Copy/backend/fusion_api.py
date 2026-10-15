"""Local competition workspace: durable jobs and evidence-backed assessments."""
import asyncio
import json
import os
import sqlite3
import uuid
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from fusion_engine import analyze, collect, demo_results, evidence_digest, normalize_domain, now, public_addresses
from fusion_ai import configured, explain
from fusion_explain import interpret, audience_report
from fusion_footprint import footprint
from fusion_compare import compare
from fusion_breach import check_email, check_breach, get_stats
from starlette.middleware.trustedhost import TrustedHostMiddleware
import sys
from pathlib import Path

# Add scanners directory to path
scanners_path = Path(__file__).parent / 'scanners'
sys.path.insert(0, str(scanners_path))

try:
    from google_dork import scan_google_dorks, scan_person_dorks
except ImportError:
    scan_google_dorks = None
    scan_person_dorks = None

DB = Path(os.environ.get('NETRA_DB', Path(__file__).with_name('fusion.db')))
TASKS = set()
LIMIT = asyncio.Semaphore(3)

@contextmanager
def connection():
    db = sqlite3.connect(DB, timeout=10)
    try:
        with db:
            db.execute('CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, document TEXT NOT NULL)')
            yield db
    finally:
        db.close()

def save(case):
    with connection() as db:
        db.execute('INSERT OR REPLACE INTO cases VALUES (?, ?)', (case['id'], json.dumps(case)))

def retrieve(identifier):
    with connection() as db:
        row = db.execute('SELECT document FROM cases WHERE id = ?', (identifier,)).fetchone()
    if not row:
        raise HTTPException(404, 'Assessment not found')
    case = json.loads(row[0])
    if case['status'] == 'COMPLETED':
        case['audience'] = interpret(case)
        case['footprint'] = footprint(case)
    return case

@asynccontextmanager
async def lifespan(app):
    with connection() as db:
        for identifier, document in db.execute('SELECT id, document FROM cases').fetchall():
            case = json.loads(document)
            if case['status'] in ('QUEUED', 'RUNNING'):
                case.update(status='FAILED', error='Server restarted during collection. Start a new assessment.')
                db.execute('UPDATE cases SET document = ? WHERE id = ?', (json.dumps(case), identifier))
    yield
    for task in list(TASKS):
        task.cancel()
    await asyncio.gather(*TASKS, return_exceptions=True)

app = FastAPI(title='NETRA Fusion', version='3.0', lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['localhost', '127.0.0.1', 'testserver'])

class Request(BaseModel):
    domain: str = Field(default='northstar.example', max_length=300)
    demo: bool = False
    demo_profile: Literal['baseline', 'improved'] = 'baseline'

class EmailCheckRequest(BaseModel):
    email: str = Field(default='', max_length=254)
    consent: bool = False

class BreachCheckRequest(BaseModel):
    query: str = Field(default='', max_length=300)
    search_type: Literal['email_address', 'username', 'domain'] = 'email_address'
    consent: bool = False

class PersonDorkRequest(BaseModel):
    name: str = Field(default='', max_length=120)
    username: str = Field(default='', max_length=100)
    location: str = Field(default='', max_length=100)
    employer: str = Field(default='', max_length=100)

class DomainDorkRequest(BaseModel):
    domain: str = Field(default='', max_length=300)

async def run(case):
    async with LIMIT:
        try:
            case.update(status='RUNNING', progress=10)
            save(case)
            results = {}
            if case['demo']:
                results = demo_results(case.get('demo_profile') == 'improved')
            else:
                await asyncio.to_thread(public_addresses, case['domain'])
                async def one(name):
                    return name, await asyncio.to_thread(collect, name, case['domain'])
                for future in asyncio.as_completed([one(name) for name in ('web', 'dns', 'certificates', 'google_dork')]):
                    name, result = await future
                    results[name] = result
                    case['events'].append({'time': now(), 'stage': 'Collect', 'message': name + ': ' + result['status']})
                    case['progress'] += 13  # 4 collectors = 52% total for collection phase
                    save(case)
                # Get IP addresses from DNS results for geolocation
                ip_addresses = results.get('dns', {}).get('data', {}).get('A', []) + results.get('dns', {}).get('data', {}).get('AAAA', [])
                if ip_addresses:
                    geo_result = await asyncio.to_thread(collect, 'geolocation', ip_addresses)
                    results['geolocation'] = geo_result
                    case['events'].append({'time': now(), 'stage': 'Collect', 'message': 'geolocation: ' + geo_result['status']})
                    case['progress'] += 13  # Geolocation = 13% (total 65% for collection)
            case['events'].append({'time': now(), 'stage': 'Challenge', 'message': 'Check evidence coverage and suppress unsupported deductions.'})
            assessment = analyze(case['domain'], results)
            case.update(status='COMPLETED', progress=100, completed_at=now(), results=results,
                        assessment=assessment, evidence_sha256=evidence_digest(results))
            case['events'].append({'time': now(), 'stage': 'Report', 'message': 'Evidence bundle and prioritized remediation ready.'})
            save(case)
        except Exception as exc:
            case.update(status='FAILED', error=str(exc) if isinstance(exc, ValueError) else 'Collection failed. Retry the assessment.', progress=100)
            save(case)

@app.get('/api/health')
def health():
    return {'status': 'ok', 'version': '3.0', 'reasoning': 'deterministic', 'ai_available': configured(), 'live_collectors': ['DNS', 'HTTPS/TLS', 'certificate transparency']}

@app.post('/api/email-check')
async def email_check(request: EmailCheckRequest):
    return await check_email(request.email, request.consent)

@app.post('/api/breach-check')
async def breach_check(request: BreachCheckRequest):
    return await check_breach(request.query, request.search_type, request.consent)

@app.get('/api/breach-stats')
async def breach_stats():
    return await get_stats()

@app.post('/api/person-dork')
async def person_dork(request: PersonDorkRequest):
    """Generate Google Dork queries to find a person's public social profiles.
    
    Generates query strings only - never executes searches or scrapes data.
    """
    if scan_person_dorks is None:
        raise HTTPException(503, 'Person dork scanner module not available.')
    
    name = request.name.strip()
    if not name:
        raise HTTPException(422, 'A person name is required.')
    
    if len(name) > 120:
        raise HTTPException(422, 'Name is too long (max 120 characters).')
    
    try:
        result = await asyncio.to_thread(
            scan_person_dorks,
            name=name,
            username=request.username.strip(),
            location=request.location.strip(),
            employer=request.employer.strip()
        )
        return result
    except Exception as exc:
        raise HTTPException(500, f'Person dork generation failed: {str(exc)}')

@app.post('/api/domain-dork')
async def domain_dork(request: DomainDorkRequest):
    """Generate Google Dork queries for a domain.

    Generates query strings only - never executes searches or scrapes data.
    """
    if scan_google_dorks is None:
        raise HTTPException(503, 'Domain dork scanner module not available.')

    domain = request.domain.strip()
    if not domain:
        raise HTTPException(422, 'A domain is required.')

    try:
        result = await asyncio.to_thread(scan_google_dorks, domain)
        return result
    except Exception as exc:
        raise HTTPException(500, f'Domain dork generation failed: {str(exc)}')

@app.post('/api/cases', status_code=202)
async def create(request: Request):
    if len(TASKS) >= 12:
        raise HTTPException(429, 'Assessment queue is full. Try again shortly.')
    try:
        domain = 'northstar.example' if request.demo else normalize_domain(request.domain)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    case = {'id': str(uuid.uuid4()), 'domain': domain, 'demo': request.demo, 'demo_profile': request.demo_profile if request.demo else None, 'created_at': now(),
            'status': 'QUEUED', 'progress': 0, 'events': [{'time': now(), 'stage': 'Discover', 'message': 'Synthetic demo selected.' if request.demo else 'Public domain assessment queued.'}]}
    save(case)
    task = asyncio.create_task(run(case))
    TASKS.add(task)
    task.add_done_callback(TASKS.discard)
    return case

@app.get('/api/cases')
def cases():
    with connection() as db:
        data = [json.loads(row[0]) for row in db.execute('SELECT document FROM cases')]
    return [{k: c.get(k) for k in ('id', 'domain', 'demo', 'created_at', 'status')} |
            {'score': c.get('assessment', {}).get('score'), 'coverage': c.get('assessment', {}).get('coverage')} for c in sorted(data, key=lambda c: c['created_at'], reverse=True)[:200]]

@app.delete('/api/cases')
def clear_cases():
    with connection() as db:
        active = [json.loads(document) for (document,) in db.execute('SELECT document FROM cases')
                  if json.loads(document).get('status') in ('QUEUED', 'RUNNING')]
        if active:
            raise HTTPException(409, 'Wait for active assessments to finish before clearing history.')
        deleted = db.execute('DELETE FROM cases').rowcount
    return {'deleted': deleted}

@app.get('/api/cases/{identifier}')
def detail(identifier: str):
    return retrieve(identifier)

@app.get('/api/cases/{identifier}/export')
def export(identifier: str):
    return retrieve(identifier)

@app.get('/api/cases/{identifier}/report')
def readable_report(identifier: str):
    case = retrieve(identifier)
    if case['status'] != 'COMPLETED':
        raise HTTPException(409, 'Complete the website checkup first.')
    return HTMLResponse(audience_report(case), headers={'Content-Disposition': 'attachment; filename="netra-website-checkup.html"'})

@app.get('/api/cases/{identifier}/compare/{baseline}')
def comparison(identifier: str, baseline: str):
    before, after = retrieve(baseline), retrieve(identifier)
    if before['status'] != 'COMPLETED' or after['status'] != 'COMPLETED':
        raise HTTPException(409, 'Both checkups must be complete.')
    try:
        return compare(before, after)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

AI_BUSY = set()

@app.post('/api/cases/{identifier}/explain')
async def ai_explanation(identifier: str):
    case = retrieve(identifier)
    if case['status'] != 'COMPLETED':
        raise HTTPException(409, 'Complete the assessment first.')
    if case.get('ai_explanation'):
        return case
    if identifier in AI_BUSY or len(AI_BUSY) >= 2:
        raise HTTPException(429, 'An AI explanation is already running. Try again shortly.')
    AI_BUSY.add(identifier)
    try:
        case['ai_explanation'] = await asyncio.to_thread(explain, case)
        save(case)
        return case
    except ValueError as exc:
        raise HTTPException(503, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(503, 'AI explanation unavailable. The evidence report is unchanged.') from exc
    finally:
        AI_BUSY.discard(identifier)

DIST = Path(__file__).parent.parent / 'frontend' / 'dist'
if DIST.exists():
    app.mount('/assets', StaticFiles(directory=DIST / 'assets'), name='assets')

@app.get('/favicon.svg')
def favicon():
    path = DIST / 'favicon.svg'
    if not path.exists():
        raise HTTPException(404, 'Frontend favicon is unavailable.')
    return FileResponse(path, media_type='image/svg+xml')

@app.get('/')
def frontend():
    if not (DIST / 'index.html').exists():
        raise HTTPException(503, 'Build the frontend first: npm run build')
    return FileResponse(DIST / 'index.html')
