# Prediction Reliability and Explainability

## Scope and model versions

Notebook 09 explains, but does not retrain, recalibrate, or replace, the saved
OELP models. The fixed retrospective TEST forecast cutoff is **2010-09-10**;
all reported purchase and expected-revenue metrics use the aligned **3,373**
customer cohort. Individual features are computed only from transactions
strictly before that cutoff.

The saved Purchase Clock is `purchase-clock-v2`, trained through 2010-03-01.
It is a discrete-time logistic hazard model with nine 10-day intervals. Its
saved preprocessing pipeline produces 21 transformed predictors; probabilities
are cumulative survival complements:

```text
P(T <= H) = 1 - product(1 - h_t), for intervals t through H
```

The saved spending bundle is `spending-forecast-v2`, with separate 30-, 60-,
and 90-day Ridge pipelines. Each conditional model uses its saved imputation,
log1p feature transformation, TRAIN-fitted clipping, scaling, and one-hot
encoding. The trained target is log-space; inference uses the original
horizon-specific smearing correction when converting back to spending.
Expected revenue remains the saved two-stage calculation:

```text
expected revenue(H) = purchase probability(H) * conditional expected spending(H)
```

`src/explainability.py` inspects and uses these saved objects directly. It does
not contain copied coefficients or call a model-training function.

## Explanation methods and limits

For each interval, the fitted preprocessing is applied to the actual
customer/interval row. The logistic coefficient contributions are additive in
log-odds:

```text
logit(h_t) = intercept + sum(coefficient_j * transformed_feature_j)
h_t = sigmoid(logit(h_t))
```

The reconstructed hazard is checked against the saved fitted logistic estimator
with `rtol=1e-10` and `atol=1e-12`. Cumulative purchase probabilities are
reconstructed from the ordered nine-hazard curve and checked against the saved
inference for P30, P60, and P90.

Because cumulative probability is nonlinear, the app does not present interval
logit coefficients as additive P30/P60/P90 effects. Instead, it shows two
reference analyses:

1. A single-input sensitivity replaces one model input with its TRAIN-derived
   reference and recomputes the entire hazard curve. The signed effect is
   `original probability - reference-replacement probability`.
2. A combined reference profile replaces all eligible inputs with the TRAIN
   median/lexical mode profile.

These are model-input sensitivities, **not causal effects**. Replacing one
derived input (such as recency, frequency, or a fitted segment) can create an
unrealistic combination. The combined profile is a reproducible reference, not
a claim that a real customer has exactly that profile.

Conditional spending is reconstructed from the fitted transformed Ridge score.
The UI reports log-space contributions, the final smearing-adjusted conditional
estimate, purchase probability, and saved expected-revenue product. It does not
exponentiate individual feature effects into additive currency amounts or divide
by a near-zero probability to derive spending.

TRAIN references and 1st/99th percentile numeric support bounds are saved in
`models/prediction_reliability/reference_profile.json`. The purchase profile
uses the exact saved Purchase Clock TRAIN split after its saved segmentation
transform; the spending profiles use each horizon's own TRAIN split and
segmentation transform. Reference profile version:
`prediction-reliability-reference-v1`, feature schema:
`customer-forecast-features-v2`.

## Historical calibration protocol

Bin edges are selected before TEST evaluation from validation predictions only.
The policy first requires at least 30 validation customers in every populated
bin, then prefers greater minimum populated-bin support and fewer empty bins.
The 30-day horizon selects ten equal-width bins. The 60- and 90-day horizons
select validation-quantile bins. The 90-day edges use the available July 1
validation-vintage P90 probability distribution; no validation outcomes select
those edges.

Validation cohorts:

| Horizon | Validation cutoff | Customers | Model vintage |
|---|---:|---:|---|
| 30 days | 2010-08-01 | 3,159 | validation-vintage Purchase Clock, available by 2010-06-30 |
| 60 days | 2010-07-01 | 2,973 | validation-vintage Purchase Clock, available by 2010-06-30 |
| 90-day probability bins | 2010-07-01 | 2,973 | validation-vintage P90 probabilities only |

