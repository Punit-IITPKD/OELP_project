"""Cached saved-model revenue exposure and retention-planning API services."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from api import service
from src.retention_planner import (
    EligibilityPolicy,
    RANKING_STRATEGIES,
    RetentionScenario,
    allocate_contact_budget,
    rank_retention_candidates,
    simulate_retention_scenario,
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

HORIZONS = (30, 60, 90)
SUPPORTED_BEHAVIOR_FILTERS = (
    "none",
    "declining_purchase_rate",
    "declining_revenue_rate",
)


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    return json.loads(
        frame.to_json(orient="records", date_format="iso")
    )


def _finite_or_none(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    number = float(value)
    return number if np.isfinite(number) else None


@lru_cache(maxsize=4)
def _read_json_artifact(path: str) -> dict[str, Any]:
    """Cache immutable research artifacts for warm API reads."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _attach_group_reliability(
    frame: pd.DataFrame,
    artifact: dict[str, Any],
) -> pd.DataFrame:
    lookup = {
        (str(item["group"]), int(item["horizon_days"])): item
        for item in artifact["evaluation"]["subgroups"]
        if item.get("group_type") == "history_group"
    }
    result = frame.copy()
    evidence = [
        lookup.get((str(group), int(horizon)))
        for group, horizon in zip(
            result["history_group"],
            result["horizon_days"],
            strict=True,
        )
    ]
    result["reliability_status"] = [
        item.get("status", "reliability_evidence_unavailable")
        if item
        else "reliability_evidence_unavailable"
        for item in evidence
    ]
    result["reliability_evidence_count"] = [
        int(item["customer_count"]) if item else 0 for item in evidence
    ]
    result["reliability_group_brier_score"] = [
        _finite_or_none(item.get("brier_score")) if item else None
        for item in evidence
    ]
    result["reliability_group_calibration_gap"] = [
        _finite_or_none(item.get("calibration_gap")) if item else None
        for item in evidence
    ]
    result["reliability_evidence_cutoff"] = artifact["metadata"]["forecast_cutoff"]
    result["reliability_is_individual_guarantee"] = False
    return result


@lru_cache(maxsize=1)
def get_revenue_forecasts() -> dict[int, pd.DataFrame]:
    """Build one forecast cohort per horizon from the existing cached bundle."""
    analytics = service.get_analytics()
    behavior = service._get_behavior_analytics().snapshot.copy()
    behavior = behavior.rename(columns={"Customer ID": "customer_id"})
    reliability = service.get_reliability_artifact()
    forecasts = {}
    behavior_columns = [
        "customer_id",
        "cutoff_date",
        "history_sufficiency",
        "purchase_rate_ratio",
        "revenue_rate_ratio",
        "gap_deviation_score",
        "policy_status",
        "available_indicator_count",
    ]
    behavior["cutoff_date"] = pd.to_datetime(behavior["cutoff_date"], errors="raise")
    for horizon in HORIZONS:
        frame = prepare_revenue_forecast_table(analytics.snapshot, horizon)
        frame = frame.merge(
            behavior.loc[:, behavior_columns],
            on=["customer_id", "cutoff_date"],
            how="left",
            validate="one_to_one",
            indicator="_behavior_match",
        )
        if not frame["_behavior_match"].eq("both").all():
            raise ValueError("Behavior indicators do not match the saved forecast cohort.")
        frame = frame.drop(columns="_behavior_match")
        frame = _attach_group_reliability(frame, reliability)
        frame = calculate_reference_exposure(frame, None, RevenueExposureConfig())
        frame = calculate_opportunity_proxy(frame, RevenueExposureConfig())
        forecasts[horizon] = frame
    return forecasts


def _check_horizon(horizon_days: int) -> int:
    if horizon_days not in HORIZONS:
        raise ValueError(f"horizon_days must be one of {HORIZONS}.")
    return int(horizon_days)


def _make_eligibility_policy(filters: dict[str, Any] | None) -> EligibilityPolicy:
    filters = filters or {}
    behavior_filter = filters.get("behavior_filter", "none")
    if behavior_filter not in SUPPORTED_BEHAVIOR_FILTERS:
        raise ValueError("Unsupported behavior_filter.")
    return EligibilityPolicy(
        hist_segments=(
            (str(filters["hist_segment"]),)
            if filters.get("hist_segment")
            else None
        ),
        history_groups=(
            (str(filters["history_group"]),)
            if filters.get("history_group")
            else None
        ),
        require_sufficient_behavior_history=bool(
            filters.get("require_sufficient_behavior_history", False)
        ),
        behavior_filter=behavior_filter,
    )


