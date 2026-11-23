"""Leakage-aware retention-ranking, exposure, and scenario research utilities."""

from __future__ import annotations

import json
import platform
import time
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
import sklearn

from src import purchase_clock as pc
from src import temporal_framework as tf
from src.behavior_monitor import (
    BehaviorConfig,
    calculate_behavior_scores,
    compute_behavior_features,
    prepare_purchase_events,
)
from src.customer_intelligence import CustomerIntelligence
from src.forecast_application import build_forecast_snapshot
from src.retention_planner import (
    EligibilityPolicy,
    RANKING_STRATEGIES,
    RetentionScenario,
    allocate_contact_budget,
    rank_retention_candidates,
)
from src.revenue_exposure import (
    RevenueExposureConfig,
    calculate_exposure_concentration,
    calculate_opportunity_proxy,
    calculate_reference_exposure,
    compute_forecast_disagreement,
    prepare_revenue_forecast_table,
    summarize_portfolio_exposure,
)

TEST_CUTOFF = pd.Timestamp("2010-09-10")
HORIZONS = (30, 60, 90)
TOP_FRACTIONS = (0.01, 0.05, 0.10, 0.20)
DEFAULT_RESAMPLES = 500
DEFAULT_SEED = 20261125
HIGH_VALUE_QUANTILE = 0.75
SCREENING_POLICY_VERSION = "retention-screening-v1"
TARGET_PREFIXES = ("Purchased_", "FutureRevenue_", "FutureOrders_")


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, pd.DataFrame):
        return _json_safe(value.to_dict(orient="records"))
    if isinstance(value, pd.Series):
        return _json_safe(value.to_dict())
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(_json_safe(payload), indent=2, allow_nan=False, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _require_unique(frame: pd.DataFrame, keys: list[str], *, name: str) -> None:
    missing = [column for column in keys if column not in frame]
    if missing:
        raise ValueError(f"{name} is missing key columns: {missing}")
    if frame[keys].isna().any().any():
        raise ValueError(f"{name} has missing values in keys {keys}.")
    if frame.duplicated(keys).any():
        raise ValueError(f"{name} has duplicate rows for keys {keys}.")


def _ordered_scores(
    customer_table: pd.DataFrame,
    strategies: Sequence[str] = RANKING_STRATEGIES,
) -> dict[str, pd.DataFrame]:
    """Precompute each full ranking once and reuse it across budgets."""
    rankings = {}
    for strategy in strategies:
        rankings[strategy] = rank_retention_candidates(customer_table, strategy)
    return rankings


def _selected_metrics(
    ordered_ids: Sequence[int],
    outcomes: pd.DataFrame,
    fraction: float,
) -> dict[str, Any]:
    if not np.isfinite(fraction) or not 0 <= fraction <= 1:
        raise ValueError("budget_fraction must be within [0, 1].")
    outcome_columns = ["customer_id", "purchased"]
    missing = [column for column in outcome_columns if column not in outcomes]
    if missing:
        raise ValueError(f"observed_outcomes is missing columns: {missing}")
    _require_unique(outcomes, ["customer_id"], name="observed_outcomes")
    if outcomes["purchased"].isna().any():
        raise ValueError("Observed purchase outcomes cannot be missing.")
    if not outcomes["purchased"].isin([0, 1, False, True]).all():
        raise ValueError("purchased must be a binary outcome.")
    count = int(np.ceil(len(ordered_ids) * fraction)) if fraction else 0
    count = min(count, len(ordered_ids))
    selected = [int(customer_id) for customer_id in list(ordered_ids)[:count]]
    if selected:
        selected_outcomes = outcomes.set_index("customer_id").loc[selected, "purchased"]
        nonpurchase = 1 - selected_outcomes.astype(float).to_numpy()
        selected_nonpurchase_rate = float(nonpurchase.mean())
        selected_purchase_rate = float(1.0 - selected_nonpurchase_rate)
    else:
        nonpurchase = np.empty(0)
        selected_nonpurchase_rate = None
        selected_purchase_rate = None
    all_nonpurchases = int((1 - outcomes["purchased"].astype(int)).sum())
    captured_nonpurchases = int(nonpurchase.sum())
    return {
        "budget_fraction": float(fraction),
        "eligible_customers": len(ordered_ids),
        "selected_customers": count,
        "selected_customer_ids": selected,
        "future_nonpurchase_rate": selected_nonpurchase_rate,
        "future_purchase_rate": selected_purchase_rate,
        "nonpurchase_capture_rate": (
            captured_nonpurchases / all_nonpurchases
            if all_nonpurchases
            else None
        ),
        "observable_nonpurchase_count": captured_nonpurchases,
        "status": "evaluated" if count else "no_customers_selected",
    }


def evaluate_ranking_at_budget(
    customer_scores: pd.DataFrame,
    observed_outcomes: pd.DataFrame,
    budget_fraction: float,
) -> dict[str, Any]:
    """Measure observable outcomes among the top-ranked budget share.

    Scores and outcomes are joined only after ranking order is fixed. Results
    describe historical selection, not intervention response.
    """
    if "customer_id" not in customer_scores:
        raise ValueError("customer_scores must include customer_id.")
    _require_unique(customer_scores, ["customer_id"], name="customer_scores")
    if "priority_rank" in customer_scores:
        order = customer_scores.sort_values(
            ["priority_rank", "customer_id"], kind="mergesort"
        )
    elif "priority_score" in customer_scores:
        order = customer_scores.sort_values(
            ["priority_score", "customer_id"],
            ascending=[False, True],
            kind="mergesort",
        )
    else:
        raise ValueError("customer_scores must include priority_rank or priority_score.")
    _require_unique(observed_outcomes, ["customer_id"], name="observed_outcomes")
    score_ids = set(customer_scores["customer_id"].astype(int))
    outcome_ids = set(observed_outcomes["customer_id"].astype(int))
    if score_ids != outcome_ids:
        raise ValueError(
            "Ranked customers and observed outcomes must match exactly; "
            f"scores_only={len(score_ids - outcome_ids)}, "
            f"outcomes_only={len(outcome_ids - score_ids)}."
        )
    result = _selected_metrics(
        order["customer_id"].astype(int).tolist(),
        observed_outcomes,
        budget_fraction,
    )
    if "ranking_strategy" in customer_scores and len(customer_scores):
        result["ranking_strategy"] = str(customer_scores["ranking_strategy"].iloc[0])
    result.pop("selected_customer_ids", None)
    return result


def compare_ranking_baselines(
    validation_cohort: pd.DataFrame | None,
    test_cohort: pd.DataFrame,
    ranking_policies: Mapping[str, Mapping[str, pd.DataFrame]],
    *,
    budget_fractions: Sequence[float] = TOP_FRACTIONS,
    selection_fraction: float = 0.10,
) -> dict[str, Any]:
    """Select a pre-specified method on validation, then evaluate frozen TEST.

    ``ranking_policies`` maps strategy names to their validation and TEST
    precomputed orderings. Each cohort has separate outcomes and a
    TRAIN-thresholded ``historically_valuable`` indicator. For a horizon with
    no prospective validation cohort, no TEST-selected winner is reported.
    """
    _require_unique(test_cohort, ["customer_id"], name="test_cohort")
    if "purchased" not in test_cohort:
        raise ValueError("test_cohort requires a retrospective purchased outcome.")
    if not 0 < selection_fraction <= 1:
        raise ValueError("selection_fraction must be in (0, 1].")
    if not ranking_policies:
        raise ValueError("At least one ranking policy is required.")
    unknown = sorted(set(ranking_policies).difference(RANKING_STRATEGIES))
    if unknown:
        raise ValueError(f"Unsupported ranking policies: {unknown}")

    test_outcomes = test_cohort[["customer_id", "purchased"]].copy()
    test_valuable = (
        test_cohort.loc[test_cohort["historically_valuable"], "customer_id"]
        .astype(int)
        .tolist()
        if "historically_valuable" in test_cohort
        else []
    )
    comparisons: list[dict[str, Any]] = []
    validation_results: list[dict[str, Any]] = []
    test_results: list[dict[str, Any]] = []
    test_high_value_results: list[dict[str, Any]] = []
    for strategy, cohorts in ranking_policies.items():
        if "test" not in cohorts:
            raise ValueError(f"{strategy} is missing its TEST ranking.")
        test_ranking = cohorts["test"]
        _require_unique(test_ranking, ["customer_id"], name=f"{strategy} TEST ranking")
        if set(test_ranking["customer_id"].astype(int)) != set(
            test_cohort["customer_id"].astype(int)
        ):
            raise ValueError(f"{strategy} TEST ranking cohort does not match outcomes.")
        for fraction in budget_fractions:
            metric = evaluate_ranking_at_budget(
                test_ranking,
                test_outcomes,
                float(fraction),
            )
            metric["cohort"] = "TEST_retrospective"
            test_results.append(metric)
            if test_valuable:
                high_value_ranking = test_ranking.loc[
                    test_ranking["customer_id"].astype(int).isin(test_valuable)
                ]
                high_value_outcomes = test_cohort.loc[
                    test_cohort["historically_valuable"],
                    ["customer_id", "purchased"],
                ]
                high_value_metric = evaluate_ranking_at_budget(
                    high_value_ranking,
                    high_value_outcomes,
                    float(fraction),
                )
                high_value_metric["ranking_strategy"] = strategy
                high_value_metric["cohort"] = "TEST_historically_valuable"
                test_high_value_results.append(high_value_metric)

        if validation_cohort is None or validation_cohort.empty:
            continue
        if "validation" not in cohorts:
            raise ValueError(f"{strategy} is missing its validation ranking.")
        validation_ranking = cohorts["validation"]
        _require_unique(
            validation_ranking, ["customer_id"], name=f"{strategy} validation ranking"
        )
        valuable_ids = set(
            validation_cohort.loc[
                validation_cohort["historically_valuable"], "customer_id"
            ].astype(int)
        ) if "historically_valuable" in validation_cohort else set()
        subset = validation_ranking.loc[
            validation_ranking["customer_id"].astype(int).isin(valuable_ids)
        ].copy()
        if subset.empty:
            rate = None
            selected_count = 0
        else:
            outcomes = validation_cohort.loc[
                validation_cohort["customer_id"].astype(int).isin(valuable_ids),
                ["customer_id", "purchased"],
            ]
            metric = evaluate_ranking_at_budget(
                subset,
                outcomes,
                selection_fraction,
            )
            rate = metric["future_nonpurchase_rate"]
            selected_count = metric["selected_customers"]
        validation_results.append(
            {
                "ranking_strategy": strategy,
                "selection_fraction": float(selection_fraction),
                "historically_valuable_candidates": len(valuable_ids),
                "selected_customers": selected_count,
                "future_nonpurchase_rate": rate,
                "selection_cohort": "prospective_validation",
            }
        )

    selected_strategy: str | None = None
    selected_validation_rate: float | None = None
    if validation_results:
        # Python max keeps the first policy on ties: the caller supplies the
        # frozen, documented RANKING_STRATEGIES order.
        available = [
            item
            for item in validation_results
            if item["future_nonpurchase_rate"] is not None
        ]
        if available:
            winner = max(available, key=lambda item: item["future_nonpurchase_rate"])
            selected_strategy = str(winner["ranking_strategy"])
            selected_validation_rate = float(winner["future_nonpurchase_rate"])

    selected_test = None
    if selected_strategy is not None:
        chosen_rank = ranking_policies[selected_strategy]["test"]
        chosen_subset = chosen_rank.loc[
            chosen_rank["customer_id"].astype(int).isin(test_valuable)
        ].copy()
        chosen_outcomes = test_cohort.loc[
            test_cohort["historically_valuable"], ["customer_id", "purchased"]
        ]
        selected_test = evaluate_ranking_at_budget(
            chosen_subset,
            chosen_outcomes,
            selection_fraction,
        )
        selected_test["ranking_strategy"] = selected_strategy
        selected_test["cohort"] = "locked_TEST_retrospective"

    return {
        "validation_status": (
            "prospective_validation_available"
            if validation_cohort is not None and not validation_cohort.empty
            else "no_prospective_validation"
        ),
        "validation_selection_fraction": float(selection_fraction),
        "selected_strategy_from_validation": selected_strategy,
        "validation_selected_nonpurchase_rate": selected_validation_rate,
        "validation_comparisons": validation_results,
        "test_baseline_comparisons": test_results,
        "test_historically_valuable_baseline_comparisons": test_high_value_results,
        "validation_selected_test_result": selected_test,
        "test_selection_used": False,
        "interpretation": (
            "Historical nonpurchase among selected customers is not recoverable "
            "revenue and does not estimate campaign response."
        ),
    }


def measure_selection_overlap(
    selected_customer_ids_by_strategy: Mapping[str, Sequence[int]],
) -> pd.DataFrame:
    """Return pairwise selection overlap and Jaccard similarity."""
    names = list(selected_customer_ids_by_strategy)
    sets = {
        name: set(map(int, selected_customer_ids_by_strategy[name]))
        for name in names
    }
    rows = []
    for first in names:
        for second in names:
            intersection = len(sets[first] & sets[second])
            union = len(sets[first] | sets[second])
            rows.append(
                {
                    "strategy_a": first,
                    "strategy_b": second,
                    "selected_a": len(sets[first]),
                    "selected_b": len(sets[second]),
                    "intersection": intersection,
                    "union": union,
                    "jaccard_similarity": intersection / union if union else None,
                }
            )
    return pd.DataFrame(rows)


def bootstrap_ranking_metrics(
    customer_evaluation: pd.DataFrame,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Bootstrap a fixed selected cohort's observable nonpurchase rate."""
    if "purchased" not in customer_evaluation:
        raise ValueError("customer_evaluation must include purchased outcomes.")
    if customer_evaluation["purchased"].isna().any():
        raise ValueError("customer_evaluation outcomes cannot be missing.")
    outcomes = customer_evaluation["purchased"].astype(int).to_numpy()
    if not np.isin(outcomes, [0, 1]).all():
        raise ValueError("purchased outcomes must be binary.")
    resamples = int(config.get("resamples", DEFAULT_RESAMPLES))
    seed = int(config.get("seed", DEFAULT_SEED))
    if resamples < 100:
        raise ValueError("resamples must be at least 100.")
    if not len(outcomes):
        return {
            "status": "no_selected_customers",
            "customer_count": 0,
            "metric": "future_nonpurchase_rate",
            "lower": None,
            "upper": None,
            "resamples": resamples,
        }
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(outcomes), size=(resamples, len(outcomes)))
    bootstrap_values = (1 - outcomes[draws]).mean(axis=1)
    return {
        "status": "estimated",
        "customer_count": int(len(outcomes)),
        "metric": "future_nonpurchase_rate",
        "estimate": float((1 - outcomes).mean()),
        "lower": float(np.quantile(bootstrap_values, 0.025)),
        "upper": float(np.quantile(bootstrap_values, 0.975)),
        "confidence_level": 0.95,
        "method": "customer-level percentile bootstrap of a fixed selected cohort",
        "resamples": resamples,
        "seed": seed,
    }


def evaluate_scenario_sensitivity(
    forecasts: pd.DataFrame,
    scenario_grid: Sequence[RetentionScenario],
    strategies: Sequence[str] = RANKING_STRATEGIES,
) -> dict[str, Any]:
    """Vectorize scenario outcomes and summarize selection stability."""
    if not scenario_grid:
        raise ValueError("scenario_grid cannot be empty.")
    unknown = sorted(set(strategies).difference(RANKING_STRATEGIES))
    if unknown:
        raise ValueError(f"Unknown ranking strategies: {unknown}")
    rankings = _ordered_scores(forecasts, strategies)
    detail_rows: list[dict[str, Any]] = []
    selections: dict[tuple[int, str], set[int]] = {}
    allocation_cache: dict[
        tuple[int, str, float, float, int], pd.DataFrame
    ] = {}
    allocation_inputs: dict[
        tuple[int, str, float, float, int], tuple[np.ndarray, np.ndarray, list[int]]
    ] = {}
    for scenario_index, scenario in enumerate(scenario_grid):
        if not isinstance(scenario, RetentionScenario):
            raise TypeError("scenario_grid must contain RetentionScenario objects.")
        horizon_rows = forecasts.loc[
            forecasts["horizon_days"].eq(scenario.horizon_days)
        ]
        if horizon_rows.empty:
            raise ValueError(
                f"No forecast rows exist for {scenario.horizon_days} days."
            )
        for strategy in strategies:
            ranked = rankings[strategy].loc[
                rankings[strategy]["horizon_days"].eq(scenario.horizon_days)
            ]
            allocation_key = (
                scenario.horizon_days,
                strategy,
                float(scenario.campaign_budget_gbp),
                float(scenario.contact_cost_gbp),
                int(scenario.maximum_contacts),
            )
            if allocation_key not in allocation_cache:
                allocation_cache[allocation_key] = allocate_contact_budget(
                    ranked,
                    scenario.campaign_budget_gbp,
                    scenario.contact_cost_gbp,
                    scenario.maximum_contacts,
                )
            allocation = allocation_cache[allocation_key]
            if allocation_key not in allocation_inputs:
                allocation_inputs[allocation_key] = (
                    pd.to_numeric(
                        allocation["purchase_probability"], errors="coerce"
                    ).to_numpy(dtype=float),
                    pd.to_numeric(
                        allocation["conditional_expected_spending_gbp"],
                        errors="coerce",
                    ).to_numpy(dtype=float),
                    allocation["customer_id"].astype(int).tolist(),
                )
            probability, conditional_spending, selected_ids_list = (
                allocation_inputs[allocation_key]
            )
            if (
                not np.isfinite(probability).all()
                or ((probability < 0) | (probability > 1)).any()
                or not np.isfinite(conditional_spending).all()
                or (conditional_spending < 0).any()
            ):
                raise ValueError("Scenario forecasts must contain finite, valid values.")
            selected_ids = set(selected_ids_list)
            selections[(scenario_index, strategy)] = selected_ids
            response_probability = float(scenario.assumed_response_probability)
            purchase_uplift = float(
                scenario.assumed_purchase_uplift_if_responded
            )
            incremental_probability = np.minimum(
                1.0 - probability,
                response_probability * purchase_uplift,
            )
            incremental_revenue = float(
                np.dot(incremental_probability, conditional_spending)
            )
            budget_pence = int(
                (Decimal(str(scenario.campaign_budget_gbp)) * 100).quantize(
                    Decimal("1"), rounding=ROUND_HALF_UP
                )
            )
            contact_cost_pence = int(
                (Decimal(str(scenario.contact_cost_gbp)) * 100).quantize(
                    Decimal("1"), rounding=ROUND_HALF_UP
                )
            )
            campaign_cost_pence = len(selected_ids_list) * contact_cost_pence
            campaign_cost_gbp = campaign_cost_pence / 100.0
            contribution = (
                float(scenario.assumed_gross_margin_rate) * incremental_revenue
                - campaign_cost_gbp
                if scenario.assumed_gross_margin_rate is not None
                else None
            )
            detail_rows.append(
                {
                    "scenario_index": scenario_index,
                    "horizon_days": scenario.horizon_days,
                    "ranking_strategy": strategy,
                    "campaign_budget_gbp": budget_pence / 100.0,
                    "contact_cost_gbp": contact_cost_pence / 100.0,
                    "maximum_contacts": scenario.maximum_contacts,
                    "assumed_response_probability": response_probability,
                    "assumed_purchase_uplift_if_responded": purchase_uplift,
                    "assumed_gross_margin_rate": (
                        float(scenario.assumed_gross_margin_rate)
                        if scenario.assumed_gross_margin_rate is not None
                        else None
                    ),
                    "selected_customer_count": len(selected_ids_list),
                    "campaign_cost_gbp": campaign_cost_gbp,
                    "budget_remaining_gbp": (
                        budget_pence - campaign_cost_pence
                    ) / 100.0,
                    "budget_utilization": (
                        campaign_cost_pence / budget_pence
                        if budget_pence
                        else 0.0
                    ),
                    "hypothetical_incremental_revenue_gbp": incremental_revenue,
                    "hypothetical_incremental_contribution_gbp": contribution,
                    "causal_estimate": False,
                }
            )
    details = pd.DataFrame(detail_rows)

    stability_rows = []
    for strategy in strategies:
        for horizon in sorted({scenario.horizon_days for scenario in scenario_grid}):
            same_budget_groups: dict[tuple[float, float, int], list[set[int]]] = {}
            relevant = [
                (index, scenario)
                for index, scenario in enumerate(scenario_grid)
                if scenario.horizon_days == horizon
            ]
            for index, scenario in relevant:
                key = (
                    float(scenario.campaign_budget_gbp),
                    float(scenario.contact_cost_gbp),
                    int(scenario.maximum_contacts),
                )
                same_budget_groups.setdefault(key, []).append(
                    selections[(index, strategy)]
                )
            jaccard_values = []
            for sets in same_budget_groups.values():
                for first_index, first in enumerate(sets):
                    for second in sets[first_index + 1 :]:
                        union = first | second
                        jaccard_values.append(
                            len(first & second) / len(union) if union else 1.0
                        )
            stability_rows.append(
                {
                    "horizon_days": horizon,
                    "ranking_strategy": strategy,
                    "selection_order_depends_on_response_or_uplift": False,
                    "same_budget_response_uplift_jaccard_min": (
                        float(min(jaccard_values)) if jaccard_values else 1.0
                    ),
                    "same_budget_response_uplift_jaccard_median": (
                        float(np.median(jaccard_values))
                        if jaccard_values
                        else 1.0
                    ),
                    "comparison_count": len(jaccard_values),
                    "interpretation": (
                        "Scores are intentionally independent of campaign response "
                        "and uplift assumptions; this is a design invariance, not "
                        "evidence of campaign efficacy."
                    ),
                }
            )
    return {
        "scenario_count": len(scenario_grid),
        "strategy_count": len(strategies),
        "results": details.to_dict(orient="records"),
        "selection_stability": stability_rows,
        "scenario_inputs_are_hypothetical": True,
    }


def _load_behavior_config(root: Path) -> BehaviorConfig:
    path = root / "models" / "behavior_monitor" / "metadata.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    if metadata.get("feature_version") != "behavior-monitor-v1":
        raise ValueError("Notebook 08 behavior artifact version is unsupported.")
    return BehaviorConfig(**metadata["config"])


def _add_behavior_indicators(
    forecast_table: pd.DataFrame,
    events: pd.DataFrame,
    cutoff: pd.Timestamp,
    config: BehaviorConfig,
) -> pd.DataFrame:
    features = compute_behavior_features(events, cutoff, config)
    scores = calculate_behavior_scores(
        features,
        {
            "feature_version": "behavior-monitor-v1",
            "policy_version": "behavior-continuous-v1",
            "ewma_lambda": config.ewma_lambda,
        },
    )
    behavior = features.merge(
        scores.drop(
            columns=[
                "cutoff_date",
                "history_sufficiency",
                "gap_deviation_score",
                "policy_version",
            ],
            errors="ignore",
        ),
        on="Customer ID",
        how="left",
        validate="one_to_one",
        suffixes=("", "_score"),
    )
    behavior = behavior.rename(
        columns={
            "Customer ID": "customer_id",
            "purchase_rate_ratio": "purchase_rate_ratio",
            "revenue_rate_ratio": "revenue_rate_ratio",
            "history_sufficiency": "history_sufficiency",
        }
    )
    behavior["cutoff_date"] = pd.to_datetime(behavior["cutoff_date"], errors="raise")
    columns = [
        "customer_id",
        "cutoff_date",
        "history_sufficiency",
        "purchase_rate_ratio",
        "revenue_rate_ratio",
        "gap_deviation_score",
        "policy_status",
        "available_indicator_count",
    ]
    merged = forecast_table.merge(
        behavior.loc[:, columns],
        on=["customer_id", "cutoff_date"],
        how="left",
        validate="one_to_one",
        indicator="_behavior_match",
    )
    if not merged["_behavior_match"].eq("both").all():
        raise ValueError("Notebook 08 indicators do not align with the forecast cohort.")
    return merged.drop(columns="_behavior_match")


def _attach_test_reliability(
    forecast_table: pd.DataFrame,
    reliability_artifact: dict[str, Any],
) -> pd.DataFrame:
    items = reliability_artifact["evaluation"]["subgroups"]
    lookup = {
        (str(item["group"]), int(item["horizon_days"])): item
        for item in items
        if item.get("group_type") == "history_group"
    }
    result = forecast_table.copy()
    matched = [
        lookup.get((str(group), int(horizon)))
        for group, horizon in zip(
            result["history_group"], result["horizon_days"], strict=True
        )
    ]
    result["reliability_status"] = [
        item.get("status", "reliability_evidence_unavailable")
        if item
        else "reliability_evidence_unavailable"
        for item in matched
    ]
    result["reliability_evidence_count"] = [
        int(item["customer_count"]) if item else 0 for item in matched
    ]
    result["reliability_group_brier_score"] = [
        item.get("brier_score") if item else None for item in matched
    ]
    result["reliability_group_calibration_gap"] = [
        item.get("calibration_gap") if item else None for item in matched
    ]
    result["reliability_evidence_cutoff"] = reliability_artifact["metadata"][
        "forecast_cutoff"
    ]
    result["reliability_is_individual_guarantee"] = False
    return result


def _read_role(root: Path, horizon: int, role: str) -> pd.DataFrame:
    path = root / "data" / "processed" / "temporal" / f"predictive_splits_{horizon}d.csv"
    frame = pd.read_csv(path, parse_dates=["cutoff_date"])
    rows = frame.loc[frame["split_role"].eq(role)].copy()
    if rows.empty:
        return rows
    _require_unique(rows, ["Customer ID", "cutoff_date"], name=f"{horizon}d {role}")
    expected_horizon = f"Purchased_{horizon}d"
    if expected_horizon not in rows:
        raise ValueError(f"{path.name} has no {expected_horizon} outcome.")
    return rows


def _forecast_at_validation_cutoff(
    intelligence: CustomerIntelligence,
    transactions: pd.DataFrame,
    orders: pd.DataFrame,
    horizon: int,
    cutoff: pd.Timestamp,
    validation_features: pd.DataFrame,
    events: pd.DataFrame,
    behavior_config: BehaviorConfig,
) -> pd.DataFrame:
    features = tf.compute_historical_features(orders, cutoff)
    if features.empty:
        raise ValueError(f"No pre-cutoff features exist at {cutoff.date()}.")
    _require_unique(
        validation_features,
        ["Customer ID", "cutoff_date"],
        name="validation split features",
    )
    segment_features = validation_features.loc[
        :, ["Customer ID", "cutoff_date", "Hist_Segment"]
    ].copy()
    features = features.merge(
        segment_features,
        on=["Customer ID", "cutoff_date"],
        how="left",
        validate="one_to_one",
        indicator="_segment_match",
    )
    if not features["_segment_match"].eq("both").all():
        raise ValueError("Validation cutoff segment features do not align.")
    features = features.drop(columns="_segment_match")
    features["history_group"] = pc._history_group(features["Frequency"])
    predictions = intelligence.predict_customers(
        transactions,
        cutoff,
        horizons=[horizon],
    )
    keys = ["Customer ID", "cutoff_date"]
    _require_unique(features, keys, name="validation features")
    _require_unique(predictions, keys, name="validation predictions")
    if set(map(tuple, features[keys].to_numpy())) != set(
        map(tuple, predictions[keys].to_numpy())
    ):
        raise ValueError("Validation features and forecasts do not align exactly.")
    combined = features.merge(
        predictions,
        on=keys,
        how="inner",
        validate="one_to_one",
        suffixes=("", "_prediction"),
    )
    prepared = prepare_revenue_forecast_table(combined, horizon)
    return _add_behavior_indicators(
        prepared,
        events,
        cutoff,
        behavior_config,
    )


def _build_ranking_cohort(
    forecasts: pd.DataFrame,
    outcomes: pd.DataFrame,
    spending_threshold: float,
    *,
    role: str,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Keep outcomes separate until forecast features and rank orders are fixed."""
    if forecasts.empty or outcomes.empty:
        raise ValueError(f"{role} cohort is empty.")
    _require_unique(forecasts, ["customer_id"], name=f"{role} forecasts")
    _require_unique(outcomes, ["Customer ID", "cutoff_date"], name=f"{role} outcomes")
    outcome = outcomes.loc[
        :, ["Customer ID", "cutoff_date", "Purchased", "FutureRevenue"]
    ].copy()
    outcome = outcome.rename(
        columns={
            "Customer ID": "customer_id",
            "Purchased": "purchased",
            "FutureRevenue": "observed_future_revenue_gbp",
        }
    )
    outcome["customer_id"] = pd.to_numeric(
        outcome["customer_id"], errors="raise"
    ).astype("int64")
    outcome["cutoff_date"] = pd.to_datetime(outcome["cutoff_date"], errors="raise")
    if set(forecasts["customer_id"].astype(int)) != set(outcome["customer_id"]):
        raise ValueError(f"{role} forecast and outcome customer IDs do not match.")
    predictions = forecasts.copy()
    predictions["historically_valuable"] = (
        predictions["historical_gross_spending_gbp"] >= spending_threshold
    )
    rankings = _ordered_scores(predictions)
    cohort = predictions[
        [
            "customer_id",
            "cutoff_date",
            "hist_segment",
            "history_group",
            "historical_gross_spending_gbp",
            "history_sufficiency",
            "historically_valuable",
        ]
    ].merge(
        outcome.loc[
            :,
            [
                "customer_id",
                "cutoff_date",
                "purchased",
                "observed_future_revenue_gbp",
            ],
        ],
        on=["customer_id", "cutoff_date"],
        how="inner",
        validate="one_to_one",
    )
    if len(cohort) != len(predictions):
        raise ValueError(f"{role} forecast and outcome rows do not align one-to-one.")
    cohort["purchased"] = pd.to_numeric(cohort["purchased"], errors="raise").astype(int)
    cohort["observed_future_revenue_gbp"] = pd.to_numeric(
        cohort["observed_future_revenue_gbp"], errors="raise"
    )
    if not cohort["purchased"].isin([0, 1]).all():
        raise ValueError(f"{role} Purchased outcome must be binary.")
    if (
        not np.isfinite(cohort["observed_future_revenue_gbp"].to_numpy(dtype=float)).all()
        or (cohort["observed_future_revenue_gbp"] < 0).any()
    ):
        raise ValueError(f"{role} future revenue must be finite and non-negative.")
    return cohort, {
        strategy: rankings[strategy]
        for strategy in RANKING_STRATEGIES
    }


def _ranking_comparisons(
    cohort: pd.DataFrame,
    rankings: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    outcomes = cohort[["customer_id", "purchased"]]
    comparisons = []
    selected: dict[str, list[int]] = {}
    for strategy, ranking in rankings.items():
        for fraction in TOP_FRACTIONS:
            metrics = evaluate_ranking_at_budget(ranking, outcomes, fraction)
            metrics["ranking_strategy"] = strategy
            comparisons.append(metrics)
        fraction = 0.10
        count = int(np.ceil(len(ranking) * fraction))
        selected[strategy] = ranking.head(count)["customer_id"].astype(int).tolist()
    overlap = measure_selection_overlap(selected)
    return {
        "comparisons": comparisons,
        "selection_overlap_at_10_percent": overlap.to_dict(orient="records"),
        "selection_sizes_at_10_percent": {
            name: len(ids) for name, ids in selected.items()
        },
    }


def _scenario_grid() -> list[RetentionScenario]:
    return [
        RetentionScenario(
            horizon_days=horizon,
            campaign_budget_gbp=budget,
            contact_cost_gbp=cost,
            maximum_contacts=3373,
            assumed_response_probability=response,
            assumed_purchase_uplift_if_responded=uplift,
            assumed_gross_margin_rate=None,
        )
        for horizon in HORIZONS
        for response in (0.05, 0.10, 0.20)
        for uplift in (0.02, 0.05, 0.10)
        for cost in (1.00, 3.00, 5.00)
        for budget in (100.00, 500.00, 1000.00)
    ]


def _forecast_perturbation_sensitivity(
    forecast_tables: Mapping[int, pd.DataFrame],
) -> list[dict[str, Any]]:
    rows = []
    for horizon, base in forecast_tables.items():
        base_sets: dict[str, set[int]] = {}
        for strategy in ("nonreturn_spending_proxy", "pareto_risk_value"):
            ranked = rank_retention_candidates(base, strategy)
            base_sets[strategy] = set(
                ranked.head(int(np.ceil(len(ranked) * 0.10)))["customer_id"].astype(int)
            )
        for probability_offset in (-0.05, 0.0, 0.05):
            for spending_scale in (0.8, 1.0, 1.2):
                perturbed = base.copy()
                perturbed["purchase_probability"] = np.clip(
                    perturbed["purchase_probability"] + probability_offset, 0, 1
                )
                perturbed["conditional_expected_spending_gbp"] *= spending_scale
                perturbed[
                    "nonreturn_weighted_conditional_spending_proxy_gbp"
                ] = (
                    (1 - perturbed["purchase_probability"])
                    * perturbed["conditional_expected_spending_gbp"]
                )
                for strategy in ("nonreturn_spending_proxy", "pareto_risk_value"):
                    ranked = rank_retention_candidates(perturbed, strategy)
                    chosen = set(
                        ranked.head(int(np.ceil(len(ranked) * 0.10)))[
                            "customer_id"
                        ].astype(int)
                    )
                    union = chosen | base_sets[strategy]
                    rows.append(
                        {
                            "horizon_days": horizon,
                            "ranking_strategy": strategy,
                            "purchase_probability_offset": probability_offset,
                            "conditional_spending_scale": spending_scale,
                            "top_ten_percent_jaccard_vs_saved_forecast": (
                                len(chosen & base_sets[strategy]) / len(union)
                                if union
                                else 1.0
                            ),
                            "interpretation": (
                                "Illustrative perturbation only; not a calibrated "
                                "individual prediction interval."
                            ),
                        }
                    )
    return rows


def run_revenue_exposure_analysis(
    project_root: str | Path,
    *,
    bootstrap_resamples: int = DEFAULT_RESAMPLES,
    random_seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    """Reproduce Notebook 10 evaluation using only saved models and data."""
    started = time.perf_counter()
    root = Path(project_root).resolve()
    data_dir = root / "data"
    metrics_dir = data_dir / "metrics"
    transactions_path = data_dir / "processed" / "online_retail_cleaned_data.csv"
    orders_path = data_dir / "processed" / "temporal" / "orders.csv"
    segments_path = data_dir / "processed" / "customer_segments.csv"
    for path in (transactions_path, orders_path, segments_path):
        if not path.is_file():
            raise FileNotFoundError(f"Required historical input is unavailable: {path}")
    transactions = pd.read_csv(
        transactions_path,
        parse_dates=["InvoiceDate"],
    )
    orders = pd.read_csv(orders_path, parse_dates=["PurchaseDate"])
    segments = pd.read_csv(segments_path)
    if orders.empty or transactions.empty:
        raise ValueError("The historical transaction and order sources cannot be empty.")
    intelligence = CustomerIntelligence.from_artifacts(root)
    test_snapshot = build_forecast_snapshot(
        transactions,
        orders,
        segments,
        intelligence,
        TEST_CUTOFF.isoformat(),
    )
    inference_ms = (time.perf_counter() - started) * 1000

    reliability_path = metrics_dir / "prediction_reliability_evaluation.json"
    if not reliability_path.is_file():
        raise FileNotFoundError("Notebook 09 reliability evaluation is unavailable.")
    reliability_artifact = json.loads(reliability_path.read_text(encoding="utf-8"))
    if (
        reliability_artifact.get("metadata", {}).get("artifact_version")
        != "prediction-reliability-v1"
    ):
        raise ValueError("Unsupported Notebook 09 reliability artifact version.")
    if reliability_artifact["metadata"]["forecast_cutoff"] != TEST_CUTOFF.date().isoformat():
        raise ValueError("Notebook 09 reliability evidence has the wrong forecast cutoff.")

    behavior_config = _load_behavior_config(root)
    events = prepare_purchase_events(orders)
    test_forecasts: dict[int, pd.DataFrame] = {}
    summaries: dict[int, dict[str, Any]] = {}
    concentration_rows: list[dict[str, Any]] = []
    for horizon in HORIZONS:
        prepared = prepare_revenue_forecast_table(test_snapshot, horizon)
        prepared = _add_behavior_indicators(
            prepared,
            events,
            TEST_CUTOFF,
            behavior_config,
        )
        prepared = _attach_test_reliability(prepared, reliability_artifact)
        # No current or historical forecast is a justified business counterfactual.
        prepared = calculate_reference_exposure(
            prepared,
            None,
            RevenueExposureConfig(),
        )
        prepared = calculate_opportunity_proxy(prepared, RevenueExposureConfig())
        test_forecasts[horizon] = prepared
        summary = summarize_portfolio_exposure(prepared, RevenueExposureConfig())
        summary["reliability_evidence_version"] = reliability_artifact["metadata"][
            "artifact_version"
        ]
        summary["reliability_evidence_cutoff"] = reliability_artifact["metadata"][
            "forecast_cutoff"
        ]
        summary["reliability_group_coverage"] = int(
            prepared["reliability_status"].ne("reliability_evidence_unavailable").sum()
        )
        summary["history_sufficiency_counts"] = (
            prepared["history_sufficiency"].value_counts(dropna=False).to_dict()
        )
        summaries[horizon] = summary
        for metric in (
            "historical_gross_spending_gbp",
            "personalized_expected_revenue_gbp",
            "nonreturn_weighted_conditional_spending_proxy_gbp",
        ):
            concentration = calculate_exposure_concentration(
                prepared,
                metric,
            )
            concentration["horizon_days"] = horizon
            concentration_rows.extend(concentration.to_dict(orient="records"))

    portfolio_forecast_disagreements = {
        str(horizon): compute_forecast_disagreement(
            test_forecasts[horizon], horizon
        ).agg(
            {
                "historical_minus_personalized_forecast_difference_gbp": "sum",
                "segment_minus_personalized_forecast_difference_gbp": "sum",
            }
        ).to_dict()
        for horizon in HORIZONS
    }
    saved_revenue_diagnostics = reliability_artifact["evaluation"]["revenue"]
    saved_revenue_groups = reliability_artifact["evaluation"][
        "revenue_by_history_group"
    ]
    metadata = json.loads(
        (root / "models" / "spending_model" / "metadata.json").read_text(
            encoding="utf-8"
        )
    )
    prospective_protocol = metadata["joint_validation_protocol"]

    evaluation_start = time.perf_counter()
    split_cache = {horizon: _read_role(root, horizon, "TEST") for horizon in HORIZONS}
    strategy_evaluations: dict[str, Any] = {}
    ranking_comparisons: dict[str, Any] = {}
    validation_cutoffs: dict[str, Any] = {}
    validation_cohorts: dict[int, pd.DataFrame | None] = {}
    test_cohorts: dict[int, pd.DataFrame] = {}
    test_rankings_by_horizon: dict[int, dict[str, pd.DataFrame]] = {}
    validation_rankings_by_horizon: dict[int, dict[str, pd.DataFrame] | None] = {}
    for horizon in HORIZONS:
        test_split = split_cache[horizon]
        if test_split["cutoff_date"].nunique() != 1 or pd.Timestamp(
            test_split["cutoff_date"].iloc[0]
        ) != TEST_CUTOFF:
            raise ValueError(f"{horizon}-day TEST split is not at the approved cutoff.")
        test_outcomes = test_split.rename(
            columns={
                f"Purchased_{horizon}d": "Purchased",
                f"FutureRevenue_{horizon}d": "FutureRevenue",
            }
        )
        test_cohort, test_rankings = _build_ranking_cohort(
            test_forecasts[horizon],
            test_outcomes,
            float(
                _read_role(root, horizon, "TRAIN")["Monetary_Gross"].quantile(
                    HIGH_VALUE_QUANTILE
                )
            ),
            role="TEST",
        )
        test_cohorts[horizon] = test_cohort
        test_rankings_by_horizon[horizon] = test_rankings
        protocol = prospective_protocol[str(horizon)]
        validation_status = protocol["status"]
        if validation_status != "prospective":
            validation_cohorts[horizon] = None
            validation_rankings_by_horizon[horizon] = None
            validation_cutoffs[str(horizon)] = {
                "status": "not_available_for_policy_selection",
                "cutoff": protocol.get("cutoff"),
                "reason": protocol.get("reason"),
            }
            continue
        cutoff = pd.Timestamp(protocol["cutoff"])
        validation_cutoffs[str(horizon)] = {
            "status": "prospective",
            "cutoff": cutoff.date().isoformat(),
            "purchase_model_available_by": protocol[
                "purchase_model_available_by"
            ],
        }
        validation_split = _read_role(root, horizon, "VAL")
        if (
            validation_split["cutoff_date"].nunique() != 1
            or pd.Timestamp(validation_split["cutoff_date"].iloc[0]) != cutoff
        ):
            raise ValueError(
                f"{horizon}-day validation outcomes do not match their prospective cutoff."
            )
        validation_forecasts = _forecast_at_validation_cutoff(
            intelligence,
            transactions,
            orders,
            horizon,
            cutoff,
            validation_split,
            events,
            behavior_config,
        )
        validation_outcomes = validation_split.rename(
            columns={
                f"Purchased_{horizon}d": "Purchased",
                f"FutureRevenue_{horizon}d": "FutureRevenue",
            }
        )
        validation_threshold = float(
            _read_role(root, horizon, "TRAIN")["Monetary_Gross"].quantile(
                HIGH_VALUE_QUANTILE
            )
        )
        validation_cohort, validation_rankings = _build_ranking_cohort(
            validation_forecasts,
            validation_outcomes,
            validation_threshold,
            role="validation",
        )
        validation_cohorts[horizon] = validation_cohort
        validation_rankings_by_horizon[horizon] = validation_rankings

    all_test_comparisons = {}
    for horizon in HORIZONS:
        policies: dict[str, dict[str, pd.DataFrame]] = {}
        for strategy in RANKING_STRATEGIES:
            cohort_policy: dict[str, pd.DataFrame] = {
                "test": test_rankings_by_horizon[horizon][strategy]
            }
            if validation_rankings_by_horizon[horizon] is not None:
                cohort_policy["validation"] = validation_rankings_by_horizon[
                    horizon
                ][strategy]
            policies[strategy] = cohort_policy
        comparison = compare_ranking_baselines(
            validation_cohorts[horizon],
            test_cohorts[horizon],
            policies,
            budget_fractions=TOP_FRACTIONS,
        )
        comparison["validation_cutoff"] = validation_cutoffs[str(horizon)]
        comparison["test_cutoff"] = TEST_CUTOFF.date().isoformat()
        comparison["historically_valuable_rule"] = (
            "gross spending at or above the horizon-specific TRAIN 75th percentile"
        )
        ranking_comparisons[str(horizon)] = comparison
        test_rankings = {
            strategy: policies[strategy]["test"]
            for strategy in RANKING_STRATEGIES
        }
        all_test_comparisons[str(horizon)] = _ranking_comparisons(
            test_cohorts[horizon],
            test_rankings,
        )
        selected_strategy = comparison["selected_strategy_from_validation"]
        selected_result = comparison["validation_selected_test_result"]
        if selected_strategy and selected_result:
            selected = ranking_comparisons[str(horizon)][
                "validation_selected_test_result"
            ]
            validation_rate = comparison["validation_selected_nonpurchase_rate"]
            winner_rate = selected["future_nonpurchase_rate"]
            baseline_rates = {
                row["ranking_strategy"]: row["future_nonpurchase_rate"]
                for row in comparison[
                    "test_historically_valuable_baseline_comparisons"
                ]
                if row["budget_fraction"] == 0.1
            }
            strategy_evaluations[str(horizon)] = {
                "selected_on_validation": selected_strategy,
                "validation_high_value_nonpurchase_rate": validation_rate,
                "test_high_value_nonpurchase_rate": winner_rate,
                "test_high_value_baseline_rates": baseline_rates,
                "improved_on_all_test_baselines": bool(
                    winner_rate is not None
                    and all(
                        winner_rate > value
                        for name, value in baseline_rates.items()
                        if name != selected_strategy and value is not None
                    )
                ),
                "test_outcomes_used_for_selection": False,
            }
        else:
            strategy_evaluations[str(horizon)] = {
                "selected_on_validation": None,
                "validation_high_value_nonpurchase_rate": None,
                "test_high_value_nonpurchase_rate": None,
                "improved_on_all_test_baselines": None,
                "test_outcomes_used_for_selection": False,
                "status": "retrospective_exploratory_no_prospective_selection",
            }

    # Add fixed-cohort bootstrap intervals for the validation-selected policy's
    # TEST high-spending subset. This describes outcome-rate uncertainty only.
    for horizon in HORIZONS:
        comparison = ranking_comparisons[str(horizon)]
        strategy = comparison["selected_strategy_from_validation"]
        if strategy is None:
            continue
        rank = rank_retention_candidates(
            test_forecasts[horizon].loc[
                test_forecasts[horizon]["historical_gross_spending_gbp"]
                >= float(
                    _read_role(root, horizon, "TRAIN")["Monetary_Gross"].quantile(
                        HIGH_VALUE_QUANTILE
                    )
                )
            ],
            strategy,
        )
        selected_count = int(np.ceil(len(rank) * 0.10))
        selected_ids = set(rank.head(selected_count)["customer_id"].astype(int))
        selected_outcomes = test_cohorts[horizon].loc[
            test_cohorts[horizon]["customer_id"].isin(selected_ids),
            ["customer_id", "purchased"],
        ]
        interval = bootstrap_ranking_metrics(
            selected_outcomes,
            {"resamples": bootstrap_resamples, "seed": random_seed + horizon},
        )
        strategy_evaluations[str(horizon)]["test_selected_cohort_bootstrap_95"] = interval
    ranking_elapsed_ms = (time.perf_counter() - evaluation_start) * 1000

    scenario_start = time.perf_counter()
    scenario_analysis: dict[str, Any] = {}
    all_sensitivity_rows: list[dict[str, Any]] = []
    for horizon in HORIZONS:
        analysis = evaluate_scenario_sensitivity(
            test_forecasts[horizon],
            [scenario for scenario in _scenario_grid() if scenario.horizon_days == horizon],
        )
        scenario_analysis[str(horizon)] = {
            "scenario_count": analysis["scenario_count"],
            "selection_stability": analysis["selection_stability"],
        }
        all_sensitivity_rows.extend(analysis["results"])
    perturbations = _forecast_perturbation_sensitivity(test_forecasts)
    scenario_elapsed_ms = (time.perf_counter() - scenario_start) * 1000

    evaluation = {
        "metadata": {
            "artifact_version": "revenue-exposure-evaluation-v1",
            "forecast_cutoff": TEST_CUTOFF.date().isoformat(),
            "evaluation_customer_count": int(len(test_snapshot)),
            "currency_code": "GBP",
            "purchase_clock_model_version": intelligence.purchase_bundle[
                "metadata"
            ]["model_version"],
            "spending_model_version": intelligence.spending_bundle["metadata"][
                "model_version"
            ],
            "reliability_artifact_version": reliability_artifact["metadata"][
                "artifact_version"
            ],
            "screening_policy_version": SCREENING_POLICY_VERSION,
            "selection_metric": "observable future nonpurchase rate among high historical spenders",
            "selection_fraction": 0.10,
            "high_value_quantile_from_training": HIGH_VALUE_QUANTILE,
            "top_fraction_metrics": list(TOP_FRACTIONS),
            "bootstrap_resamples": bootstrap_resamples,
            "random_seed": random_seed,
            "test_outcomes_used_for_selection": False,
        },
        "financial_definitions": {
            "expected_revenue": "saved purchase probability * saved conditional expected spending",
            "reference_exposure": "max(0, documented matched reference expected revenue - current expected revenue)",
            "reference_exposure_status": "not_estimable",
            "reference_exposure_total_gbp": None,
            "reference_exposure_reason": "No defensible, chronologically valid matched reference forecast exists in the saved data.",
            "forecast_disagreement": "Differences among saved forecast models; not causal and not revenue exposure.",
            "opportunity_proxy": "(1 - purchase probability) * conditional expected spending; screening proxy only, not recoverable loss.",
            "scenario_incremental_probability": "min(1 - current purchase probability, assumed response probability * assumed uplift if responded)",
            "scenario_incremental_revenue": "scenario incremental probability * saved conditional expected spending",
            "scenario_contribution": "assumed gross margin * hypothetical incremental revenue - campaign contact costs; only when margin is supplied",
            "causal_effect": None,
        },
        "portfolio_by_horizon": {
            str(horizon): summaries[horizon] for horizon in HORIZONS
        },
        "forecast_disagreements": portfolio_forecast_disagreements,
        "revenue_model_test_diagnostics": saved_revenue_diagnostics,
        "revenue_model_history_group_diagnostics": saved_revenue_groups,
        "concentration": concentration_rows,
        "ranking_method_comparisons": all_test_comparisons,
        "validation_selected_strategy_evaluation": strategy_evaluations,
        "ranking_selection_and_test_evaluation": ranking_comparisons,
        "validation_cutoffs": validation_cutoffs,
        "hypotheses": {},
        "limitations": [
            "The dataset has no randomized retention treatment or response outcomes; no causal campaign uplift is estimated.",
            "No defensible same-customer counterfactual business reference is available; reference-based revenue exposure is not estimable.",
            "Historical-rate and segment-aware forecasts are alternative models, not causal counterfactuals.",
            "The nonreturn-weighted spending proxy applies conditional spending in a hypothetical nonpurchase scenario.",
            "The final 90-day model has no prospective validation vintage; 90-day ranking comparisons are exploratory and cannot select a policy.",
            "The 30- and 60-day validation-selected ranking methods are evaluated once on the frozen historical TEST cohort.",
            "Notebook 09 TEST calibration and revenue bias are historical group/portfolio diagnostics, not individual prediction intervals.",
        ],
    }
    scenario_payload = {
        "metadata": {
            "artifact_version": "retention-scenario-sensitivity-v1",
            "currency_code": "GBP",
            "scenario_inputs_are_hypothetical": True,
            "scenario_count_per_horizon": len(
                [scenario for scenario in _scenario_grid() if scenario.horizon_days == 30]
            ),
            "horizons": list(HORIZONS),
            "strategies": list(RANKING_STRATEGIES),
            "no_treatment_effect_estimation": True,
        },
        "scenario_results": all_sensitivity_rows,
        "scenario_selection_stability": scenario_analysis,
        "forecast_perturbation_sensitivity": perturbations,
        "interpretation": (
            "Scenario values are user-defined illustrations. Perturbation ranges "
            "are not calibrated individual confidence intervals."
        ),
    }

    # Hypothesis labels are decided from the recorded empirical comparisons,
    # never from expected scenario benefits.
    h1_concentrated = any(
        row["metric"] == "historical_gross_spending_gbp"
        and row["top_customer_share"] == 0.1
        and row["portfolio_share"] is not None
        and row["portfolio_share"] >= 0.5
        for row in concentration_rows
    )
    h2_distinct = any(
        row["strategy_a"] != row["strategy_b"]
        and row["jaccard_similarity"] is not None
        and row["jaccard_similarity"] < 1
        for rows in all_test_comparisons.values()
        for row in rows["selection_overlap_at_10_percent"]
    )
    h3_bias = any(
        float(item.get("mean_forecast_bias", 0)) != 0
        for item in saved_revenue_diagnostics
    )
    h4_budget_varies = len(
        {row["selected_customer_count"] for row in all_sensitivity_rows}
    ) > 1
    evaluation["hypotheses"] = {
        "H1_financial_concentration": {
            "status": "supported_descriptively" if h1_concentrated else "not_supported_at_prespecified_threshold",
            "threshold": "top 10% historical gross-spending share of at least 50%",
            "evidence": "See horizon-specific top-customer concentration rows.",
        },
        "H2_risk_value_interaction": {
            "status": "rankings_are_distinct" if h2_distinct else "no_material_selection_differences",
            "evidence": "Compared deterministic ranking overlaps; distinct selections alone do not imply better interventions.",
        },
        "H3_forecast_reliability_sensitivity": {
            "status": "forecast_bias_observed" if h3_bias else "no_mean_bias_in_saved_test_diagnostics",
            "evidence": "Uses the fixed TEST revenue diagnostics from Notebook 09 without correcting production forecasts.",
        },
        "H4_budget_sensitivity": {
            "status": "selection_changes_with_budget_or_cost" if h4_budget_varies else "selection_counts_stable_in_grid",
            "evidence": "Scenario grids vary contact cost and budget under explicit hypothetical response/uplift assumptions.",
        },
        "H5_scenario_robustness": {
            "status": "descriptive_assumption_independent_screening_orders",
            "evidence": "Screening rankings do not depend on campaign response/uplift assumptions; this is by design, not causal robustness.",
        },
        "H6_predictive_ranking": {
            "status": (
                "supported_on_locked_test"
                if any(
                    result.get("improved_on_all_test_baselines") is True
                    for result in strategy_evaluations.values()
                )
                else "not_supported_on_locked_test"
            ),
            "evidence": "30- and 60-day ranking rules are selected on prospective validation outcomes and evaluated on the locked TEST against matched high-value baselines; 90-day selection is unavailable.",
        },
    }
    evaluation["timings"] = {
        "forecast_snapshot_build_ms": inference_ms,
        "ranking_evaluation_ms": ranking_elapsed_ms,
        "scenario_grid_ms": scenario_elapsed_ms,
    }
    profiling = {
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "model_versions": {
            "purchase_clock": evaluation["metadata"]["purchase_clock_model_version"],
            "spending": evaluation["metadata"]["spending_model_version"],
            "behavior": "behavior-monitor-v1",
            "reliability": reliability_artifact["metadata"]["artifact_version"],
        },
        "cohort_size": int(len(test_snapshot)),
        "horizons": list(HORIZONS),
        "timings": evaluation["timings"],
        "scenario_count": len(all_sensitivity_rows),
        "validation_customer_counts": {
            str(horizon): (
                int(len(validation_cohorts[horizon]))
                if validation_cohorts[horizon] is not None
                else None
            )
            for horizon in HORIZONS
        },
        "warm_api": {"status": "not_measured"},
    }
    _write_json(metrics_dir / "revenue_exposure_evaluation.json", evaluation)
    _write_json(metrics_dir / "retention_scenario_sensitivity.json", scenario_payload)
    _write_json(metrics_dir / "revenue_exposure_profiling.json", profiling)
    model_metadata = {
        "artifact_version": "revenue-exposure-v1",
        "artifact_kind": "research_metadata_no_fitted_model",
        "screening_policy_version": SCREENING_POLICY_VERSION,
        "forecast_cutoff": TEST_CUTOFF.date().isoformat(),
        "currency_code": "GBP",
        "supported_horizons": list(HORIZONS),
        "source_model_versions": evaluation["metadata"],
        "reference_exposure": {
            "status": "not_estimable",
            "reference_method": None,
            "reference_definition": None,
            "reason": evaluation["financial_definitions"][
                "reference_exposure_reason"
            ],
        },
        "ranking_strategies": list(RANKING_STRATEGIES),
        "validation_policy_selection": validation_cutoffs,
        "fitted_model_created": False,
    }
    _write_json(root / "models" / "revenue_exposure" / "metadata.json", model_metadata)
    return {
        "project_root": str(root),
        "forecast_snapshot": test_snapshot,
        "forecast_tables": test_forecasts,
        "test_cohorts": test_cohorts,
        "validation_cohorts": validation_cohorts,
        "evaluation": evaluation,
        "scenario_sensitivity": scenario_payload,
        "profiling": profiling,
    }


def profile_warm_revenue_api(
    project_root: str | Path,
    *,
    repetitions: int = 5,
) -> dict[str, Any]:
    """Measure the seven portfolio/customer/scenario routes in-process."""
    if repetitions < 3:
        raise ValueError("At least three warm repetitions are required.")
    from fastapi.testclient import TestClient

    from api.main import app

    requests = [
        ("summary", "GET", "/api/revenue-exposure/summary?horizon_days=30", None),
        ("customers", "GET", "/api/revenue-exposure/customers?horizon_days=30&page=1&page_size=25", None),
        ("scatter", "GET", "/api/revenue-exposure/scatter?horizon_days=30&limit=100", None),
        ("customer", "GET", "/api/customers/12346/revenue-exposure?horizon_days=30", None),
        ("concentration", "GET", "/api/revenue-exposure/concentration?horizon_days=30", None),
        ("evaluation", "GET", "/api/revenue-exposure/evaluation", None),
        (
            "scenario",
            "POST",
            "/api/retention/scenarios",
            {
                "horizon_days": 30,
                "campaign_budget_gbp": 100.0,
                "contact_cost_gbp": 2.0,
                "maximum_contacts": 50,
                "assumed_response_probability": 0.1,
                "assumed_purchase_uplift_if_responded": 0.05,
                "assumed_gross_margin_rate": None,
                "ranking_strategy": "nonreturn_spending_proxy",
                "eligibility_filters": {},
            },
        ),
        (
            "compare_strategies",
            "POST",
            "/api/retention/compare-strategies",
            {
                "scenario": {
                    "horizon_days": 30,
                    "campaign_budget_gbp": 100.0,
                    "contact_cost_gbp": 2.0,
                    "maximum_contacts": 50,
                    "assumed_response_probability": 0.1,
                    "assumed_purchase_uplift_if_responded": 0.05,
                    "assumed_gross_margin_rate": None,
                },
                "ranking_strategies": [
                    "historical_gross_spending",
                    "nonreturn_spending_proxy",
                ],
                "eligibility_filters": {},
            },
        ),
    ]
    timings: dict[str, Any] = {}
    with TestClient(app) as client:
        for name, method, path, body in requests:
            warm = (
                client.get(path)
                if method == "GET"
                else client.post(path, json=body)
            )
            if warm.status_code != 200:
                raise RuntimeError(
                    f"Warm-up request {path} returned {warm.status_code}: "
                    f"{warm.text[:500]}"
                )
            values = []
            status_codes = []
            for _ in range(repetitions):
                start = time.perf_counter()
                response = (
                    client.get(path)
                    if method == "GET"
                    else client.post(path, json=body)
                )
                values.append((time.perf_counter() - start) * 1000)
                status_codes.append(response.status_code)
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Warm request {path} returned {response.status_code}: "
                        f"{response.text[:500]}"
                    )
            timings[name] = {
                "path": path,
                "method": method,
                "status_codes": status_codes,
                "repetitions": repetitions,
                "median_ms": float(np.median(values)),
                "p95_ms": float(np.quantile(values, 0.95)),
                "measurement": "in-process FastAPI TestClient after warm-up",
            }
    result = {
        "status": "measured",
        "measurement_environment": "in-process FastAPI TestClient",
        "endpoints": timings,
    }
    profiling_path = (
        Path(project_root)
        / "data"
        / "metrics"
        / "revenue_exposure_profiling.json"
    )
    profiling = json.loads(profiling_path.read_text(encoding="utf-8"))
    profiling["warm_api"] = result
    _write_json(profiling_path, profiling)
    return result
