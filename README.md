# NETRA Fusion

An evidence-first domain security workspace implementing a discover → challenge → report workflow for domain security assessment.

## Run the merged application

From this folder:

```powershell
python run_netra.py
```

Open **http://127.0.0.1:8001** and choose **Try demo**. The supplied build and project-local dependencies are installed on this computer. The demo needs no network access or API key. Stop the server with Ctrl+C.

For a fresh checkout, install and build first:

```powershell
python -m pip install --target .runtime -r "netra - Copy/backend/fusion_requirements.txt"
cd "netra - Copy/frontend"
npm ci
npm run build
cd ../..
python run_netra.py
```

Use a current Node.js version compatible with the installed Vite release; this build was verified with Node 24 and Python 3.14. The original copied `backend/venv` points to a different user's Python installation and is not used.

## What is implemented

| Feature | Behavior |
| --- | --- |
| Live domain collection | Public DNS A/AAAA/MX/NS/TXT/CAA/DMARC, verified HTTPS/TLS, crt.sh certificate names |
| Evidence-aware scoring | Twelve checks, explicit deductions, observation coverage, unknown state, advisory CAA handling |
| Deterministic skeptic | Cross-checks suppress unsupported findings; no claim of independent AI agents |
| Three explanation levels | Summary, explanation, and technical evidence with severity and text filters |
| Asset relationships | Interactive domain/IP/mail/certificate graph plus complete collected inventory |
| Technology signals | Self-reported response headers and bounded HTML heuristics, clearly labeled |
| Remediation planner | Prioritized fixes, staged NGINX examples, what-if score, selected plan export |
| Durable history | SQLite assessments with timestamps, provenance, status, and previous same-domain score |
| Portfolio queue | Up to 10 domains per submission, text or single-column CSV import, three concurrent jobs |
| Offline competition demo | Synthetic `northstar.example` evidence, explicitly labeled throughout |
| Evidence export | JSON including raw observations, review trail, methodology, and SHA-256 evidence digest |
| Printable report | Print current view or save to PDF using the browser print dialog |
| Optional Gemini | Explicitly requested, cached narrative explaining normalized findings; cannot alter stored scores |
| Responsive UI | Desktop/mobile layouts, keyboard navigation, accessible input labels, appearance toggle |

## What was merged

The working entry point is `netra - Copy/backend/fusion_api.py`; the frontend entry point uses `src/Fusion.jsx`. The existing `fusion_engine.py` was connected and its framing and CAA checks corrected. NETRA's legacy application and scanners remain in the folder as reference source.

Fusion implements an evidence-challenge workflow with deterministic cross-checks, not Firecracker verification, MCP scanner execution, or autonomous exploit agents. The original NETRA WHOIS/geolocation modules are not part of Fusion's current collector set. This is a working competition prototype, not a complete replacement for a penetration test.

## Optional AI setup

Set `GEMINI_API_KEY` and `GEMINI_MODEL` in the process environment before starting the server. Choose a model available to your Google account. No secrets are embedded in the frontend, source files, or exported evidence. The application does not automatically load the old NETRA `.env`.

Click **Explain with Gemini** to send the domain, demo flag, score, coverage, and normalized finding explanations to Google. Raw response bodies, cookies, and headers are excluded. AI output remains separately labeled and should be reviewed against the source findings. A provider failure leaves the deterministic report unchanged. Live provider verification requires credentials and was not performed.

Implementation reference: [Google's GenerateContent REST API](https://ai.google.dev/api/generate-content).

## Scoring and interpretation

The score starts at 100 and subtracts observed deductions, with at most 85 points available in this limited ruleset. It is a configuration score, not a breach probability. Unknown checks do not deduct. When no checks are observed, the score is null. Incomplete coverage makes the score provisional. CAA absence is advisory with zero deduction because inherited policy is not checked. Confidence values are rule heuristics, not statistical probabilities.

The application performs normal public DNS queries and a bounded HTTPS root-page request, not strictly passive collection. Certificate transparency names are historical and may be inactive. A successful TLS handshake does not enumerate every supported protocol. Expired/untrusted certificates currently make the shared HTTPS/TLS collector unknown, rather than positively classifying certificate failure. Header presence does not establish a robust policy. No benchmark percentiles or compliance certifications are inferred.

## Local security boundaries

The launcher binds to loopback. Live targets must resolve only to public IPs; the HTTPS socket is pinned to a validated IP while preserving SNI and certificate validation. Redirects are recorded without following them. Collection has timeouts and response-size bounds, and the queue is capped at 12 active/pending jobs. Trusted-host checks reject arbitrary Host headers.

This is a single-user local workspace without authentication. Do not expose it as a public service without adding authentication, authorization, persistent worker infrastructure, and deployment controls. Evidence exports can include public response headers and HTML; review them before sharing. The digest detects changes when checked against a separately trusted copy; it is not a digital signature or tamper-proof chain of custody.

## Development and verification

```powershell
python -m pip install --target .runtime httpx
python -m unittest test_fusion -v
cd "netra - Copy/frontend"
npm run build
node test-ui.mjs
```

Browser tests require the local server and Microsoft Edge. Screenshots are written to `test-results`. The API reference is available at http://127.0.0.1:8001/docs.

For frontend development, `npm run dev` serves port 3000 and proxies `/api` to the Fusion backend at port 8001. Saved Fusion assessments live in `netra - Copy/backend/fusion.db`, separate from the legacy database. Interrupted jobs are marked failed when the backend restarts.

## Competition demonstration

1. Open the offline demo and identify it as synthetic.
2. Explain the score alongside evidence coverage, then open a specific deduction.
3. Switch among the three explanation levels.
4. Show the skeptic suppressing missing X-Frame-Options when an observed CSP framing control exists.
5. Select an asset and explain the distinction between DNS observations and historical certificate names.
6. Choose fixes in the remediation planner; explain that the projected score is a simulation.
7. Export the evidence bundle, then reopen the assessment from history.
8. If network access is available, run a public-domain assessment and show honest unknown states when a source fails.

Pitch: **“NETRA Fusion turns scattered public security signals into traceable findings and a prioritized action plan. Every deduction has evidence, every collection gap stays visible, and optional AI explains without deciding the score.”**

Next development priorities: separate certificate failure classification from HTTP collection, improve policy-semantic validation, import real SARIF scanner evidence for repository analysis, and add authenticated multi-user deployment. These are future work, not current capabilities.
