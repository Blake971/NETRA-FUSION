# Explain the NETRA workspace

Audience introduction: “NETRA reads a website's public records, explains the evidence in everyday language, and helps us organize further research and improvements.”

| Panel | What it does | How to explain it |
| --- | --- | --- |
| Website checkup | Shows score, observed coverage, plain-language findings, glossary and presenter mode | Our starting point: what looks expected, what needs attention, and what could not be checked. |
| My action plan | Saves owners, progress and notes; exports a checklist; starts a recheck | Our to-do list. Checking a box does not change the measured score. |
| Public information | Shows homepage links, registry registration, TLS status, email policy and supplied-selector DKIM lookup | The public facts that help us understand the website. |
| Google search assistant | Generates thirteen categories of Google-wide or website-scoped search query; copies or opens them; saves links, notes and triage status | A research assistant that helps us ask better questions and remember useful results. |
| Hosting and ownership | Shows public IP/network location, CDN evidence, registry organization and resource hosts | The public delivery layer is visible; the origin and operator may remain undisclosed. |
| Email exposure | Uses HIBP for a permitted email check, or shows a fictional example | Known incident metadata, with a clear difference between no known match and an unavailable provider. |
| Compare results | Compares observed controls, sampled names/addresses and earlier planned actions | Evidence of what changed between two checkups. Missing data is not a fix. |
| Past checkups | Searches and reopens saved assessments | Our local history. |
| Multiple websites | Queues up to ten website domains from text or CSV | One place to organize several checkups. |
| Workspace guide | Explains every panel and downloads the SQLite backup | Help for the audience and a way to preserve our local work. |
| Accuracy lab | Evaluates eighteen labeled synthetic scenarios and exports results | A repeatable experiment showing how selected rules handle gaps, controls and unknowns. |
| Evidence review (Advanced details) | Shows observation, alternative explanation and conclusion | Why we reached a conclusion, and what we cannot claim. |
| Technical overview (Advanced details) | Shows category deductions, technologies, trail and optional configured Gemini explanation | The detailed dashboard for a technical reviewer. |
| Recorded evidence (Advanced details) | Filters findings and displays original collector results and their digest | The supporting observations behind the report. |
| Connection map (Advanced details) | Displays domain, addresses, mail servers and historical certificate names | How public records connect names and infrastructure. |
| Technical fixes (Advanced details) | Models selected fixes and provides configuration examples | An estimate of possible improvement, verified only by another checkup. |

## Five-minute demonstration

1. Choose **Try example**. Explain that `northstar.example` and its records are fictional.
2. Show **Website checkup**: the baseline is 55/100 with all nine configured checks observed. Full coverage means these nine checks, not a complete security audit.
3. Show **Public information**, then generate queries in **Google search assistant**. Google-wide research is available without a checkup. Select Website scope to prefill the current domain; fictional .example website queries are preview-only.
4. Save a sample public link with a note. Explain that it remains an unverified research lead and does not deduct points.
5. Open **Evidence review** to show an observation and a competing explanation. Review is rule-based; do not describe it as multiple independent AI agents.
6. Save an action, create the improved example, and choose the baseline in **Compare results**. The improved fixture scores 100 because its configured controls were deliberately changed. This does not claim a real website was repaired.
7. Run **Accuracy lab**. The eighteen expected outcomes should match. False alarms and missed gaps are measured only on this small controlled corpus; they are not a real-world accuracy estimate.

## Local use and backup

Double-click **Start NETRA.cmd**, or run `python run_netra.py`. Open http://127.0.0.1:8001. `python run_netra.py --check` checks installed Python dependencies, the frontend build and database access. Startup does not install dependencies or contact an AI provider.

In **Workspace guide**, download the workspace backup. It contains cases, research and action notes. SQLite's backup API creates a consistent snapshot; the temporary server copy is deleted after download.

To restore: stop NETRA first, preserve a copy of the existing `netra - Copy/backend/fusion.db`, then replace it with your downloaded backup renamed `fusion.db`. Restart NETRA. If you configured `NETRA_DB`, restore to that path instead. Backups from this version include the supplemental and research tables. Do not replace the database while the server is running.

