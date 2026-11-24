# Customer Retention Trajectory Analysis

Notebook 11 studies observed purchase and revenue trajectories before a fixed
historical cutoff. It is descriptive research on the Year 1 Online Retail data,
not a live retention system, churn classifier, or causal analysis.

## Reproduction

Run with the project's locked Python 3.11 analysis and test dependencies:

```bash
uv run --no-project --python 3.11 --with-requirements requirements-ci.txt \
  --with jupyter --with ipykernel python -m jupyter execute --inplace \
  notebooks/11_Customer_Retention_Trajectory_Analysis.ipynb
```

The notebook reads the canonical `data/processed/temporal/orders.csv` events and
the existing Notebook 06/07/08/09/10 artifacts. It writes its evaluation and
profiling summaries to `data/metrics/trajectory_analysis_*.json` and eligible,
frozen TRAIN-fitted representations to `models/trajectory_analysis/`. It does not
rewrite Purchase Clock or spending-model files.

## Trajectory definition and support

The primary representation is six consecutive 30-day calendar windows covering
180 days before the cutoff. Rates use observed exposure days. Before a customer's
first observed transaction, windows remain unobserved rather than being filled
with zero purchases. Partial first windows are exposure-adjusted. Transactions at
the cutoff and later are excluded. Customer history is left-truncated because
the source does not contain acquisition dates.

The official forecast TEST cutoff is September 10, 2010. There are 3,373
customers in that historical cohort and 1,281 have only one purchase. At the
30-day TRAIN cutoff (June 1), 2,703 customers are available: 1,130 meet summary
trajectory support and 480 meet the stricter six-window functional-analysis
support. At the validation cutoff (August 1), those counts are 1,291 and 590. At
the TEST cutoff they are 1,306 and 659. These support groups overlap by design:
functional eligibility is a stricter history requirement, and counts in the
summary history categories are mutually exclusive.

Shape-cluster eligibility is a separate population: all six windows must be
observed, at least two windows must contain purchases, and at least one
interpurchase gap must be completed before the cutoff. Eligibility is not the
same as assignment: an assignment is returned only when a supported frozen
cluster model exists.

Longer prediction horizons have less usable training history. At the 60-day
TRAIN cutoff (May 1), 867 customers meet summary support and 56 meet functional
support. At the 90-day TRAIN cutoff (March 1), all 1,712 available customers
have fewer than the four observed windows required for summary features. The
90-day trajectory training path is therefore not supported by this dataset's
observation period.

## Clustering and static-segment comparison

Candidate clustering is limited to two through six groups. Imputation,
standardization, and cluster centers are fitted on TRAIN; candidate choice uses
VAL silhouette plus repeated seed and resampling stability on TRAIN. A cluster
solution is not promoted as a reusable customer segmentation unless every
cluster contains at least 5% of eligible TRAIN and VAL customers. This avoids
promoting a stable but very small rare-outlier partition as a generally supported
behavior group.

The summary-feature representation's highest-VAL-silhouette candidate was two
clusters (VAL silhouette 0.801; TRAIN seed ARI 1.000; mean resampling ARI
0.973), but its smallest group represented only 1.95% of eligible TRAIN and
1.01% of eligible VAL customers. No summary-feature cluster model was promoted.

A separate shape-based model standardizes each customer's eligible six-window
purchase-rate curve by that customer's own mean and standard deviation before
TRAIN-fitted imputation, scaling, and K-means. Shape eligibility requires all
six windows observed, at least two purchase-active windows, and a completed
pre-cutoff interpurchase gap. This distinguishes repeated purchasing patterns
from nearly inactive or one-time customers and from overall purchase level.
The notebook rebuilds every candidate on TRAIN-only eligible customers and
selects only if stability, validation silhouette, and minimum group support
pass. Shape eligibility is 679 TRAIN, 980 VAL, and 1,100 TEST customers; the
TEST cohort contains 3,373 customers in total. Three clusters were selected
from candidates meeting the prespecified mean stability thresholds (seed ARI
≥0.75, resampling ARI ≥0.60) and 5% minimum TRAIN/VAL group-share rules. The
selected candidate's VAL silhouette is 0.1423, mean TRAIN seed ARI 0.7983
(minimum 0.3974), and mean TRAIN resampling ARI 0.7980 (minimum 0.3394). Its
smallest TRAIN and VAL shares are 27.7% and 27.3%. Six clusters also passed
those mean and support thresholds, but its VAL silhouette was lower (0.1383),
so the notebook selected three rather than forcing the previous six-cluster
choice. All 1,100 TEST-eligible customers receive an assignment; the cluster
sizes are 316, 321, and 463. Unsupported customers remain unassigned. These
are arbitrary shape groups, not risk categories or evidence of causal
differences.

The rejected summary candidate and supported shape solution are compared with
historical static labels only for their assigned TEST customers. For the shape
solution, normalized mutual information is 0.0172 and adjusted Rand index is
-0.0086, indicating little agreement with those static labels. These are
descriptive concordance statistics, not validation of predictive value. No
future TEST outcomes were used to choose cluster counts.

## Functional curve representation

