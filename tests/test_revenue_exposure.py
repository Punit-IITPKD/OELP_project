from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.revenue_exposure import (
    RevenueExposureConfig,
    calculate_exposure_concentration,
    calculate_opportunity_proxy,
    calculate_reference_exposure,
    compute_forecast_disagreement,
    prepare_revenue_forecast_table,
    summarize_portfolio_exposure,
)


def snapshot(horizon: int = 30) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Customer ID": [2, 1],
            "cutoff_date": ["2010-09-10", "2010-09-10"],
            "Hist_Segment": ["Recent / Active", "Lapsed / At-Risk"],
            "history_group": ["Five or more purchases", "Exactly one purchase"],
            "Recency": [5, 100],
            "Frequency": [6, 1],
            "Monetary_Gross": [500.0, 100.0],
            f"purchase_probability_{horizon}d": [0.25, 0.0],
            f"personalized_conditional_revenue_{horizon}d": [80.0, 0.0],
            f"personalized_expected_revenue_{horizon}d": [20.0, 0.0],
            f"historical_rate_expected_revenue_{horizon}d": [40.0, 0.0],
            f"segment_expected_revenue_{horizon}d": [30.0, 0.0],
        }
    )


def test_forecast_decomposition_and_horizon_alignment() -> None:
    prepared = prepare_revenue_forecast_table(snapshot(30), 30)
    first = prepared.loc[prepared["customer_id"].eq(2)].iloc[0]
    assert first["personalized_expected_revenue_gbp"] == pytest.approx(20)
    assert first["conditional_expected_spending_gbp"] == pytest.approx(80)
    assert first["nonreturn_weighted_conditional_spending_proxy_gbp"] == pytest.approx(60)
    assert prepared["horizon_days"].eq(30).all()
    assert prepared["currency_code"].eq("GBP").all()
    with pytest.raises(ValueError, match="missing required columns"):
        prepare_revenue_forecast_table(snapshot(30), 60)


def test_invalid_probabilities_revenue_and_horizon_are_rejected() -> None:
    invalid = snapshot()
    invalid.loc[0, "purchase_probability_30d"] = 1.01
    with pytest.raises(ValueError, match="between zero and one"):
        prepare_revenue_forecast_table(invalid, 30)

    invalid = snapshot()
    invalid.loc[0, "personalized_expected_revenue_30d"] = 19
    with pytest.raises(ValueError, match="does not equal"):
        prepare_revenue_forecast_table(invalid, 30)

    invalid = snapshot()
    invalid.loc[0, "personalized_conditional_revenue_30d"] = -1
    with pytest.raises(ValueError, match="non-negative"):
        prepare_revenue_forecast_table(invalid, 30)

    invalid = snapshot()
    invalid["FutureRevenue_30d"] = [0, 50]
    with pytest.raises(ValueError, match="future outcome"):
        prepare_revenue_forecast_table(invalid, 30)

    with pytest.raises(ValueError, match="horizon_days"):
        prepare_revenue_forecast_table(snapshot(), 45)