The final 90-day spending model has no eligible prospective validation vintage.
For that reason, Notebook 09 reports retrospective TEST revenue diagnostics but
does not use them to select a calibrator or forecasting method. No probability
recalibration was fitted. Original saved model outputs remain unchanged.

For each fixed bin, the evaluation reports its customer count, mean predicted
probability, and observed purchase rate. ECE is the count-weighted absolute
difference between those two bin means; MCE is the largest absolute difference
among populated bins. Both depend on bin edges and are diagnostics, not
universal reliability scores. The overall signed calibration gap is
`mean(predicted probability) - observed purchase rate`.

### Fixed-cutoff TEST purchase results

All values below use the frozen bins and all 3,373 TEST customers.

| Horizon | Mean predicted | Observed rate | Signed gap | Brier | Log loss | ROC-AUC | AP | ECE | MCE |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 30 days | 0.3315 | 0.2793 | +0.0522 | 0.1785 | 0.5403 | 0.7209 | 0.5376 | 0.0606 | 0.1689 |
| 60 days | 0.4779 | 0.4714 | +0.0065 | 0.2142 | 0.6226 | 0.7218 | 0.7163 | 0.0623 | 0.1290 |
| 90 days | 0.5654 | 0.5734 | -0.0080 | 0.2153 | 0.6282 | 0.7194 | 0.7847 | 0.0689 | 0.2545 |

Notebook 09 also reruns the existing purchase evaluation on the saved
predictions and asserts agreement with Notebook 06's reported values to the
source precision. It does not rewrite the official Notebook 06 or Notebook 07
results.

## Group evidence and bootstrap uncertainty

Required prospective groups use only information available at the prediction
cutoff: exact purchase-history count bands, forecast-time historical segment,
TRAIN-defined recency band, validation-defined predicted-probability band, and
calibration bin. Each group is shown with support count and its own point
metrics. Groups with fewer than 100 TEST customers are marked
`insufficient_evaluation_support`; that label does not mean the group is
unreliable. ROC-AUC/AP are null when their outcome-class requirements are not
met.

The 95% percentile intervals use 500 fixed-seed customer-level bootstrap
resamples. The fixed-model predictions and outcomes are resampled together by
customer; neither hazard rows nor repeated observations are treated as
independent. Intervals describe empirical group-metric uncertainty, not
parameter uncertainty, the chance that one customer will purchase, or an
individual guarantee.

At 30 days, all three required history groups meet the 100-customer minimum:

| Historical purchases | n | Predicted | Observed | Brier | AP | Signed calibration gap |
|---|---:|---:|---:|---:|---:|---:|
| Exactly one | 1,281 | 0.1551 | 0.1374 | 0.1192 | 0.1812 | +0.0177 |
| Two to four | 1,366 | 0.3328 | 0.2709 | 0.1997 | 0.3532 | +0.0619 |
| Five or more | 726 | 0.6403 | 0.5455 | 0.2433 | 0.7129 | +0.0948 |

The 95% bootstrap Brier intervals for these groups are respectively
`[0.1056, 0.1323]`, `[0.1907, 0.2093]`, and `[0.2297, 0.2587]`. The interval
method and successful resample count are stored per group and horizon.

The two saved forecast-time segments are `Lapsed / At-Risk` (2,088 customers)
and `Recent / Active` (1,285) at 30 days. Their Brier scores are 0.1434 and
0.2356; their signed calibration gaps are +0.0266 and +0.0939. These are
historical subgroup diagnostics, not prospective segment guarantees.

## Revenue forecast reliability

The following table uses the original Notebook 07 TEST definition and all
3,373 customers. Portfolio bias is predicted total minus actual total; it is
not a per-customer guarantee.

