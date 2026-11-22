from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

from src import purchase_clock as pc
from src import spending_model as sm
from src import temporal_framework as tf
from src.customer_features import build_customer_features
from src.customer_intelligence import CustomerIntelligence
from src.data_preparation import clean_transactions
from src.interpurchase import (
    build_interpurchase_gaps,
    fit_interpurchase_distributions,
    summarize_interpurchase_gaps,
)
from src.segmentation import (
    evaluate_kmeans_candidates,
    fit_descriptive_segmentation,
    select_cluster_count,
)
from src.statistical_analysis import (
    bootstrap_median_ci,
    bootstrap_proportion_ci,
    estimate_historical_gap_percentile,
    summarize_numeric_features,
    validate_segment_outcomes,
    validate_threshold_baseline,
)

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def _synthetic_transactions() -> pd.DataFrame:
    rows = []
    transactions = [
        (70001, "A1", "2009-12-10 10:00:00", 2, 12.5),
        (70001, "A2", "2010-03-01 12:00:00", 1, 25.0),
        (70001, "A3", "2010-08-30 15:00:00", 3, 8.0),
        (70002, "B1", "2010-09-09 08:00:00", 1, 40.0),
        (70003, "D1", "2010-01-03 08:00:00", 1, 10.0),
        (70003, "D2", "2010-04-03 08:00:00", 2, 15.0),
        (70003, "D3", "2010-09-01 08:00:00", 2, 20.0),
    ]
    for customer_id, invoice, date, quantity, price in transactions:
        rows.append(
            {
                "Invoice": invoice,
                "StockCode": "ITEM",
                "Description": "sample item",
                "Quantity": quantity,
                "InvoiceDate": pd.Timestamp(date),
                "Price": price,
                "Customer ID": customer_id,
                "Country": "United Kingdom",
            }
        )
    return pd.DataFrame(rows)


def test_cleaning_matches_notebook01_retention_rules():
    frame = _synthetic_transactions()
    cancellation = frame.iloc[[0]].copy()
    cancellation["Invoice"] = "C101"
    cancellation["Quantity"] = -1
    missing_customer = frame.iloc[[1]].copy()
    missing_customer["Customer ID"] = np.nan
    duplicate = frame.iloc[[2]].copy()
    zero_price = frame.iloc[[3]].copy()
    zero_price["Price"] = 0.0
    input_frame = pd.concat(
        [frame, duplicate, cancellation, missing_customer, zero_price],
        ignore_index=True,
    )
    cleaned, report = clean_transactions(input_frame, return_report=True)

    assert len(cleaned) == len(frame) + 2
    assert cleaned["Customer ID"].notna().all()
    assert cleaned["Invoice"].astype(str).str.startswith("C").sum() == 1
    assert cleaned["Price"].eq(0).sum() == 1
    assert report["duplicate_rows_removed"] == 1
    assert report["missing_customer_rows_removed"] == 1
    assert report["retained_cancellation_rows"] == 1
    assert report["retained_zero_price_rows"] == 1
    assert input_frame["Customer ID"].isna().sum() == 1


def test_cleaning_rejects_invalid_schema_and_nonfinite_values():
    transactions = _synthetic_transactions()
    with pytest.raises(ValueError, match="missing required columns"):
        clean_transactions(transactions.drop(columns=["Invoice"]))

    invalid_price = transactions.copy()
    invalid_price.loc[0, "Price"] = np.inf
    with pytest.raises(ValueError, match="Price must contain finite values"):
        clean_transactions(invalid_price)

    fractional_id = transactions.copy()
    fractional_id["Customer ID"] = fractional_id["Customer ID"].astype(float)
    fractional_id.loc[0, "Customer ID"] = 70001.5
    with pytest.raises(ValueError, match="whole numbers"):
        clean_transactions(fractional_id)


