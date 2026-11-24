from __future__ import annotations

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.customer_trajectories import (
    TrajectoryConfig,
    build_customer_trajectory,
    build_customer_trajectory_matrix,
    calculate_trajectory_features,
    validate_trajectory_leakage,
)


def _orders(rows: list[tuple[int, str, str, float]]) -> pd.DataFrame:
    return pd.DataFrame(
        rows,
        columns=["Customer ID", "Invoice", "PurchaseDate", "GrossRevenue"],
    )


def test_matrix_respects_left_truncation_and_cutoff_boundary() -> None:
    events = _orders(
        [
            (10, "1001", "2020-02-20", 20.0),
            (10, "1002", "2020-03-05", 25.0),
            (10, "1003", "2020-04-01", 30.0),
            (10, "at-cutoff", "2020-04-15", 99_999.0),
            (22, "2001", "2020-03-01", 5.0),
        ]
    )

    matrix = build_customer_trajectory_matrix(
        events,
        cutoff_date="2020-04-15",
        window_days=30,
        lookback_days=90,
    )
    customer = matrix.loc[matrix["Customer ID"].eq(10)].set_index("window_index")
    later = matrix.loc[matrix["Customer ID"].eq(22)].set_index("window_index")

    assert customer.loc[0, "window_observation_status"] == "pre_observation"
    assert pd.isna(customer.loc[0, "purchase_count"])
    assert customer.loc[1, "purchase_count"] == 2
    assert customer.loc[2, "purchase_count"] == 1
    assert customer.loc[2, "gross_revenue"] == 30
    assert customer["pre_cutoff_purchase_count"].iloc[0] == 3
    assert later.loc[0, "window_observation_status"] == "pre_observation"
    assert later.loc[1, "window_observation_status"] == "partially_exposed"
    assert later.loc[1, "observed_exposure_days"] == pytest.approx(15)


def test_summary_features_report_history_support_and_completed_gaps() -> None:
    events = _orders(
        [
            (31, "3001", "2020-01-05", 10.0),
            (31, "3002", "2020-02-05", 20.0),
            (31, "3003", "2020-03-05", 30.0),
            (31, "3004", "2020-04-05", 40.0),
            (31, "3005", "2020-05-05", 50.0),
            (31, "3006", "2020-06-05", 60.0),
            (31, "3007", "2020-06-20", 70.0),
        ]
    )
    config = TrajectoryConfig(
        window_days=30,
        lookback_days=180,
        min_summary_observed_windows=4,
        min_summary_active_windows=2,
        min_functional_observed_windows=6,
        min_functional_active_windows=3,
    )
    matrix = build_customer_trajectory_matrix(
        events, "2020-07-01", window_days=30, lookback_days=180
    )
    features = calculate_trajectory_features(matrix, config).iloc[0]

    assert features["observed_windows"] == 6
    assert features["active_purchase_windows"] == 6
    assert features["completed_purchase_gaps"] == 6
    assert features["eligible_for_summary_trajectory"]
    assert features["eligible_for_functional_analysis"]


def test_future_rows_do_not_change_past_trajectory_or_features() -> None:
    cutoff = "2020-04-01"
    historical = _orders(
        [
            (42, "4001", "2020-01-03", 10.0),
            (42, "4002", "2020-01-20", 12.0),
            (42, "4003", "2020-02-15", 15.0),
            (42, "4004", "2020-03-16", 19.0),
        ]
    )
    extended = pd.concat(
        [
            historical,
            _orders([(42, "4005", "2020-05-15", 1_000_000.0)]),
        ],
        ignore_index=True,
    )

    result = validate_trajectory_leakage(
        historical,
        extended,
        cutoff,
        TrajectoryConfig(),
    )

    assert result == {
        "trajectory_matrix_unchanged": True,
        "trajectory_features_unchanged": True,
    }
    assert_frame_equal(
        build_customer_trajectory(42, historical, cutoff, TrajectoryConfig()),
        build_customer_trajectory(42, extended, cutoff, TrajectoryConfig()),
        check_dtype=False,
    )


def test_cutoff_must_be_timezone_naive_and_grid_aligned() -> None:
    events = _orders([(5, "5001", "2020-01-01", 10.0)])
    one_window = build_customer_trajectory_matrix(
        events, "2020-02-01", window_days=30, lookback_days=30
    )
    assert len(one_window) == 1
    with pytest.raises(ValueError, match="timezone-naive"):
        build_customer_trajectory_matrix(
            events, "2020-02-01T00:00:00+00:00", window_days=30, lookback_days=90
        )
    with pytest.raises(ValueError, match="multiple"):
        TrajectoryConfig(window_days=30, lookback_days=100)
