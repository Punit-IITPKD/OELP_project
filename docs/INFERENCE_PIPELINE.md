# Customer intelligence inference API

This package exposes the validated Year 1 research pipeline as Python functions.
Normal inference does not run notebooks, train models, tune parameters, or read
future outcomes.

## Executable example

Run from the repository root after installing `requirements.txt`:

```python
import pandas as pd

from src.customer_intelligence import CustomerIntelligence

transactions = pd.read_csv(
    "data/processed/online_retail_cleaned_data.csv",
    parse_dates=["InvoiceDate"],
)
intelligence = CustomerIntelligence.from_artifacts()

# The September 10, 2010 TEST cutoff supports all three saved horizons.
predictions = intelligence.predict_customers(
    transactions,
    cutoff_date="2010-09-10",
    customer_ids=[12346, 12349],
)
print(predictions.to_string(index=False))
```

For a single customer, pass one ID; for a batch, pass an iterable or omit
`customer_ids` to predict for every customer with eligible pre-cutoff history.
The result is one row per customer and cutoff. A customer with no valid
pre-cutoff order is rejected when explicitly requested and otherwise omitted.

## Input and cleaning contract

Input is a pandas DataFrame with these transaction columns:

| Column | Meaning / expected values |
| --- | --- |
| `Invoice` | Invoice identifier; `C`-prefixed invoices represent cancellations |
| `StockCode` | Product code |
| `Description` | Product description; missing descriptions are retained |
| `Quantity` | Whole-number quantity |
| `InvoiceDate` | Parseable transaction timestamp |
| `Price` | Finite unit price |
| `Customer ID` | Numeric whole-number customer identifier |
| `Country` | Country label |

`src.data_preparation.clean_transactions()` removes full-row duplicates and
rows without a customer ID. It retains customer-linked cancellations,
zero-price rows, and extreme values. It does not impute customer IDs or apply
arbitrary quantity/price thresholds. `return_report=True` returns the cleaning
counts and decisions with the frame.

`src.customer_features.build_customer_features()` reproduces Notebook 02's
15-column customer feature table, including gross/net spending, AOV,
cancellation counts/rate, median inter-purchase days, and the existing
Yeo-Johnson/log1p transformations. Single-purchase customers keep a missing
inter-purchase value.

`src.interpurchase` exposes invoice-level gap rows, per-customer gap summaries,
and the four Notebook 03 maximum-likelihood fits (Exponential, Weibull, Gamma,
and Log-Normal). Zero-day gaps are retained in the descriptive gap table but
excluded from distribution fits. KS statistics are directional only; fitted
parameter KS p-values are not reported.

`src.statistical_analysis` also exposes the Notebook 05 numerical summaries,
effect sizes, seeded bootstrap confidence intervals, training-period gap
percentiles, two-group survival/log-rank calculations, and retrospective
segment/threshold validation. Outcome-validation functions require future
labels by design and are for evaluation only; they are not used by the
customer-inference service.

`src.segmentation.fit_descriptive_segmentation()` reproduces Notebook 04's
full-period log1p RFM → `StandardScaler` → K-Means descriptive segmentation.
It excludes AOV, inter-purchase gaps, cancellation rate, and the at-risk flag
from clustering. This full-period descriptive segmentation is **not** used for
prediction. Prediction uses the saved TRAIN-only transformations through
`src.temporal_framework`.

## Inference API and output

Application-facing entry points:

```python
from src.customer_intelligence import CustomerIntelligence, predict_customers

service = CustomerIntelligence.from_artifacts()
predictions = service.predict_customers(
    transactions,
    cutoff_date="2010-08-01",
    horizons=[30],
)
```

`CustomerIntelligence.from_artifacts(project_root=None)` loads the saved model
bundles and derives the Year 1 date limits from
`data/processed/temporal/orders.csv`. `CustomerIntelligence.predict_customers`
accepts a transaction DataFrame, one historical cutoff, an optional customer
ID or list, and optional forecast horizons. The module-level
`predict_customers(...)` helper performs the same operation while loading the
artifacts for that call.

The output contains `Customer ID`, `cutoff_date`, and for each requested
horizon:

- `prediction_protocol_{H}d`: prospective validation, retrospective
  exploratory validation, or historical out-of-time TEST status.
- `global_purchase_probability_{H}d`,
  `segment_purchase_probability_{H}d`, and
  `purchase_probability_{H}d` (the personalized probability).
- `historical_rate_expected_revenue_{H}d`,
  `segment_conditional_revenue_{H}d`,
  `segment_expected_revenue_{H}d`,
  `personalized_conditional_revenue_{H}d`, and
  `personalized_expected_revenue_{H}d`.

Expected revenue for the two-stage methods is purchase probability multiplied
by the corresponding conditional revenue forecast. No future dates, targets,
or evaluation labels are returned.

## Saved artifacts and eligible cutoffs

The API loads the existing files without changing or retraining them:

- `models/purchase_clock/purchase_clock.joblib` and its metadata.
- `models/purchase_clock/validation_vintage/purchase_clock.joblib` and its metadata.
- `models/spending_model/spending_models.joblib`, metadata, and feature schema.
- `data/processed/temporal/orders.csv` for Year 1 date boundaries.

Each purchase-clock model and each spending horizon has its own saved
TRAIN-fitted segmentation transform. The API verifies that transform schema
and segment labels are compatible and never reuses one horizon's labels for
another horizon's spending model.

Only the historical Notebook 07 cutoffs are accepted:

| Cutoff | Supported forecast | Status |
| --- | --- | --- |
| `2010-06-01` | 90 days | Retrospective / exploratory |
| `2010-07-01` | 60 days | Prospective validation vintage |
| `2010-08-01` | 30 days | Prospective validation vintage |
| `2010-09-10` | 30, 60, and 90 days | Historical out-of-time TEST |

Future transaction rows supplied in the same Year 1 extract are discarded
before feature construction. A transaction on the cutoff is excluded; features
use only records strictly earlier than the cutoff. Forecast horizons must be
fully observable by the Year 1 data end.

## Restrictions

- These are historical forecasts for UCI Online Retail II Year 1
  (December 2009–December 2010), not real-time forecasts.
- A future return within a horizon is an observed purchase event, not proof of
  permanent retention. No return within a horizon is not a permanent churn
  label.
- `2010-06-01` 90-day joint validation is explicitly retrospective because
  the selected purchase model's validation outcomes were not mature at that
  cutoff. It is marked as such in the output.
- The input must represent the complete Year 1 customer transaction history
  available to the chosen cutoff. The API does not predict customers without
  at least one valid prior order.
- Do not add Year 2 data, interpret the descriptive at-risk flag as churn, use
  future outcomes as inputs, or fit/retrain models during inference.
- `data/processed/purchase_clock` and `data/processed/spending_forecast` are
  notebook-generated evaluation exports, not inference inputs.

## Tests

From the repository root:

```bash
python -m pytest -q tests
```

The tests cover cleaning decisions, Notebook 02 feature parity, Notebook 03
inter-purchase statistics, Notebook 04 cluster labels/profiles, Notebook 05
statistical results, prediction cutoffs, segmentation compatibility, model
loading, batch/single-customer inference, future-row exclusion, and regression
comparisons to the saved Notebook 06/07 TEST results. The CI workflow runs this
same test suite.