def test_duplicate_customer_cutoff_pairs_fail() -> None:
    invalid = pd.concat([snapshot(), snapshot().iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="must be unique"):
        prepare_revenue_forecast_table(invalid, 30)


def test_forecast_disagreement_is_not_exposure() -> None:
    prepared = prepare_revenue_forecast_table(snapshot(), 30)
    compared = compute_forecast_disagreement(prepared, 30)
    first = compared.loc[compared["customer_id"].eq(2)].iloc[0]
    assert first["historical_minus_personalized_forecast_difference_gbp"] == 20
    assert first["segment_minus_personalized_forecast_difference_gbp"] == 10
    assert "not_revenue_exposure" in first["difference_interpretation"]
    assert "estimated_revenue_exposure_gbp" not in compared


def test_reference_exposure_is_null_without_a_defensible_reference() -> None:
    prepared = prepare_revenue_forecast_table(snapshot(), 30)
    result = calculate_reference_exposure(
        prepared,
        None,
        RevenueExposureConfig(),
    )
    assert result["estimated_revenue_exposure_gbp"].isna().all()
    assert result["exposure_status"].eq("not_estimable").all()
    assert result["exposure_method"].isna().all()


def test_reference_exposure_requires_documentation_and_exact_match() -> None:
    prepared = prepare_revenue_forecast_table(snapshot(), 30)
    reference = pd.DataFrame(
        {
            "customer_id": [2],
            "cutoff_date": ["2010-09-10"],
            "horizon_days": [30],
            "reference_expected_revenue_gbp": [40.0],
        }
    )
    with pytest.raises(ValueError, match="definition and method"):
        calculate_reference_exposure(prepared, reference, RevenueExposureConfig())
    result = calculate_reference_exposure(
        prepared,
        reference,
        RevenueExposureConfig(
            reference_definition="Predeclared matched business target",
            reference_method="documented_business_baseline",
        ),
    )
    matched = result.loc[result["customer_id"].eq(2)].iloc[0]
    unmatched = result.loc[result["customer_id"].eq(1)].iloc[0]
    assert matched["estimated_revenue_exposure_gbp"] == 20
    assert matched["exposure_status"] == "estimable"
    assert pd.isna(unmatched["estimated_revenue_exposure_gbp"])
    assert unmatched["exposure_status"] == "reference_not_matched"

    duplicate = pd.concat([reference, reference], ignore_index=True)
    with pytest.raises(ValueError, match="unique"):
        calculate_reference_exposure(
            prepared,
            duplicate,
            RevenueExposureConfig(
                reference_definition="baseline",
                reference_method="documented_business_baseline",
            ),
        )


def test_proxy_handles_zero_and_near_zero_probabilities_without_claiming_loss() -> None:
    table = pd.DataFrame(
        {
            "purchase_probability": [0.0, 1e-12, 1.0],
            "conditional_expected_spending_gbp": [0.0, 100.0, 300.0],
        }
    )
    result = calculate_opportunity_proxy(table, RevenueExposureConfig())
    np.testing.assert_allclose(
        result["nonreturn_weighted_conditional_spending_proxy_gbp"],
        [0.0, 100.0 * (1 - 1e-12), 0.0],
    )
    assert result["opportunity_proxy_interpretation"].str.contains(
        "not observed loss"
    ).all()

    invalid = table.copy()
    invalid.loc[0, "purchase_probability"] = np.inf
    with pytest.raises(ValueError, match="finite"):
        calculate_opportunity_proxy(invalid, RevenueExposureConfig())


def test_portfolio_summary_preserves_not_estimable_as_null_not_zero() -> None:
    prepared = prepare_revenue_forecast_table(snapshot(), 30)
    summary = summarize_portfolio_exposure(prepared, RevenueExposureConfig())
    assert summary["eligible_customers"] == 2
    assert summary["estimated_revenue_exposure_total_gbp"] is None
    assert summary["exposure_status"] == "not_estimable"
    assert summary["exposure_coverage"] == 0
    assert summary["opportunity_proxy_total_gbp"] == pytest.approx(60)
    with pytest.raises(ValueError, match="unique"):
        summarize_portfolio_exposure(
            pd.concat([prepared, prepared.iloc[[0]]], ignore_index=True),
            RevenueExposureConfig(),
        )


def test_exposure_concentration_is_deterministic_and_gbp_labeled() -> None:
    prepared = prepare_revenue_forecast_table(snapshot(), 30)
    result = calculate_exposure_concentration(
        prepared,
        "historical_gross_spending_gbp",
        proportions=(0.5, 1.0),
    )
    assert result.loc[0, "selected_customers"] == 1
    assert result.loc[0, "selected_total_gbp"] == 500
    assert result.loc[0, "portfolio_share"] == pytest.approx(5 / 6)
    assert result.loc[1, "portfolio_share"] == pytest.approx(1)

    with pytest.raises(ValueError, match="proportions"):
        calculate_exposure_concentration(
            prepared, "historical_gross_spending_gbp", proportions=(0, 1.1)
        )
