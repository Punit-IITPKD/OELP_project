from __future__ import annotations

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.behavior_monitor import (
    BehaviorConfig,
    build_behavior_trajectory,
    compute_behavior_features,
    compute_completed_gaps,
    compute_ewma_features,
    calculate_behavior_scores,
    evaluate_binary_risk,
    evaluate_frozen_alert_threshold,
    paired_customer_bootstrap_difference,
    prepare_purchase_events,
)


def _orders(rows: list[tuple[int, str, str, float]]) -> pd.DataFrame:
    return pd.DataFrame(
        rows,
        columns=["Customer ID", "Invoice", "PurchaseDate", "GrossRevenue"],
    )


def test_prepare_purchase_events_sorts_and_applies_purchase_exclusions() -> None:
    events = prepare_purchase_events(
        _orders(
            [
                (7, "1003", "2020-01-11 09:00:00", 12.0),
                (7, "1001", "2020-01-01 09:00:00", 10.0),
                (7, "1002", "2020-01-01 09:00:00", 8.0),
                (7, "C1004", "2020-01-12 09:00:00", 20.0),
                (14103, "1005", "2020-01-13 09:00:00", 30.0),
            ]
        )
    )

    assert events["Invoice"].tolist() == ["1001", "1002", "1003"]
    gaps = compute_completed_gaps(events)
    assert gaps["completed_gap_days"].tolist() == [0.0, 10.0]


def test_snapshot_uses_half_open_nonoverlapping_windows_and_fractional_gaps() -> None:
    cutoff = pd.Timestamp("2020-06-01")
    rows = [
        (10, f"i{days}", (cutoff - pd.Timedelta(days=days)).strftime("%Y-%m-%d"), 20.0)
        for days in (150, 120, 100, 90, 80, 60, 40, 20, 5)
    ]
    rows.append((10, "at-cutoff", cutoff.strftime("%Y-%m-%d"), 999.0))
    features = compute_behavior_features(_orders(rows), cutoff)
    row = features.iloc[0]

    assert row["historical_order_count"] == 9
    assert row["reference_order_count"] == 6
    assert row["recent_order_count"] == 2
    assert row["reference_observed_days"] == 90
    assert row["recent_observed_days"] == 30
    assert row["current_elapsed_gap_days"] == 5
    assert row["feature_version"] == "behavior-monitor-v1"
    assert row["history_sufficiency"] == "sufficient"


def test_short_history_is_not_treated_as_verified_reference_inactivity() -> None:
    cutoff = pd.Timestamp("2020-06-01")
    features = compute_behavior_features(
        _orders([(22, "one", "2020-05-12 12:00:00", 50.0)]),
        cutoff,
    )
    row = features.iloc[0]

    assert row["recent_observed_days"] == pytest.approx(19.5)
    assert row["reference_observed_days"] == 0
    assert pd.isna(row["purchase_rate_ratio"])
    assert pd.isna(row["revenue_rate_ratio"])
    assert pd.isna(row["median_completed_gap_days"])
    assert pd.isna(row["gap_deviation_score"])
    assert row["history_sufficiency"] == "insufficient"


def test_future_transactions_cannot_change_a_past_snapshot() -> None:
    cutoff = pd.Timestamp("2020-06-01")
    historical = _orders(
        [
            (33, "a", "2020-01-01", 30.0),
            (33, "b", "2020-02-01", 45.0),
            (33, "c", "2020-03-01", 50.0),
            (33, "d", "2020-05-01", 20.0),
        ]
    )
    future = _orders([(33, "future", "2020-07-01", 100_000.0)])
    baseline = compute_behavior_features(historical, cutoff)
    augmented = compute_behavior_features(
        pd.concat([historical, future], ignore_index=True),
        cutoff,
    )
    assert_frame_equal(baseline, augmented, check_dtype=False)


def test_exact_cutoff_timestamp_is_excluded_from_gap_and_snapshot() -> None:
    cutoff = pd.Timestamp("2020-06-01 00:00:00")
    events = prepare_purchase_events(
        _orders(
            [
                (9, "before", "2020-05-31 23:59:59", 12.0),
                (9, "boundary", "2020-06-01 00:00:00", 80.0),
            ]
        )
    )
    gaps = compute_completed_gaps(events, cutoff)
    snapshot = compute_behavior_features(events, cutoff)

    assert gaps.empty
    assert snapshot.iloc[0]["historical_order_count"] == 1
    assert snapshot.iloc[0]["current_elapsed_gap_days"] == pytest.approx(1 / 86_400)


