from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components.ui import gbp, percent, render_historical_notice, render_page_intro, show_download_csv
from app.services.demo_service import load_forecast_snapshot, load_order_history

render_page_intro(
    "Customer Intelligence",
    "Review a customer’s pre-cutoff purchase history and saved-model forecasts.",
)
render_historical_notice()

snapshot = load_forecast_snapshot()
orders = load_order_history()
customer_ids = snapshot["Customer ID"].astype(int).tolist()
customer_id = st.selectbox(
    "Search eligible customer",
    customer_ids,
    format_func=lambda value: f"Customer {value:,}",
)
record = snapshot.loc[snapshot["Customer ID"].eq(customer_id)].iloc[0]
cutoff = pd.Timestamp(record["cutoff_date"])

st.subheader(f"Customer {customer_id:,}")
left, right = st.columns([1, 2])
with left:
    st.markdown("**Pre-cutoff profile**")
    profile = pd.DataFrame(
        [
            ("Forecast-time segment", record["Hist_Segment"]),
            ("Full-year descriptive segment", record["Descriptive_Segment"]),
            ("History sufficiency", record["history_group"]),
            (
                "First purchase",
                pd.Timestamp(record["FirstPurchaseDate"]).strftime("%d %b %Y"),
            ),
            (
                "Last purchase",
                pd.Timestamp(record["LastPurchaseDate"]).strftime("%d %b %Y"),
            ),
            ("Model recency", f"{record['Recency']:.0f} days"),
            ("Historical orders", f"{record['Frequency']:.0f}"),
            ("Gross spend before cutoff", gbp(record["Monetary_Gross"])),
        ],
        columns=["Profile field", "Value"],
    )
    st.dataframe(profile, hide_index=True, width="stretch")
with right:
    st.markdown("**Purchase-return probability**")
    fig = go.Figure()
    horizons = [30, 60, 90]
    for label, prefix in (
        ("Global", "global"),
        ("Segment-aware", "segment"),
        ("Personalized", "personalized"),
    ):
        fig.add_scatter(
            x=horizons,
            y=[record[f"{prefix}_P{horizon}"] for horizon in horizons],
            mode="lines+markers",
            name=label,
            hovertemplate="%{x} days<br>%{y:.1%}<extra>%{fullData.name}</extra>",
        )
    personalized_days = list(range(10, 91, 10))
    fig.add_scatter(
        x=personalized_days,
        y=[record[f"personalized_purchase_{day}d"] for day in personalized_days],
        mode="lines",
        name="Personalized · 10-day intervals",
        line=dict(color="#0F766E", dash="dot"),
        hovertemplate="%{x} days<br>%{y:.1%}<extra>%{fullData.name}</extra>",
    )
    fig.update_layout(
        xaxis_title="Days after historical cutoff",
        yaxis_title="Cumulative probability of a purchase",
        yaxis_tickformat=".0%",
        yaxis_range=[0, 1],
        height=340,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", y=-0.25),
    )
    st.plotly_chart(fig, width="stretch")

    probability_columns = st.columns(3)
    for column, horizon in zip(probability_columns, horizons):
        column.metric(
            f"Purchase within {horizon} days",
            percent(record[f"purchase_probability_{horizon}d"]),
        )

st.markdown("**Personalized expected revenue**")
revenue_metrics = st.columns(3)
for column, horizon in zip(revenue_metrics, horizons):
    column.metric(
        f"Next {horizon} days",
        gbp(record[f"personalized_expected_revenue_{horizon}d"]),
        help="Estimated expected revenue from the saved two-stage model.",
    )

delay_columns = st.columns(3)
delay_columns[0].metric(
    "Historical gaps", f"{int(record['n_historical_gaps']):,}"
)
delay_columns[1].metric(
    "Regularized expected gap",
    f"{record['regularized_expected_gap_days']:.0f} days",
)
delay_columns[2].metric(
    "Delay ratio", f"{record['delay_ratio']:.2f}"
)
st.caption(
    "Probabilities are model estimates, not guarantees. A history sufficiency label "
    "describes the amount of past purchase history available."
)

st.subheader("Purchase history before the cutoff")
history = orders.loc[
    orders["Customer ID"].eq(customer_id) & orders["PurchaseDate"].lt(cutoff)
].sort_values("PurchaseDate")
if history.empty:
    st.info("No valid purchase orders exist before this customer’s cutoff.")
else:
    fig = go.Figure(
        go.Bar(
            x=history["PurchaseDate"],
            y=history["GrossRevenue"],
            marker_color="#2563EB",
            customdata=history[["Invoice"]],
            hovertemplate="%{x|%d %b %Y}<br>Order %{customdata[0]}<br>£%{y:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis_title="Purchase date",
        yaxis_title="Gross order revenue (£)",
        height=300,
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig, width="stretch")
    st.dataframe(
        history.rename(
            columns={
                "Invoice": "Order",
                "PurchaseDate": "Purchase date",
                "GrossRevenue": "Gross revenue",
            }
        ),
        hide_index=True,
        width="stretch",
        column_config={
            "Gross revenue": st.column_config.NumberColumn(format="£%.2f")
        },
    )

export_fields = [
    "Customer ID",
    "cutoff_date",
    "Hist_Segment",
    "history_group",
    "global_purchase_probability_30d",
    "segment_purchase_probability_30d",
    "purchase_probability_30d",
    "global_purchase_probability_60d",
    "segment_purchase_probability_60d",
    "purchase_probability_60d",
    "global_purchase_probability_90d",
    "segment_purchase_probability_90d",
    "purchase_probability_90d",
    "personalized_expected_revenue_30d",
    "personalized_expected_revenue_60d",
    "personalized_expected_revenue_90d",
]
show_download_csv(
    "Download this customer forecast",
    snapshot.loc[snapshot["Customer ID"].eq(customer_id), export_fields],
    f"customer_{customer_id}_forecast.csv",
)
