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
from fusion_intelligence import intelligence
from fusion_research import build_research_router
from fusion_local import build_local_router
from fusion_hosting import attribution
from fusion_breach import build_breach_router
from starlette.middleware.trustedhost import TrustedHostMiddleware

DB = Path(os.environ.get('NETRA_DB', Path(__file__).with_name('fusion.db')))
TASKS = set()
LIMIT = asyncio.Semaphore(3)

@contextmanager
def connection():
    db = sqlite3.connect(DB, timeout=10)
    try:
        with db:
            db.execute('CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, document TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS actions (case_id TEXT, finding_id TEXT, owner TEXT, status TEXT, notes TEXT, updated_at TEXT, PRIMARY KEY(case_id, finding_id))')
            db.execute('CREATE TABLE IF NOT EXISTS research (id TEXT PRIMARY KEY, case_id TEXT, url TEXT, document TEXT, UNIQUE(case_id,url))')
            db.execute('CREATE TABLE IF NOT EXISTS supplemental (case_id TEXT, kind TEXT, document TEXT, PRIMARY KEY(case_id,kind))')
            yield db
    finally:
        db.close()

def save(case):
    with connection() as db:
        db.execute('INSERT OR REPLACE INTO cases VALUES (?, ?)', (case['id'], json.dumps(case)))

def retrieve(identifier):
    with connection() as db:
        row = db.execute('SELECT document FROM cases WHERE id = ?', (identifier,)).fetchone()
        actions = db.execute('SELECT finding_id, owner, status, notes, updated_at FROM actions WHERE case_id = ?', (identifier,)).fetchall()
        supplemental = [json.loads(r[0]) for r in db.execute('SELECT document FROM supplemental WHERE case_id=?',(identifier,))]
        research = [json.loads(r[0]) for r in db.execute('SELECT document FROM research WHERE case_id=?',(identifier,))]
    if not row:
        raise HTTPException(404, 'Assessment not found')
    case = json.loads(row[0])
    case['supplemental'] = supplemental
    case['research'] = research
    case['actions'] = {r[0]: {'owner': r[1], 'status': r[2], 'notes': r[3], 'updated_at': r[4]} for r in actions}
    if case['status'] == 'COMPLETED':
        case['audience'] = interpret(case)
        case['footprint'] = footprint(case)
        case['intelligence'] = intelligence(case)
        case['attribution'] = attribution(case)
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

app = FastAPI(title='NETRA Fusion', version='3.2', lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['localhost', '127.0.0.1', 'testserver'])

class Request(BaseModel):
    domain: str = Field(default='northstar.example', max_length=300)
    demo: bool = False
    demo_profile: Literal['baseline', 'improved'] = 'baseline'

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
                for future in asyncio.as_completed([one(name) for name in ('web', 'dns', 'certificates', 'registration', 'hosting')]):
                    name, result = await future
                    results[name] = result
                    case['events'].append({'time': now(), 'stage': 'Collect', 'message': name + ': ' + result['status']})
                    case['progress'] += 14
                    save(case)
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
    return {'status': 'ok', 'version': '3.2', 'reasoning': 'deterministic', 'ai_available': configured(), 'live_collectors': ['DNS', 'HTTPS/TLS', 'certificate transparency', 'RDAP registration', 'Public endpoint location']}

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

@app.get('/api/cases/{identifier}')
def detail(identifier: str):
    return retrieve(identifier)

@app.get('/api/cases/{identifier}/export')
def export(identifier: str):
    return retrieve(identifier)

class ActionRequest(BaseModel):
    owner: str = Field(default='', max_length=80)
    status: Literal['To do', 'In progress', 'Ready to recheck'] = 'To do'
    notes: str = Field(default='', max_length=1000)

@app.patch('/api/cases/{identifier}/actions/{finding_id}')
def update_action(identifier: str, finding_id: str, request: ActionRequest):
    case = retrieve(identifier)
    if case['status'] != 'COMPLETED':
        raise HTTPException(409, 'Complete the checkup before making an action plan.')
    if finding_id not in {f['id'] for f in case['assessment']['findings']}:
        raise HTTPException(422, 'Choose a finding from this checkup.')
    with connection() as db:
        db.execute('INSERT OR REPLACE INTO actions VALUES (?, ?, ?, ?, ?, ?)', (identifier, finding_id, request.owner.strip(), request.status, request.notes.strip(), now()))
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

app.include_router(build_research_router(connection, retrieve))
app.include_router(build_local_router(connection, retrieve, analyze))
app.include_router(build_breach_router())

DIST = Path(__file__).parent.parent / 'frontend' / 'dist'
if (DIST / 'assets').exists():
    app.mount('/assets', StaticFiles(directory=DIST / 'assets'), name='assets')

@app.get('/')
def frontend():
    if not (DIST / 'index.html').exists():
        raise HTTPException(503, 'Build the frontend first: npm run build')
    return FileResponse(DIST / 'index.html')
