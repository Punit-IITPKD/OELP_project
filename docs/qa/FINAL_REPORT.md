# Phase 8 release QA report

## Outcome

The local release checks passed on `feat/phase8-final-e2e-qa`, based on main
commit `a4aaaaa22e2e629d8bb5d8d2c48cb5acdab945a1`. The 67-file canonical
artifact baseline is unchanged. The working React/FastAPI app starts cleanly,
and its preview routes are available.

The branch is ready for PR review after the current head's GitHub Actions
checks pass. It has not been merged or deployed. Review live PR checks before
merging; this report intentionally does not duplicate those time-sensitive
statuses.

## Verified gates

| Area | Result |
|---|---|
| Python tests | 195 passed; one Starlette/httpx deprecation warning |
| React tests | 32 passed |
| Typecheck | Passed |
| Production build | Passed; 2,163 modules transformed |
| Browser release suite | 28 passed on Chromium |
| Desktop and narrow-phone routes | All 10 routes passed at each viewport |
| WCAG automated scan | No serious or critical axe findings across all 10 routes |
| Live API smoke | 37/37 GET operations returned HTTP 200; one calibration endpoint returned PNG |
| API operations | 42 OpenAPI operations: 37 GET and 5 POST |
| Research/model artifact integrity | All 67 baseline files match |
| Final research evaluation check | Passed without writing files |
| Trajectory snapshot check | Passed without writing files |
| Dependency audit | 0 critical, 0 high, 0 moderate |
| Static analysis / privacy dataflow | 0 findings / 0 findings |

## Scientific and deployment boundaries

- No notebook, model, prediction, metric, processed-data, or serving artifact
  was changed.
- No notebook was re-executed because notebook cells can retrain models or
  overwrite research outputs. Reproducibility was checked against saved
  artifacts and the locked test environment instead.
- The study remains historical: UCI Online Retail Year 1, with a
  `2010-09-10` forecast cutoff. This is not a live forecast or causal retention
  estimate.
- The production deployment URL was not supplied or tested. Only the running
  Replit development preview was checked.
- Chromium was available; Firefox/WebKit, Lighthouse, a timed spoken demo, and
  a production load test were not executed.

## Remaining warning

Pytest reports that Starlette's `TestClient` use of `httpx` is deprecated and
recommends `httpx2`. The warning does not fail the suite. The package audit is
clear after raising vulnerable dependency floors and refreshing the
`postcss-selector-parser` resolution.

See [the coverage matrix](TEST_COVERAGE_MATRIX.md),
[model validation](MODEL_VALIDATION.md),
[API integration results](API_INTEGRATION.md),
[browser results](FRONTEND_E2E.md),
[performance measurements](PERFORMANCE_RELIABILITY.md),
[security and accessibility](SECURITY_ACCESSIBILITY.md),
[deployment readiness](DEPLOYMENT_READINESS.md),
[demo rehearsal notes](DEMO_REHEARSAL.md),
[known limitations](KNOWN_LIMITATIONS.md), and
[the final checklist](FINAL_CHECKLIST.md).
