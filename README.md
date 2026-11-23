# OELP Customer Intelligence

A six-page React website backed by FastAPI for exploring the Year 1 Online Retail
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
port 5000. Vite forwards `/api` requests to FastAPI. Python packages are resolved
from `requirements.txt` by `uv`.

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

Run the frontend checks and Python test suite:

```bash
pnpm run typecheck
pnpm test
pnpm run build
python -m pytest -q tests
```

The tests cover the analytics and inference pipeline, API routes, upload mapping,
the saved evaluation summary, and frontend pages and behaviors.
