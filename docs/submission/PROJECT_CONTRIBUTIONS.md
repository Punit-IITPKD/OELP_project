# Project Contributions

## Research and analysis

1. **Integrated eleven-notebook research pipeline.** The work documents transaction quality, customer features, interpurchase distributions, segmentation, temporal validation, purchase timing, spending, behavior, reliability, revenue screening, and trajectories as connected but distinct analyses.
2. **Explicit temporal evaluation.** The Purchase Clock and spending evaluations use outcome-matured TRAIN/VAL/TEST cutoffs and a locked 3,373-customer TEST cohort at 30, 60, and 90 days. Horizon results are not treated as interchangeable.
3. **Descriptive segmentation with stability reporting.** Two RFM clusters are reported for 4,312 customers with saved seed-stability results. The labels are explicitly not presented as prospective churn scores.
4. **Forecast reliability and explanation context.** The saved model evaluation includes calibration, subgroup diagnostics, customer-level bootstrap intervals, and input-sensitivity checks; these are framed as group diagnostics and noncausal sensitivities.
5. **Evidence-bounded behavior and retention analysis.** Supported, inconclusive, unsupported, and not-evaluable outcomes remain distinct. Reference-based exposure stays null/not estimable, and scenario assumptions are not presented as measured uplift.
6. **Method-specific trajectory evidence.** Three selected trajectory-shape clusters are descriptive. The report separates the 1,100-customer cluster support, 659 eligible functional curves, TRAIN-fitted explained variance, and TEST reconstruction error.

## Engineering

1. **Read-only research evidence endpoint and overview.** The dashboard exposes a generated evidence registry and source provenance without training models during a request.
2. **Frozen-model application serving.** The React/FastAPI system loads saved model artifacts and a validated trajectory snapshot; research notebooks remain an offline workflow.
3. **Route-level frontend loading.** Pages are loaded by route, separating the initial overview from chart-heavy features.
4. **Regression and artifact safeguards.** The merged Phase 8 baseline includes Python and React coverage, Chromium walkthrough coverage, API smoke checks, typechecking, production build, and a 67-file protected-artifact baseline.

## What this project does not claim

- It does not establish a causal effect of a retention campaign.
- It does not establish trajectory-based incremental prediction beyond the saved Purchase Clock.
- It does not convert an inactivity threshold, segment, or trajectory cluster into a permanent churn label or risk rank.
- It does not claim performance on a current retailer or a prospective deployment population.
- It does not treat expected revenue, forecast disagreement, or the nonreturn-weighted proxy as realized or recoverable revenue.
