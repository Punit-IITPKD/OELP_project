# OELP Customer Intelligence

A ten-page React website backed by FastAPI for exploring the Year 1 Online Retail
dataset, saved customer-segmentation outputs, and existing purchase-clock and
expected-revenue models. It loads saved artifacts; it does not train or tune models.

## Run the app

The Replit Run button starts the FastAPI service and Vite website together:

```bash
pnpm dev
```

Install the frontend dependencies and start the app:

```bash
pnpm install
pnpm dev
```

The launcher starts FastAPI on the internal port 8000 and exposes only Vite on
port 5000. Vite forwards `/api` requests to FastAPI. Its API launcher explicitly
uses Python 3.11 and the hash-locked `requirements-ci.txt` environment that is
used for research and regression testing.

The earlier Streamlit interface remains available separately:

```bash
uv run --no-project --with-requirements requirements.txt \
  streamlit run app/main.py --server.port 5000 --server.address 0.0.0.0
```

## App pages

1. **Business Overview** — historical sales, monthly trends, customer segments, and
   a separately labeled saved-forecast summary.
2. **Segments** — descriptive RFM groups, historical forecast cohorts, and searchable
   customer records.
3. **Customer Intelligence** — a saved customer’s pre-cutoff order history,
   probabilities, expected revenue, and return curve.
4. **Forecasting** — historical cohort filters, probability curves, and model
   comparisons across the validated horizons.
5. **Upload Analysis** — CSV or `.xlsx` mapping, validation, descriptive analysis, and
   downloads. Uploads are not used for forecasts.
6. **Model Performance** — saved test metrics from Notebooks 06 and 07.
7. **Behavior Monitoring** — cutoff-safe historical purchase-gap, rate, revenue,
   and trajectory indicators, with the saved research evaluation.
8. **Revenue & Retention** — saved forecast disagreements, nullable reference-based
   exposure, ranking evidence, customer-level screening signals, and hypothetical
   contact-budget scenarios.
9. **Trajectory Explorer** — exposure-adjusted historical purchase and revenue
   curves, history support, frozen functional scores, and method-availability
   reporting.
10. **Research Overview** — a typed, read-only synthesis of all 11 notebooks,
    evidence statuses, saved evaluations, method-specific cohort coverage,
    reproducibility commands, and source checksums.

Customer Intelligence also provides on-demand saved-model explanations and
group-level reliability context. Model Performance includes calibration,
subgroup, expected-revenue, and methodology views. See
[Prediction Reliability and Explainability](docs/PREDICTION_RELIABILITY_AND_EXPLAINABILITY.md)
for the fixed-cutoff evaluation, TRAIN-only references, methods, results, and
reproduction commands.

The dashboard uses React route-level code splitting; chart-heavy pages load their
charting code only when opened. The landing page uses compact SVG charts and
does not download the Recharts rendering chunk.

## Phase 7 research consolidation

The final research summary is generated deterministically from the saved notebooks,
evaluation metrics, temporal metadata, and model metadata. It does not retrain
models or modify the original prediction outputs.

- [Final research evaluation](docs/FINAL_RESEARCH_EVALUATION.md)
- [System architecture](docs/FINAL_SYSTEM_ARCHITECTURE.md)
- [Reproducibility guide](docs/FINAL_REPRODUCIBILITY_GUIDE.md)
- [Demonstration guide](docs/FINAL_DEMONSTRATION_GUIDE.md)
- [Engineering validation](docs/FINAL_ENGINEERING_VALIDATION.md)

## Forecast scope and data handling

- The app’s initial inference snapshot is **September 10, 2010**, with validated
  30-, 60-, and 90-day horizons.
- Forecast features use only transactions strictly before the selected historical
  cutoff. The saved TEST outcomes appear only in the evaluation page and are not
  prediction inputs.
- Full-year descriptive metrics and segments are explicitly separate from the
  pre-cutoff forecast cohort.
- Uploaded files are limited to 25 MB and processed in memory for the active session.
  They are not saved to project files, passed to the forecasting models, or used to
  produce predictions. Upload mode is descriptive-only.
- The dashboard uses the existing Year 1 data and saved model artifacts under
  `data/processed/` and `models/`.
- Behavior indicators are historical observations at the September 10, 2010
  cutoff. They are not churn labels, live recommendations, or enabled alert
  categories.

## Behavioral change research

Notebook 08 uses the official matured temporal splits and selects its behavior-only
model on validation data before evaluating the locked September 10, 2010 TEST
cohort. It compares a behavior-only candidate with global inactivity, recency,
personalized delay ratio, and the saved Purchase Clock. The saved Purchase Clock
vintages are not available at the official TRAIN cutoffs, so a conditional
Purchase-Clock-plus-behavior Candidate F is not fitted; incremental value beyond
the Purchase Clock is therefore unresolved.