def _enriched_ranked_customers(
    horizon_days: int,
    strategy: str,
    filters: dict[str, Any] | None = None,
) -> pd.DataFrame:
    if strategy not in RANKING_STRATEGIES:
        raise ValueError(f"ranking_strategy must be one of {RANKING_STRATEGIES}.")
    forecasts = get_revenue_forecasts()[_check_horizon(horizon_days)]
    policy = _make_eligibility_policy(filters)
    ranking = rank_retention_candidates(forecasts, strategy, policy)
    if filters and filters.get("history_sufficiency"):
        ranking = ranking.loc[
            ranking["history_sufficiency"].eq(filters["history_sufficiency"])
        ].copy()
    ranking = ranking.reset_index(drop=True)
    ranking["priority_rank"] = np.arange(1, len(ranking) + 1)
    return ranking


def get_revenue_summary(horizon_days: int) -> dict[str, Any]:
    horizon = _check_horizon(horizon_days)
    frame = get_revenue_forecasts()[horizon]
    summary = summarize_portfolio_exposure(frame, RevenueExposureConfig())
    disagreement = compute_forecast_disagreement(frame, horizon)
    differences = [
        "historical_minus_personalized_forecast_difference_gbp",
        "segment_minus_personalized_forecast_difference_gbp",
    ]
    summary["forecast_disagreement"] = {
        column: {
            "portfolio_difference_gbp": _finite_or_none(disagreement[column].sum()),
            "median_customer_difference_gbp": _finite_or_none(
                disagreement[column].median()
            ),
            "median_absolute_customer_difference_gbp": _finite_or_none(
                disagreement[column].abs().median()
            ),
            "interpretation": "model disagreement, not revenue exposure",
        }
        for column in differences
    }
    summary["reliability_evidence_cutoff"] = frame[
        "reliability_evidence_cutoff"
    ].iloc[0]
    summary["reliability_group_coverage"] = int(
        frame["reliability_status"].ne("reliability_evidence_unavailable").sum()
    )
    summary["history_sufficiency_counts"] = (
        frame["history_sufficiency"].value_counts(dropna=False).to_dict()
    )
    return summary


def get_revenue_customers(
    horizon_days: int,
    *,
    page: int = 1,
    page_size: int = 25,
    ranking_strategy: str = "nonreturn_spending_proxy",
    filters: dict[str, Any] | None = None,
    search: str | None = None,
    sort_by: str = "priority_rank",
    sort_descending: bool = False,
) -> dict[str, Any]:
    ranking = _enriched_ranked_customers(
        horizon_days,
        ranking_strategy,
        filters,
    )
    sort_columns = {
        "priority_rank": "priority_rank",
        "customer_id": "customer_id",
        "recency_days": "recency_days",
        "purchase_probability": "purchase_probability",
        "conditional_expected_spending_gbp": "conditional_expected_spending_gbp",
        "personalized_expected_revenue_gbp": "personalized_expected_revenue_gbp",
        "nonreturn_weighted_conditional_spending_proxy_gbp": (
            "nonreturn_weighted_conditional_spending_proxy_gbp"
        ),
        "historical_gross_spending_gbp": "historical_gross_spending_gbp",
    }
    if sort_by not in sort_columns:
        raise ValueError(f"sort_by must be one of {tuple(sort_columns)}.")
    if search:
        query = search.strip()
        if query and not query.isdigit():
            raise ValueError("Customer search must contain digits only.")
        if query:
            ranking = ranking.loc[
                ranking["customer_id"].astype(str).str.contains(query, regex=False)
            ]
    ranking = ranking.sort_values(
        [sort_columns[sort_by], "customer_id"],
        ascending=[not sort_descending, True],
        kind="mergesort",
    )
    total = len(ranking)
    offset = (page - 1) * page_size
    items = ranking.iloc[offset : offset + page_size].copy()
    return {
        "horizon_days": int(horizon_days),
        "ranking_strategy": ranking_strategy,
        "items": _records(items),
        "total": total,
        "page": page,
        "page_size": page_size,
        "exposure_status": "not_estimable",
    }


