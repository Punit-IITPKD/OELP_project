# Reproducibility guide

## Environment

- Python: **3.11** for the FastAPI service, saved-model loading, and Python tests.
- Python dependencies: hash-locked `requirements-ci.txt`, generated from
  `requirements-ci.in`. The Replit launcher explicitly selects Python 3.11 with
  `uv`, even when the base Replit Python module is newer.
- Node.js: **24** in the configured Replit runtime.
- Package manager: **pnpm 10** with the workspace lockfile.

The raw Year 1 source workbook and canonical processed files are present in the
repository checkout. Saved models and evaluation artifacts are also required
for the historical application. A clean clone therefore needs the normal Git
checkout, including the tracked data and model files.

## Install and run

Install the JavaScript workspace and launch the API and React development
server together:

```bash
pnpm install --frozen-lockfile
pnpm dev
```

The configured web launcher is `scripts/run-oelp-web.sh`. It starts FastAPI on
the internal port 8000 with the locked Python 3.11 environment, waits for
`/api/health`, then starts Vite on port 5000.

To run only FastAPI:

```bash
PYTHONPATH=. uv run --no-project --python 3.11 \
  --with-requirements requirements-ci.txt \
  uvicorn api.main:app --host 127.0.0.1 --port 8000
```

To run the front end by itself when the API is already available:

```bash
pnpm --filter @workspace/oelp-customer-intelligence run dev:vite
```

## Phase 7 aggregate artifact generation

The final evaluation and trajectory serving snapshot are derived artifacts.
Neither command fits a model or changes saved predictions.

```bash
PYTHONPATH=. uv run --no-project --python 3.11 \
  --with-requirements requirements-ci.txt \
  python scripts/build_final_evaluation.py

PYTHONPATH=. uv run --no-project --python 3.11 \
  --with-requirements requirements-ci.txt \
  python scripts/build_trajectory_serving_snapshot.py
```

Verify that both checked-in outputs match their sources without writing files:

```bash
PYTHONPATH=. uv run --no-project --python 3.11 \
  --with-requirements requirements-ci.txt \
  python scripts/build_final_evaluation.py --check

PYTHONPATH=. uv run --no-project --python 3.11 \
  --with-requirements requirements-ci.txt \
  python scripts/build_trajectory_serving_snapshot.py --check
```

The evaluation builder reads the 11 notebook files, saved evaluation summaries,
temporal split metadata, and model metadata. It writes
`data/metrics/final_project_evaluation.json` atomically and records source
SHA-256 values. The trajectory builder reads the canonical historical order
data and frozen trajectory model artifacts, creates cutoff-safe serving
records, and writes `data/serving/trajectory_snapshot.json.gz` atomically. A
source or model metadata change makes `--check` fail until the output is
regenerated and reviewed.

Measure fresh-process startup, cold API requests, and warmed endpoint latency
without fitting models:

```bash
PYTHONPATH=. uv run --no-project --python 3.11 \
  --with-requirements requirements-ci.txt \
  python scripts/benchmark_phase7.py --trials 3 --warm-samples 20
```

The benchmark starts a fresh Uvicorn process for each cold measurement, records
process-start-to-health-ready time, then measures warm samples after one
endpoint warm-up. It reports medians and nearest-rank p95 values, response
sizes, CPU count, and process RSS after warm-up. The trajectory customer
example is a real saved ID (18102); the benchmark reads its aggregate,
cutoff-safe trajectory response only.

## Tests and production build

Run the same locked Python environment used by CI:

```bash
PYTHONPATH=. uv run --no-project --python 3.11 \
  --with-requirements requirements-ci.txt \
  pytest -q tests
```

Run the React checks:

```bash
pnpm test
pnpm run typecheck
pnpm --filter @workspace/oelp-customer-intelligence run build
```

The root command `pnpm run build` also builds the workspace libraries and app.

## Re-executing notebooks

Notebook execution is a research operation, not an application startup step.
It can rewrite notebook outputs and, for model notebooks, regenerate artifacts.
Use a disposable working copy and inspect the notebook's input/output paths
before running it. Do not execute notebooks to start the app or validate the
Phase 7 aggregate builders.

General execution pattern:

```bash
uv run --no-project --python 3.11 \
  --with-requirements requirements-ci.txt \
  --with jupyter --with ipykernel \
  python -m jupyter execute --inplace notebooks/<notebook-file>.ipynb
```

Notebook 10 requires its saved artifact build step before execution:

```bash
uv run --no-project --python 3.11 --with-requirements requirements-ci.txt \
  python scripts/build_notebook10.py
uv run --no-project --python 3.11 --with-requirements requirements-ci.txt \
  --with jupyter --with ipykernel \
  python -m jupyter execute --inplace \
  notebooks/10_Revenue_at_Risk_and_Retention_Planning.ipynb
```

Notebook 11 can be executed with the general pattern using
`notebooks/11_Customer_Retention_Trajectory_Analysis.ipynb`. Notebook-specific
data, methods, metrics, and caveats are documented in the notebook registry and
the linked research-method documents.

## Common setup and validation issues

- **Python 3.13 model-loading differences:** use the explicit Python 3.11 `uv`
  commands above. Do not rely on the shell's default Python version.
- **Stale generated evaluation:** run `build_final_evaluation.py --check` to
  identify changed or missing sources; rebuild only after reviewing the source
  changes.
- **Stale trajectory snapshot:** run `build_trajectory_serving_snapshot.py
  --check`. Rebuild it only when canonical historical inputs or frozen model
  metadata intentionally change.
- **Missing data or models:** the API fails explicitly if required saved
  artifacts are unavailable. A research summary with stale source hashes
  returns HTTP 503 rather than serving an old summary.
- **Notebook output changes:** notebook re-execution may update outputs and
  artifacts. Review those changes separately; the Phase 7 tasks do not require
  re-training or changing the saved Purchase Clock or spending forecasts.