def test_cleaned_year1_customer_features_match_notebook02():
    transactions = pd.read_csv(
        PROCESSED / "online_retail_cleaned_data.csv",
        parse_dates=["InvoiceDate"],
    )
    actual = build_customer_features(transactions)
    expected = pd.read_csv(PROCESSED / "customer_features.csv")

    assert actual.columns.tolist() == expected.columns.tolist()
    assert actual["Customer ID"].tolist() == expected["Customer ID"].tolist()
    for column in expected.columns.difference(["Customer ID"]):
        np.testing.assert_allclose(
            actual[column].to_numpy(dtype=float),
            expected[column].to_numpy(dtype=float),
            rtol=1e-6,
            atol=5e-7,
            equal_nan=True,
            err_msg=f"Notebook 02 feature differs: {column}",
        )
    assert actual.loc[actual["Frequency"].eq(1), "Median_InterPurchase_Days"].isna().all()


def test_interpurchase_gaps_and_fitted_statistics_match_notebook03():
    transactions = pd.read_csv(
        PROCESSED / "online_retail_cleaned_data.csv",
        parse_dates=["InvoiceDate"],
    )
    gaps = build_interpurchase_gaps(transactions)
    positive = gaps.loc[gaps["gap_days"].gt(0)]
    assert len(gaps) == 14_901
    assert gaps["gap_days"].eq(0).sum() == 70
    assert len(positive) == 14_831
    assert gaps["gap_days"].ge(0).all()

    summary = summarize_interpurchase_gaps(gaps)
    assert summary["Gap_Count"].sum() == len(gaps)
    assert summary.loc[summary["Gap_Count"].eq(1), "Std_InterPurchase_Days"].isna().all()

    actual = fit_interpurchase_distributions(gaps)
    expected = pd.read_csv(PROCESSED / "interpurchase_distribution_results.csv")
    assert actual["distribution"].tolist() == expected["distribution"].tolist()
    assert actual["n_observations"].eq(expected["n_observations"]).all()
    for column in (
        "log_likelihood",
        "aic",
        "bic",
        "ks_statistic",
        "p90_model_days",
        "p95_model_days",
        "param1",
        "param2",
        "param3",
    ):
        np.testing.assert_allclose(
            actual[column].to_numpy(dtype=float),
            expected[column].to_numpy(dtype=float),
            rtol=1e-6,
            atol=1e-5,
            equal_nan=True,
        )


def test_numeric_summary_includes_iqr_and_percentiles():
    result = summarize_numeric_features(
        pd.DataFrame({"frequency": [1, 2, 3, 10]}), ["frequency"]
    )
    assert result.loc["frequency", "iqr"] == pytest.approx(3.0)
    assert "90%" in result.columns
    assert np.isfinite(result.loc["frequency", "skewness"])


def test_notebook05_validation_statistics_and_threshold_are_reproducible():
    analysis = pd.read_csv(PROCESSED / "temporal" / "combined_cutoffB.csv")
    expected = pd.read_json(
        PROCESSED / "temporal" / "validation_results.json", typ="series"
    ).to_dict()
    actual = validate_segment_outcomes(analysis)
    for result_name, values in actual.items():
        for metric, value in values.items():
            if isinstance(value, (int, float)):
                assert value == pytest.approx(expected[result_name][metric], abs=1e-10)
            else:
                assert value == expected[result_name][metric]

    orders = pd.read_csv(
        PROCESSED / "temporal" / "orders.csv",
        parse_dates=["PurchaseDate"],
    )
    threshold, n_gaps = estimate_historical_gap_percentile(
        orders, "2010-08-01", percentile=90
    )
    assert threshold == pytest.approx(80.2322222222, abs=1e-9)
    assert n_gaps == 7_544
    baseline = validate_threshold_baseline(analysis, threshold)
    for metric, value in baseline.items():
        if isinstance(value, (int, float)):
            assert value == pytest.approx(
                expected["threshold_baseline_90d"][metric], abs=1e-10
            )
        else:
            assert value == expected["threshold_baseline_90d"][metric]

    assert bootstrap_proportion_ci(893, 1_135) == pytest.approx((0.763, 0.810), abs=0.0005)
    active = analysis.loc[
        analysis["Hist_Segment"].eq("Recent / Active"), "FutureOrders_90d"
    ]
    assert bootstrap_median_ci(active) == pytest.approx((1.0, 2.0))