def get_revenue_customer(
    customer_id: int,
    horizon_days: int,
) -> dict[str, Any]:
    horizon = _check_horizon(horizon_days)
    frame = get_revenue_forecasts()[horizon]
    match = frame.loc[frame["customer_id"].eq(customer_id)]
    if match.empty:
        raise KeyError(customer_id)
    result = _records(match)[0]
    result["limitations"] = [
        "Group calibration evidence does not guarantee this customer's forecast.",
        "The nonreturn-weighted spending value is a screening proxy, not lost or recoverable revenue.",
        "Revenue exposure is not estimable without a valid matched reference.",
        "Hypothetical campaign results do not estimate causal uplift.",
    ]
    return result


def get_revenue_scatter(
    horizon_days: int,
    *,
    limit: int = 1000,
    hist_segment: str | None = None,
    history_sufficiency: str | None = None,
) -> dict[str, Any]:
    horizon = _check_horizon(horizon_days)
    frame = get_revenue_forecasts()[horizon]
    if hist_segment:
        frame = frame.loc[frame["hist_segment"].eq(hist_segment)]
    if history_sufficiency:
        frame = frame.loc[frame["history_sufficiency"].eq(history_sufficiency)]
    frame = frame.sort_values("customer_id", kind="mergesort")
    if len(frame) > limit:
        indices = np.linspace(0, len(frame) - 1, num=limit, dtype=np.int64)
        frame = frame.iloc[np.unique(indices)]
    points = frame.loc[
        :,
        [
            "customer_id",
            "hist_segment",
            "history_group",
            "history_sufficiency",
            "purchase_probability",
            "nonreturn_probability",
            "historical_gross_spending_gbp",
            "conditional_expected_spending_gbp",
            "personalized_expected_revenue_gbp",
            "nonreturn_weighted_conditional_spending_proxy_gbp",
            "reliability_status",
            "exposure_status",
        ],
    ]
    return {
        "horizon_days": horizon,
        "x_axis": "nonreturn_probability",
        "y_axis": "conditional_expected_spending_gbp",
        "color_by": "hist_segment",
        "points": _records(points),
        "returned_points": int(len(points)),
        "eligible_customers": int(len(frame)),
        "point_selection": "deterministic evenly spaced sample from the filtered customer IDs",
        "interpretation": (
            "X is nonreturn probability and Y is conditional expected spending. "
            "Color is historical segment; exposure remains not estimable."
        ),
    }


def get_revenue_concentration(horizon_days: int) -> dict[str, Any]:
    horizon = _check_horizon(horizon_days)
    frame = get_revenue_forecasts()[horizon]
    rows = []
    for metric in (
        "historical_gross_spending_gbp",
        "personalized_expected_revenue_gbp",
        "historical_rate_expected_revenue_gbp",
        "segment_expected_revenue_gbp",
        "nonreturn_weighted_conditional_spending_proxy_gbp",
    ):
        concentration = calculate_exposure_concentration(frame, metric)
        records = _records(concentration)
        for item in records:
            item["metric"] = metric
        rows.extend(records)
    return {
        "horizon_days": horizon,
        "eligible_customers": int(len(frame)),
        "items": rows,
        "interpretation": "Concentration describes the selected metric, not causal loss or recoverable revenue.",
    }


def get_revenue_evaluation() -> dict[str, Any]:
    metrics_dir = service.PROJECT_ROOT / "data" / "metrics"
    artifact = metrics_dir / "revenue_exposure_evaluation.json"
    sensitivity_artifact = metrics_dir / "retention_scenario_sensitivity.json"
    if not artifact.is_file() or not sensitivity_artifact.is_file():
        raise FileNotFoundError(
            "Notebook 10 revenue-exposure evaluation artifact is unavailable."
        )
    payload = dict(_read_json_artifact(str(artifact)))
    if payload.get("metadata", {}).get("artifact_version") != "revenue-exposure-evaluation-v1":
        raise ValueError("Unsupported revenue-exposure evaluation artifact.")
    payload["scenario_sensitivity"] = _read_json_artifact(
        str(sensitivity_artifact)
    )
    return payload


