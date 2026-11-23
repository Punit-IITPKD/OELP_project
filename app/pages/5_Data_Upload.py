from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components.ui import gbp, render_page_intro
from app.config import MAX_UPLOAD_BYTES
from app.services.upload_service import (
    build_order_frequency_distribution,
    build_revenue_trend,
    inspect_upload,
    map_transaction_columns,
    parse_uploaded_file,
    validate_source_headers,
)
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
st.write(", ".join(TRANSACTION_COLUMNS))
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

try:
    validate_source_headers(raw_frame)
except ValueError as error:
    st.error(str(error))
    st.stop()

st.subheader("Uploaded file")
st.caption(f"{len(raw_frame):,} rows · {len(raw_frame.columns):,} columns")
with st.expander("Preview source rows"):
    st.dataframe(raw_frame.head(20), hide_index=True, width="stretch")

st.subheader("Map upload columns")
st.caption(
    "Choose the source header for each required transaction field. "
    "Extra source columns are ignored, and each source header can be used only once."
)
source_headers = list(raw_frame.columns)
source_options = [None, *source_headers]
mapping_columns = st.columns(2)
column_mapping = {}
for index, required_column in enumerate(TRANSACTION_COLUMNS):
    default_index = (
        source_headers.index(required_column) + 1
        if required_column in source_headers
        else 0
    )
    with mapping_columns[index % 2]:
        column_mapping[required_column] = st.selectbox(
            required_column,
            source_options,
            index=default_index,
            key=f"upload_column_mapping_{index}",
            format_func=lambda header: (
                "Choose a source header" if header is None else str(header)
            ),
        )

try:
    mapped_frame = map_transaction_columns(raw_frame, column_mapping)
except ValueError as error:
    st.error(f"Column mapping needs attention: {error}")
    st.stop()

st.dataframe(
    pd.DataFrame(
        {
            "Required transaction field": TRANSACTION_COLUMNS,
            "Mapped source header": [
                str(column_mapping[field]) for field in TRANSACTION_COLUMNS
            ],
        }
    ),
    hide_index=True,
    width="stretch",
)

st.subheader("Missing values before cleaning")
st.dataframe(
    mapped_frame.isna().sum().rename("Missing values").to_frame(),
    width="stretch",
)

try:
    result = inspect_upload(mapped_frame)
except (ValueError, TypeError, KeyError) as error:
    st.error(f"Validation stopped: {error}")
    st.stop()

summary = result["summary"]
metrics = st.columns(4)
metrics[0].metric("Input rows", f"{summary['input_rows']:,}")
metrics[1].metric("Cleaned rows", f"{summary['cleaned_rows']:,}")
metrics[2].metric("Rows excluded", f"{summary['excluded_rows']:,}")
metrics[3].metric("Customers", f"{summary['customer_count']:,}")

order_metrics = st.columns(4)
order_metrics[0].metric("Purchase orders", f"{summary['order_count']:,}")
order_metrics[1].metric(
    "Positive-order gross revenue",
    gbp(summary["positive_gross_revenue"], decimals=2),
)
order_metrics[2].metric(
    "Cancellation rows retained", f"{summary['cancellation_rows']:,}"
)
order_metrics[3].metric("Exact duplicates found", f"{summary['duplicate_rows']:,}")
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
orders = result["orders"]
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

st.subheader("Purchase activity in this upload")
left, right = st.columns(2)
with left:
    st.markdown("**Gross purchase revenue over time**")
    trend, period_label, trend_message = build_revenue_trend(orders)
    if trend_message:
        st.info(trend_message)
    else:
        fig = px.bar(
            trend,
            x="Period",
            y="GrossRevenue",
            labels={
                "Period": period_label,
                "GrossRevenue": "Gross purchase revenue (£)",
            },
            color_discrete_sequence=["#2563EB"],
        )
        fig.update_layout(
            title=f"{period_label} gross purchase revenue",
            height=320,
            margin=dict(l=10, r=10, t=55, b=10),
        )
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "Includes only positive-revenue purchase invoices; cancellation invoices "
            "are excluded. Period totals use invoice-level orders."
        )
with right:
    st.markdown("**Customer purchase frequency**")
    frequency = build_order_frequency_distribution(orders)
    fig = px.bar(
        frequency,
        x="Purchase frequency",
        y="Customers",
        labels={
            "Purchase frequency": "Purchase orders per customer",
            "Customers": "Customers",
        },
        color_discrete_sequence=["#0F766E"],
    )
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Each purchase is one valid invoice, not one transaction line. "
        "The final group combines customers with four or more orders."
    )

st.markdown("**Customer RFM distributions**")
st.caption(
    "These descriptive features use the uploaded purchase history only. "
    "Gross spend and average order value charts use a log x-axis and include "
    "positive values only."
)
rfm_charts = [
    ("Recency", "Recency", "Days since last purchase", False),
    ("Frequency", "Frequency", "Purchase orders per customer", False),
    ("Gross spend", "Monetary_Gross", "Gross spend per customer (£)", True),
    ("Average order value", "AOV", "Average gross order value (£)", True),
]
for row_start in (0, 2):
    left, right = st.columns(2)
    for column, (title, feature, axis_label, positive_only) in zip(
        (left, right), rfm_charts[row_start : row_start + 2]
    ):
        values = pd.to_numeric(features[feature], errors="coerce")
        values = values.loc[values.notna()]
        if positive_only:
            values = values.loc[values.gt(0)]
        if values.empty:
            column.info(f"No usable {title.lower()} values are available to chart.")
            continue
        fig = px.histogram(
            x=values,
            nbins=35,
            labels={"x": axis_label, "count": "Customers"},
            title=f"{title} distribution",
            log_x=positive_only,
            color_discrete_sequence=["#2563EB"],
        )
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=55, b=10))
        column.plotly_chart(fig, width="stretch")

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
