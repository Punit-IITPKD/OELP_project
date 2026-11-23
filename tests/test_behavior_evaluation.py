from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.behavior_evaluation import (
    predict_nonpurchase_probability,
    select_behavior_model,
)


def _cohort(size: int, seed: int) -> tuple[pd.DataFrame, np.ndarray]:
    rng = np.random.default_rng(seed)
    behavior = rng.normal(size=size)
    outcomes = (behavior + rng.normal(scale=0.8, size=size) > 0).astype(int)
    return (
        pd.DataFrame(
            {
                "gap_deviation_score": behavior,
                "unsupported_feature": np.nan,
            }
        ),
        outcomes,
    )


def test_validation_selects_only_train_supported_features_and_scores_probabilities() -> None:
    train, train_y = _cohort(160, 10)
    validation, validation_y = _cohort(100, 20)
    validation["unsupported_feature"] = 999.0

    selected = select_behavior_model(
        train,
        train_y,
        validation,
        validation_y,
        ("gap_deviation_score", "unsupported_feature"),
    )
    scores = predict_nonpurchase_probability(selected, validation)

    assert selected.feature_columns == ("gap_deviation_score",)
    assert selected.regularization_c in {0.1, 1.0, 10.0}
    assert len(scores) == len(validation)
    assert np.isfinite(scores).all()
    assert ((scores >= 0) & (scores <= 1)).all()


def test_model_selection_rejects_missing_features_and_single_class_roles() -> None:
    train, train_y = _cohort(80, 30)
    validation, validation_y = _cohort(60, 40)
    with pytest.raises(ValueError, match="missing"):
        select_behavior_model(
            train,
            train_y,
            validation,
            validation_y,
            ("not_a_feature",),
        )
    with pytest.raises(ValueError, match="both outcome classes"):
        select_behavior_model(
            train,
            np.zeros(len(train), dtype=int),
            validation,
            validation_y,
            ("gap_deviation_score",),
        )