The notebook reports a clearly labeled grid-based PCA approximation rather than
claiming a specialized functional-data estimator. Smoothing and component count
are selected on VAL reconstruction error; the PCA transformation itself is fit
on TRAIN only. PCA explained-variance ratios are therefore labeled TRAIN
explained variance, not TEST variance capture. Held-out TEST is evaluated
separately with reconstruction RMSE on its observed log-rate grid. Across 50
subsamples of 80% of TRAIN curves, aligned component-direction cosine means are
reported as a TRAIN stability analysis. Correlations with static and Notebook 08
features are reported with within-component Benjamini–Hochberg adjustment.
The selected moving-average representation has three components, explaining
98.82% of TRAIN variance; its held-out TEST reconstruction RMSE is 0.00625.
Aligned component-direction cosine means across TRAIN resamples are 0.9997,
0.9980, and 0.9980. Component scores describe associations in recorded curves;
they are not causal mechanisms or forecasts.

## Runtime and memory measurements

The locked run used Python 3.11.17, NumPy 2.4.6, pandas 3.1.1, and
scikit-learn 1.9.1 on a four-CPU Linux environment. Notebook execution took
234 seconds; peak traced Python memory was 270 MB and process high-water RSS was
638 MB. The first cold summary API request took 12.64 seconds because it loads
the historical cohort and frozen representations. With the worker cache warm,
the summary median/p95 was 11.6/13.4 ms, customer detail 19.4/26.0 ms, cluster
profiles 35.3/53.2 ms, and customer pagination 14.9/19.0 ms (10 measured
requests per route). All supplied warm engineering targets are met; the cold
first-request delay remains the main runtime caveat.

## Standalone predictive comparison

For the 30-day historical outcome, five models were compared on the same 1,306
TEST customers: a recency baseline, static RFM features, Notebook 08 behavior
indicators, trajectory summaries, and the saved Purchase Clock. Candidate
selection and supervised fitting used earlier TRAIN/VAL data. The trajectory
model's TEST ROC AUC was 0.672 and Brier score was 0.227; static RFM scored 0.664
and 0.226, and the saved Purchase Clock scored 0.678 and 0.231. The paired
trajectory-minus-RFM Brier difference was 0.00086 (95% bootstrap interval
[-0.00589, 0.00725]); the difference versus Purchase Clock was -0.00397
([-0.01219, 0.00405]). Both intervals include zero. This is a standalone
comparison, not evidence that trajectories add conditional value beyond the
Purchase Clock.

A separate analysis also evaluates functional-component predictors against
recency, RFM, Notebook 08, trajectory-summary, and Purchase Clock baselines on
the exact same functionally supported TEST customers. Its cohort size, metrics,
and paired bootstrap Brier intervals are recorded separately; it is not directly
compared with the larger summary-eligible cohort. For the 659 functional
customers, component scores scored AUC 0.647/Brier 0.231, compared with
0.643/0.230 for static RFM and 0.657/0.235 for Purchase Clock. Paired
component-versus-RFM and component-versus-Purchase-Clock Brier intervals both
include zero; this cohort does not establish incremental predictive value.

The saved Purchase Clock's training/validation vintage is not available at the
official trajectory TRAIN cutoffs. The combined frozen Purchase Clock plus
trajectory model is therefore explicitly marked
`not_fitted_due_to_vintage_unavailability`. Existing saved purchase and
spending predictions and artifacts are unchanged.

No finite-horizon nonpurchase is labeled permanent churn. No causal retention
effect, individual guarantee, or unsupported cluster association is reported.
For 30-, 60-, and 90-day outcomes, feature-level association estimates include
bootstrap intervals and Benjamini–Hochberg adjustment. See the JSON evaluation
file for full candidate tables, silhouette / Davies–Bouldin / Calinski–Harabasz
scores, stability checks, calibration metrics, paired intervals, support
counts, component relationships, and method-specific limitations.

## Fit within the wider project

Notebook 11 extends the project's earlier interpurchase (03), static
segmentation (04), and temporal-validation (05) analyses. It compares its
longitudinal representation with the existing Purchase Clock (06), spending
forecast (07), Notebook 08 behavioral-change indicators, Notebook 09 prediction
reliability, and Notebook 10 revenue-at-risk planning. These earlier models,
research metrics, and statistical conclusions are not recalculated or altered.
The main unresolved data need is longer, less left-truncated customer history
with confirmed acquisition dates, followed by validation across multiple future
cohorts and independently logged retention interventions.

## API and dashboard

The React app adds a **Trajectory explorer** at `/trajectories`, linked from
Customer Intelligence. It labels summary-trajectory eligibility,
shape-cluster eligibility, actual cluster assignments, and FDA eligibility as
separate counts and per-customer fields. It also shows the saved cutoff, method
availability, historical customer search and filters, pagination, visible-page
CSV export, observed rate curves, support details, saved cluster profiles,
functional mean/components and customer score positions, and same-cohort
prediction summaries. TRAIN explained variance is labeled separately from TEST
reconstruction RMSE. Group-level future-purchase and feature-level associations
at 30/60/90 days include bootstrap intervals and adjusted q-values.

FastAPI exposes:

- `GET /api/trajectories/summary`
- `GET /api/trajectories/clusters`
- `GET /api/trajectories/customers`
- `GET /api/trajectories/evaluation`
- `GET /api/customers/{customer_id}/trajectory`
- `GET /api/customers/{customer_id}/trajectory/explanation`

The service loads saved outputs only; it does not fit models while serving
requests. Filtering, history eligibility, and all reported curves stop at the
September 10, 2010 cutoff.
