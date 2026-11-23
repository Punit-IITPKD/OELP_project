# PR #4 clean integration strategy

## Current state

PR #3 targets `main` and introduces the Streamlit presentation alongside the
notebook evaluation exporter and saved evaluation artifacts. PR #4 is based on
PR #3 and adds the React/FastAPI application. Retargeting PR #4 directly to
`main` would include every PR #3 change in its diff; rewriting the published
PR #4 branch would also risk losing review context. Neither action is part of
this correction.

## Safe sequence

1. Keep PR #4 based on PR #3 while correcting and validating the React/FastAPI
   implementation. Do not force-push, retarget, or merge either pull request.
2. For a React-only route to `main`, create a new branch from the latest
   `main`; do not reuse or rewrite the published PR #4 branch.
3. Bring forward the small shared foundation needed by the React app:
   - From PR #3: `scripts/export_notebook_evaluation.py`, the saved
     `data/metrics/notebook_evaluation_summary.json` and calibration images,
     `app/config.py`, `app/__init__.py`,
     `app/services/__init__.py`, and `app/services/upload_service.py`.
   - From PR #4: `src/forecast_application.py`, `api/`, the customer
     intelligence web artifact, the OpenAPI spec and generated client
     packages, `scripts/run-oelp-web.sh`, and their required dependency and
     test changes.
   - Keep the shared modeling and inference modules already present on `main`;
     do not replace or retrain them.
4. Exclude Streamlit-only presentation files from the clean branch:
   `app/main.py`, `app/components/ui.py`, `app/pages/`,
   `app/services/demo_service.py`, and `tests/test_streamlit_app.py`. Keep
   the small `app` support package listed above because the current API
   imports its configuration and upload-analysis service.
5. Run the same Python regression, API, generated-client, frontend, and
   saved-prediction parity checks on the clean branch. Open a separate PR
   targeting `main` only after those checks pass.

## Review boundary

This document records the safe integration path; it does not create a new
branch or pull request, change either PR's base, or close PR #4. The current
PR #4 remains the reviewable correction branch until the clean main-targeted
branch is verified and the repository owner chooses how to proceed.
