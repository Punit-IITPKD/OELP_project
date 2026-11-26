# Phase 8 API integration results

## Live route checks

The running FastAPI app exposed 42 OpenAPI operations:

| Method | Count | Verification |
|---|---:|---|
| GET | 37 | All returned HTTP 200 in the live smoke check |
| POST | 5 | Scenario and comparison exercised in Playwright and Python tests; all three upload operations exercised with a synthetic CSV |

The GET smoke also checked the model calibration asset endpoint, which
correctly returned `image/png`. Customer-specific calls used saved customer
18102. The full Python suite passed 195 tests.

## Data and model integrity

- Forecast, explanation, reliability, behavior, revenue exposure, and
  trajectory responses share the same saved customer and historical cutoff.
- Historical transactions in the customer demonstration are strictly earlier
  than `2010-09-10`.
- API model-performance metrics match the saved Notebook results.
- The two scenario POST operations are explicitly hypothetical and
  noncausal; no outreach or contact is initiated.
- CSV preview, analysis, and export use synthetic data held in memory by the
  test flow. The flow does not persist customer uploads.

## Negative and recovery cases

Python coverage checks unknown customer IDs, invalid upload mappings,
unsupported forecast horizons, invalid trajectory filters, date-window
validation, invalid scenario assumptions, and cutoff leakage. Browser
automation intercepts one overview request as HTTP 503, verifies the visible
error state and absence of stale dashboard metrics, then retries successfully.

## API limitations

The app does not implement login, user roles, or role-based authorization.
This QA run did not add an authentication layer. Treat any public deployment
as publicly accessible unless access control is configured separately.
