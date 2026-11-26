# Phase 8 performance and reliability measurements

## API latency

Measurements used the locked Python 3.11.17 environment on a four-CPU
workspace. Cold values are medians of three fresh Uvicorn processes; warm
values use 20 requests after one warm-up. These are local engineering
measurements, not production SLAs.

| Endpoint | Prior Phase 7 cold median | Current cold median | Current warm median / p95 |
|---|---:|---:|---:|
| Trajectory summary | 311.9 ms | 265.9 ms | 7.1 / 7.6 ms |
| Customer 18102 trajectory | 349.8 ms | 270.2 ms | 8.7 / 11.7 ms |
| Research summary | 44.1 ms | 51.0 ms | 7.2 / 12.2 ms |

Process start to healthy API response measured 3,920 ms median across nine
starts, compared with 3,907 ms in the earlier Phase 7 measurement. The small
difference is not treated as a startup improvement. The research cold and
warm p95 values are based on small samples and vary from the earlier run.

Warm-process RSS after endpoint warm-up:

| Endpoint | RSS |
|---|---:|
| Research summary | 231,968,768 bytes (about 221.2 MiB) |
| Trajectory summary | 259,026,944 bytes (about 247.1 MiB) |
| Customer 18102 trajectory | 259,772,416 bytes (about 247.8 MiB) |

## Frontend bundles

The production build emitted **918,927 bytes of JavaScript across 23 files**.
The prior Phase 7 build emitted 917,397 bytes across 23 files.

| Route graph | Prior Phase 7 raw / gzip | Current raw / gzip |
|---|---:|---:|
| Initial business overview | 306,125 / 95,685 bytes | 307,062 / 95,860 bytes |
| Research overview | — | 320,924 / 99,634 bytes |
| Segments, including chart library | — | 706,015 / 204,531 bytes |

The initial overview graph increased by 937 raw bytes (0.31%) and 175 gzip
bytes (0.18%). The shared chart implementation remains a lazy route dependency;
the initial business overview does not load that 396,015-byte chart chunk.
This preserves route-level splitting with no material first-route regression.

## Reliability checks

The browser suite tested retry recovery after a one-time 503 response. The
served trajectory snapshot passed its provenance and byte-reproducibility
check. No production load test, multi-process capacity test, or public-network
latency test was run.
