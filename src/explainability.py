"""Model-faithful explanations for the saved purchase and spending pipelines.

The module never fits or mutates a model. Logistic contributions are exact in
log-odds space; changes to cumulative probabilities and spending are explicitly
reported as single-input model sensitivities, not causal effects.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import pandas as pd
from scipy.special import expit

from src import purchase_clock as pc
from src import spending_model as sm

HORIZONS = (30, 60, 90)
RECONSTRUCTION_RTOL = 1e-10
RECONSTRUCTION_ATOL = 1e-12


def _one_customer(features: pd.DataFrame, *, name: str) -> pd.DataFrame:
    if not isinstance(features, pd.DataFrame) or len(features) != 1:
        raise ValueError(f"{name} must contain exactly one customer row.")
    if features.empty:
        raise ValueError(f"{name} cannot be empty.")
    return features.copy().reset_index(drop=True)


def _model_horizon(bundle: Mapping[str, Any], horizon_days: int) -> tuple[int, Mapping]:
    horizon = int(horizon_days)
    models = bundle.get("horizon_models", {})
    model = models.get(horizon, models.get(str(horizon)))
    if horizon not in HORIZONS or not isinstance(model, Mapping):
        raise ValueError(f"No saved personalized spending model for {horizon} days.")
    return horizon, model


def _raw_value(value: Any) -> Any:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def inspect_fitted_purchase_model(purchase_bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Describe the saved purchase model and its fitted transformations."""
    pipeline = purchase_bundle.get("personalized_pipeline")
    if pipeline is None or not hasattr(pipeline, "named_steps"):
        raise ValueError("Purchase bundle has no fitted personalized pipeline.")
    estimator = pipeline.named_steps.get("model")
    preprocessor = pipeline.named_steps.get("preprocess")
    if estimator is None or preprocessor is None or not hasattr(estimator, "coef_"):
        raise ValueError("Saved purchase pipeline does not support exact coefficients.")
    feature_names = preprocessor.get_feature_names_out().tolist()
    return {
        "model_version": purchase_bundle.get("metadata", {}).get("model_version"),
        "estimator": type(estimator).__name__,
        "preprocessing_steps": [
            {"name": name, "class": type(step).__name__}
            for name, step in pipeline.steps
        ],
        "numeric_predictors": list(pc.NUMERIC_FEATURES),
        "categorical_predictors": list(pc.CATEGORICAL_FEATURES),
        "transformed_feature_names": feature_names,
        "coefficient_count": int(np.asarray(estimator.coef_).shape[-1]),
        "coefficient_decomposition_supported": bool(
            np.asarray(estimator.coef_).ndim == 2
            and np.asarray(estimator.coef_).shape[0] == 1
            and len(feature_names) == np.asarray(estimator.coef_).shape[1]
        ),
        "training_cutoff": purchase_bundle.get("metadata", {}).get("training_cutoff"),
    }


