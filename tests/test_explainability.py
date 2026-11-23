from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src import purchase_clock as pc
from src import spending_model as sm
from src import temporal_framework as tf
from src.explainability import (
    compute_cumulative_purchase_probability,
    decompose_expected_revenue,
    explain_conditional_spending,
    explain_customer_purchase_clock,
    explain_interval_hazard,
    inspect_fitted_purchase_model,
    inspect_spending_model,
)
from src.customer_intelligence import CustomerIntelligence
from src.prediction_reliability import assess_distribution_support
from src.reliability_research import build_reference_profile

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def models_and_features():
    purchase = pc.load_purchase_clock_artifacts(ROOT / "models" / "purchase_clock")
    spending = sm.load_spending_artifacts(ROOT / "models" / "spending_model")
    orders = pd.read_csv(
        ROOT / "data" / "processed" / "temporal" / "orders.csv",
        parse_dates=["PurchaseDate"],
    )
    features = tf.compute_historical_features(orders, pd.Timestamp("2010-09-10"))
    customer = (
        features.sort_values("Customer ID")
        .iloc[[0]]
        .loc[:, list(sm.BASE_FEATURE_COLUMNS)]
        .reset_index(drop=True)
    )
    references = json.loads(
        (ROOT / "models" / "prediction_reliability" / "reference_profile.json")
        .read_text(encoding="utf-8")
    )
    return purchase, spending, features, customer, references


def test_purchase_pipeline_supports_exact_logit_decomposition(models_and_features):
    purchase, _, _, customer, references = models_and_features
    inspected = inspect_fitted_purchase_model(purchase)
    assert inspected["estimator"] == "LogisticRegression"
    assert inspected["coefficient_decomposition_supported"] is True
    assert inspected["coefficient_count"] == 21

    result = explain_interval_hazard(
        purchase, customer, interval_days=30
    )
    prepared = pc._apply_bundle_segmentation(purchase, customer)
    expanded = pc._expand_person_period_features(prepared)
    row = expanded.loc[expanded[pc.INTERVAL_COL].eq("3")]
    matrix = pc._model_matrix(row)
    saved_hazard = purchase["personalized_pipeline"].predict_proba(matrix)[0, 1]
    assert result["reconstructed_hazard"] == pytest.approx(
        saved_hazard, rel=1e-10, abs=1e-12
    )
    assert sum(
        term["logit_contribution"] for term in result["feature_contributions"]
    ) + result["logit_intercept"] == pytest.approx(
        result["reconstructed_logit"], rel=1e-12, abs=1e-12
    )


def test_cumulative_probabilities_match_saved_purchase_clock_and_effect_sign(models_and_features):
    purchase, _, _, customer, references = models_and_features
    result = explain_customer_purchase_clock(
        purchase,
        customer,
        references["purchase_clock"]["reference_values"],
    )
    saved = pc.predict_purchase_clock(purchase, customer).iloc[0]
    for horizon in (30, 60, 90):
        assert result["purchase_probabilities"][str(horizon)] == pytest.approx(
            saved[f"personalized_P{horizon}"], rel=1e-10, abs=1e-12
        )
    for effect in result["feature_effects"]:
        for horizon, reference_probability in effect["reference_probabilities"].items():
            assert effect["probability_effects"][horizon] == pytest.approx(
                result["purchase_probabilities"][horizon] - reference_probability,
                rel=1e-12,
                abs=1e-12,
            )
    assert len(result["interval_decompositions"]) == 9
    assert "not causal" in " ".join(result["model_input_limitations"]).lower()


def test_cumulative_probability_validation_and_monotonicity():
    hazards = np.linspace(0.01, 0.09, 9)
    result = compute_cumulative_purchase_probability(hazards, (30, 60, 90))
    assert result[30] <= result[60] <= result[90]
    assert result[90] == pytest.approx(1.0 - np.prod(1.0 - hazards))
    with pytest.raises(ValueError, match="9-interval"):
        compute_cumulative_purchase_probability([0.1, 0.2], 30)
    with pytest.raises(ValueError, match="finite probabilities"):
        compute_cumulative_purchase_probability([np.nan] * 9, 90)
    with pytest.raises(ValueError, match="30, 60, or 90"):
        compute_cumulative_purchase_probability(hazards, 45)


