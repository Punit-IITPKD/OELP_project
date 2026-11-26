# Phase 8 baseline

## Source and environment

| Item | Baseline |
|---|---|
| Main commit | `a4aaaaa22e2e629d8bb5d8d2c48cb5acdab945a1` |
| QA branch | `feat/phase8-final-e2e-qa` |
| Locked Python runtime | Python 3.11.17 through `uv` |
| Workspace Python runtime | Python 3.13.11 |
| Node.js | 24.22.3 |
| pnpm | 10.26.1 |
| uv | 0.13.4 |
| Python dependency lock | `requirements-ci.txt`, SHA-256 `6fabc2dda3210fafe8bace67df37000c0db4a7ea288caa30d9a602d9a3300d28` |
| Frontend dependency lock | `pnpm-lock.yaml`, SHA-256 `eddf07410556f00d4f0f3d226f91ad78e57478712f2d99bb4634ed72afbd4f8d` |
| Runtime launcher | `scripts/run-oelp-web.sh` (API on 8000 and Vite on 5000) |
| Baseline port check | Ports 5000, 8000, and 4173 were free |
| Browser available | Chromium 155.0.8059.79 |
| Dataset files | Canonical raw workbook and processed/temporal data are present |
| Local Replit settings | Preserved from the workspace; excluded from the Phase 8 branch commits |

## Baseline quality gates

| Check | Result |
|---|---|
| `pnpm install --frozen-lockfile` | Passed; lockfile unchanged |
| Python suite, locked Python 3.11 | 195 passed; 1 deprecation warning |
| React/Vitest suite | 32 passed |
| Typecheck | Passed |
| Production build | Passed |
| GitHub Actions on `main` | Both jobs passed on `a4aaaaa`; [run 45606729422](https://github.com/Punit-IITPKD/OELP_project/actions/runs/45606729422) |

The Python warning is emitted by Starlette's test client: using `httpx` with
`starlette.testclient` is deprecated and the warning recommends `httpx2`.
It is recorded for triage rather than suppressed.

## Artifact baseline

`artifact-integrity-baseline.json` records SHA-256 and byte size for every
tracked file under `models/`, `notebooks/`, `data/raw/`, `data/processed/`,
`data/metrics/`, and `data/serving/`. It contains 67 files and was captured at
the main commit before product-code changes. Use
`python scripts/qa_artifact_integrity.py verify docs/qa/artifact-integrity-baseline.json`
to check for changes.

## Security scan baseline

The initial Replit dependency audit reported 11 critical, 55 high, and 38
moderate advisory records associated with the general dependency manifest and
lockfile. Static analysis and privacy/dataflow scans reported no findings.
Dependency records include multiple advisories for the same package; the
release report will distinguish the scanner's records from unique affected
packages and the locked runtime versions actually used by the launcher.
