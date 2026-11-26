# Phase 8 test coverage matrix

| Area | Evidence | Result | Notes |
|---|---|---|---|
| Locked Python suite | `uv run --no-project --python 3.11 --with-requirements requirements-ci.txt pytest -q tests` | 195 passed | Python 3.11.17; one deprecation warning |
| React unit tests | `pnpm test` | 32 passed | Vitest |
| TypeScript | `pnpm run typecheck` | Passed | Workspace libraries and app |
| Production build | `pnpm run build` | Passed | 2,163 modules transformed |
| Desktop routes | Playwright release-readiness suite | 10/10 passed | All application routes |
| Narrow-phone routes | Playwright release-readiness suite | 10/10 passed | 360 px viewport; no document-level horizontal overflow |
| Navigation state | Playwright | Passed | Navigation, back/forward, refresh, and deep link |
| Keyboard access | Playwright | Passed | Navigation links and scrollable tables |
| Runtime failure recovery | Playwright | Passed | Simulated one-time HTTP 503, visible error, retry, recovered dashboard |
| Customer demonstration | Playwright | Passed | Saved customer 18102 forecast, explanation, reliability context |
| Durable research references | Playwright | Passed | Production source links point to durable `main` paths, not the temporary feature branch |
| Upload flow | Playwright + Python API tests | Passed | Synthetic in-memory CSV preview, analysis, export; invalid mapping rejected |
| Retention scenario | Playwright + Python tests | Passed | Scenario and six-strategy comparison; response is marked hypothetical/noncausal |
| Accessibility | axe-core through Playwright | Passed | No serious or critical findings on all 10 routes |
| API surface smoke | Live OpenAPI-driven GET smoke | 37/37 returned HTTP 200 | Includes calibration PNG response |
| Model and prediction checks | Python tests and artifact manifest | Passed | Full 3,373-customer inference comparisons; 67 canonical files unchanged |
| Saved aggregate checks | Final evaluation and trajectory snapshot builders with `--check` | Passed | Read-only checks |
| Dependency security | Replit dependency audit | Passed | 0 critical/high/moderate after floors and lock refresh |
| Static analysis | Replit SAST scan | Passed | 0 findings |
| Privacy/dataflow scan | Replit HoundDog scan | Passed | 0 findings |
| GitHub Actions | PR head checks | Review live PR | Do not merge until required checks are green |
| Public production URL | Not supplied | Not executed | Development preview is not production verification |
| Other browser engines | Firefox/WebKit not available | Not executed | Chromium 155 used |
| Notebook re-execution | Intentionally not run | Not executed | Avoids retraining or overwriting saved research outputs |
| Timed live presentation | Not performed | Not executed | Core flow was exercised in browser automation |