@pytest.mark.parametrize("horizon", [30, 60, 90])
def test_spending_score_and_revenue_decomposition_match_saved_pipeline(
    models_and_features, horizon
):
    purchase, spending, _, customer, references = models_and_features
    profile = references["spending"][str(horizon)]["reference_values"]
    inspected = inspect_spending_model(spending, horizon)
    assert inspected["estimator"] == "Ridge"
    explanation = explain_conditional_spending(
        spending, customer, horizon, profile
    )
    segmented = sm.apply_spending_segmentation(spending, customer, horizon)
    model = spending["horizon_models"][horizon]["personalized_conditional"]
    expected_conditional = sm.predict_personalized_conditional(model, segmented)[0]
    assert explanation["conditional_expected_spending"] == pytest.approx(
        expected_conditional, rel=1e-10, abs=1e-10
    )
    assert sum(
        term["log_score_contribution"]
        for term in explanation["log_score_contributions"]
    ) + explanation["log_score_intercept"] == pytest.approx(
        explanation["log_score"], rel=1e-12, abs=1e-12
    )

    purchase_predictions = pc.predict_purchase_clock(purchase, customer)
    revenue_predictions = sm.predict_expected_revenue(
        spending, customer, purchase_predictions
    )
    saved_revenue = float(
        revenue_predictions.iloc[0][f"personalized_expected_revenue_{horizon}d"]
    )
    product = decompose_expected_revenue(
        float(purchase_predictions.iloc[0][f"personalized_P{horizon}"]),
        explanation["conditional_expected_spending"],
        saved_revenue,
    )
    assert product["reconstructed_expected_revenue"] == pytest.approx(
        saved_revenue, rel=1e-10, abs=1e-10
    )


def test_expected_revenue_decomposition_handles_zero_probability():
    result = decompose_expected_revenue(0.0, 123.45, 0.0)
    assert result["personalized_expected_revenue"] == 0.0
    with pytest.raises(AssertionError, match="differs"):
        decompose_expected_revenue(0.0, 123.45, 10.0)


def test_reference_profile_is_required_and_unsupported_horizons_fail(models_and_features):
    purchase, spending, _, customer, references = models_and_features
    with pytest.raises(ValueError, match="missing model feature"):
        explain_customer_purchase_clock(purchase, customer, {})
    with pytest.raises(ValueError, match="No saved personalized spending model"):
        inspect_spending_model(spending, 45)


def test_reference_profile_rebuild_is_deterministic_and_train_scoped(models_and_features):
    purchase, spending, _, _, references = models_and_features
    rebuilt = build_reference_profile(ROOT, purchase, spending)
    assert rebuilt["artifact_version"] == "prediction-reliability-reference-v1"
    assert rebuilt["purchase_clock"]["source_role"] == "TRAIN"
    assert rebuilt["purchase_clock"]["reference_values"] == (
        references["purchase_clock"]["reference_values"]
    )
    assert rebuilt["recency_band_edges"] == references["recency_band_edges"]
    assert rebuilt["forecast_cutoff"] == "2010-09-10"


def test_single_purchase_customer_and_customer_cutoff_alignment(models_and_features):
    purchase, _, features, _, references = models_and_features
    one_purchase = (
        features.loc[features["Frequency"].eq(1)]
        .sort_values("Customer ID")
        .iloc[[0]]
        .loc[:, list(sm.BASE_FEATURE_COLUMNS)]
        .reset_index(drop=True)
    )
    explanation = explain_customer_purchase_clock(
        purchase,
        one_purchase,
        references["purchase_clock"]["reference_values"],
    )
    assert explanation["customer_id"] == int(one_purchase.iloc[0]["Customer ID"])
    assert len(explanation["interval_decompositions"]) == 9
    multiple_customers = pd.concat(
        [
            one_purchase,
            one_purchase.assign(**{"Customer ID": int(one_purchase.iloc[0]["Customer ID"]) + 1}),
        ],
        ignore_index=True,
    )
    with pytest.raises(ValueError, match="one customer"):
        explain_interval_hazard(purchase, multiple_customers, 30)


def test_missing_saved_artifact_fails_explicitly():
    with pytest.raises(FileNotFoundError):
        pc.load_purchase_clock_artifacts(ROOT / "models" / "missing-purchase-clock")


