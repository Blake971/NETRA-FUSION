"""User-directed search planning and durable research leads. Never scrapes Google."""
import json
import re
import uuid
from urllib.parse import urlsplit, urlencode
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from fusion_transport import timestamp

PURPOSES = {
 'pages':('Public pages','','Find public pages about your topic.'),
 'documents':('Public documents','(filetype:pdf OR filetype:doc OR filetype:docx)','Find indexed documents; review their relevance and intended audience.'),
 'papers':('Research papers','(filetype:pdf OR site:arxiv.org OR site:pubmed.ncbi.nlm.nih.gov) research','Find papers and scholarly references.'),
 'social':('Public social profiles','(site:linkedin.com OR site:github.com OR site:instagram.com OR site:x.com OR site:facebook.com)','Find public profile references. Matching names do not prove identity or ownership.'),
 'presentations':('Slides and presentations','(filetype:ppt OR filetype:pptx OR filetype:pdf) presentation','Find publicly indexed presentation material.'),
 'spreadsheets':('Public spreadsheets','(filetype:xls OR filetype:xlsx OR filetype:csv)','Review whether indexed spreadsheets were intentionally published.'),
 'login':('Sign-in pages','(inurl:login OR inurl:signin)','Find public entry pages without accessing accounts.'),
 'directories':('Directory listings','intitle:"index of"','Find indexed listings; a listing is not automatically a security issue.'),
 'code':('Code references','site:github.com','Find public code mentions; a mention does not prove ownership.'),
 'privacy':('Privacy and legal pages','(privacy OR terms OR imprint OR "legal notice")','Look for self-published organization and legal information.'),
 'contact':('Published contact pages','(inurl:contact OR inurl:about)','Look for official contact or about pages.'),
 'security':('Security reporting','("security.txt" OR "responsible disclosure")','Find public reporting instructions.'),
 'subdomains':('Domain references','','Find public references to a website; indexing is not a live inventory.')
}

def queries(domain='', purpose='all', keyword='', scope='google'):
    keyword = re.sub(r'[^\w .-]',' ',keyword,flags=re.UNICODE).strip()[:120]
    subject = keyword or re.sub(r'[^\w .-]',' ',domain,flags=re.UNICODE).strip()[:253]
    if not subject:
        raise ValueError('Enter a topic, organization, public profile name or website.')
    if scope=='website':
        from fusion_engine import normalize_domain
        domain=normalize_domain(domain)
    output=[]
    for key,(title,operators,meaning) in PURPOSES.items():
        if purpose not in ('all',key): continue
        # External social/code/paper sites cannot also match a site:target filter.
        external=key in ('social','code','papers')
        prefix=('site:'+domain if not external else '"'+domain+'"') if scope=='website' else ''
        if scope=='website' and key=='subdomains':prefix='site:*.'+domain+' -site:www.'+domain
        topic='"'+subject+'"' if scope=='google' or keyword else ''
        query=' '.join(x for x in (prefix,topic,operators) if x)
        output.append({'id':key,'title':title,'query':query,'meaning':meaning,
                       'scope_note':'External references to this domain' if scope=='website' and external else 'Within the selected website' if scope=='website' else 'Across Google',
                       'url':'https://www.google.com/search?'+urlencode({'q':query})})
    return output

def generate_response(request, fallback='', demo=False):
    if request.purpose not in PURPOSES and request.purpose!='all':
        raise HTTPException(422,'Choose a listed research purpose.')
    domain=request.domain or fallback
    try: result=queries(domain,request.purpose,request.keyword,request.scope)
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    return {'queries':result,'demo':demo,'scope':request.scope,'notice':'Search suggestions only; Google results are not fetched or identity-verified.'}

