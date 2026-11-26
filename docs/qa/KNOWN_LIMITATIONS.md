# Phase 8 known limitations

1. **Historical scope:** This is a 2009–2010 dataset with a
   `2010-09-10` forecast cutoff, not live retail data or prospective
   validation.
2. **No authentication:** The app has no login or role-based authorization.
   A deployment is public unless a separate access-control layer is added.
3. **No production verification:** No production URL was supplied, so public
   deployment behavior, network latency, and deployment configuration were
   not tested.
4. **No notebook execution:** Notebooks were not re-executed because this
   could retrain models or rewrite conclusions and outputs. Saved artifacts
   and derived summaries passed read-only reproducibility checks.
5. **Browser scope:** Chromium 155 was used. Firefox/WebKit and manual
   screen-reader review were not available.
6. **Demo scope:** Core flows passed browser automation, but a timed spoken
   demonstration was not rehearsed.
7. **Load scope:** Local endpoint measurements are not an SLA. No production
   or multi-user load test was run.
8. **Remaining test warning:** Starlette's test client warns that its use of
   `httpx` is deprecated and recommends `httpx2`.
9. **No merge or deploy:** The PR must be reviewed by a person and merged
   separately; no production deploy was attempted.