def test_fixed_test_cohort_predictions_match_existing_customer_intelligence():
    cutoff = pd.Timestamp("2010-09-10")
    orders = pd.read_csv(
        ROOT / "data" / "processed" / "temporal" / "orders.csv",
        parse_dates=["PurchaseDate"],
    )
    transactions = pd.read_csv(
        ROOT / "data" / "processed" / "online_retail_cleaned_data.csv",
        parse_dates=["InvoiceDate"],
    )
    features = tf.compute_historical_features(orders, cutoff)
    model_features = features.loc[:, list(sm.BASE_FEATURE_COLUMNS)].reset_index(drop=True)
    intelligence = CustomerIntelligence.from_artifacts(ROOT)
    current = intelligence.predict_customers(transactions, cutoff)
    purchase_bundle = pc.load_purchase_clock_artifacts(ROOT / "models" / "purchase_clock")
    spending_bundle = sm.load_spending_artifacts(ROOT / "models" / "spending_model")
    direct_purchase = pc.predict_purchase_clock(purchase_bundle, model_features)
    direct_revenue = sm.predict_expected_revenue(
        spending_bundle, model_features, direct_purchase
    )
    assert len(current) == 3373
    assert current["Customer ID"].tolist() == direct_purchase["Customer ID"].tolist()
    for horizon in (30, 60, 90):
        np.testing.assert_allclose(
            current[f"purchase_probability_{horizon}d"],
            direct_purchase[f"personalized_P{horizon}"],
            rtol=1e-12,
            atol=1e-12,
        )
        np.testing.assert_allclose(
            current[f"personalized_expected_revenue_{horizon}d"],
            direct_revenue[f"personalized_expected_revenue_{horizon}d"],
            rtol=1e-12,
            atol=1e-12,
        )


def test_future_transactions_do_not_change_cutoff_forecasts_or_support_flags(
    models_and_features,
):
    purchase, spending, _, customer, references = models_and_features
    orders = pd.read_csv(
        ROOT / "data" / "processed" / "temporal" / "orders.csv",
        parse_dates=["PurchaseDate"],
    )
    future_order = orders.iloc[[0]].copy()
    future_order["Customer ID"] = customer.iloc[0]["Customer ID"]
    future_order["PurchaseDate"] = pd.Timestamp("2010-10-15")
    if "Invoice" in future_order:
        future_order["Invoice"] = "FUTURE-LEAKAGE-TEST"
    future_order["GrossRevenue"] = 1_000_000.0
    extended_orders = pd.concat([orders, future_order], ignore_index=True)
    original = tf.compute_historical_features(orders, pd.Timestamp("2010-09-10"))
    extended = tf.compute_historical_features(
        extended_orders, pd.Timestamp("2010-09-10")
    )
    customer_id = int(customer.iloc[0]["Customer ID"])
    original_row = original.loc[original["Customer ID"].eq(customer_id)].iloc[[0]]
    extended_row = extended.loc[extended["Customer ID"].eq(customer_id)].iloc[[0]]
    pd.testing.assert_frame_equal(
        original_row.reset_index(drop=True),
        extended_row.reset_index(drop=True),
        check_dtype=False,
    )

    saved_input = original_row.loc[:, list(sm.BASE_FEATURE_COLUMNS)].reset_index(drop=True)
    extended_input = extended_row.loc[:, list(sm.BASE_FEATURE_COLUMNS)].reset_index(drop=True)
    original_purchase = pc.predict_purchase_clock(purchase, saved_input)
    extended_purchase = pc.predict_purchase_clock(purchase, extended_input)
    original_revenue = sm.predict_expected_revenue(
        spending, saved_input, original_purchase
    )
    extended_revenue = sm.predict_expected_revenue(
        spending, extended_input, extended_purchase
    )
    for horizon in (30, 60, 90):
        np.testing.assert_allclose(
            original_purchase[f"personalized_P{horizon}"],
            extended_purchase[f"personalized_P{horizon}"],
            rtol=0,
            atol=0,
        )
        np.testing.assert_allclose(
            original_revenue[f"personalized_expected_revenue_{horizon}d"],
            extended_revenue[f"personalized_expected_revenue_{horizon}d"],
            rtol=0,
            atol=0,
        )
    original_flags = assess_distribution_support(
        pc._apply_bundle_segmentation(purchase, saved_input).iloc[0].to_dict(),
        references["purchase_clock"],
    )
    extended_flags = assess_distribution_support(
        pc._apply_bundle_segmentation(purchase, extended_input).iloc[0].to_dict(),
        references["purchase_clock"],
    )
    assert original_flags == extended_flags
