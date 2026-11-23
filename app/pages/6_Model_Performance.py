from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.components.ui import render_page_intro
from app.config import METRICS_DIR

render_page_intro(
    "Model Performance",
    "Out-of-time TEST results extracted from the saved Notebook 06 and 07 outputs.",
)

summary_path = METRICS_DIR / "notebook_evaluation_summary.json"
if not summary_path.is_file():
    st.error(
        "Verified notebook evaluation results are unavailable. "
        "Run `python scripts/export_notebook_evaluation.py` after confirming the notebook outputs."
    )
    st.stop()

summary = json.loads(summary_path.read_text(encoding="utf-8"))
purchase_metrics = pd.DataFrame(summary["purchase_clock"]["test_metrics"])
purchase_history = pd.DataFrame(summary["purchase_clock"]["history_group_metrics"])
revenue_metrics = pd.DataFrame(summary["spending_forecast"]["test_metrics"])
revenue_groups = pd.DataFrame(summary["spending_forecast"]["group_metrics"])

st.info(
    "All displayed metrics are for the saved TEST split at the September 10, 2010 "
    "cutoff (3,373 customers). TEST outcomes are used for evaluation only, never "
    "as prediction inputs."
)

st.subheader("Purchase-return model")
personalized = purchase_metrics.loc[purchase_metrics["model"].eq("Personalized")]
best_90d = personalized.loc[personalized["horizon_days"].eq(90)].iloc[0]
columns = st.columns(4)
columns[0].metric("90-day Brier score", f"{best_90d['brier_score']:.3f}")
columns[1].metric("90-day ROC-AUC", f"{best_90d['roc_auc']:.3f}")
columns[2].metric("90-day average precision", f"{best_90d['average_precision']:.3f}")
columns[3].metric("90-day calibration error", f"{best_90d['calibration_error']:.3f}")

fig = go.Figure()
for model_name, group in purchase_metrics.groupby("model", sort=False):
    group = group.sort_values("horizon_days")
    fig.add_scatter(
        x=group["mean_predicted_probability"],
        y=group["actual_purchase_rate"],
        mode="lines+markers",
        name=model_name,
        customdata=group["horizon_days"],
        hovertemplate=(
            "%{customdata}-day horizon<br>Predicted %{x:.1%}"
            "<br>Observed %{y:.1%}<extra>%{fullData.name}</extra>"
        ),
    )
fig.add_scatter(
    x=[0, 1],
    y=[0, 1],
    mode="lines",
    name="Perfect aggregate calibration",
    line=dict(color="#64748B", dash="dash"),
)
fig.update_layout(
    title="Mean predicted probability vs observed rate",
    xaxis_title="Mean predicted probability",
    yaxis_title="Observed purchase rate",
    xaxis_tickformat=".0%",
    yaxis_tickformat=".0%",
    xaxis_range=[0, 1],
    yaxis_range=[0, 1],
    height=360,
    margin=dict(l=10, r=10, t=55, b=10),
)
st.plotly_chart(fig, width="stretch")
st.caption(
    "Each point summarizes a full horizon and model; the diagrams below show the "
    "customer-level reliability bins from the saved evaluation output."
)

calibration_path = METRICS_DIR / "purchase_clock_test_calibration.png"
calibration_90_path = METRICS_DIR / "purchase_clock_test_calibration_90d.png"
left, right = st.columns(2)
with left:
    if calibration_path.is_file():
        st.image(
            calibration_path,
            caption="TEST reliability diagrams for 30-, 60-, and 90-day horizons",
            width="stretch",
        )
with right:
    if calibration_90_path.is_file():
        st.image(
            calibration_90_path,
            caption="TEST 90-day reliability diagram",
            width="stretch",
        )

st.dataframe(
    purchase_metrics.sort_values(["horizon_days", "model"]),
    hide_index=True,
    width="stretch",
    column_config={
        "actual_purchase_rate": st.column_config.NumberColumn(format="%.1%%"),
        "mean_predicted_probability": st.column_config.NumberColumn(format="%.1%%"),
        "brier_score": st.column_config.NumberColumn(format="%.4f"),
        "log_loss": st.column_config.NumberColumn(format="%.4f"),
        "roc_auc": st.column_config.NumberColumn(format="%.4f"),
        "average_precision": st.column_config.NumberColumn(format="%.4f"),
        "calibration_error": st.column_config.NumberColumn(format="%.4f"),
    },
)

