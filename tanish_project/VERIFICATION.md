# NETRA Fusion 3.2 verification

Verified on 2026-09-19 in the local Windows workspace.

- `python -m unittest test_fusion test_audience test_depth test_research_expansion -q`: 52 tests passed. Includes unknown-data scoring, TLS failure classification and retained handshake evidence, email edge cases, RDAP identity checks, Google-first and website-scoped query safety, source-aware comparisons, research CRUD and case isolation, hosting/CDN attribution boundaries, DNS retry behavior, SQLite backup integrity, and supplemental observations without score changes.
- `npm run build`: production frontend build passed.
- `node test-ui.mjs`: technical evidence filtering, simulation, exports, interactive graph, history and mobile checks passed.
- `node test-audience-ui.mjs`: plain-language results, presenter controls, readable report, persistent actions, improved example comparison, glossary and responsive layout passed.
- `node test-workspace-ui.mjs`: guide, evaluation, fictional registration, thirteen search templates, research create/edit/export/reload/remove, evidence review, backup and mobile layout passed. No browser page errors.
- `node test-expansion-ui.mjs`: Google-first search without an assessment, website scope, external social references, fictional email exposure, hosting provenance, responsive light/dark layouts and no browser errors passed.
- `python run_netra.py --check`: dependencies, built frontend and database access passed.
- Live RDAP lookup for `example.com`: succeeded through IANA bootstrap and Verisign; returned exact-domain registration and expiry information.
- Live hosting lookup for `example.com`: public DNS addresses were enriched by `ipapi.co` as Cloudflare network addresses. The origin remained explicitly unestablished. `ipwho.is` is retained as a fallback after a provider timeout.
- Reviewed rendered desktop and mobile search-assistant screenshots in `test-results`.

The controlled lab matched 18/18 expected outcomes. This is a small offline rule-fixture test, not a live-site accuracy measurement. Provider outages, arbitrary registry responses, real email delivery, full TLS configuration and live Gemini calls are not comprehensively tested. A Starlette test-client deprecation warning remains; tests pass.

The single-user local server is bound to 127.0.0.1:8001. This verification does not certify a public multi-user deployment.
