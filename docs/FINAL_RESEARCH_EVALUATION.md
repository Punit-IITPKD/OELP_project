# Final research evaluation

## Abstract

This project studies repeat purchasing in the Year 1 portion of the UCI Online
Retail II data. Eleven notebooks cover transaction quality, customer features,
interpurchase intervals, descriptive RFM segments, temporal validation, purchase
probability, expected spending, behavioral indicators, model reliability,
retention screening, and historical purchasing trajectories.

The Phase 7 summary consolidates saved notebook evaluations and model metadata.
It is not a twelfth model and does not refit or calibrate any saved model. The
analysis is a historical backtest, not a live business forecast, customer churn
label, causal retention estimate, or individual guarantee.

## Dataset, population, and protocol

The saved analysis spans 2009-12-01 through 2010-12-09 and uses a fixed
2010-09-10 TEST cutoff for the 30-, 60-, and 90-day purchase evaluation. The
locked prediction cohort contains 3,373 customers at each horizon. Outcome
windows mature at different dates, so metrics are compared only when the target,
horizon, cohort, and protocol match.

Models and ranking rules are selected using historical TRAIN/VAL data where
specified; TEST is held out for the final reported comparison. The source
artifacts retain the exact temporal splits, model versions, metric definitions,
and per-method population counts. Notebook 11 uses narrower, method-specific
history support and reports those populations separately.

## Notebook contribution matrix

| Notebook | Contribution and validated finding | What remains unproven |
|---|---|---|
| 01 — Exploratory data analysis | Documents transaction quality, extreme-price handling, and why missing customer IDs are not imputed for customer-level analysis. The observation window is short and left-truncated. | A first observed order is not necessarily customer acquisition; transactions without customer IDs cannot be assigned to customer histories. |
| 02 — Customer feature engineering | Builds customer-level recency, frequency, spend, and purchase-gap features. Missing recency and gap values are preserved when the observed history cannot support them. | A single observed purchase does not provide an interpurchase gap; no imputation can recover unobserved history. |
| 03 — Interpurchase distributions | Gamma has the lowest saved AIC among the compared positive-gap distributions. The empirical P90 gap is 101.9 days. | Parametric fits are descriptive; the 101.9-day threshold is not a churn label or a prospective decision rule. |
| 04 — K-means customer segments | Descriptive RFM K-means selects two clusters for 4,312 customers. Mean seed ARI is 0.998 and the minimum is 0.9935. | Stable descriptive clusters are not prospective churn scores or evidence of treatment response. |
| 05 — Statistical validation and time splits | Establishes separate, outcome-matured TRAIN/VAL/TEST cutoffs for 30-, 60-, and 90-day targets, all evaluated at the 2010-09-10 TEST cutoff. | Historical association does not establish causation. Different horizon cohorts and end dates are not interchangeable. |
| 06 — Personalized Purchase Clock | Across the three saved TEST horizons, the Personalized model has the highest ROC-AUC and average precision and lowest Brier score among the saved Global, Segment-aware, and Personalized comparisons. | Calibration varies by horizon; the results are historical and not current-business predictions. |
| 07 — Future spending forecasts | The Personalized two-stage estimate has the lowest saved MAE at 30, 60, and 90 days. The forecasts combine purchase probability with conditional expected spending. | Bias and aggregate calibration still vary. Expected revenue is not a realized amount, and disagreement between models is not a loss. |
| 08 — Behavioral change detection | H1 (unusually long personal gap) and H3 (falling revenue rate) are supported in multiple horizons. H2 and H4 are inconclusive. Behavior-only predictors did not outperform the saved Purchase Clock on the recorded TEST average-precision comparisons. | H5 is not evaluable: no chronologically eligible saved Purchase Clock vintage exists at the official TRAIN cutoffs. No operational alert policy is supported. |
| 09 — Prediction reliability and explainability | Adds fixed-bin calibration, subgroup diagnostics, customer-level bootstrap intervals for aggregate metrics, and saved-model input sensitivity. The 30-day Personalized model has Brier 0.178534 and fixed-bin ECE 0.060562 on 3,373 TEST customers. | These are historical group diagnostics, not individual confidence guarantees. Input substitutions are noncausal sensitivities. |
| 10 — Revenue exposure and retention planning | Separates expected revenue, forecast disagreement, a nonreturn-weighted spending proxy, and hypothetical campaign scenarios. Ranking rules are selected on validation and evaluated on locked TEST. | Reference-based revenue exposure is not estimable; the predictive ranking hypothesis is not supported on locked TEST. The 90-day ranking is exploratory. Response and uplift assumptions are hypothetical, not causal. |
| 11 — Customer retention trajectories | Selects three descriptive shape clusters; 1,100 TEST customers meet the shape-clustering support rule. Functional PCA evaluates 659 TEST curves using a TRAIN-fitted representation: 98.82% TRAIN cumulative explained variance and TEST reconstruction RMSE 0.006248. | Clusters are not risk ranks. Standalone trajectory comparisons do not establish conditional incremental value beyond the saved Purchase Clock. |

