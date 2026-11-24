# Final engineering validation

## Environment and quality gates

Validated from the Phase 7 branch based on `main` at `3fc4ca9`. The locked
runtime was Python 3.11.17, four reported CPUs, Node.js 24, and pnpm 10.

| Check | Result |
|---|---|
| Python test suite | **195 passed** |
| React test suite | **31 passed** |
| TypeScript workspace and app typecheck | **Passed** |
| Root production build (`pnpm run build`) | **Passed** |
| Final evaluation artifact `--check` | **Passed** |
| Trajectory serving snapshot `--check` | **Passed** |

The Python run emitted one `StarletteDeprecationWarning`: Starlette's test
client currently uses `httpx` and recommends `httpx2`. No test failed. The
production Vite build completed without chunk-size or other build warnings.

## Routes and integration coverage

The React tests exercise all ten routes: `/`, `/segments`, `/intelligence`,
`/behavior`, `/forecasting`, `/upload`, `/model-performance`,
`/revenue-exposure`, `/trajectories`, and `/research`. They verify lazy route
loading, page navigation, and the Research Overview's saved evidence, filters,
and error/retry state.

The complete Python suite covers the existing health, overview, segment,
customer, purchase history, forecast, explanation, reliability, behavior,
revenue, retention-scenario, trajectory, upload, and evaluation APIs. It also
validates the new read-only `GET /api/research/summary` response schema and
source provenance. Cross-module integration checks use real saved customer
IDs for a one-purchase/lapsed customer (12918), a frequent/recent customer
(18102), a sparse-history customer (12346), and a trajectory/FDA-eligible
customer (12417). Purchase history remains strictly before the saved cutoff;
financial formulas, GBP units, noncausal scenario status, and unsupported
trajectory values are checked.

## Saved artifact and prediction parity

All **14 tracked model files**, **24 tracked processed-data files**, **14
tracked notebook files**, and **12 pre-existing metric files** match their
`main` Git object hashes exactly. The only added item under `data/metrics` is
the derived final research summary. No existing notebook, model, processed
data, TEST metric, or research-result file changed.

The locked saved-model inference was compared with the original `main` code
for all **3,373 customers**. Customer IDs, cutoff, and all 33 saved prediction
fields—Global, Segment-aware, and Personalized purchase probabilities; the
nine saved Personalized purchase-curve points; and all saved historical,
segment, and Personalized conditional-spending and revenue fields—match
exactly. Both exported prediction tables have SHA-256
`863394fe20af09edc6aa2f49549e52404669a3dc1fc3fd0ea8781ab9a575ee4a`.

The trajectory snapshot is a derived, read-only artifact of **717,108
compressed bytes**. Rebuilding it uses historical transactions and already
saved trajectory models; it does not fit or update a model. Snapshot table
serialization normalizes insignificant floating-point drift at 12 decimal
places so its byte-for-byte reproducibility check remains stable.

## Backend performance

Measurements use the same fresh-Uvicorn-process harness, locked Python
environment, and 4-CPU environment before and after the optimization. Each
cold value is the median of three fresh processes; warm values use 20 requests
after one warm-up. Times are milliseconds.

| Request | Cold before | Cold after | Warm median before / p95 | Warm median after / p95 |
|---|---:|---:|---:|---:|
| Trajectory summary | 4,261.8 | 311.9 | 6.9 / 8.0 | 6.7 / 7.3 |
| Customer 18102 trajectory | 4,292.6 | 349.8 | 9.3 / 11.1 | 8.8 / 11.1 |
| Research summary (new endpoint) | — | 44.1 | — | 6.9 / 8.3 |

The comparable cold trajectory reductions are **92.7%** for the summary and
**91.9%** for the customer response. The research endpoint's three cold
samples ranged from 44.0 to 336.1 ms; its p95 is the largest sample because
the sample count is three.

Process start to healthy API response measured **3,747 ms median** before
(six starts) and **3,907 ms median** after (nine starts). This is a 160 ms
increase, not a startup improvement; the change deliberately moves expensive
trajectory feature/cluster computation out of the request path rather than
optimizing server startup. One after-run startup outlier raised its observed
maximum to 7,365 ms.

Warm-process RSS after endpoint warm-up was 260,399,104 bytes before and
260,661,248 bytes after for the trajectory summary (about 248.4 and 248.7
MiB). The research endpoint measured 231,772,160 bytes (about 221.1 MiB).
These are process RSS observations, not memory limits or deployment capacity
claims.

The optimization builds `data/serving/trajectory_snapshot.json.gz` offline
from historical pre-cutoff data and saved artifacts. API requests load and
cache that validated snapshot instead of rebuilding trajectory features and
assigning saved clusters on first use.

## Frontend bundle and visual verification

The previous production build emitted one 889,810-byte JavaScript bundle
(240,940 bytes gzip). The current production build emits 917,397 JavaScript
bytes in 23 files; total emitted JavaScript is 3.1% larger because code is
split into route and shared chunks. The largest output chunk fell from
889,810 to 396,015 bytes.

The actual initial home-route graph is **306,125 bytes** (95,685 bytes summed
gzip), a **65.6% raw / 60.3% gzip reduction** from the prior single bundle.
The HTML entry's statically loaded JavaScript is 299,037 bytes. Chart-heavy
routes and their 396,015-byte shared chart implementation are loaded only
when needed.

| Lazy page chunk | Raw bytes |
|---|---:|
| Business overview | 6,747 |
| Segments | 9,520 |
| Customer intelligence | 26,626 |
| Behavior indicators | 24,110 |
| Forecasting | 7,044 |
| Upload analysis | 11,679 |
| Model performance | 12,409 |
| Revenue and retention | 35,265 |
| Trajectory explorer | 32,085 |
| Research overview | 20,570 |

The Research Overview was visually checked in the running app at 1440×1000 and
402×874. The desktop evidence cards and notebook tables fit the content area;
the mobile view stacks cards and keeps navigation compact without visible
horizontal overflow. Current browser logs showed Vite/React development
information only and no application errors.

## Known limitations

- This remains a historical 2009–2010 study, not a live retail forecast or
  prospective validation.
- The final research endpoint caches its validated summary in process memory;
  source-manifest verification runs when the process loads the summary. A
  stale or missing artifact returns an error instead of serving an old summary.
- The cold benchmark is an engineering measurement from this environment, not
  a GitHub-runner SLA. No wall-clock performance threshold was added to CI.
- Total emitted JavaScript grew slightly, though the initial route payload was
  substantially reduced. The shared chart chunk remains the largest lazy
  chunk.
- No notebooks were rerun because their cells may retrain or export research
  models. Reproducibility and service checks use the saved artifacts without
  changing them.
