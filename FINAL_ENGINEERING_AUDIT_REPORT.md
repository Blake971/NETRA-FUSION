# NETRA Fusion Final Engineering Audit Report

Date: 2026-10-07
Status: Local validation complete
Application URL: http://127.0.0.1:8001

## 1. Executive Summary

NETRA Fusion is a local React/Vite frontend backed by a Python/FastAPI service. The active application is served by `run_netra.py`, using `netra - Copy/frontend` and `netra - Copy/backend/fusion_api.py`.

The application builds, starts locally, completes the offline demo, supports domain assessment, renders evidence-backed results, exports reports, maintains assessment history, and now supports clearing saved history. Person and organization search modes are available directly from the main search bar and generate explicit encoded Google query links.

The system remains a local single-user security assessment prototype. It is not authenticated for public deployment and does not perform exploit verification.

## 2. Architecture Audited

- Frontend: React 18, Vite 8, Framer Motion, CSS and Tailwind dependencies.
- Backend: Python, FastAPI, Uvicorn, SQLite.
- Frontend entry: `netra - Copy/frontend/src/main.jsx` and `Fusion.jsx`.
- Backend entry: `netra - Copy/backend/fusion_api.py`.
- Launcher: `run_netra.py`.
- Persistence: SQLite `fusion.db` under the Fusion backend.
- API style: REST endpoints under `/api`.
- AI: Optional Gemini explanation, explicitly separated from deterministic scoring.
- Browser validation: Microsoft Edge through Playwright.

## 3. Features Verified

- Offline synthetic assessment using `northstar.example`.
- Live domain validation and public-target restrictions.
- DNS, HTTPS/TLS, certificate transparency, Google dork, and optional geolocation collection paths.
- Deterministic scoring, evidence coverage, findings, challenge review, and remediation planning.
- Overview, evidence room, public footprint, asset graph, Google Dorks, remediation, comparison, history, and portfolio views.
- JSON evidence export and printable report flow.
- Session persistence and assessment history.
- Clear history confirmation, API deletion, empty state, and disabled action state.
- Domain assessment from the main search bar.
- Person/username search from the main search bar.
- Organization research query generation from the main search bar.
- Email exposure mode using the official Have I Been Pwned API when `HIBP_API_KEY` is configured.
- Individual open links for LinkedIn, GitHub, X/Twitter, Facebook, Instagram, YouTube, Reddit, TikTok, Threads, Bluesky, Pinterest, and Twitch.

## 4. Major Fixes Made

### Build and JSX stability

- Repaired malformed JSX closures in `Fusion.jsx`.
- Restored missing `motion.div` and `AnimatePresence` closures.
- Corrected geolocation map and fragment boundaries.
- Confirmed production Vite build succeeds.

### Security

- Removed the hard-coded Gemini API key from `run_netra.py`.
- Gemini is now enabled only through process environment variables.
- Preserved trusted-host validation, public-IP checks, bounded collection, and queue limits.
- Added clear-history deletion protection while cases are persisted as `QUEUED` or `RUNNING`.

### Search and OSINT workflow

- Added a main search type selector with Domain assessment, Person/username, and Organization modes.
- Prevented person or organization names from being sent through domain validation.
- Added URL encoding for all generated queries.
- Replaced popup-dependent behavior with explicit links using `target="_blank"` and `rel="noreferrer"`.
- Person mode now generates one independently openable query link per social or professional platform.
- Added consent-based HIBP email checks with transient results and no workspace storage.
- Restored categorized organization queries: public pages, documents, social profiles, presentations, spreadsheets, code, contact/about, privacy/legal, security reporting, sign-in pages, and directory listings.
- Moved generated query links directly below the main search bar.
- Removed redundant Google Dork and person/organization placeholder panels from the rendered view.

### History

- Added `DELETE /api/cases`.
- Added confirmation and loading behavior to the Assessment history view.
- Clear history resets the selected case and session storage.
- Fixed a race where completed jobs could be incorrectly treated as active during deletion.

### UI and animation

- Added a restrained reconnaissance network visual to the welcome state.
- Added flowing connections, pulsing nodes, and a central correlation core.
- Added `prefers-reduced-motion` handling.
- Added a favicon and removed the browser favicon 404.
- Added an explicit `/favicon.svg` backend route so the compiled Vite public asset is served by the launcher.
- Preserved existing route transitions and interaction animations.

## 5. Validation Results

### Backend

Command:

```powershell
python -m unittest test_fusion -v
```

Result: 23 tests passed.