def test_descriptive_segmentation_reproduces_notebook04_profiles_and_labels():
    features = pd.read_csv(PROCESSED / "customer_features.csv")
    features = features.loc[~features["Customer ID"].isin(tf.ADMIN_EXCLUDE)].copy()
    result = fit_descriptive_segmentation(features)
    expected = pd.read_csv(PROCESSED / "customer_segments.csv")
    expected_profiles = pd.read_csv(PROCESSED / "cluster_profiles.csv")

    assignments = result.customers[["Customer ID", "Cluster", "Segment_Name"]].merge(
        expected[["Customer ID", "Cluster", "Segment_Name"]],
        on="Customer ID",
        suffixes=("_actual", "_expected"),
        validate="one_to_one",
    )
    assert assignments["Cluster_actual"].equals(assignments["Cluster_expected"])
    assert assignments["Segment_Name_actual"].equals(assignments["Segment_Name_expected"])
    pd.testing.assert_frame_equal(
        result.profiles[expected_profiles.columns].reset_index(drop=True),
        expected_profiles.reset_index(drop=True),
        check_dtype=False,
        check_exact=False,
        atol=1e-8,
        rtol=1e-8,
    )
    assert result.metrics["silhouette_score"] == pytest.approx(0.422250, abs=1e-6)
    assert result.kmeans.n_features_in_ == 3
    actual_metrics = evaluate_kmeans_candidates(features)
    expected_metrics = pd.read_csv(PROCESSED / "clustering_metrics.csv")
    pd.testing.assert_frame_equal(
        actual_metrics,
        expected_metrics,
        check_dtype=False,
        check_exact=False,
        atol=1e-8,
        rtol=1e-8,
    )
    assert select_cluster_count(actual_metrics, features) == 2


@pytest.fixture(scope="module")
def customer_intelligence():
    return CustomerIntelligence.from_artifacts(ROOT)


def test_saved_artifacts_generate_notebook06_purchase_and_notebook07_revenue_results(
    customer_intelligence,
):
    transactions = pd.read_csv(
        PROCESSED / "online_retail_cleaned_data.csv",
        parse_dates=["InvoiceDate"],
    )
    predictions = customer_intelligence.predict_customers(
        transactions, "2010-09-10"
    )
    assert len(predictions) == 3_373
    assert predictions["Customer ID"].nunique() == 3_373
    assert predictions["cutoff_date"].eq(pd.Timestamp("2010-09-10")).all()
    assert not set(predictions.columns).intersection(pc.TARGET_COLUMNS)
    assert not any(column.startswith("Future") for column in predictions.columns)

    orders = pd.read_csv(
        PROCESSED / "temporal" / "orders.csv",
        parse_dates=["PurchaseDate"],
    )
    split = pd.read_csv(
        PROCESSED / "temporal" / "predictive_splits_90d.csv",
        parse_dates=["cutoff_date"],
    )
    test_features = split.loc[split["split_role"].eq("TEST"), list(sm.FEATURE_COLUMNS)]
    targets = tf.compute_future_targets(
        orders,
        test_features,
        pd.Timestamp("2010-09-10"),
        orders["PurchaseDate"].max(),
        horizons=list(sm.HORIZONS),
    )
    joined = test_features[["Customer ID", "cutoff_date"]].merge(
        predictions,
        on=["Customer ID", "cutoff_date"],
        validate="one_to_one",
    )

    expected_purchase_metrics = {
        30: (0.178534, 0.720882, 0.537588),
        60: (0.214200, 0.721767, 0.716292),
        90: (0.215308, 0.719368, 0.784723),
    }
    expected_personalized_revenue = {
        30: (871.295288, 639_659.396),
        60: (1466.124975, 1_257_116.377),
        90: (2111.733507, 1_861_869.512),
    }
    for horizon in sm.HORIZONS:
        y = targets[f"Purchased_{horizon}d"].to_numpy(dtype=int)
        probability = joined[f"purchase_probability_{horizon}d"].to_numpy(dtype=float)
        actual_purchase = (
            brier_score_loss(y, probability),
            roc_auc_score(y, probability),
            average_precision_score(y, probability),
        )
        np.testing.assert_allclose(
            actual_purchase, expected_purchase_metrics[horizon], atol=1e-6, rtol=0
        )
        actual_revenue = targets[f"FutureRevenue_{horizon}d"].to_numpy(dtype=float)
        revenue = joined[
            f"personalized_expected_revenue_{horizon}d"
        ].to_numpy(dtype=float)
        metrics = sm.evaluate_expected_revenue(actual_revenue, revenue)
        assert metrics["rmse"] == pytest.approx(
            expected_personalized_revenue[horizon][0], abs=1e-6
        )
        assert metrics["total_predicted_revenue"] == pytest.approx(
            expected_personalized_revenue[horizon][1], abs=0.01
        )