st.subheader("Purchase model performance by history sufficiency")
st.dataframe(
    purchase_history.sort_values(["horizon_days", "history_group"]),
    hide_index=True,
    width="stretch",
    column_config={
        "actual_purchase_rate": st.column_config.NumberColumn(format="%.1%%"),
        "mean_predicted_probability": st.column_config.NumberColumn(format="%.1%%"),
        "brier_score": st.column_config.NumberColumn(format="%.4f"),
        "roc_auc": st.column_config.NumberColumn(format="%.4f"),
    },
)

st.divider()
st.subheader("Expected-revenue model")
st.dataframe(
    revenue_metrics.sort_values(["horizon_days", "model"]),
    hide_index=True,
    width="stretch",
    column_config={
        "mae": st.column_config.NumberColumn(format="£%.2f"),
        "rmse": st.column_config.NumberColumn(format="£%.2f"),
        "mean_forecast_bias": st.column_config.NumberColumn(format="£%.2f"),
        "total_predicted_revenue": st.column_config.NumberColumn(format="£%.0f"),
        "total_actual_revenue": st.column_config.NumberColumn(format="£%.0f"),
        "total_revenue_bias": st.column_config.NumberColumn(format="£%.0f"),
        "aggregate_calibration_ratio": st.column_config.NumberColumn(format="%.3f"),
    },
)

fig = go.Figure()
for model_name, group in revenue_metrics.groupby("model", sort=False):
    group = group.sort_values("horizon_days")
    fig.add_scatter(
        x=group["horizon_days"],
        y=group["total_predicted_revenue"],
        mode="lines+markers",
        name=f"{model_name} · predicted",
    )
fig.add_scatter(
    x=sorted(revenue_metrics["horizon_days"].unique()),
    y=[
        revenue_metrics.loc[
            revenue_metrics["horizon_days"].eq(horizon), "total_actual_revenue"
        ].iloc[0]
        for horizon in sorted(revenue_metrics["horizon_days"].unique())
    ],
    mode="lines+markers",
    name="Observed revenue",
    line=dict(color="#334155", dash="dash"),
)
fig.update_layout(
    title="Portfolio revenue: predicted vs observed",
    xaxis_title="Forecast horizon (days)",
    yaxis_title="Revenue (£)",
    height=360,
    margin=dict(l=10, r=10, t=55, b=10),
)
st.plotly_chart(fig, width="stretch")

history_groups = revenue_groups.loc[
    revenue_groups["group_type"].eq("history_group")
].copy()
st.subheader("Expected-revenue performance by history sufficiency")
st.dataframe(
    history_groups.sort_values(["horizon_days", "model", "group"]),
    hide_index=True,
    width="stretch",
    column_config={
        "mae": st.column_config.NumberColumn(format="£%.2f"),
        "rmse": st.column_config.NumberColumn(format="£%.2f"),
        "mean_forecast_bias": st.column_config.NumberColumn(format="£%.2f"),
        "aggregate_calibration_ratio": st.column_config.NumberColumn(format="%.3f"),
    },
)

st.subheader("Portfolio calibration ratio")
fig = go.Figure()
for model_name, group in revenue_metrics.groupby("model", sort=False):
    group = group.sort_values("horizon_days")
    fig.add_scatter(
        x=group["horizon_days"],
        y=group["aggregate_calibration_ratio"],
        mode="lines+markers",
        name=model_name,
        hovertemplate="%{x} days<br>Ratio %{y:.2f}<extra>%{fullData.name}</extra>",
    )
fig.add_hline(y=1, line_dash="dash", line_color="#64748B")
fig.update_layout(
    xaxis_title="Forecast horizon (days)",
    yaxis_title="Predicted / observed revenue",
    height=320,
    margin=dict(l=10, r=10, t=20, b=10),
)
st.plotly_chart(fig, width="stretch")

with st.expander("Metric definitions and provenance"):
    st.markdown(
        "- **Brier score / log loss:** probability error measures; lower is better.\n"
        "- **ROC-AUC / average precision:** ranking measures; higher is better.\n"
        "- **Calibration error:** weighted gap between predicted and observed purchase rate.\n"
        "- **MAE / RMSE:** customer-level revenue error in dataset currency.\n"
        "- **Portfolio calibration ratio:** predicted total divided by observed total; 1.0 is exact.\n\n"
        "The JSON and calibration images on this page are exported from saved outputs "
        "in Notebooks 06 and 07. The exporter does not execute or change those notebooks."
    )
