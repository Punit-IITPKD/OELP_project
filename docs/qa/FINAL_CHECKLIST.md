# Phase 8 final release checklist

## Local checks

- [x] Locked Python 3.11 test suite: 195 passed.
- [x] React/Vitest suite: 32 passed.
- [x] Workspace and app typecheck.
- [x] Production build.
- [x] Playwright release suite: 28 passed.
- [x] All 10 routes checked at desktop and 360 px phone widths.
- [x] axe-core run across all 10 routes; no serious or critical findings.
- [x] 37 GET API operations returned HTTP 200.
- [x] Error/retry, customer, source links, upload, and scenario flows exercised.
- [x] Final evaluation and trajectory snapshot passed read-only checks.
- [x] All 67 canonical research/model artifacts match the pre-change baseline.
- [x] Dependency audit, static analysis, and privacy/dataflow scans are clear.
- [x] `.replit` and the working Replit workflow configuration preserved.

## Review gates

- [ ] Confirm required GitHub Actions are green on the current PR head.
- [ ] Review known limitations, especially absent application-level
  authentication and untested production deployment.
- [ ] Human approval and merge.
- [ ] Production deployment and post-deploy verification, if authorized.

The PR must not be merged automatically. GitHub check status should be checked
on the latest head commit immediately before merge.