The generated notebook registry adds each notebook's objective, method, dataset,
cutoff, population, horizon coverage, source version, major findings, source
fields, limitations, and a reproduction command. The registry is in
`data/metrics/final_project_evaluation.json`; its `source_manifest` includes
SHA-256 hashes for all eleven notebooks and their evidence artifacts.

## Prediction and spending evaluation

### Purchase probability

The table below shows the saved Personalized Purchase Clock rows. The three
metrics answer different questions and are not combined into a single model
score.

| Horizon | TEST customers | ROC-AUC | Average precision | Brier score |
|---:|---:|---:|---:|---:|
| 30 days | 3,373 | 0.720882 | 0.537588 | 0.178534 |
| 60 days | 3,373 | 0.721767 | 0.716292 | 0.214200 |
| 90 days | 3,373 | 0.719368 | 0.784723 | 0.215308 |

The source values are `purchase_clock.test_metrics` in
`data/metrics/notebook_evaluation_summary.json`. Fixed-bin calibration results
are separately recorded in
`data/metrics/prediction_reliability_evaluation.json`. Calibration error
definitions depend on their saved binning protocol; values from different
notebooks must not be treated as interchangeable.

### Expected revenue

The saved Personalized two-stage TEST results are:

| Horizon | MAE (£) | RMSE (£) | Mean bias (£) | Aggregate calibration ratio |
|---:|---:|---:|---:|---:|
| 30 days | 243.18 | 871.30 | -29.96 | 0.864 |
| 60 days | 383.78 | 1,466.12 | -92.37 | 0.801 |
| 90 days | 547.38 | 2,111.73 | -187.86 | 0.746 |

These values are for the same locked 3,373-customer TEST cohort per horizon.
They are aggregate diagnostics, not promises for a specific customer. The
two-stage expected-revenue quantity is saved purchase probability multiplied by
saved conditional expected spending.

## Hypothesis evidence

The JSON registry preserves the original saved labels and maps them to five
display categories: `supported`, `not_supported`, `inconclusive`,
`not_evaluable`, and `descriptive_only`. For Notebook 08, the saved average
precision differences and 95% intervals are retained by horizon when present.
The original source artifact and field accompany each item.

| Notebook hypothesis | Consolidated status | Interpretation |
|---|---|---|
| 08-H1 | Supported | Evidence is supported in multiple horizons for the personal-gap indicator. |
| 08-H2 | Inconclusive | Saved intervals do not resolve the recent purchase-rate comparison. |
| 08-H3 | Supported | Evidence is supported in multiple horizons for declining revenue rate. |
| 08-H4 | Inconclusive | Direction/persistence evidence remains uncertain. |
| 08-H5 | Not evaluable | Candidate F was not fitted because eligible historical Purchase Clock vintages were unavailable. |
| 10-H1 | Descriptive only | Financial concentration is reported descriptively. |
| 10-H2 | Descriptive only | Ranking overlap is not evidence of better interventions. |
| 10-H3 | Descriptive only | Saved TEST forecast bias is a diagnostic, not a forecast correction. |
| 10-H4 | Descriptive only | Budget/cost sensitivity depends on explicit hypothetical inputs. |
| 10-H5 | Descriptive only | Screening-order stability is not causal scenario robustness. |
| 10-H6 | Not supported | The validation-selected ranking policy did not consistently beat matched baselines on locked TEST; 90-day selection is unavailable. |