def explain_interval_hazard(
    purchase_bundle: Mapping[str, Any],
    customer_features: pd.DataFrame,
    interval_days: int,
) -> dict[str, Any]:
    """Reconstruct one fitted logistic interval hazard and its exact logit terms."""
    interval = int(interval_days)
    if interval < pc.INTERVAL_DAYS or interval > 90 or interval % pc.INTERVAL_DAYS:
        raise ValueError("interval_days must be a 10-day interval from 10 through 90.")
    customer = _one_customer(customer_features, name="customer_features")
    prepared = pc._apply_bundle_segmentation(purchase_bundle, customer)
    expanded = pc._expand_person_period_features(prepared)
    selected = expanded.loc[
        expanded[pc.INTERVAL_COL].astype(str).eq(str(interval // pc.INTERVAL_DAYS))
    ]
    if len(selected) != 1:
        raise AssertionError("Expected one expanded row for the selected interval.")
    matrix = pc._model_matrix(selected)

    pipeline = purchase_bundle["personalized_pipeline"]
    preprocessor = pipeline.named_steps["preprocess"]
    estimator = pipeline.named_steps["model"]
    transformed = np.asarray(preprocessor.transform(matrix), dtype=float)
    coefficients = np.asarray(estimator.coef_, dtype=float)
    intercepts = np.asarray(estimator.intercept_, dtype=float)
    if coefficients.shape != (1, transformed.shape[1]) or intercepts.size != 1:
        raise ValueError("The fitted purchase estimator is not binary logistic regression.")

    names = preprocessor.get_feature_names_out().tolist()
    contributions = transformed[0] * coefficients[0]
    reconstructed_logit = float(intercepts[0] + contributions.sum())
    reconstructed_hazard = float(expit(reconstructed_logit))
    fitted_hazard = float(estimator.predict_proba(transformed)[0, 1])
    if not np.isclose(
        reconstructed_hazard,
        fitted_hazard,
        rtol=RECONSTRUCTION_RTOL,
        atol=RECONSTRUCTION_ATOL,
    ):
        raise AssertionError("Logistic hazard decomposition does not match saved inference.")

    raw_row = prepared.iloc[0]
    feature_terms = []
    for name, value, coefficient, contribution in zip(
        names, transformed[0], coefficients[0], contributions, strict=True
    ):
        source_name = name.split("__", 1)[-1]
        feature_terms.append(
            {
                "transformed_feature": name,
                "model_feature": source_name,
                "transformed_value": float(value),
                "coefficient": float(coefficient),
                "logit_contribution": float(contribution),
            }
        )
    feature_terms.sort(key=lambda term: abs(term["logit_contribution"]), reverse=True)
    return {
        "interval_days": interval,
        "customer_id": int(raw_row[pc.CUSTOMER_ID]),
        "input_cutoff": pd.Timestamp(raw_row[pc.CUTOFF_COL]).date().isoformat(),
        "logit_intercept": float(intercepts[0]),
        "reconstructed_logit": reconstructed_logit,
        "predicted_hazard": fitted_hazard,
        "reconstructed_hazard": reconstructed_hazard,
        "reconstruction_tolerance": {
            "rtol": RECONSTRUCTION_RTOL,
            "atol": RECONSTRUCTION_ATOL,
        },
        "feature_contributions": feature_terms,
    }


def _decompose_prepared_hazards(
    purchase_bundle: Mapping[str, Any],
    prepared_features: pd.DataFrame,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """Transform all interval rows once and return exact hazards and logit terms."""
    expanded = pc._expand_person_period_features(prepared_features)
    matrix = pc._model_matrix(expanded)
    pipeline = purchase_bundle["personalized_pipeline"]
    preprocessor = pipeline.named_steps["preprocess"]
    estimator = pipeline.named_steps["model"]
    transformed = np.asarray(preprocessor.transform(matrix), dtype=float)
    coefficients = np.asarray(estimator.coef_, dtype=float)
    intercepts = np.asarray(estimator.intercept_, dtype=float)
    if coefficients.shape != (1, transformed.shape[1]) or intercepts.size != 1:
        raise ValueError("The fitted purchase estimator is not binary logistic regression.")
    names = preprocessor.get_feature_names_out().tolist()
    contributions = transformed * coefficients[0]
    logits = intercepts[0] + contributions.sum(axis=1)
    reconstructed_hazards = expit(logits)
    fitted_hazards = estimator.predict_proba(transformed)[:, 1]
    if not np.allclose(
        reconstructed_hazards,
        fitted_hazards,
        rtol=RECONSTRUCTION_RTOL,
        atol=RECONSTRUCTION_ATOL,
    ):
        raise AssertionError("Batched logistic decomposition differs from fitted inference.")

    details: list[dict[str, Any]] = []
    for index, row in expanded.reset_index(drop=True).iterrows():
        interval_day = int(row[pc.INTERVAL_COL]) * pc.INTERVAL_DAYS
        terms = [
            {
                "transformed_feature": name,
                "model_feature": name.split("__", 1)[-1],
                "transformed_value": float(transformed[index, feature_index]),
                "coefficient": float(coefficients[0, feature_index]),
                "logit_contribution": float(contributions[index, feature_index]),
            }
            for feature_index, name in enumerate(names)
        ]
        terms.sort(key=lambda term: abs(term["logit_contribution"]), reverse=True)
        details.append(
            {
                "interval_days": interval_day,
                "customer_id": int(row[pc.CUSTOMER_ID]),
                "input_cutoff": pd.Timestamp(row[pc.CUTOFF_COL]).date().isoformat(),
                "logit_intercept": float(intercepts[0]),
                "reconstructed_logit": float(logits[index]),
                "predicted_hazard": float(fitted_hazards[index]),
                "reconstructed_hazard": float(reconstructed_hazards[index]),
                "reconstruction_tolerance": {
                    "rtol": RECONSTRUCTION_RTOL,
                    "atol": RECONSTRUCTION_ATOL,
                },
                "feature_contributions": terms,
            }
        )
    return fitted_hazards.reshape(len(prepared_features), 9), details


def compute_cumulative_purchase_probability(
    interval_hazards: Sequence[float] | np.ndarray,
    horizon_days: int | Sequence[int],
) -> float | dict[int, float]:
    """Reconstruct cumulative return probability from ordered 10-day hazards."""
    hazards = np.asarray(interval_hazards, dtype=float)
    if hazards.ndim != 1 or hazards.size != 9:
        raise ValueError("interval_hazards must be a one-dimensional 9-interval curve.")
    if not np.isfinite(hazards).all() or ((hazards < 0) | (hazards > 1)).any():
        raise ValueError("All interval hazards must be finite probabilities in [0, 1].")
    requested = (int(horizon_days),) if isinstance(horizon_days, (int, np.integer)) else tuple(
        int(day) for day in horizon_days
    )
    if not requested or any(day not in HORIZONS for day in requested):
        raise ValueError("horizon_days must contain supported values 30, 60, or 90.")
    survival = np.cumprod(1.0 - hazards)
    values = {
        day: float(1.0 - survival[day // pc.INTERVAL_DAYS - 1])
        for day in requested
    }
    return values[requested[0]] if isinstance(horizon_days, (int, np.integer)) else values


def _reference_value(reference_profile: Mapping[str, Any], feature: str) -> Any:
    if feature not in reference_profile:
        raise ValueError(f"Reference profile is missing model feature {feature!r}.")
    return reference_profile[feature]


def explain_cumulative_probability(
    purchase_bundle: Mapping[str, Any],
    customer_features: pd.DataFrame,
    reference_profile: Mapping[str, Any],
    horizons: Sequence[int] = HORIZONS,
) -> dict[str, Any]:
    """Compare fitted probabilities with TRAIN-reference single-input sensitivities."""
    customer = _one_customer(customer_features, name="customer_features")
    supported = tuple(int(day) for day in horizons)
    if not supported or any(day not in HORIZONS for day in supported):
        raise ValueError("horizons must be selected from 30, 60, and 90 days.")
    prepared = pc._apply_bundle_segmentation(purchase_bundle, customer)
    original_hazard_matrix, interval_details = _decompose_prepared_hazards(
        purchase_bundle, prepared
    )
    original_hazards = original_hazard_matrix[0]
    original_probabilities = compute_cumulative_purchase_probability(
        original_hazards, supported
    )

    input_features = [*pc.NUMERIC_FEATURES, "Hist_Segment"]
    variants: list[pd.DataFrame] = []
    variant_features: list[str] = []
    values: dict[str, Any] = {}
    customer_id = int(prepared.iloc[0][pc.CUSTOMER_ID])
    combined_reference = prepared.copy()
    for feature in input_features:
        if feature in combined_reference:
            combined_reference[feature] = _reference_value(reference_profile, feature)
    combined_reference[pc.CUSTOMER_ID] = customer_id + 999_999_999
    variants.append(combined_reference)
    variant_features.append("__combined_reference_profile__")
    for index, feature in enumerate(input_features):
        if feature not in prepared:
            continue
        value = _reference_value(reference_profile, feature)
        values[feature] = _raw_value(value)
        variant = prepared.copy()
        variant[feature] = value
        # The model uses no ID feature; unique synthetic keys keep row validation
        # and the customer alignment explicit while batching all perturbations.
        variant[pc.CUSTOMER_ID] = customer_id + index + 1_000_000_000
        variants.append(variant)
        variant_features.append(feature)

    effects = []
    if variants:
        batch = pd.concat(variants, ignore_index=True)
        batch_hazard_matrix, _ = _decompose_prepared_hazards(purchase_bundle, batch)
        # Matrix operations keep the perturbation pass vectorized across features.
        survival = np.cumprod(1.0 - batch_hazard_matrix, axis=1)
        probability_matrix = 1.0 - survival
        for index, feature in enumerate(variant_features[1:], start=1):
            effects.append(
                {
                    "feature": feature,
                    "original_value": _raw_value(prepared.iloc[0][feature]),
                    "reference_value": values[feature],
                    "effect_direction": "original minus reference-replacement probability",
                    "reference_probabilities": {
                        str(day): float(probability_matrix[
                            index, day // pc.INTERVAL_DAYS - 1
                        ])
                        for day in supported
                    },
                    "probability_effects": {
                        str(day): float(
                            original_probabilities[day]
                            - probability_matrix[
                                index, day // pc.INTERVAL_DAYS - 1
                            ]
                        )
                        for day in supported
                    },
                }
            )
    effects.sort(
        key=lambda item: max(
            abs(value) for value in item["probability_effects"].values()
        ),
        reverse=True,
    )
    return {
        "customer_id": customer_id,
        "cutoff_date": pd.Timestamp(prepared.iloc[0][pc.CUTOFF_COL]).date().isoformat(),
        "purchase_probabilities": {
            str(day): float(original_probabilities[day]) for day in supported
        },
        "reference_profile_probabilities": {
            str(day): float(
                probability_matrix[0, day // pc.INTERVAL_DAYS - 1]
            )
            for day in supported
        },
        "interval_hazards": [float(value) for value in original_hazards],
        "interval_decompositions": interval_details,
        "reference_profile_definition": reference_profile.get(
            "_definition", "TRAIN-only medians for numeric inputs and TRAIN mode for categories."
        ),
        "method": "single-input model sensitivity against a TRAIN-derived reference",
        "limitations": [
            "Feature changes are model-input substitutions, not causal interventions.",
            "Changing one derived feature at a time can create an unrealistic feature combination.",
            "Historical features and fitted segment membership are not direct customer controls.",
        ],
        "feature_effects": effects,
    }


def explain_customer_purchase_clock(
    purchase_bundle: Mapping[str, Any],
    customer_features: pd.DataFrame,
    reference_profile: Mapping[str, Any],
) -> dict[str, Any]:
    """Return model-backed P30/P60/P90, exact hazards, and reference sensitivities."""
    customer = _one_customer(customer_features, name="customer_features")
    prepared = pc._apply_bundle_segmentation(purchase_bundle, customer)
    cumulative = explain_cumulative_probability(
        purchase_bundle, customer, reference_profile, HORIZONS
    )
    return {
        "customer_id": int(customer.iloc[0][pc.CUSTOMER_ID]),
        "cutoff_date": pd.Timestamp(customer.iloc[0][pc.CUTOFF_COL]).date().isoformat(),
        "model_version": purchase_bundle.get("metadata", {}).get("model_version"),
        "model_input": {
            feature: _raw_value(prepared.iloc[0][feature])
            for feature in [*pc.NUMERIC_FEATURES, "Hist_Segment"]
            if feature in prepared
        },
        "purchase_probabilities": cumulative["purchase_probabilities"],
        "reference_profile_probabilities": cumulative[
            "reference_profile_probabilities"
        ],
        "interval_hazards": cumulative["interval_hazards"],
        "cumulative_probability_reconstruction": cumulative["purchase_probabilities"],
        "explanation_method": cumulative["method"],
        "feature_effects": cumulative["feature_effects"],
        "interval_decompositions": cumulative["interval_decompositions"],
        "model_input_limitations": cumulative["limitations"],
        "reconstruction_tolerance": {
            "rtol": RECONSTRUCTION_RTOL,
            "atol": RECONSTRUCTION_ATOL,
        },
    }


def _spending_feature_names(preprocessor: Any) -> list[str]:
    """Recover fitted transformed-column names even for the legacy log transformer."""
    names: list[str] = []
    for transformer_name, transformer, columns in preprocessor.transformers_:
        if transformer == "drop":
            continue
        source_columns = list(columns) if not isinstance(columns, slice) else []
        if hasattr(transformer, "named_steps"):
            steps = transformer.named_steps
            encoder = steps.get("onehot")
            imputer = steps.get("imputer")
            if encoder is not None:
                transformed_names = encoder.get_feature_names_out(source_columns).tolist()
            elif imputer is not None:
                transformed_names = imputer.get_feature_names_out(source_columns).tolist()
            else:
                transformed_names = source_columns
        elif hasattr(transformer, "get_feature_names_out"):
            transformed_names = transformer.get_feature_names_out(source_columns).tolist()
        else:
            transformed_names = source_columns
        names.extend(f"{transformer_name}__{name}" for name in transformed_names)
    return names


def inspect_spending_model(
    spending_bundle: Mapping[str, Any],
    horizon_days: int,
) -> dict[str, Any]:
    """Describe the saved horizon-specific Ridge model and retransformation."""
    horizon, model = _model_horizon(spending_bundle, horizon_days)
    personalized = model.get("personalized_conditional")
    if not isinstance(personalized, Mapping):
        raise ValueError(f"Saved {horizon}-day model has no personalized conditional pipeline.")
    pipeline = personalized.get("pipeline")
    if pipeline is None or not hasattr(pipeline, "named_steps"):
        raise ValueError("Saved personalized spending pipeline is unavailable.")
    estimator = pipeline.named_steps.get("ridge")
    preprocessor = pipeline.named_steps.get("preprocess")
    if estimator is None or preprocessor is None or not hasattr(estimator, "coef_"):
        raise ValueError("Saved spending pipeline does not support a Ridge decomposition.")
    names = _spending_feature_names(preprocessor)
    coefficients = np.asarray(estimator.coef_, dtype=float).reshape(-1)
    if len(names) != len(coefficients):
        raise ValueError("Could not align fitted spending coefficients with transformed features.")
    return {
        "model_version": spending_bundle.get("metadata", {}).get("model_version"),
        "horizon_days": horizon,
        "estimator": type(estimator).__name__,
        "preprocessing_steps": [
            {"name": name, "class": type(step).__name__}
            for name, step in pipeline.steps
        ],
        "transformed_feature_names": names,
        "coefficient_count": int(len(coefficients)),
        "alpha": float(personalized["alpha"]),
        "smearing_factor": float(personalized["smearing_factor"]),
        "retransformation": str(personalized["retransformation"]),
    }


def explain_conditional_spending(
    spending_bundle: Mapping[str, Any],
    customer_features: pd.DataFrame,
    horizon_days: int,
    reference_profile: Mapping[str, Any],
) -> dict[str, Any]:
    """Explain one saved Ridge score in log space and its exact retransformation."""
    customer = _one_customer(customer_features, name="customer_features")
    horizon, model = _model_horizon(spending_bundle, horizon_days)
    segmented = sm.apply_spending_segmentation(
        spending_bundle, customer, horizon
    )
    model_input = sm.validate_features(segmented, require_segment=True)
    personalized = model["personalized_conditional"]
    pipeline = personalized["pipeline"]
    preprocessor = pipeline.named_steps["preprocess"]
    estimator = pipeline.named_steps["ridge"]
    transformed = np.asarray(preprocessor.transform(model_input), dtype=float)
    coefficients = np.asarray(estimator.coef_, dtype=float).reshape(-1)
    names = _spending_feature_names(preprocessor)
    if transformed.shape != (1, len(coefficients)) or len(names) != len(coefficients):
        raise ValueError("Fitted spending feature matrix and coefficients do not align.")

    log_contributions = transformed[0] * coefficients
    reconstructed_log_score = float(
        float(np.asarray(estimator.intercept_).reshape(-1)[0])
        + log_contributions.sum()
    )
    fitted_log_score = float(pipeline.predict(model_input)[0])
    if not np.isclose(
        reconstructed_log_score,
        fitted_log_score,
        rtol=RECONSTRUCTION_RTOL,
        atol=RECONSTRUCTION_ATOL,
    ):
        raise AssertionError("Ridge score decomposition does not match saved inference.")
    smear = float(personalized["smearing_factor"])
    conditional_spending = float(sm._inverse_log_mean(np.array([fitted_log_score]), smear)[0])
    model_features = [*sm.NUMERIC_FEATURES, "Hist_Segment"]
    variants: list[pd.DataFrame] = []
    changed_features: list[str] = []
    for index, feature in enumerate(model_features):
        if feature not in model_input:
            continue
        if feature not in reference_profile:
            raise ValueError(f"Spending reference profile is missing {feature!r}.")
        variant = model_input.copy()
        variant[feature] = reference_profile[feature]
        variant[sm.CUSTOMER_ID] = int(model_input.iloc[0][sm.CUSTOMER_ID]) + index + 1_000_000_000
        variants.append(variant)
        changed_features.append(feature)

    reference_effects = []
    if variants:
        batch = pd.concat(variants, ignore_index=True)
        reference_scores = np.asarray(pipeline.predict(batch), dtype=float)
        reference_amounts = sm._inverse_log_mean(reference_scores, smear)
        for index, feature in enumerate(changed_features):
            reference_effects.append(
                {
                    "feature": feature,
                    "reference_value": _raw_value(reference_profile[feature]),
                    "log_score_difference": float(
                        fitted_log_score - reference_scores[index]
                    ),
                    "conditional_spending_difference": float(
                        conditional_spending - reference_amounts[index]
                    ),
                    "effect_direction": "original minus reference-replacement estimate",
                }
            )
    reference_effects.sort(
        key=lambda item: abs(item["conditional_spending_difference"]),
        reverse=True,
    )

    contributions = [
        {
            "transformed_feature": name,
            "model_feature": name.split("__", 1)[-1],
            "transformed_value": float(value),
            "coefficient": float(coefficient),
            "log_score_contribution": float(contribution),
        }
        for name, value, coefficient, contribution in zip(
            names, transformed[0], coefficients, log_contributions, strict=True
        )
    ]
    contributions.sort(key=lambda item: abs(item["log_score_contribution"]), reverse=True)
    return {
        "customer_id": int(model_input.iloc[0][sm.CUSTOMER_ID]),
        "cutoff_date": pd.Timestamp(model_input.iloc[0][sm.CUTOFF_COL]).date().isoformat(),
        "horizon_days": horizon,
        "spending_model_version": spending_bundle.get("metadata", {}).get("model_version"),
        "model_input": {
            feature: _raw_value(model_input.iloc[0][feature])
            for feature in [*sm.NUMERIC_FEATURES, "Hist_Segment"]
            if feature in model_input
        },
        "log_score": fitted_log_score,
        "log_score_intercept": float(np.asarray(estimator.intercept_).reshape(-1)[0]),
        "log_score_contributions": contributions,
        "smearing_factor": smear,
        "retransformation_method": str(personalized["retransformation"]),
        "conditional_expected_spending": conditional_spending,
        "reference_sensitivities": reference_effects,
        "limitations": [
            "Ridge contributions are additive in the fitted log1p target space, not in pounds.",
            "The saved smearing correction and clipping are applied after the log-space score.",
            "Single-input substitutions are model sensitivities, not causal effects.",
        ],
    }


def decompose_expected_revenue(
    purchase_probability: float,
    conditional_expected_spending: float,
    saved_expected_revenue: float,
) -> dict[str, float]:
    """Validate the existing two-stage product without inferring spending by division."""
    probability = float(purchase_probability)
    conditional = float(conditional_expected_spending)
    saved = float(saved_expected_revenue)
    values = np.asarray([probability, conditional, saved], dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Expected-revenue decomposition requires finite values.")
    if not 0.0 <= probability <= 1.0 or conditional < 0.0 or saved < 0.0:
        raise ValueError("Expected-revenue inputs are outside their supported ranges.")
    reconstructed = probability * conditional
    if not np.isclose(
        reconstructed,
        saved,
        rtol=RECONSTRUCTION_RTOL,
        atol=RECONSTRUCTION_ATOL,
    ):
        raise AssertionError("Two-stage revenue product differs from saved inference.")
    return {
        "purchase_probability": probability,
        "conditional_expected_spending": conditional,
        "personalized_expected_revenue": saved,
        "reconstructed_expected_revenue": reconstructed,
    }