def test_ewma_is_only_returned_when_both_periods_have_enough_completed_gaps() -> None:
    cutoff = pd.Timestamp("2021-01-01")
    days_before_cutoff = [
        300, 280, 260, 240, 220, 200, 180, 160, 140, 120, 100, 80,
        27, 20, 13, 6,
    ]
    rows = [
        (4, f"invoice-{index}", (cutoff - pd.Timedelta(days=days)).isoformat(), 10.0)
        for index, days in enumerate(days_before_cutoff)
    ]
    result = compute_ewma_features(_orders(rows), cutoff, BehaviorConfig(ewma_lambda=0.6))
    row = result.iloc[0]

    assert row["reference_ewma_gap_count"] >= 4
    assert row["recent_ewma_gap_count"] >= 4
    assert pd.notna(row["reference_ewma_gap_days"])
    assert pd.notna(row["recent_ewma_gap_days"])
    assert row["ewma_lambda"] == 0.6


def test_trajectory_is_compact_and_strictly_pre_cutoff() -> None:
    cutoff = pd.Timestamp("2020-12-01")
    events = _orders(
        [
            (8, "old", "2020-01-01", 25.0),
            (8, "recent", "2020-11-15", 75.0),
            (8, "cutoff", "2020-12-01", 500.0),
        ]
    )
    trajectory = build_behavior_trajectory(events, 8, cutoff)

    assert len(trajectory) <= 13
    assert trajectory["order_count"].sum() == 2
    assert trajectory["gross_revenue"].sum() == 100
    assert (trajectory["period_end"] <= cutoff).all()


def test_continuous_scores_do_not_create_unvalidated_alerts() -> None:
    features = compute_behavior_features(
        _orders(
            [
                (5, f"i{index}", f"2020-{month:02d}-01", float(index + 1))
                for index, month in enumerate((1, 2, 3, 4, 5))
            ]
        ),
        "2020-06-01",
    )
    scores = calculate_behavior_scores(
        features,
        {"feature_version": "behavior-monitor-v1", "ewma_lambda": 0.4},
    )

    assert scores.iloc[0]["policy_status"] == "continuous_indicators_only"
    assert "alert" not in " ".join(scores.columns).lower()
    assert scores.iloc[0]["available_indicator_count"] >= 1


def test_config_validates_windows_and_ewma_lambda() -> None:
    with pytest.raises(ValueError, match="recent_window_days"):
        BehaviorConfig(recent_window_days=0)
    with pytest.raises(ValueError, match="ewma_lambda"):
        BehaviorConfig(ewma_lambda=1.2)


def test_ranking_metrics_frozen_threshold_and_paired_bootstrap() -> None:
    outcomes = pd.Series([0, 1, 0, 1, 1, 0, 0, 1] * 20)
    risk = pd.Series([0.2, 0.8, 0.1, 0.7, 0.6, 0.3, 0.2, 0.9] * 20)
    baseline = pd.Series([0.5, 0.6, 0.4, 0.7, 0.5, 0.4, 0.3, 0.8] * 20)
    ids = pd.Series([f"customer-{i}" for i in range(len(outcomes))])
    metrics = evaluate_binary_risk(outcomes, risk)
    threshold_metrics = evaluate_frozen_alert_threshold(outcomes, risk, 0.6)
    bootstrap = paired_customer_bootstrap_difference(
        outcomes,
        risk,
        baseline,
        ids,
        n_resamples=100,
    )

    assert metrics["average_precision"] > 0.5
    assert metrics["budget_customer_count"] == 16
    assert 0 <= threshold_metrics["alert_coverage"] <= 1
    assert bootstrap["valid_resamples"] == 100
    assert bootstrap["customer_clusters"] == len(outcomes)


def test_invalid_order_contract_fails_explicitly() -> None:
    duplicate = _orders(
        [
            (4, "same", "2020-01-01", 10.0),
            (4, "same", "2020-01-02", 20.0),
        ]
    )
    with pytest.raises(ValueError, match="unique"):
        prepare_purchase_events(duplicate)
    with pytest.raises(ValueError, match="non-negative"):
        prepare_purchase_events(_orders([(4, "bad", "2020-01-01", -1.0)]))
