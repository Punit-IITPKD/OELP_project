# Phase 8 model and prediction validation

## Protected-artifact integrity

`docs/qa/artifact-integrity-baseline.json` records SHA-256 and size for
67 canonical files under `models/`, `notebooks/`, `data/raw/`,
`data/processed/`, `data/metrics/`, and `data/serving/`. The final verification
reported:

```text
PASS: 67 canonical artifacts match a4aaaaa22e2e629d8bb5d8d2c48cb5acdab945a1
```

There are no tracked changes under the protected research, model, prediction,
metrics, or serving paths.

## Saved-model parity

`tests/test_explainability.py` loads the saved Purchase Clock and spending
artifacts and compares predictions for the complete 3,373-customer forecast
cohort at 30, 60, and 90 days. Purchase probabilities and personalized expected
revenue are compared to direct inference from those saved models at
`rtol=1e-12` and `atol=1e-12`.

Additional regression coverage verifies that:

- Saved customer forecasts align with the cached historical snapshot.
- The model-performance API is identical to the saved Notebook evaluation
  output, including the 3,373-customer TEST cohort and metrics.
- Purchase history is strictly before the recorded `2010-09-10` cutoff.
- Adding a future transaction does not change a past forecast, feature row,
  support flag, or trajectory snapshot.
- Reloading saved Purchase Clock and spending artifacts produces identical
  inference.

The full Python test suite passed: 195 tests.

## Reproducibility checks

Both saved derived outputs passed read-only checks:

```text
Final research summary is reproducible: data/metrics/final_project_evaluation.json
Trajectory serving snapshot is reproducible: data/serving/trajectory_snapshot.json.gz (717108 bytes)
```

No model fitting or notebook execution was performed. Notebook execution is
intentionally excluded because it can retrain models or rewrite outputs.