This is a single-user local final-year-project build. Internet collectors depend on DNS and public providers; unavailable observations are labeled. Registration queries require an exact registry domain match; arbitrary subdomains may have no registration response. DMARC inheritance and actual email delivery are not tested. DKIM checks require an administrator-supplied selector and do not validate message signatures or cryptographic key strength. No Google scraping or automatic search-result collection is implemented. Gemini remains optional and requires configured credentials.

## Implementation references

- [IANA RDAP bootstrap registry](https://www.iana.org/assignments/rdap-dns/rdap-dns.xhtml): discovers the relevant registry service.
- [Python TLS certificate errors](https://docs.python.org/3/library/ssl.html#ssl.SSLCertVerificationError): separates expired, hostname, validity and trust failures.
- [DMARC RFC 9989](https://www.rfc-editor.org/rfc/rfc9989.html): current policy context, including testing mode. NETRA implements limited direct-record checks, not complete protocol validation.
- [DKIM RFC 6376](https://www.rfc-editor.org/rfc/rfc6376.html): selector records and empty-key revocation semantics.


## Google-first research (3.2)

Open Google search assistant immediately; a website checkup is optional. Enter a research topic, organization or public profile name. Select documents, papers, social profiles, slides or another category. Copy the generated query or open it on Google. Search results are not automatically downloaded or identity-verified.

Switch Search scope to A specific website and enter a domain, or use the domain prefilled from the current checkup. Document searches restrict results to that website. Social, code and paper searches instead look for domain references on external sites, because combining unrelated site restrictions would hide useful results. Open a checkup to save links and notes in its notebook.

## Hosting, operator and original files

Hosting and ownership uses ipapi.co, with ipwho.is as a fallback and a ten-minute in-memory cache. It shows approximate network-location data for up to two public IPs, with source and time. The registrar sells/manages domain registrations; nameservers provide DNS; the network provider operates the public IP space. These roles do not establish the website owner. NETRA displays a registrant organization only when the registry publishes it, and links to official about/legal/contact pages found in the homepage.

Cloudflare indicators come from response headers and public network metadata. A CF-Ray suffix identifies an observed edge code, not the origin. HTML resource hosts show where the page references browser-facing files, not where Cloudflare retrieves upstream content. The underlying file server and a private registrant identity may remain unestablished. This tool does not bypass CDN protection or infer personal addresses.

Transient DNS failures are retried once, independent DNS records run concurrently, and a failed connection can try another validated public IP. Certificate verification remains enabled. Provider retries are bounded, and unavailable records remain unknown. Run a fresh checkup to attempt collection again without changing old evidence.

## Email exposure setup and demonstration

Email exposure is independent of a website checkup. Show fictional breach example works offline and does not send the entered address anywhere. Real lookups require an HIBP subscription/API key configured as HIBP_API_KEY in the server environment. Restart the local server after configuring it. Do not paste the key into the frontend or commit it to a file.

A real lookup requires the user to confirm ownership/permission and acknowledge that the address is sent to HIBP. The result includes incident names, dates, affected data categories and public source links. It does not include leaked passwords or breach dumps. HIBP incident verification is shown explicitly; a breach listing is not proof of current mailbox access. The panel does not persist email inputs/results in the database, backups or case exports. Leaving the panel clears its state.

No known public match is a limited provider result, not proof of safety. Missing keys, invalid subscriptions, rate limits and provider failures are errors, never no-match results. Sensitive/retired/opted-out records may be omitted by the provider. The official HIBP website and breach directory are linked for manual follow-up.

References: [HIBP API](https://haveibeenpwned.com/API/v3), [Cloudflare public versus origin addresses](https://developers.cloudflare.com/fundamentals/concepts/cloudflare-ip-addresses/), [ipapi location metadata](https://ipapi.co/api/), [fallback location metadata](https://ipwhois.io/documentation).