The separate Notebook 11 incremental-prediction question is **inconclusive**.
The saved paired 95% Brier-difference interval on the 1,306-customer summary
trajectory subset includes zero; this does not establish equivalence or
conditional incremental value. The functional-curve subset is narrower still.

## Financial definitions

| Quantity | Definition and status |
|---|---|
| Observed historical revenue | Transaction value in the historical source data; not a future forecast. |
| Predicted conditional spending | Saved expected spending conditional on a purchase. |
| Expected future revenue | Saved purchase probability × conditional expected spending. |
| Forecast disagreement | Differences between saved model forecasts; not a shortfall or loss. |
| Reference-based revenue exposure | `null`, status `not_estimable`; no defensible matched reference forecast is saved. |
| Nonreturn-weighted spending proxy | `(1 − purchase probability) × conditional expected spending`; screening proxy only, not recoverable revenue. |
| Hypothetical campaign incremental revenue | Depends on user-entered hypothetical response/uplift assumptions; no causal estimate. |
| Hypothetical incremental contribution | Only calculated when a gross-margin assumption is supplied; still hypothetical. |

The application and API must preserve the reference exposure total as null and
must not replace it with a manufactured loss estimate.

## Statistical interpretation and threats to validity

- The customer histories are short and left-truncated; first observed purchase
  does not necessarily mean acquisition.
- “No purchase within the next H days” is horizon-specific and is not proof of
  permanent churn.
- Different horizon populations, support rules, and feature availability limit
  cross-table comparisons.
- TEST is reserved for evaluation. A missing eligible saved model vintage is
  reported as not evaluable rather than filled with a new fit.
- Bootstrap intervals quantify the saved fixed-model metric procedure; they do
  not represent individual outcome uncertainty or parameter uncertainty.
- RFM groups, trajectory clusters, and reliability groups are descriptive
  groupings, not risk ranks or causal mechanisms.
- The dataset has no randomized retention treatment or response outcomes.
- Several source analyses are descriptive, and missing evidence is not treated
  as negative evidence.

## Future research

Useful next evidence would include longer histories, additional prospective
cutoffs, chronologically eligible Purchase Clock vintages for conditional
comparisons, and randomized retention experiments with measured response and
incremental outcomes. Those additions are outside the current saved evidence.

## Conclusion

The notebooks contribute a reproducible historical workflow, descriptive
segmentation, validated purchase and spending comparisons, and method-specific
reliability and trajectory evidence. The evidence supports retaining the
Personalized Purchase Clock as the strongest saved probability comparator in
this backtest, while keeping spending calibration, behavioral utility, revenue
exposure, and causal campaign value appropriately qualified. The Phase 7
consolidation reports these limits rather than expanding the claims.

## Primary sources

- `data/metrics/final_project_evaluation.json`
- `data/metrics/notebook_evaluation_summary.json`
- `data/metrics/behavior_monitor_evaluation.json`
- `data/metrics/prediction_reliability_evaluation.json`
- `data/metrics/revenue_exposure_evaluation.json`
- `data/metrics/trajectory_analysis_evaluation.json`
- `data/processed/temporal/temporal_split_metadata.json`
- `models/trajectory_analysis/metadata.json`

The generated `source_manifest` contains the SHA-256 digest for each of the 30
inputs. In addition to all 11 notebook files listed in the contribution matrix,
those inputs are:

**Saved evaluations**

- `data/metrics/notebook_evaluation_summary.json`
- `data/metrics/behavior_monitor_evaluation.json`
- `data/metrics/prediction_reliability_evaluation.json`
- `data/metrics/revenue_exposure_evaluation.json`
- `data/metrics/trajectory_analysis_evaluation.json`
- `data/metrics/retention_scenario_sensitivity.json`

**Processed evidence**

- `data/processed/segmentation_metadata.json`
- `data/processed/temporal/temporal_split_metadata.json`
- `data/processed/temporal/validation_results.json`
- `data/processed/customer_features.csv`
- `data/processed/interpurchase_distribution_results.csv`
- `data/processed/inactivity_threshold.json`
- `data/processed/clustering_metrics.csv`

**Saved model metadata**

- `models/purchase_clock/metadata.json`
- `models/spending_model/metadata.json`
- `models/behavior_monitor/metadata.json`
- `models/prediction_reliability/metadata.json`
- `models/revenue_exposure/metadata.json`
- `models/trajectory_analysis/metadata.json`