The suite covers domain validation, private-target blocking, trusted hosts, evidence scoring, partial evidence, CORS, headers, certificate expiry, AI failure/caching, full demo lifecycle, clear-history deletion, HIBP consent enforcement, and missing-key behavior.

### Frontend

Command:

```powershell
cd "netra - Copy/frontend"
npm run build
```

Result: production build passed.

Latest generated bundle sizes were approximately:

- JavaScript: 299.78 kB, 95.93 kB gzip.
- CSS: 51.02 kB, 11.23 kB gzip.

### Browser workflow

Command:

```powershell
node test-ui.mjs
```

Result: passed.

Verified behavior includes:

- Demo creation.
- Evidence filtering and technical detail view.
- Remediation score projection.
- Action-plan export.
- Interactive asset graph selection.
- Assessment history reopening and reload persistence.
- Portfolio empty state.
- Mobile horizontal-overflow check.
- No browser page errors.

### Search workflow

Organization live check:

- Input: `Acme Corporation`.
- Generated queries: 11.
- All links target Google search URLs.
- All links are encoded and use `target="_blank"`.
- Person mode was verified with `Ada Lovelace` and generated 12 encoded, individually openable social/profile links.
- Organization mode was verified with `Acme Corporation` and generated 11 encoded, individually openable research links.
- HIBP email mode was verified with consent and returned the expected missing-key message without a provider request.

### History workflow

- Created a synthetic assessment.
- Opened Assessment history.
- Confirmed Clear history.
- Confirmed the empty state and disabled button.
- Confirmed `/api/cases` returned an empty list.

## 6. Security Assessment

Positive controls verified:

- Loopback-only launcher binding.
- Trusted-host middleware.
- Public domain normalization.
- Private and local target rejection.
- Public IP validation before collection.
- HTTPS socket pinning and SNI preservation in the collector path.
- Collection timeouts and response-size limits.
- Queue limits for assessments.
- Optional AI receives normalized findings rather than raw response bodies, cookies, or headers.
- No embedded Gemini credential remains in the launcher.
- Google query links are generated only; searches are not executed automatically.
- HIBP email checks require explicit permission, do not store the email or result, and do not run when `HIBP_API_KEY` is missing.
- Generated links are explicit user actions and open in new tabs with `rel="noreferrer"`.

Remaining security concerns:

- No authentication or authorization exists because this is a local single-user workspace.
- Do not expose the server publicly without adding authentication, authorization, rate limiting, deployment isolation, and secure secret management.
- Evidence exports may contain public headers and HTML-derived observations. Review before sharing.
- Public certificate transparency names are historical observations and may not represent active assets.
- A security score is a limited configuration score, not breach probability or compliance certification.

## 7. Dependency and Performance Notes

- Production frontend dependency audit was clean after the Axios update.
- Remaining development dependency advisories are transitive Tailwind-era issues; automatic remediation requires a breaking Tailwind major upgrade and was not forced.
- The active Fusion frontend bundle is under 300 kB before gzip and uses CSS transforms/opacity for the custom animation layer.
- No formal Core Web Vitals capture was performed.
- No large image assets or heavy canvas particle system were introduced.
- Polling is scoped to active assessments and is cleaned up when the assessment finishes.

## 8. Responsive and Accessibility Notes

Verified:

- Desktop browser workflow.
- Mobile viewport horizontal-overflow prevention.
- Keyboard-accessible graph nodes.
- Visible focus styles in the Fusion stylesheet.
- Accessible labels for search inputs, search type, findings, and generated visual content.
- Reduced-motion behavior for the custom network animation.
- Explicit links instead of popup-only query actions.

## 9. External Services Not Fully Verified

- Live Gemini generation was not performed because no valid provider key/model was configured.
- Live public-domain collection depends on DNS, HTTPS, certificate transparency, and network availability.
- Google result contents are not fetched or identity-verified by NETRA.
- Live HIBP results were not fetched because no API key was configured locally.
- Geolocation provider freshness and accuracy were not independently benchmarked.

## 10. Run Instructions

From the repository root:

```powershell
python run_netra.py
```

Open:

```text
http://127.0.0.1:8001
```

Use `Try demo` for an offline assessment. Use the main search type dropdown for domain, person/username, organization, or Email exposure (HIBP) workflows. Use Assessment history to review or clear saved cases.

## 11. Final Status

The current local build is stable for the verified demo and assessment workflows. The organization query feature provides categorized open links, history can be cleared safely, animations are present with reduced-motion support, and the full available regression coverage passes.

The main production-readiness blocker is deployment security: the current local single-user model must not be exposed as a public service without an authentication and authorization layer.
