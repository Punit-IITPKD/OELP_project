from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components.ui import gbp, render_historical_notice, render_page_intro, show_download_csv
from app.services.demo_service import load_forecast_snapshot

render_page_intro(
    "Purchase Forecasting",
    "Compare saved-model return probabilities and expected revenue for the eligible historical cohort.",
)
render_historical_notice()

snapshot = load_forecast_snapshot()
segment_options = sorted(snapshot["Hist_Segment"].dropna().unique().tolist())
history_options = sorted(snapshot["history_group"].dropna().unique().tolist())
left, right = st.columns(2)
with left:
    selected_segments = st.multiselect(
        "Forecast-time segment",
        segment_options,
        default=segment_options,
    )
with right:
    selected_history = st.multiselect(
        "History sufficiency",
        history_options,
        default=history_options,
    )

cohort = snapshot.loc[
    snapshot["Hist_Segment"].isin(selected_segments)
    & snapshot["history_group"].isin(selected_history)
].copy()
if cohort.empty:
    st.warning("Select at least one segment and history group.")
    st.stop()

metrics = st.columns(4)
metrics[0].metric("Customers in cohort", f"{len(cohort):,}")
for column, horizon in zip(metrics[1:], (30, 60, 90)):
    column.metric(
        f"Expected returners · {horizon} days",
        f"{cohort[f'purchase_probability_{horizon}d'].sum():,.0f}",
    )

horizons = [30, 60, 90]
model_columns = {
    "Global": "global_purchase_probability_{}d",
    "Segment-aware": "segment_purchase_probability_{}d",
    "Personalized": "purchase_probability_{}d",
}
fig = go.Figure()
for model_name, template in model_columns.items():
    fig.add_scatter(
        x=horizons,
        y=[cohort[template.format(horizon)].mean() for horizon in horizons],
        mode="lines+markers",
        name=model_name,
        hovertemplate="%{x} days<br>%{y:.1%}<extra>%{fullData.name}</extra>",
    )
fig.update_layout(
    title="Average cumulative purchase probability by model",
    xaxis_title="Days after September 10, 2010",
    yaxis_title="Mean probability across selected customers",
    yaxis_tickformat=".0%",
    yaxis_range=[0, 1],
    height=380,
    margin=dict(l=10, r=10, t=55, b=10),
    legend=dict(orientation="h", y=-0.25),
)
st.plotly_chart(fig, width="stretch")

st.subheader("Personalized cumulative return curve")
days = list(range(10, 91, 10))
mean_curve = [cohort[f"personalized_purchase_{day}d"].mean() for day in days]
fig = go.Figure(
    go.Scatter(
        x=days,
        y=mean_curve,
        mode="lines+markers",
        line=dict(color="#0F766E", width=3),
        hovertemplate="%{x} days<br>%{y:.1%}<extra></extra>",
    )
)
fig.update_layout(
    xaxis_title="Days after historical cutoff",
    yaxis_title="Mean cumulative purchase probability",
    yaxis_tickformat=".0%",
    yaxis_range=[0, 1],
    height=320,
    margin=dict(l=10, r=10, t=20, b=10),
)
st.plotly_chart(fig, width="stretch")

revenue_rows = []
for horizon in horizons:
    revenue_rows.append(
        {
            "Horizon": f"{horizon} days",
            "Expected returners": cohort[f"purchase_probability_{horizon}d"].sum(),
            "Historical-rate expected revenue": cohort[
                f"historical_rate_expected_revenue_{horizon}d"
            ].sum(),
            "Segment-aware expected revenue": cohort[
                f"segment_expected_revenue_{horizon}d"
            ].sum(),
            "Personalized expected revenue": cohort[
                f"personalized_expected_revenue_{horizon}d"
            ].sum(),
        }
    )
revenue_table = pd.DataFrame(revenue_rows)
st.subheader("Cohort revenue forecast")
st.dataframe(
    revenue_table,
    hide_index=True,
    width="stretch",
    column_config={
        "Historical-rate expected revenue": st.column_config.NumberColumn(format="£%.0f"),
        "Segment-aware expected revenue": st.column_config.NumberColumn(format="£%.0f"),
        "Personalized expected revenue": st.column_config.NumberColumn(format="£%.0f"),
        "Expected returners": st.column_config.NumberColumn(format="%.1f"),
    },
)

fig = go.Figure()
for label, column, color in (
    ("Historical-rate", "Historical-rate expected revenue", "#94A3B8"),
    ("Segment-aware", "Segment-aware expected revenue", "#2563EB"),
    ("Personalized", "Personalized expected revenue", "#0F766E"),
):
    fig.add_bar(
        x=revenue_table["Horizon"],
        y=revenue_table[column],
        name=label,
        marker_color=color,
        hovertemplate="%{x}<br>£%{y:,.0f}<extra>%{fullData.name}</extra>",
    )
fig.update_layout(
    barmode="group",
    title="Expected revenue by horizon and model",
    yaxis_title="Expected revenue (£)",
    height=360,
    margin=dict(l=10, r=10, t=55, b=10),
)
st.plotly_chart(fig, width="stretch")

st.caption(
    "The page uses only pre-cutoff features. Model probabilities are estimates; "
    "expected revenue is the saved two-stage model output, not booked revenue."
)
show_download_csv(
    "Download this cohort’s predictions",
    cohort,
    "historical_customer_forecasts.csv",
)