The generated configuration and evaluation are saved under
`models/behavior_monitor/` and `data/metrics/behavior_monitor_*.json`. To rerun the
study and refresh those artifacts:

```bash
jupyter execute --inplace notebooks/08_Behavioral_Change_Detection.ipynb
```

See [Behavior Monitoring](docs/BEHAVIOR_MONITORING.md) for feature definitions,
evaluation results, API routes, and limitations.

## Prediction reliability and explainability

Notebook 09 explains the saved Purchase Clock and spending models and evaluates
their historical calibration and subgroup performance without replacing the
original forecasts. Its versioned reliability artifacts are stored under
`models/prediction_reliability/` and `data/metrics/`. The study uses the fixed
September 10, 2010 TEST cutoff, TRAIN-only explanation references, and
validation-selected calibration bins. Customer explanations are model-input
sensitivities, not causal effects or individual confidence guarantees.

See [Prediction Reliability and Explainability](docs/PREDICTION_RELIABILITY_AND_EXPLAINABILITY.md)
for results and method details.

To run the analysis and refresh its artifacts:

```bash
uv run --no-project --python 3.11 --with-requirements requirements-ci.txt \
  jupyter execute --inplace notebooks/09_Prediction_Reliability_and_Explainability.ipynb
```

## Revenue exposure and retention planning

Notebook 10 keeps current expected revenue, disagreement between saved forecast
methods, reference-based exposure, and the nonreturn-spending screening proxy as
separate quantities. There is no defensible, matched reference forecast in the
saved data, so estimated exposure is explicitly not estimable. The planner uses
the existing saved models and does not modify them. Scenario benefits depend on
user-entered hypothetical response and uplift assumptions; causal retention
uplift is not estimated.

Thirty- and 60-day ranking rules are selected on the corresponding prospective
validation cutoffs and then evaluated on the locked September 10, 2010 TEST
cohort. The 90-day ranking comparison is exploratory because no eligible
prospective validation vintage is available. In the locked TEST, the
validation-selected policy did not outperform all matched high-spending
baselines. See [Revenue Exposure and Retention Planning](docs/REVENUE_EXPOSURE_AND_RETENTION_PLANNING.md)
for the definitions, results, API routes, and limits.

## Customer retention trajectories

Notebook 11 builds exposure-aware 30-day purchase and revenue histories at the
official temporal cutoffs, screens TRAIN-fitted clustering for stability and
minimum group support, and evaluates a TRAIN-fitted grid-based functional PCA
approximation. Summary-feature clusters fail the minimum-size rule because they
isolate a very small group. Shape clustering uses a distinct support rule:
all six windows observed, at least two purchase-active windows, and one
completed pre-cutoff interpurchase gap. A shape model is saved only if its
TRAIN stability and TRAIN/VAL size checks pass; unsupported customers remain
unassigned. Summary eligibility, shape eligibility, cluster assignments, and
functional-analysis eligibility are reported separately. PCA variance ratios
are labeled TRAIN explained variance, while TEST reconstruction error is
reported separately. Standalone TEST comparisons do not establish incremental
value beyond the saved Purchase Clock.

See [Customer Trajectory Analysis](docs/CUSTOMER_TRAJECTORY_ANALYSIS.md) for
support counts, evaluation results, limitations, API routes, and reproduction
instructions.

To execute the reproducible Notebook 11 analysis:

```bash
uv run --no-project --python 3.11 --with-requirements requirements-ci.txt \
  --with jupyter --with ipykernel python -m jupyter execute --inplace \
  notebooks/11_Customer_Retention_Trajectory_Analysis.ipynb
```

To rebuild the analysis, write its saved research artifacts, execute Notebook 10,
and measure the warmed API routes in the locked Python 3.11 environment:

```bash
uv run --no-project --python 3.11 --with-requirements requirements-ci.txt \
  python scripts/build_notebook10.py
uv run --no-project --python 3.11 --with-requirements requirements-ci.txt \
  --with jupyter --with ipykernel python -m jupyter execute --inplace \
  notebooks/10_Revenue_at_Risk_and_Retention_Planning.ipynb
```

## Model-performance summary

The small, versioned metrics file and calibration figures under `data/metrics/` are
extracted from saved executed outputs in Notebooks 06 and 07. The exporter reads the
notebooks without executing or modifying them:

```bash
python scripts/export_notebook_evaluation.py
```

## Tests

Run the frontend checks and Python test suite:

```bash
pnpm run typecheck
pnpm test
pnpm run build
python -m pytest -q tests
```

The tests cover the analytics and inference pipeline, API routes, upload mapping,
the saved evaluation summaries, behavior features, and frontend pages and behaviors.
