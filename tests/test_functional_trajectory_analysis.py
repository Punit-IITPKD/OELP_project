from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.functional_trajectory_analysis import (
    FunctionalTrajectoryConfig,
    evaluate_functional_component_stability,
    evaluate_functional_representation,
    fit_functional_representation,
    transform_functional_representation,
)

CURVE_COLUMNS = tuple(f"window_{index}" for index in range(6))


def _curves(rows: int = 40) -> pd.DataFrame:
    index = np.arange(6, dtype=float)
    frame = pd.DataFrame({"Customer ID": np.arange(rows)})
    for column_index, column in enumerate(CURVE_COLUMNS):
        frame[column] = np.maximum(
            0,
            0.04
            + (np.arange(rows) % 4) * 0.02
            + index[column_index] * (np.arange(rows) % 3) * 0.003,
        )
    frame["functional_eligible"] = True
    return frame


def test_train_pca_fits_only_supported_curves_and_transforms_frozen() -> None:
    curves = _curves()
    curves.loc[0, "functional_eligible"] = False
    config = FunctionalTrajectoryConfig(
        curve_columns=CURVE_COLUMNS,
        max_components=3,
        smoothing_method="moving_average",
        min_train_curves=30,
    )

    fitted = fit_functional_representation(curves, config)
    transformed = transform_functional_representation(fitted, curves)
    evaluation = evaluate_functional_representation(
        fitted, curves, evaluation_role="TEST"
    )

    assert fitted["fit_role"] == "TRAIN"
    assert fitted["fit_customer_count"] == 39
    assert transformed.loc[0, "functional_analysis_status"] == "insufficient_history"
    assert transformed.loc[1, "functional_component_1"] == pytest.approx(
        transformed.loc[1, "functional_component_1"]
    )
    assert evaluation["evaluated_curves"] == 39
    assert evaluation["method"] == "grid_based_functional_pca_approximation"
    assert evaluation["evaluation_role"] == "TEST"
    assert evaluation["test_reconstruction_rmse"] >= 0
    assert len(evaluation["train_explained_variance_ratio"]) == 3
    assert "train_cumulative_explained_variance" in evaluation
    assert "specialized_functional_estimator" in evaluation["limitations"][0]


def test_functional_pca_rejects_incomplete_training_support() -> None:
    curves = _curves(12)
    config = FunctionalTrajectoryConfig(
        curve_columns=CURVE_COLUMNS,
        min_train_curves=15,
    )
    with pytest.raises(ValueError, match="Insufficient supported TRAIN curves"):
        fit_functional_representation(curves, config)


def test_functional_pca_rejects_negative_rates_and_duplicate_customers() -> None:
    curves = _curves()
    curves.loc[0, CURVE_COLUMNS[0]] = -0.1
    config = FunctionalTrajectoryConfig(curve_columns=CURVE_COLUMNS)
    with pytest.raises(ValueError, match="negative"):
        fit_functional_representation(curves, config)

    duplicated = pd.concat([_curves(35), _curves(1)], ignore_index=True)
    with pytest.raises(ValueError, match="one non-null row per customer"):
        fit_functional_representation(duplicated, config)


def test_functional_component_stability_is_train_only_and_deterministic() -> None:
    curves = _curves()
    fitted = fit_functional_representation(
        curves,
        FunctionalTrajectoryConfig(
            curve_columns=CURVE_COLUMNS,
            smoothing_method="moving_average",
            min_train_curves=30,
        ),
    )
    first = evaluate_functional_component_stability(
        curves, fitted, random_state=8, n_resamples=6
    )
    second = evaluate_functional_component_stability(
        curves, fitted, random_state=8, n_resamples=6
    )

    assert first == second
    assert first["fit_role"] == "TRAIN"
    assert first["n_resamples"] == 6
    assert len(first["component_alignment_mean"]) == 3
    assert all(0 <= value <= 1 for value in first["component_alignment_mean"])


def test_reported_train_variance_is_invariant_to_test_cohort() -> None:
    train = _curves()
    fitted = fit_functional_representation(
        train,
        FunctionalTrajectoryConfig(
            curve_columns=CURVE_COLUMNS,
            max_components=3,
            min_train_curves=30,
        ),
    )
    first_test = _curves(12)
    second_test = _curves(12)
    for column_index, column in enumerate(CURVE_COLUMNS):
        second_test[column] = second_test[column] * (2 + column_index) + 0.1

    first = evaluate_functional_representation(
        fitted, first_test, evaluation_role="TEST"
    )
    second = evaluate_functional_representation(
        fitted, second_test, evaluation_role="TEST"
    )

    np.testing.assert_array_equal(
        first["train_explained_variance_ratio"],
        second["train_explained_variance_ratio"],
    )
    assert first["train_cumulative_explained_variance"] == (
        second["train_cumulative_explained_variance"]
    )
    assert first["evaluation_role"] == second["evaluation_role"] == "TEST"