def test_batch_single_customer_and_future_rows_do_not_change_inference(
    customer_intelligence,
):
    transactions = _synthetic_transactions()
    batch = customer_intelligence.predict_customers(transactions, "2010-09-10")
    one = customer_intelligence.predict_customers(
        transactions, "2010-09-10", customer_ids=70001
    )
    assert len(batch) == 3
    assert len(one) == 1
    assert one.iloc[0]["Customer ID"] == 70001

    future = transactions.iloc[[0]].copy()
    future["Invoice"] = "A4"
    future["InvoiceDate"] = pd.Timestamp("2010-09-12")
    future["Quantity"] = 1
    with_future = customer_intelligence.predict_customers(
        pd.concat([transactions, future], ignore_index=True),
        "2010-09-10",
        customer_ids=70001,
    )
    numeric = [
        column
        for column in one.select_dtypes(include="number")
        if column not in {"Customer ID"}
    ]
    np.testing.assert_allclose(one[numeric], with_future[numeric], rtol=0, atol=1e-12)

    at_cutoff = transactions.iloc[[0]].copy()
    at_cutoff["Invoice"] = "A5"
    at_cutoff["InvoiceDate"] = pd.Timestamp("2010-09-10")
    boundary = customer_intelligence.predict_customers(
        pd.concat([transactions, at_cutoff], ignore_index=True),
        "2010-09-10",
        customer_ids=70001,
    )
    np.testing.assert_allclose(one[numeric], boundary[numeric], rtol=0, atol=1e-12)


def test_historical_eligibility_and_spending_transform_compatibility(
    customer_intelligence,
):
    transactions = _synthetic_transactions()
    july = customer_intelligence.predict_customers(
        transactions, "2010-07-01", horizons=[60]
    )
    assert len(july) == 2
    assert july["prediction_protocol_60d"].eq("prospective").all()

    with pytest.raises(ValueError, match="is historically eligible"):
        customer_intelligence.predict_customers(transactions, "2010-08-15")
    with pytest.raises(ValueError, match="not validated"):
        customer_intelligence.predict_customers(
            transactions, "2010-08-01", horizons=[60]
        )
    with pytest.raises(ValueError, match="no valid pre-cutoff"):
        customer_intelligence.predict_customers(
            transactions, "2010-09-10", customer_ids=[99999]
        )
    out_of_scope = transactions.iloc[[0]].copy()
    out_of_scope["InvoiceDate"] = pd.Timestamp("2011-01-01")
    with pytest.raises(ValueError, match="beyond the Year 1 model scope"):
        customer_intelligence.predict_customers(
            pd.concat([transactions, out_of_scope], ignore_index=True),
            "2010-09-10",
            customer_ids=70001,
        )


def test_saved_segmentation_schema_mismatch_is_rejected(customer_intelligence):
    bad_spending = dict(customer_intelligence.spending_bundle)
    bad_spending["segment_transforms"] = dict(
        customer_intelligence.spending_bundle["segment_transforms"]
    )
    bad_transform = dict(bad_spending["segment_transforms"][30])
    bad_transform["feature_columns"] = ["Recency", "Frequency"]
    bad_spending["segment_transforms"][30] = bad_transform
    with pytest.raises(ValueError, match="incompatible segmentation feature schema"):
        CustomerIntelligence(
            customer_intelligence.purchase_bundle,
            bad_spending,
            validation_purchase_bundle=customer_intelligence.validation_purchase_bundle,
            dataset_end=customer_intelligence.dataset_end,
            dataset_start=customer_intelligence.dataset_start,
        )
