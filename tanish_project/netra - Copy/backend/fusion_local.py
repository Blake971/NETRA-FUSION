"""Local project utilities: supplemental evidence, backup and evaluation."""
import asyncio
import json
import os
import sqlite3
import tempfile
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from pydantic import BaseModel, Field
from fusion_email import selector_lookup
from fusion_lab import benchmark

class SelectorRequest(BaseModel):
    selector: str = Field(min_length=1,max_length=64,pattern=r'^[A-Za-z0-9][A-Za-z0-9_.-]*$')

def build_local_router(connect,retrieve,analyze):
    router=APIRouter()
    active=set()

    @router.get('/api/lab')
    def lab():
        return benchmark(analyze)

    @router.post('/api/cases/{case_id}/dkim')
    async def dkim(case_id: str,request: SelectorRequest):
        case=retrieve(case_id)
        token=case_id+':'+request.selector.lower()
        if token in active or len(active)>=2:
            raise HTTPException(429,'A key lookup is already running. Try again shortly.')
        if case['demo']:
            raise HTTPException(409,'DKIM lookup requires a real website checkup and a selector supplied by its email administrator.')
        with connect() as db:
            if db.execute('SELECT count(*) FROM supplemental WHERE case_id=?',(case_id,)).fetchone()[0]>=50:
                raise HTTPException(409,'This checkup has reached its supplemental-lookup limit.')
        active.add(token)
        try:
            result=await asyncio.to_thread(selector_lookup,case['domain'],request.selector)
            with connect() as db:
                db.execute('INSERT OR REPLACE INTO supplemental VALUES (?,?,?)',(case_id,'dkim:'+request.selector.lower(),json.dumps(result)))
            return result
        except ValueError as exc:
            raise HTTPException(422,str(exc)) from exc
        finally:
            active.discard(token)

    @router.get('/api/backup')
    def backup():
        folder=Path(__file__).with_name('backups')
        folder.mkdir(exist_ok=True)
        fd,name=tempfile.mkstemp(prefix='netra-',suffix='.sqlite3',dir=folder)
        os.close(fd)
        try:
            target=sqlite3.connect(name)
            try:
                with connect() as source:
                    source.backup(target)
            finally:
                target.close()
        except Exception:
            os.unlink(name)
            raise
        return FileResponse(name,filename='netra-workspace-backup.sqlite3',media_type='application/octet-stream',background=BackgroundTask(os.unlink,name))
    return router
