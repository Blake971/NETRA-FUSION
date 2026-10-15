"""Explicit, transient email exposure checks using the official HIBP API."""
import asyncio
import http.client
import json
import os
import re
import time
from urllib.parse import quote
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from fusion_transport import timestamp

SOURCES=[{'name':'Have I Been Pwned','url':'https://haveibeenpwned.com/','detail':'Check known breach exposure directly; API integration requires a key.'},
         {'name':'HIBP breach directory','url':'https://haveibeenpwned.com/PwnedWebsites','detail':'Public descriptions of known incidents. This directory does not establish whether an email was affected.'}]

class EmailRequest(BaseModel):
    email: str = Field(default='',max_length=254)
    consent: bool = False
    demo: bool = False

def provider_lookup(email,key):
    conn=http.client.HTTPSConnection('haveibeenpwned.com',timeout=12)
    try:
        conn.request('GET','/api/v3/breachedaccount/'+quote(email,safe='')+'?truncateResponse=false',
                     headers={'hibp-api-key':key,'user-agent':'NETRA-Fusion-Educational-Email-Check','accept':'application/json'})
        response=conn.getresponse();status=response.status
        retry=response.getheader('Retry-After','60')
        payload=response.read(1000001)
        if len(payload)>1000000:raise ValueError('Response exceeds limit')
        return status,json.loads(payload) if status==200 else None,retry
    finally:conn.close()

def normalize_breaches(data):
    if not isinstance(data,list):raise ValueError('Unexpected provider format')
    output=[]
    for row in data[:100]:
        if not isinstance(row,dict) or not isinstance(row.get('Name'),str):raise ValueError('Unexpected breach item')
        output.append({'name':row['Name'][:200],'title':str(row.get('Title',row['Name']))[:200],
                       'domain':str(row.get('Domain',''))[:253],'date':str(row.get('BreachDate',''))[:30],
                       'data_classes':[str(x)[:100] for x in row.get('DataClasses',[])[:30]],
                       'verified':row.get('IsVerified') is True,'spam_list':row.get('IsSpamList') is True,
                       'source':'https://haveibeenpwned.com/PwnedWebsites#'+quote(row['Name'],safe='')})
    return output

def build_breach_router():
    router=APIRouter();state={'busy':False,'next':0}
    @router.get('/api/email-check/status')
    def status():return {'configured':bool(os.environ.get('HIBP_API_KEY')),'sources':SOURCES,'storage':'Email queries and results are not stored in the workspace database.'}

    @router.post('/api/email-check')
    async def check(request:EmailRequest,response:Response):
        response.headers['Cache-Control']='no-store'
        if request.demo:
            return {'state':'MATCHES','demo':True,'observed_at':timestamp(),'breaches':[{'name':'FictionalForum','title':'Fictional forum example','domain':'forum.example','date':'2025-01-01','data_classes':['Email addresses','Passwords'],'verified':False,'source':None}],
                    'detail':'Synthetic classroom example. No email was submitted and no provider was contacted.'}
        if not request.consent:raise HTTPException(422,'Confirm this is your email or you have permission, and agree to send it to HIBP.')
        email=request.email.strip()
        if not re.fullmatch(r'[^\s@\x00-\x1f]+@[^\s@\x00-\x1f]+\.[^\s@\x00-\x1f]+',email):raise HTTPException(422,'Enter a valid email address.')
        key=os.environ.get('HIBP_API_KEY')
        if not key:raise HTTPException(503,'HIBP API key is not configured. No email check was performed; use the official source link or the example.')
        if state['busy'] or time.monotonic()<state['next']:raise HTTPException(429,'Please wait before the next email check.')
        state['busy']=True;state['next']=time.monotonic()+6
        try:
            code,data,retry=await asyncio.to_thread(provider_lookup,email,key)
            if code==429:
                state['next']=time.monotonic()+min(86400,max(6,int(retry) if str(retry).isdigit() else 60))
                raise HTTPException(429,'HIBP rate limit reached. Wait before trying again.')
            if code in (401,403):raise HTTPException(503,'HIBP rejected the API credentials or subscription. No conclusion is available.')
            if code not in (200,404):raise HTTPException(503,'HIBP is unavailable. No conclusion about exposure can be made.')
            breaches=normalize_breaches(data) if code==200 else []
            return {'state':'MATCHES' if breaches else 'NO_KNOWN_MATCH','demo':False,'breaches':breaches,'observed_at':timestamp(),
                    'detail':'Reported by Have I Been Pwned. This does not prove the mailbox itself was compromised. No known match does not prove safety; sensitive, retired or opted-out entries may be excluded.'}
        except HTTPException:raise
        except Exception:raise HTTPException(503,'The breach provider could not be checked. No exposure conclusion is available.')
        finally:state['busy']=False
    return router