def _selected_customer_details(
    selected_ids: list[int],
    horizon: int,
    scenario: RetentionScenario,
) -> list[dict[str, Any]]:
    frame = get_revenue_forecasts()[horizon].set_index("customer_id")
    rows = []
    for customer_id in selected_ids:
        customer = frame.loc[int(customer_id)]
        delta_probability = min(
            1.0 - float(customer["purchase_probability"]),
            scenario.assumed_response_probability
            * scenario.assumed_purchase_uplift_if_responded,
        )
        incremental_revenue = (
            delta_probability
            * float(customer["conditional_expected_spending_gbp"])
        )
        contribution = None
        if scenario.assumed_gross_margin_rate is not None:
            contribution = (
                incremental_revenue * scenario.assumed_gross_margin_rate
                - scenario.contact_cost_gbp
            )
        rows.append(
            {
                "customer_id": int(customer_id),
                "hist_segment": str(customer["hist_segment"]),
                "history_group": str(customer["history_group"]),
                "purchase_probability": float(customer["purchase_probability"]),
                "conditional_expected_spending_gbp": float(
                    customer["conditional_expected_spending_gbp"]
                ),
                "nonreturn_weighted_conditional_spending_proxy_gbp": float(
                    customer["nonreturn_weighted_conditional_spending_proxy_gbp"]
                ),
                "hypothetical_incremental_probability": delta_probability,
                "hypothetical_incremental_revenue_gbp": incremental_revenue,
                "hypothetical_incremental_contribution_gbp": contribution,
                "causal_estimate": False,
            }
        )
    return rows


def _run_scenario(
    scenario: RetentionScenario,
    ranking_strategy: str,
    eligibility_filters: dict[str, Any] | None,
) -> dict[str, Any]:
    horizon = _check_horizon(scenario.horizon_days)
    ranked = _enriched_ranked_customers(
        horizon,
        ranking_strategy,
        eligibility_filters,
    )
    allocation = allocate_contact_budget(
        ranked,
        scenario.campaign_budget_gbp,
        scenario.contact_cost_gbp,
        scenario.maximum_contacts,
    )
    simulation = simulate_retention_scenario(allocation, scenario)
    selected_ids = list(map(int, simulation["selected_customer_ids"]))
    simulation["selected_customers"] = _selected_customer_details(
        selected_ids,
        horizon,
        scenario,
    )
    simulation.pop("selected_customer_ids", None)
    simulation["ranking_strategy"] = ranking_strategy
    simulation["is_causal_estimate"] = False
    simulation["eligibility_filters"] = eligibility_filters or {}
    simulation["currency_code"] = "GBP"
    return simulation


def run_retention_scenario(
    scenario_payload: dict[str, Any],
    *,
    ranking_strategy: str,
    eligibility_filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if ranking_strategy not in RANKING_STRATEGIES:
        raise ValueError(f"ranking_strategy must be one of {RANKING_STRATEGIES}.")
    scenario = RetentionScenario(**scenario_payload)
    return _run_scenario(scenario, ranking_strategy, eligibility_filters)


def compare_retention_strategies(
    scenario_payload: dict[str, Any],
    ranking_strategies: list[str],
    eligibility_filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not ranking_strategies:
        raise ValueError("Select at least one ranking strategy.")
    if len(set(ranking_strategies)) != len(ranking_strategies):
        raise ValueError("Ranking strategies must be unique.")
    if any(strategy not in RANKING_STRATEGIES for strategy in ranking_strategies):
        raise ValueError(f"ranking_strategies must be chosen from {RANKING_STRATEGIES}.")
    scenario = RetentionScenario(**scenario_payload)
    results = [
        _run_scenario(scenario, strategy, eligibility_filters)
        for strategy in ranking_strategies
    ]
    return {
        "horizon_days": scenario.horizon_days,
        "scenario_assumptions": scenario_payload,
        "strategy_results": [
            {
                "ranking_strategy": result["ranking_strategy"],
                "selected_customer_count": result["selected_customer_count"],
                "campaign_cost_gbp": result["campaign_cost_gbp"],
                "budget_utilization": result["budget_utilization"],
                "hypothetical_incremental_revenue_gbp": result[
                    "hypothetical_incremental_revenue_gbp"
                ],
                "hypothetical_incremental_contribution_gbp": result[
                    "hypothetical_incremental_contribution_gbp"
                ],
                "break_even_information": result["break_even_information"],
                "causal_estimate": False,
                "selected_customers": result["selected_customers"],
                "limitations": result["limitations"],
            }
            for result in results
        ],
        "interpretation": (
            "Strategy results compare screening selections under shared assumptions; "
            "they do not predict causal campaign lift."
        ),
    }
