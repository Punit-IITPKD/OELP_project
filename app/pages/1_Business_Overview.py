from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.components.ui import gbp, render_historical_notice, render_page_intro
from app.services.demo_service import (
    ALL_ELIGIBLE_CUSTOMERS,
    summarize_forecast_cohort,
)
from app.services.demo_service import (
    load_descriptive_tables,
    load_forecast_snapshot,
    load_order_history,
)

render_page_intro(
    "Business Overview",
    "Year 1 retail performance and a separate, validated historical forecast snapshot.",
)

features, segments = load_descriptive_tables()
orders = load_order_history().copy()
orders["Month"] = orders["PurchaseDate"].dt.to_period("M").dt.to_timestamp()

min_date = orders["PurchaseDate"].min().date()
max_date = orders["PurchaseDate"].max().date()
period = st.date_input(
    "Historical sales period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    help="This filter changes historical sales figures only; it does not change the forecast cutoff.",
)
if isinstance(period, (tuple, list)) and len(period) == 2:
    start_date, end_date = period
else:
    start_date = end_date = period

historical_orders = orders.loc[
    orders["PurchaseDate"].between(
        pd.Timestamp(start_date),
        pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1),
    )
]
order_count = int(len(historical_orders))
customer_count = int(historical_orders["Customer ID"].nunique())
revenue = float(historical_orders["GrossRevenue"].sum())
average_order_value = revenue / order_count if order_count else 0.0

metric_columns = st.columns(4)
metric_columns[0].metric("Gross sales", gbp(revenue))
metric_columns[1].metric("Purchase orders", f"{order_count:,}")
metric_columns[2].metric("Customers purchasing", f"{customer_count:,}")
metric_columns[3].metric("Average order value", gbp(average_order_value))
st.caption(
    f"Historical period: {start_date:%d %b %Y}–{end_date:%d %b %Y}. "
    "Customers are counted once within the selected period."
)

monthly = (
    historical_orders.groupby("Month", as_index=False)
    .agg(GrossRevenue=("GrossRevenue", "sum"), Orders=("Invoice", "nunique"))
    .sort_values("Month")
)
left, right = st.columns(2)
with left:
    st.subheader("Monthly gross sales")
    fig = px.line(
        monthly,
        x="Month",
        y="GrossRevenue",
        markers=True,
        labels={"GrossRevenue": "Gross sales (£)", "Month": "Month"},
        color_discrete_sequence=["#2563EB"],
    )
    fig.update_layout(height=330, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, width="stretch")
with right:
    st.subheader("Monthly purchase orders")
    fig = px.bar(
        monthly,
        x="Month",
        y="Orders",
        labels={"Orders": "Orders", "Month": "Month"},
        color_discrete_sequence=["#0F766E"],
    )
    fig.update_layout(height=330, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, width="stretch")

st.divider()
st.subheader("Customer segment mix")
segment_mix = (
    segments.groupby("Segment_Name", as_index=False)
    .agg(Customers=("Customer ID", "nunique"), GrossSpend=("Monetary_Gross", "sum"))
    .sort_values("Customers", ascending=False)
)
left, right = st.columns([1, 2])
with left:
    st.dataframe(
        segment_mix.assign(
            CustomerShare=segment_mix["Customers"] / segment_mix["Customers"].sum()
        ),
        hide_index=True,
        width="stretch",
        column_config={
            "GrossSpend": st.column_config.NumberColumn("Gross spend", format="£%.2f"),
            "CustomerShare": st.column_config.ProgressColumn(
                "Customer share", format="%.1%%", min_value=0, max_value=1
            ),
        },
    )
with right:
    fig = px.bar(
        segment_mix,
        x="Segment_Name",
        y="Customers",
        color="Segment_Name",
        labels={"Segment_Name": "Full-year descriptive segment"},
        color_discrete_sequence=["#2563EB", "#0F766E"],
    )
    fig.update_layout(
        height=330,
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis_title=None,
    )
    st.plotly_chart(fig, width="stretch")

st.divider()
st.subheader("Validated forecast snapshot · 10 Sep 2010")
render_historical_notice(
    "Forecasts use only purchases before September 10, 2010. "
    "These saved-model outputs are separate from the full-year historical charts above."
)
snapshot = load_forecast_snapshot()
forecast_segments = [ALL_ELIGIBLE_CUSTOMERS] + sorted(
    snapshot["Hist_Segment"].dropna().unique().tolist()
)
selected_segment = st.selectbox(
    "Forecast-time customer segment",
    forecast_segments,
)
forecast_summary = summarize_forecast_cohort(snapshot, selected_segment)
forecast = forecast_summary["cohort"]

if forecast.empty:
    st.warning("No eligible customers match this forecast-time segment.")
else:
    forecast_metrics = st.columns(4)
    forecast_metrics[0].metric(
        "Eligible customers",
        f"{forecast_summary['eligible_customer_count']:,}",
    )
    forecast_metrics[1].metric(
        "Expected returners · 30 days",
        f"{forecast_summary['expected_returners'][30]:,.0f}",
    )
    forecast_metrics[2].metric(
        "Expected returners · 60 days",
        f"{forecast_summary['expected_returners'][60]:,.0f}",
    )
    forecast_metrics[3].metric(
        "Expected returners · 90 days",
        f"{forecast_summary['expected_returners'][90]:,.0f}",
    )

    horizon_rows = []
    for horizon in (30, 60, 90):
        horizon_rows.append(
            {
                "Horizon": f"{horizon} days",
                "Expected returners": forecast_summary["expected_returners"][horizon],
                "Personalized expected revenue": forecast_summary[
                    "expected_revenue"
                ][horizon],
            }
        )
    horizon_data = pd.DataFrame(horizon_rows)
    left, right = st.columns(2)
    with left:
        fig = px.bar(
            horizon_data,
            x="Horizon",
            y="Expected returners",
            color_discrete_sequence=["#0F766E"],
            title="Expected customers with a return purchase",
        )
        fig.update_layout(height=310, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, width="stretch")
    with right:
        fig = go.Figure(
            go.Bar(
                x=horizon_data["Horizon"],
                y=horizon_data["Personalized expected revenue"],
                marker_color="#2563EB",
                hovertemplate="%{x}<br>£%{y:,.0f}<extra></extra>",
            )
        )
        fig.update_layout(
            title="Personalized expected revenue",
            yaxis_title="Expected revenue (£)",
            height=310,
            margin=dict(l=10, r=10, t=55, b=10),
        )
        st.plotly_chart(fig, width="stretch")

    st.caption(
        "Expected returners are the sum of customer-level purchase probabilities, "
        "not a count of certain purchases. Revenue is an estimate from the saved model."
    )

with st.expander("Dataset and cohort definitions"):
    st.write(
        f"- Historical sales table: {len(orders):,} valid order rows across "
        f"{orders['Customer ID'].nunique():,} customers.\n"
        f"- Full-year descriptive segmentation: {len(segments):,} customers.\n"
        f"- Forecast snapshot: {len(snapshot):,} eligible customers before "
        f"{snapshot['cutoff_date'].iloc[0].date()}.\n"
        "- Full-year descriptive features and pre-cutoff forecast features are "
        "kept separate; their customer counts can differ."
    )
