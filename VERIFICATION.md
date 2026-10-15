# Verification — 17 September 2026

- Backend: 15 regression tests passed (`python -m unittest test_fusion -v`).
- Frontend: production build passed with Vite 8.3.0 and Node 24.13.0.
- Dependency audit: npm reported zero known vulnerabilities after build-tool and router updates. This is an advisory database check, not proof of application security.
- Browser: headless Microsoft Edge passed demo creation, finding search, technical view, remediation projection, action-plan download, asset selection, reopening history after reload, mobile horizontal-overflow detection, and empty portfolio validation. No JavaScript page errors were observed.
- Screenshots: `test-results/netra-overview.png` and `test-results/netra-mobile.png` were visually inspected.
- Live smoke assessment: `example.com` completed with successful HTTPS/TLS, DNS, and certificate transparency collectors; 9/9 configured checks observed, score 70 under methodology v1.1. This result describes the sampled response and rules at that time, not the domain's overall security.
- Optional Gemini: failure handling and cached explanation behavior were tested with mocks. A live Gemini call was not made because credentials/model configuration were not supplied.
- No exploit execution, Firecracker, repository vulnerability scanning, external threat intelligence feeds, or compliance certification was tested or claimed.

The local preview is launched with `python run_netra.py` and serves the compiled application at `http://127.0.0.1:8001`.
