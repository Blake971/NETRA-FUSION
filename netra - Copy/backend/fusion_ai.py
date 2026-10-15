"""Optional Gemini explanation. REST contract: https://ai.google.dev/api/generate-content"""
import http.client
import json
import os
import re

def configured():
    return bool(os.environ.get('GEMINI_API_KEY') and re.fullmatch(r'[a-zA-Z0-9._-]+', os.environ.get('GEMINI_MODEL', '')))

def explain(case):
    if not configured():
        raise ValueError('Set GEMINI_API_KEY and GEMINI_MODEL on the server to enable optional AI explanations.')
    assessment = case['assessment']
    # Exclude raw bodies, cookies, and headers from the provider request.
    evidence = {'domain': case['domain'], 'synthetic_demo': case['demo'], 'score': assessment['score'],
                'coverage': assessment['coverage'], 'findings': [{k: f[k] for k in ('id', 'title', 'points', 'category', 'severity', 'explanation', 'remediation')} for f in assessment['findings']]}
    payload = {
        'systemInstruction': {
            'parts': [{
                'text': '''You are a security analyst explaining a domain security assessment to a non-technical audience.

Your task:
1. Provide a clear, natural language summary of the security assessment
2. Explain what the score means in practical terms
3. Highlight the most important security issues
4. Suggest prioritized next steps in actionable language
5. Be conversational and easy to understand

Guidelines:
- Use plain language, avoid jargon where possible
- Explain technical terms when you must use them
- Focus on practical implications, not just technical details
- Be specific about what needs to be fixed and why
- If this is synthetic demo data, clearly state that at the beginning
- Mention evidence coverage if it's not 100%
- Do not invent new findings not in the data
- Do not claim compliance certifications
- Return well-structured, readable text

Format your response as:
- 2-3 sentence executive summary
- Brief explanation of the score (what it means)
- 2-3 most critical issues to address
- 3 prioritized action items
- 1-2 sentence conclusion'''
            }]
        },
        'contents': [{'parts': [{'text': json.dumps(evidence, indent=2)}]}],
        'generationConfig': {
            'maxOutputTokens': 2000,
            'temperature': 0.7
        }
    }
    conn = http.client.HTTPSConnection('generativelanguage.googleapis.com', timeout=25)
    try:
        conn.request('POST', '/v1beta/models/' + os.environ['GEMINI_MODEL'] + ':generateContent',
                     body=json.dumps(payload).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': os.environ['GEMINI_API_KEY']})
        response = conn.getresponse()
        if response.status != 200:
            raise ValueError('AI provider unavailable (HTTP ' + str(response.status) + '). Your deterministic report is unchanged.')
        data = response.read(100001)
        if len(data) > 100000:
            raise ValueError('AI response exceeded the output limit.')
        candidates = json.loads(data).get('candidates', [])
        text = '\n'.join(p.get('text', '') for p in candidates[0].get('content', {}).get('parts', [])) if candidates else ''
        if not text.strip():
            raise ValueError('The AI provider returned no explanation.')
        return {'mode': 'Gemini AI explanation — review against evidence', 'model': os.environ['GEMINI_MODEL'], 'text': text[:20000]}
    finally:
        conn.close()
