# NETRA copy: review and integration decisions

Reviewed the original master context, user guide, module specifications, architecture/API/database/frontend specifications, scanner implementations, normalization, geolocation pipeline, report entry point, legacy routes, and existing frontend workflow. The copied runtime, built assets, reports, and duplicated SALMON source were distinguished from the primary NETRA application. Secrets in `.env` files were not needed.

## What the original project contributes

| Area | Original design or code | Decision in the current interface |
| --- | --- | --- |
| Three explanation levels | `utils/normalization.py` and `docs/NETRA_MASTER_CONTEXT.md` | Default plain-language Website checkup; evidence and technical controls remain accessible |
| DNS | `scanners/dns.py`, A/AAAA/MX/NS/TXT/SOA/CNAME queries | Keep bounded Fusion DNS observations; distinguish absent records from query failures |
| SSL/TLS | `scanners/ssl.py`, certificate and protocol checks | Explain certificate renewal and encryption separately in the UI; retain existing verified handshake collector |
| Browser headers | `scanners/headers.py` | Explain each setting with an analogy and practical owner; improve the HSTS max-age check |
| Email | `scanners/email_security.py`, SPF/DMARC and guessed DKIM selectors | Strengthen obvious SPF checks; do not label DKIM absent simply because guessed selectors were not found |
| WHOIS | `scanners/whois.py`, registration normalization | Preserve legacy source. Not wired into Fusion; provider failures, date parsing, and bounded collection need further work |
| Hosting/geolocation | `utils/geolocation/`, MaxMind and public provider consensus | Preserve source. Not added as an exact-location claim: provider agreement is not proof of an origin server or person’s location |
| Certificate logs | `scanners/ct_logs.py`, crt.sh and fallback provider | Retain crt.sh collector and historical-name labeling; fallback integration remains future work |
| Digital footprint | `scanners/digital_footprint.py`, homepage technology/social hints | Add public-link/document explorer using actual anchor parsing from the existing bounded homepage response |
| Search assistant | `scanners/google_dork.py`, query-only generation | Add six domain-scoped, user-opened guided searches with plain-language purpose; no automated Google scraping |
| Risk engine | `utils/risk_engine.py` and `docs/08_RISK_ENGINE.md` | Explicit higher-is-better rule and transparent deductions; comparisons account for methodology changes |
| AI | `ai/gemini.py` and `docs/07_AI_SPEC.md` | Preserve the original principle that AI explains but never scores; basic explanations do not require a model |
| Reports | `reports/pdf_generator.py` | Add a downloadable self-contained HTML audience handout with print support; do not depend on legacy PDF data shapes |
| History | `models/scan.py`, legacy history routes | Preserve Fusion assessments; add understandable labels, search, and evidence-aware comparisons |
| SALMON | Discovery/challenge/report concept; backend scaffold | Keep deterministic evidence review clearly distinguished from autonomous AI agents or exploit verification |

## Important inconsistencies and limitations found

1. The old user guide and risk specification describe additive, higher-is-worse risk scores. The current Fusion score is higher-is-better. Both legacy documents now direct readers to the current guide instead of presenting the old ranges as current behavior.
2. The legacy footprint code recognizes social platforms through HTML substring matches. The new explorer reads actual links and validates hostname boundaries, so `github.com.attacker.example` is not recognized as GitHub. Query strings and fragments are removed from displayed links.
3. A missing DKIM result after testing common selectors does not prove DKIM is absent. The new checkup does not make that claim.
4. A header’s presence alone does not establish a valid policy. Fusion now checks for one positive numeric HSTS max-age and flags obvious SPF record-count and broad-authorization issues. These remain limited checks, not complete policy evaluators.
5. Geolocation provider confidence is heuristic. No exact origin-server map or personal-location claim was added.
6. Marking a task ready to recheck must not increase a security score. Saved action records are stored separately from collector evidence and assessed findings.
7. A previously observed gap that becomes unknown must not appear fixed. The comparison labels it as needing another check and withholds a numeric score delta when rules or evidence coverage differ.

## New audience-focused capabilities

- Everyday navigation with advanced screens collapsed by default.
- Plain-language result cards covering passed checks, gaps, advice, and missing evidence.
- Practical next steps and suggested teams to contact.
- Saved action ownership, progress, notes, and downloadable text checklist.
- Six-step presenter mode, keyboard controls, speaker notes, and a checkup-specific speaking script.
- Downloadable readable HTML handout, with escaped evidence and no external resources.
- Searchable glossary, searchable history, and restoration of the current checkup after reload.
- Public homepage links and guided search suggestions.
- Fictional before/after demo and honest assessment comparison.
- Mobile layout and light/dark appearance controls.

Protocol references used for the policy checks: [HSTS, RFC 6797](https://www.rfc-editor.org/rfc/rfc6797), [SPF, RFC 7208](https://www.rfc-editor.org/rfc/rfc7208). These checks do not implement every requirement of either specification.

Remaining development opportunities: robust registration lookup, separate TLS/HTTP failure classification, authenticated deployment, provider-backed infrastructure enrichment, and real repository-scanner evidence import. They are not represented as implemented features.
