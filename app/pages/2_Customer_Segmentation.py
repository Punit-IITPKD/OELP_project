from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components.ui import gbp, render_page_intro, show_download_csv
from app.services.demo_service import load_descriptive_tables, load_forecast_snapshot

render_page_intro(
    "Customer Segmentation",
    "Explore the full-year descriptive RFM segments separately from forecast-time segments.",
)

_, segments = load_descriptive_tables()
snapshot = load_forecast_snapshot()
descriptive_options = sorted(segments["Segment_Name"].dropna().unique().tolist())
selected = st.selectbox("Full-year descriptive segment", ["All segments", *descriptive_options])
view = segments if selected == "All segments" else segments.loc[
    segments["Segment_Name"].eq(selected)
]

segment_metrics = st.columns(4)
segment_metrics[0].metric("Customers", f"{view['Customer ID'].nunique():,}")
segment_metrics[1].metric(
    "Median orders", f"{view['Frequency'].median():,.0f}" if len(view) else "—"
)
segment_metrics[2].metric(
    "Median gross spend", gbp(view["Monetary_Gross"].median()) if len(view) else "—"
)
segment_metrics[3].metric(
    "Median recency", f"{view['Recency'].median():,.0f} days" if len(view) else "—"
)

left, right = st.columns(2)
with left:
    st.subheader("Customer count by segment")
    counts = (
        segments.groupby("Segment_Name", as_index=False)
        .agg(Customers=("Customer ID", "nunique"))
        .sort_values("Customers", ascending=False)
    )
    fig = px.bar(
        counts,
        x="Segment_Name",
        y="Customers",
        color="Segment_Name",
        color_discrete_sequence=["#2563EB", "#0F766E"],
        labels={"Segment_Name": "Full-year descriptive segment"},
    )
    fig.update_layout(showlegend=False, height=330, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, width="stretch")
with right:
    st.subheader("RFM profile")
    profile = (
        segments.groupby("Segment_Name", as_index=False)
        .agg(
            MedianRecency=("Recency", "median"),
            MedianFrequency=("Frequency", "median"),
            MedianGrossSpend=("Monetary_Gross", "median"),
        )
    )
    profile_long = profile.melt(
        id_vars="Segment_Name",
        var_name="Measure",
        value_name="Median value",
    )
    fig = px.bar(
        profile_long,
        x="Measure",
        y="Median value",
        color="Segment_Name",
        barmode="group",
        color_discrete_sequence=["#2563EB", "#0F766E"],
    )
    fig.update_layout(height=330, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, width="stretch")

st.subheader("Customer spend distribution")
positive_spend = view.loc[view["Monetary_Gross"].gt(0)]
if positive_spend.empty:
    st.info("There are no positive gross-spend values in this selection.")
else:
    fig = px.histogram(
        positive_spend,
        x="Monetary_Gross",
        color="Segment_Name",
        nbins=40,
        log_x=True,
        labels={"Monetary_Gross": "Gross spend per customer (£, log scale)"},
        color_discrete_sequence=["#2563EB", "#0F766E"],
    )
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, width="stretch")

st.subheader("Customers")
search = st.text_input("Filter by customer ID", placeholder="Type a customer ID")
table = view.copy()
if search.strip():
    table = table.loc[
        table["Customer ID"].astype(str).str.contains(search.strip(), regex=False)
    ]
st.dataframe(
    table[
        [
            "Customer ID",
            "Segment_Name",
            "Recency",
            "Frequency",
            "Monetary_Gross",
            "Monetary_Net",
            "AOV",
            "At_Risk_Flag",
        ]
    ],
    hide_index=True,
    width="stretch",
    column_config={
        "Monetary_Gross": st.column_config.NumberColumn("Gross spend", format="£%.2f"),
        "Monetary_Net": st.column_config.NumberColumn("Net spend", format="£%.2f"),
        "AOV": st.column_config.NumberColumn("Average order value", format="£%.2f"),
    },
)
show_download_csv(
    "Download this customer table",
    table,
    "customer_segments.csv",
)

st.divider()
st.subheader("Forecast-time segment mix")
st.caption(
    "These labels are produced from the saved TRAIN-fitted transform using purchases "
    f"before {snapshot['cutoff_date'].iloc[0].date()}; they are not the full-year clusters above."
)
historical_mix = (
    snapshot.groupby("Hist_Segment", as_index=False)
    .agg(Customers=("Customer ID", "nunique"))
    .sort_values("Customers", ascending=False)
)
st.dataframe(historical_mix, hide_index=True, width="stretch")
