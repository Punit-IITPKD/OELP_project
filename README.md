# OELP Customer Intelligence

A six-page Streamlit MVP for exploring the Year 1 Online Retail dataset, saved
customer-segmentation outputs, and the existing purchase-clock and expected-revenue
models. It loads the saved artifacts; it does not train or tune models.

## Run the app

The Replit workflow runs:

```bash
uv run streamlit run app/main.py --server.port 5000 --server.address 0.0.0.0
```

Install dependencies and start the app:

```bash
python -m pip install -r requirements.txt
streamlit run app/main.py --server.port 5000
```

The configured Replit workflow launches the same app on port 5000.

## App pages

1. **Business Overview** — historical Year 1 sales and a separately labeled forecast
   summary.
2. **Customer Segmentation** — full-year descriptive RFM clusters and the model’s
   separate pre-cutoff segments.
3. **Customer Intelligence** — pre-cutoff order history, purchase probabilities,
   expected revenue, and a customer-level return curve.
4. **Purchase Forecasting** — cohort filters, probability curves, and expected-revenue
   comparisons.
5. **Data Upload & Validation** — CSV or `.xlsx` validation, cleaning diagnostics,
   descriptive customer features, and downloads.
6. **Model Performance** — TEST metrics from the saved outputs in Notebooks 06 and 07.

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

## Model-performance summary

The small, versioned metrics file and calibration figures under `data/metrics/` are
extracted from saved executed outputs in Notebooks 06 and 07. The exporter reads the
notebooks without executing or modifying them:

```bash
python scripts/export_notebook_evaluation.py
```

## Tests

Run the test suite:

```bash
python -m pytest -q tests
```

The tests cover the existing analytics and inference pipeline, upload validation,
the saved evaluation summary, and a Streamlit application smoke test.
