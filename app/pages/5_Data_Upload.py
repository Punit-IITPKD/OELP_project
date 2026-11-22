from __future__ import annotations

import streamlit as st

from app.components.ui import gbp, render_page_intro
from app.config import MAX_UPLOAD_BYTES
from app.services.upload_service import inspect_upload, parse_uploaded_file
from src.data_preparation import TRANSACTION_COLUMNS

render_page_intro(
    "Data Upload & Validation",
    "Upload transaction data for session-only cleaning and descriptive customer features.",
)
st.warning(
    "Uploads are not saved to project files or used for model predictions. "
    "This page provides descriptive summaries only."
)

st.markdown("**Required transaction columns**")
st.code(", ".join(TRANSACTION_COLUMNS), language="text")
uploaded = st.file_uploader(
    "Choose a CSV or Excel workbook",
    type=["csv", "xlsx"],
    max_upload_size=MAX_UPLOAD_BYTES // (1024 * 1024),
    help="Maximum 25 MB. Data remains in this browser session and is not written to disk.",
)

if uploaded is None:
    st.info("Select a CSV or .xlsx file to validate it.")
    st.stop()

if uploaded.size > MAX_UPLOAD_BYTES:
    st.error("The selected file is larger than the 25 MB limit.")
    st.stop()

try:
    raw_frame = parse_uploaded_file(uploaded.name, uploaded.getvalue())
except (ValueError, OSError) as error:
    st.error(str(error))
    st.stop()

st.subheader("Uploaded file")
st.caption(f"{len(raw_frame):,} rows · {len(raw_frame.columns):,} columns")
with st.expander("Preview source rows"):
    st.dataframe(raw_frame.head(20), hide_index=True, width="stretch")

st.subheader("Missing values before cleaning")
st.dataframe(
    raw_frame.isna().sum().rename("Missing values").to_frame(),
    width="stretch",
)

try:
    result = inspect_upload(raw_frame)
except (ValueError, TypeError, KeyError) as error:
    st.error(f"Validation stopped: {error}")
    missing_columns = [column for column in TRANSACTION_COLUMNS if column not in raw_frame]
    if missing_columns:
        st.write("Missing required fields:", ", ".join(missing_columns))
    st.stop()

summary = result["summary"]
metrics = st.columns(4)
metrics[0].metric("Input rows", f"{summary['input_rows']:,}")
metrics[1].metric("Cleaned rows", f"{summary['cleaned_rows']:,}")
metrics[2].metric("Rows excluded", f"{summary['excluded_rows']:,}")
metrics[3].metric("Customers", f"{summary['customer_count']:,}")

order_metrics = st.columns(3)
order_metrics[0].metric("Purchase orders", f"{summary['order_count']:,}")
order_metrics[1].metric("Cancellation rows retained", f"{summary['cancellation_rows']:,}")
order_metrics[2].metric("Exact duplicates found", f"{summary['duplicate_rows']:,}")
st.caption(
    "Cancellation and zero-price lines follow the existing project cleaning rules. "
    "Duplicate and missing-customer removals are reported below."
)

report = summary["cleaning_report"]
st.dataframe(
    [
        {
            "Validation rule": "Exact duplicate rows removed",
            "Rows": report.get("duplicate_rows_removed", 0),
        },
        {
            "Validation rule": "Rows without a customer ID removed",
            "Rows": report.get("missing_customer_rows_removed", 0),
        },
        {
            "Validation rule": "Cancellation rows retained",
            "Rows": report.get("retained_cancellation_rows", 0),
        },
        {
            "Validation rule": "Zero-price rows retained",
            "Rows": report.get("retained_zero_price_rows", 0),
        },
    ],
    hide_index=True,
    width="stretch",
)

features = result["customer_features"]
cleaned = result["cleaned_transactions"]
st.subheader("Descriptive customer summary")
feature_metrics = st.columns(3)
feature_metrics[0].metric("Customers with features", f"{len(features):,}")
feature_metrics[1].metric(
    "Median gross customer spend",
    gbp(features["Monetary_Gross"].median()),
)
feature_metrics[2].metric(
    "Feature reference date",
    summary["reference_date"].strftime("%d %b %Y"),
)
st.dataframe(features.head(50), hide_index=True, width="stretch")

left, right = st.columns(2)
left.download_button(
    "Download cleaned transactions",
    data=cleaned.to_csv(index=False).encode("utf-8"),
    file_name="cleaned_transactions.csv",
    mime="text/csv",
    width="stretch",
)
right.download_button(
    "Download descriptive customer features",
    data=features.to_csv(index=False).encode("utf-8"),
    file_name="customer_features.csv",
    mime="text/csv",
    width="stretch",
)