| Horizon | Model | MAE | RMSE | Mean bias | Predicted total | Actual total |
|---:|---|---:|---:|---:|---:|---:|
| 30 | Historical spending-rate | 296.35 | 945.39 | 34.91 | 858,475.87 | 740,721.59 |
| 30 | Segment-aware two-stage | 284.04 | 1,012.54 | 3.56 | 752,723.56 | 740,721.59 |
| 30 | Personalized two-stage | 243.18 | 871.30 | -29.96 | 639,659.40 | 740,721.59 |
| 60 | Historical spending-rate | 496.24 | 1,707.90 | 57.75 | 1,763,483.07 | 1,568,678.51 |
| 60 | Segment-aware two-stage | 496.67 | 1,870.18 | -32.69 | 1,458,412.19 | 1,568,678.51 |
| 60 | Personalized two-stage | 383.78 | 1,466.12 | -92.37 | 1,257,116.38 | 1,568,678.51 |
| 90 | Historical spending-rate | 752.39 | 2,487.43 | 132.53 | 2,942,543.56 | 2,495,526.20 |
| 90 | Segment-aware two-stage | 836.26 | 2,881.40 | 97.26 | 2,823,576.74 | 2,495,526.20 |
| 90 | Personalized two-stage | 547.38 | 2,111.73 | -187.86 | 1,861,869.51 | 2,495,526.20 |

Group forecast-bias intervals are separately estimated for each of the three
revenue models, horizon, and history group. A 99th-percentile actual TEST
revenue sensitivity is reported as explicitly retrospective only; those
outcomes do not select the forecast or reliability thresholds. No MAPE is
reported because zero-revenue customers make it undefined.

Large spenders can dominate portfolio error because aggregate revenue and
RMSE depend on the scale of a customer's actual and predicted amount. The
distribution of those errors and the 99th-percentile sensitivity are shown in
the executed notebook rather than hidden by a percentage-error average.

## Uncertainty language

- **Aleatoric uncertainty:** a future customer purchase remains uncertain even
  if the estimated probability is correct.
- **Epistemic/model uncertainty:** parameters and fitted transformations were
  estimated from finite historical training data. The fixed-model bootstrap
  does not quantify this.
- **Empirical calibration uncertainty:** observed group frequencies and error
  metrics vary because evaluation groups contain finite numbers of customers;
  the reported bootstrap intervals address this limited scope.

The UI never converts these concepts into an arbitrary 0–100 reliability score
or a claim such as “95% confident this customer will return.” Sparse-history
and out-of-range labels describe evidence support only.

## API and frontend

The existing FastAPI app exposes:

- `GET /api/reliability/summary`
- `GET /api/reliability/calibration`
- `GET /api/reliability/subgroups?horizon_days=30|60|90`
- `GET /api/reliability/revenue`
- `GET /api/customers/{customer_id}/explanation?horizon_days=30|60|90`
- `GET /api/customers/{customer_id}/reliability?horizon_days=30|60|90`

Aggregate endpoints are explicitly historical TEST evaluation. Customer
explanation and reliability endpoints return saved forecast inputs, TRAIN-only
references, and group-level evidence; they do not return that customer's TEST
outcome. Model bundles and immutable aggregate artifacts use the existing
application cache and load once per API worker.

The Customer Intelligence page loads the explanation and subgroup context only
after the customer is selected and the user opens those sections. Model
Performance adds overall, calibration/reliability, subgroup, revenue-error, and
methodology tabs. Existing pages and behavior monitoring remain in place.

## Artifacts and reproducibility

Versioned outputs:

- `models/prediction_reliability/metadata.json`
- `models/prediction_reliability/reference_profile.json`
- `data/metrics/prediction_reliability_evaluation.json`
- `data/metrics/prediction_reliability_profiling.json`

Rebuild the research results and execute all Notebook 09 analysis cells with the
locked Python 3.11 dependency set:

```bash
uv run --no-project --python 3.11 --with-requirements requirements-ci.txt \
  --with jupyter --with ipykernel python -m jupyter execute --inplace \
  notebooks/09_Prediction_Reliability_and_Explainability.ipynb
```

Run Python tests and the frontend checks from the repository root:

```bash
uv run --no-project --python 3.11 --with-requirements requirements-ci.txt \
  python -m pytest -q tests
pnpm run typecheck
pnpm test
pnpm run build
```

The generated profiling file records Python, pandas, NumPy, model versions,
sample sizes, batch sizes, and measured durations. Warm endpoint timings are
recorded separately after the API integration has loaded its cached models and
artifacts. In-process API medians ranged from 17.5 ms (summary) to 83.4 ms
(customer explanation) over five warm requests; all six endpoints returned
HTTP 200 in each request. These timings are local TestClient measurements, not
deployed-network latency. Suggested latency values are engineering targets, not
results.