def clean_url(value):
    if any(ord(c)<32 for c in value):
        raise ValueError('Use a normal public HTTP or HTTPS URL.')
    parts = urlsplit(value.strip())
    if parts.scheme not in ('http','https') or not parts.hostname or parts.username or parts.password:
        raise ValueError('Use a public http:// or https:// URL without embedded credentials.')
    return parts._replace(fragment='').geturl()

class QueryRequest(BaseModel):
    purpose: str = Field(default='all',max_length=30)
    keyword: str = Field(default='',max_length=120)
    scope: Literal['google','website'] = 'google'
    domain: str = Field(default='',max_length=253)

class LeadRequest(BaseModel):
    url: str = Field(min_length=1,max_length=2000)
    title: str = Field(min_length=1,max_length=160)
    query: str = Field(default='',max_length=500)
    notes: str = Field(default='',max_length=2000)
    status: Literal['To review','Useful context','Follow up','Dismissed'] = 'To review'

def build_research_router(connect, retrieve):
    router = APIRouter()
    def entries(case_id):
        with connect() as db:
            return [json.loads(r[0]) for r in db.execute('SELECT document FROM research WHERE case_id=? ORDER BY rowid DESC',(case_id,))]

    @router.post('/api/research/queries')
    def global_generate(request: QueryRequest):
        return generate_response(request)

    @router.post('/api/cases/{case_id}/research/queries')
    def generate(case_id: str, request: QueryRequest):
        case = retrieve(case_id)
        return generate_response(request,case['domain'],case['demo'])

    @router.get('/api/cases/{case_id}/research')
    def notebook(case_id: str):
        case = retrieve(case_id)
        return {'domain':case['domain'],'demo':case['demo'],'items':entries(case_id), 'label':'User-saved research leads; not verified findings; no score effect.'}

    @router.post('/api/cases/{case_id}/research',status_code=201)
    def save_lead(case_id: str, request: LeadRequest):
        retrieve(case_id)
        try:
            url = clean_url(request.url)
        except ValueError as exc:
            raise HTTPException(422,str(exc)) from exc
        item = request.model_dump() | {'url':url,'id':str(uuid.uuid4()),'saved_at':timestamp(),'verification':'User-saved, not independently verified'}
        with connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT count(*) FROM research WHERE case_id=?',(case_id,)).fetchone()[0]>=200:
                raise HTTPException(409,'This notebook has reached its 200-lead limit.')
            if db.execute('SELECT 1 FROM research WHERE case_id=? AND url=?',(case_id,url)).fetchone():
                raise HTTPException(409,'This URL is already saved in the notebook.')
            db.execute('INSERT INTO research VALUES (?,?,?,?)',(item['id'],case_id,url,json.dumps(item)))
        return item

    @router.patch('/api/cases/{case_id}/research/{item_id}')
    def update_lead(case_id: str,item_id: str,request: LeadRequest):
        retrieve(case_id)
        try:
            url=clean_url(request.url)
        except ValueError as exc:
            raise HTTPException(422,str(exc)) from exc
        with connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT document FROM research WHERE id=? AND case_id=?',(item_id,case_id)).fetchone()
            if not row:
                raise HTTPException(404,'Research lead not found.')
            if db.execute('SELECT 1 FROM research WHERE case_id=? AND url=? AND id<>?',(case_id,url,item_id)).fetchone():
                raise HTTPException(409,'That URL is already in this notebook.')
            item=json.loads(row[0]) | request.model_dump() | {'url':url,'updated_at':timestamp()}
            db.execute('UPDATE research SET url=?,document=? WHERE id=? AND case_id=?',(url,json.dumps(item),item_id,case_id))
        return item

    @router.delete('/api/cases/{case_id}/research/{item_id}')
    def delete_lead(case_id: str,item_id: str):
        retrieve(case_id)
        with connect() as db:
            changed=db.execute('DELETE FROM research WHERE id=? AND case_id=?',(item_id,case_id)).rowcount
        if not changed:
            raise HTTPException(404,'Research lead not found.')
        return {'removed':True}
    return router
