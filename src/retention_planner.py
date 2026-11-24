"""Deterministic screening rankings and hypothetical retention scenarios.

All campaign benefits are scenario calculations from explicit user assumptions.
No function in this module estimates treatment effects or causal uplift.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Literal

import numpy as np
import pandas as pd

SUPPORTED_HORIZONS = (30, 60, 90)
RANKING_STRATEGIES = (
    "historical_gross_spending",
    "recency_only",
    "nonreturn_probability",
    "conditional_expected_spending",
    "nonreturn_spending_proxy",
    "pareto_risk_value",
)
ALLOCATION_METHOD_RANKED = "deterministic_greedy_by_screening_rank"
ALLOCATION_METHOD_BENEFIT = "deterministic_greedy_by_hypothetical_benefit_per_cost"


def _money_to_pence(value: float, *, name: str) -> int:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"{name} must be a valid GBP amount.") from error
    if not amount.is_finite() or amount < 0:
        raise ValueError(f"{name} must be finite and non-negative.")
    pence = amount * 100
    if pence != pence.to_integral_value():
        raise ValueError(f"{name} must have no more than two decimal places.")
    return int(pence)


@dataclass(frozen=True)
class RetentionScenario:
    """User-specified hypothetical campaign assumptions, with money in GBP."""

    horizon_days: int
    campaign_budget_gbp: float
    contact_cost_gbp: float
    maximum_contacts: int
    assumed_response_probability: float
    assumed_purchase_uplift_if_responded: float
    assumed_gross_margin_rate: float | None = None

    def __post_init__(self) -> None:
        if isinstance(self.horizon_days, bool) or self.horizon_days not in SUPPORTED_HORIZONS:
            raise ValueError(f"horizon_days must be one of {SUPPORTED_HORIZONS}.")
        _money_to_pence(self.campaign_budget_gbp, name="campaign_budget_gbp")
        contact_pence = _money_to_pence(
            self.contact_cost_gbp, name="contact_cost_gbp"
        )
        if contact_pence <= 0:
            raise ValueError("contact_cost_gbp must be positive.")
        if (
            isinstance(self.maximum_contacts, bool)
            or not isinstance(self.maximum_contacts, int)
            or self.maximum_contacts < 0
        ):
            raise ValueError("maximum_contacts must be a non-negative integer.")
        for name in (
            "assumed_response_probability",
            "assumed_purchase_uplift_if_responded",
        ):
            value = float(getattr(self, name))
            if not np.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be finite and within [0, 1].")
        if self.assumed_gross_margin_rate is not None:
            margin = float(self.assumed_gross_margin_rate)
            if not np.isfinite(margin) or not 0 <= margin <= 1:
                raise ValueError(
                    "assumed_gross_margin_rate must be finite and within [0, 1]."
                )


@dataclass(frozen=True)
class EligibilityPolicy:
    """Optional, explicit data-availability filters; no numeric reliability weight."""

    hist_segments: tuple[str, ...] | None = None
    history_groups: tuple[str, ...] | None = None
    require_sufficient_behavior_history: bool = False
    behavior_filter: Literal[
        "none", "declining_purchase_rate", "declining_revenue_rate"
    ] = "none"

    def __post_init__(self) -> None:
        if self.hist_segments is not None and not self.hist_segments:
            raise ValueError("hist_segments cannot be an empty tuple.")
        if self.history_groups is not None and not self.history_groups:
            raise ValueError("history_groups cannot be an empty tuple.")
        if self.behavior_filter not in {
            "none",
            "declining_purchase_rate",
            "declining_revenue_rate",
        }:
            raise ValueError("Unsupported behavior_filter.")


def _finite_column(
    table: pd.DataFrame,
    column: str,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> np.ndarray:
    if column not in table:
        raise ValueError(f"customer_table is missing required column {column!r}.")
    values = pd.to_numeric(table[column], errors="raise").to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError(f"{column} must contain only finite values.")
    if minimum is not None and (values < minimum).any():
        raise ValueError(f"{column} must be at least {minimum}.")
    if maximum is not None and (values > maximum).any():
        raise ValueError(f"{column} must be at most {maximum}.")
    return values


def _eligibility_mask(
    table: pd.DataFrame,
    policy: EligibilityPolicy,
) -> np.ndarray:
    eligible = np.ones(len(table), dtype=bool)
    if policy.hist_segments is not None:
        if "hist_segment" not in table:
            raise ValueError("hist_segment is required for the requested segment filter.")
        eligible &= table["hist_segment"].isin(policy.hist_segments).to_numpy()
    if policy.history_groups is not None:
        if "history_group" not in table:
            raise ValueError("history_group is required for the requested history filter.")
        eligible &= table["history_group"].isin(policy.history_groups).to_numpy()
    if policy.require_sufficient_behavior_history:
        if "history_sufficiency" not in table:
            raise ValueError(
                "history_sufficiency is required for the requested support filter."
            )
        eligible &= table["history_sufficiency"].eq("sufficient").to_numpy()
    if policy.behavior_filter == "declining_purchase_rate":
        if "purchase_rate_ratio" not in table:
            raise ValueError(
                "purchase_rate_ratio is required for the requested behavior filter."
            )
        ratio = pd.to_numeric(table["purchase_rate_ratio"], errors="coerce").to_numpy(
            dtype=float
        )
        eligible &= np.isfinite(ratio) & (ratio < 1)
    elif policy.behavior_filter == "declining_revenue_rate":
        if "revenue_rate_ratio" not in table:
            raise ValueError(
                "revenue_rate_ratio is required for the requested behavior filter."
            )
        ratio = pd.to_numeric(table["revenue_rate_ratio"], errors="coerce").to_numpy(
            dtype=float
        )
        eligible &= np.isfinite(ratio) & (ratio < 1)
    return eligible


def _pareto_fronts(
    customer_ids: np.ndarray,
    risk: np.ndarray,
    value: np.ndarray,
) -> np.ndarray:
    """Return exact nondominated-front numbers in O(n log n), front one is best."""
    count = len(customer_ids)
    if count == 0:
        return np.empty(0, dtype=np.int64)
    unique_values = np.unique(value)
    value_positions = len(unique_values) - np.searchsorted(
        unique_values, value, side="left"
    )
    order = np.lexsort((customer_ids, -value, -risk))
    tree = np.zeros(len(unique_values) + 1, dtype=np.int64)
    fronts = np.zeros(count, dtype=np.int64)

    def query(position: int) -> int:
        best = 0
        while position > 0:
            best = max(best, int(tree[position]))
            position -= position & -position
        return best

    def update(position: int, front: int) -> None:
        while position < len(tree):
            tree[position] = max(tree[position], front)
            position += position & -position

    cursor = 0
    while cursor < count:
        first = order[cursor]
        end = cursor + 1
        while (
            end < count
            and risk[order[end]] == risk[first]
            and value[order[end]] == value[first]
        ):
            end += 1
        group = order[cursor:end]
        front = query(int(value_positions[first])) + 1
        fronts[group] = front
        update(int(value_positions[first]), front)
        cursor = end
    return fronts


def rank_retention_candidates(
    customer_table: pd.DataFrame,
    strategy: str,
    eligibility_policy: EligibilityPolicy | None = None,
) -> pd.DataFrame:
    """Return eligible customers in a deterministic screening order.

    The Pareto strategy orders customers by nondominated risk/value fronts,
    without converting either dimension into an invented monetary weight.
    """
    if strategy not in RANKING_STRATEGIES:
        raise ValueError(f"strategy must be one of {RANKING_STRATEGIES}.")
    policy = eligibility_policy or EligibilityPolicy()
    if not isinstance(policy, EligibilityPolicy):
        raise TypeError("eligibility_policy must be an EligibilityPolicy.")
    future_target_columns = [
        column
        for column in customer_table.columns
        if column == "purchased"
        or column.startswith("Purchased_")
        or column.startswith("FutureRevenue_")
        or column.startswith("FutureOrders_")
        or column == "observed_future_revenue_gbp"
    ]
    if future_target_columns:
        raise ValueError(
            "Ranking inputs cannot include future outcomes: "
            f"{future_target_columns}"
        )
    if "customer_id" not in customer_table:
        raise ValueError("customer_table is missing required column 'customer_id'.")
    result = customer_table.copy()
    if result["customer_id"].isna().any() or result["customer_id"].duplicated().any():
        raise ValueError("customer_id must be non-missing and unique.")
    result["customer_id"] = pd.to_numeric(
        result["customer_id"], errors="raise"
    ).astype("int64")

    probability = _finite_column(
        result, "purchase_probability", minimum=0, maximum=1
    )
    value = _finite_column(
        result, "conditional_expected_spending_gbp", minimum=0
    )
    _finite_column(result, "historical_gross_spending_gbp", minimum=0)
    _finite_column(result, "recency_days", minimum=0)
    _finite_column(
        result, "nonreturn_weighted_conditional_spending_proxy_gbp", minimum=0
    )
    result["nonreturn_probability"] = 1.0 - probability
    result["selection_eligible"] = _eligibility_mask(result, policy)
    result["ranking_strategy"] = strategy
    eligible = result.loc[result["selection_eligible"]].copy()
    if strategy == "historical_gross_spending":
        score_column = "historical_gross_spending_gbp"
        eligible["priority_score"] = eligible[score_column].to_numpy(dtype=float)
        eligible["priority_score_unit"] = "GBP historical gross spending"
        ordered = eligible.sort_values(
            ["priority_score", "customer_id"],
            ascending=[False, True],
            kind="mergesort",
        )
    elif strategy == "recency_only":
        eligible["priority_score"] = eligible["recency_days"].to_numpy(dtype=float)
        eligible["priority_score_unit"] = "days since last purchase"
        ordered = eligible.sort_values(
            ["priority_score", "customer_id"],
            ascending=[False, True],
            kind="mergesort",
        )
    elif strategy == "nonreturn_probability":
        eligible["priority_score"] = eligible["nonreturn_probability"].to_numpy(
            dtype=float
        )
        eligible["priority_score_unit"] = "probability"
        ordered = eligible.sort_values(
            ["priority_score", "customer_id"],
            ascending=[False, True],
            kind="mergesort",
        )
    elif strategy == "conditional_expected_spending":
        eligible["priority_score"] = value[result["selection_eligible"].to_numpy()]
        eligible["priority_score_unit"] = "GBP conditional spending"
        ordered = eligible.sort_values(
            ["priority_score", "customer_id"],
            ascending=[False, True],
            kind="mergesort",
        )
    elif strategy == "nonreturn_spending_proxy":
        eligible["priority_score"] = eligible[
            "nonreturn_weighted_conditional_spending_proxy_gbp"
        ].to_numpy(dtype=float)
        eligible["priority_score_unit"] = "GBP screening proxy; not recoverable revenue"
        ordered = eligible.sort_values(
            ["priority_score", "customer_id"],
            ascending=[False, True],
            kind="mergesort",
        )
    else:
        risk = eligible["nonreturn_probability"].to_numpy(dtype=float)
        spending = eligible["conditional_expected_spending_gbp"].to_numpy(dtype=float)
        fronts = _pareto_fronts(
            eligible["customer_id"].to_numpy(dtype=np.int64), risk, spending
        )
        eligible["pareto_front"] = fronts
        eligible["priority_score"] = -fronts.astype(float)
        eligible["priority_score_unit"] = "negative ordinal Pareto front"
        ordered = eligible.sort_values(
            [
                "pareto_front",
                "nonreturn_probability",
                "conditional_expected_spending_gbp",
                "customer_id",
            ],
            ascending=[True, False, False, True],
            kind="mergesort",
        )
    ordered["priority_rank"] = np.arange(1, len(ordered) + 1, dtype=np.int64)
    return ordered.reset_index(drop=True)


def _contact_costs_pence(
    ranked_candidates: pd.DataFrame,
    contact_costs: float | pd.Series | str,
) -> np.ndarray:
    if isinstance(contact_costs, str):
        if contact_costs not in ranked_candidates:
            raise ValueError(f"Missing contact-cost column {contact_costs!r}.")
        values = ranked_candidates[contact_costs].to_numpy(dtype=float)
    elif isinstance(contact_costs, pd.Series):
        if not contact_costs.index.equals(ranked_candidates.index):
            raise ValueError("contact_costs Series must align with ranked_candidates.")
        values = contact_costs.to_numpy(dtype=float)
    else:
        values = np.full(len(ranked_candidates), float(contact_costs), dtype=float)
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("Every contact cost must be finite and positive.")
    return np.asarray(
        [_money_to_pence(value, name="contact_cost_gbp") for value in values],
        dtype=np.int64,
    )


def allocate_contact_budget(
    ranked_candidates: pd.DataFrame,
    campaign_budget_gbp: float,
    contact_costs: float | pd.Series | str,
    maximum_contacts: int,
    *,
    allocation_objective: Literal[
        "screening_rank", "hypothetical_benefit_per_cost"
    ] = "screening_rank",
) -> pd.DataFrame:
    """Select a deterministic budget-feasible cohort.

    Equal-cost contacts use the exact affordable-contact formula. For variable
    costs, an explicit benefit column is required for the deterministic greedy
    benefit-per-cost baseline; it is not a globally optimal knapsack solution.
    """
    budget_pence = _money_to_pence(
        campaign_budget_gbp, name="campaign_budget_gbp"
    )
    if (
        isinstance(maximum_contacts, bool)
        or not isinstance(maximum_contacts, int)
        or maximum_contacts < 0
    ):
        raise ValueError("maximum_contacts must be a non-negative integer.")
    if "customer_id" not in ranked_candidates:
        raise ValueError("ranked_candidates is missing 'customer_id'.")
    if ranked_candidates["customer_id"].duplicated().any():
        raise ValueError("ranked_candidates must have unique customer_id values.")
    cost_pence = _contact_costs_pence(ranked_candidates, contact_costs)
    if ranked_candidates.empty or budget_pence == 0 or maximum_contacts == 0:
        result = ranked_candidates.iloc[0:0].copy()
        result["contact_cost_gbp"] = pd.Series(dtype=float)
        result["cumulative_contact_cost_gbp"] = pd.Series(dtype=float)
        result["allocation_method"] = (
            ALLOCATION_METHOD_RANKED
            if allocation_objective == "screening_rank"
            else ALLOCATION_METHOD_BENEFIT
        )
        result["selection_is_globally_optimal"] = False
        return result

    equal_costs = bool(np.all(cost_pence == cost_pence[0]))
    if equal_costs:
        if allocation_objective != "screening_rank":
            raise ValueError(
                "Equal-cost contacts use the documented screening-rank order."
            )
        affordable = min(maximum_contacts, budget_pence // int(cost_pence[0]))
        selected_positions = np.arange(min(affordable, len(ranked_candidates)))
        method = ALLOCATION_METHOD_RANKED
    else:
        if allocation_objective != "hypothetical_benefit_per_cost":
            raise ValueError(
                "Variable-cost allocation requires the explicit "
                "hypothetical_benefit_per_cost objective."
            )
        benefit_column = (
            "hypothetical_incremental_contribution_gbp"
            if "hypothetical_incremental_contribution_gbp" in ranked_candidates
            else "hypothetical_incremental_revenue_gbp"
        )
        if benefit_column not in ranked_candidates:
            raise ValueError(
                "Variable-cost greedy allocation requires a scenario benefit column."
            )
        benefit = _finite_column(ranked_candidates, benefit_column, minimum=0)
        efficiency = benefit / (cost_pence.astype(float) / 100.0)
        ordered_positions = np.lexsort(
            (
                ranked_candidates["customer_id"].to_numpy(dtype=np.int64),
                -benefit,
                -efficiency,
            )
        )
        selected: list[int] = []
        remaining = budget_pence
        for position in ordered_positions:
            if len(selected) >= maximum_contacts:
                break
            if cost_pence[position] <= remaining:
                selected.append(int(position))
                remaining -= int(cost_pence[position])
        selected_positions = np.asarray(selected, dtype=np.int64)
        method = ALLOCATION_METHOD_BENEFIT

    result = ranked_candidates.iloc[selected_positions].copy()
    selected_cost = cost_pence[selected_positions]
    cumulative = np.cumsum(selected_cost, dtype=np.int64)
    if int(selected_cost.sum()) > budget_pence:
        raise AssertionError("Contact allocation exceeded campaign_budget_gbp.")
    result["contact_cost_gbp"] = selected_cost.astype(float) / 100.0
    result["cumulative_contact_cost_gbp"] = cumulative.astype(float) / 100.0
    result["allocation_method"] = method
    result["selection_is_globally_optimal"] = False
    return result.reset_index(drop=True)


def _scenario_break_even_summary(
    selected_customers: pd.DataFrame,
    scenario: RetentionScenario,
) -> dict[str, object]:
    """Solve hypothetical response/uplift thresholds under a supplied margin.

    The values are scenario thresholds, not experimentally estimated rates.
    """
    if not isinstance(scenario, RetentionScenario):
        raise TypeError("scenario must be a RetentionScenario.")
    required = ["purchase_probability", "conditional_expected_spending_gbp"]
    missing = [column for column in required if column not in selected_customers]
    if missing:
        raise ValueError(
            f"selected_customers is missing required columns: {missing}"
        )
    if scenario.assumed_gross_margin_rate is None:
        return {
            "status": "margin_not_supplied",
            "contact_cost_gbp": 0.0,
            "maximum_possible_contribution_gbp": None,
            "minimum_response_probability_for_break_even": None,
            "minimum_purchase_uplift_if_responded_for_break_even": None,
            "interpretation": (
                "Break-even contribution cannot be calculated without a gross-margin "
                "assumption; revenue and contact cost remain separate."
            ),
        }
    if selected_customers.empty:
        return {
            "status": "no_contacts",
            "contact_cost_gbp": 0.0,
            "maximum_possible_contribution_gbp": 0.0,
            "minimum_response_probability_for_break_even": None,
            "minimum_purchase_uplift_if_responded_for_break_even": None,
            "interpretation": "No contacts were selected, so there is no campaign break-even threshold.",
        }

    probability = _finite_column(
        selected_customers, "purchase_probability", minimum=0, maximum=1
    )
    conditional = _finite_column(
        selected_customers, "conditional_expected_spending_gbp", minimum=0
    )
    contact_cost = (
        len(selected_customers)
        * _money_to_pence(scenario.contact_cost_gbp, name="contact_cost_gbp")
        / 100.0
    )
    margin = float(scenario.assumed_gross_margin_rate)
    per_customer = calculate_break_even_conditions(
        selected_customers,
        scenario.contact_cost_gbp,
        margin,
        assumed_response_probability=scenario.assumed_response_probability,
    )
    feasible_count = int(
        per_customer["break_even_feasible_under_supplied_assumptions"]
        .fillna(False)
        .astype(bool)
        .sum()
    )
    required_increment = pd.to_numeric(
        per_customer["required_purchase_probability_increment"], errors="coerce"
    )
    median_required_uplift = pd.to_numeric(
        per_customer["required_purchase_uplift_if_responded"], errors="coerce"
    )
    maximum_revenue = float(np.dot(1.0 - probability, conditional))
    maximum_contribution = margin * maximum_revenue - contact_cost
    scenario_increment = np.minimum(
        1.0 - probability,
        scenario.assumed_response_probability
        * scenario.assumed_purchase_uplift_if_responded,
    )
    scenario_contribution = (
        margin * float(np.dot(scenario_increment, conditional)) - contact_cost
    )

    def minimum_factor(other_factor: float) -> float | None:
        if other_factor <= 0:
            return None
        def contribution_at(factor: float) -> float:
            delta = np.minimum(1.0 - probability, factor * other_factor)
            return margin * float(np.dot(delta, conditional)) - contact_cost

        if contribution_at(0.0) >= 0:
            return 0.0
        if contribution_at(1.0) < 0:
            return None
        low, high = 0.0, 1.0
        for _ in range(64):
            midpoint = (low + high) / 2
            if contribution_at(midpoint) >= 0:
                high = midpoint
            else:
                low = midpoint
        return high

    required_response = minimum_factor(
        scenario.assumed_purchase_uplift_if_responded
    )
    required_uplift_threshold = minimum_factor(
        scenario.assumed_response_probability
    )
    feasible = maximum_contribution >= -1e-9
    return {
        "status": (
            "break_even_reached"
            if scenario_contribution >= -1e-9
            else "break_even_not_reached"
            if feasible
            else "infeasible_under_supplied_margin"
        ),
        "contact_cost_gbp": float(contact_cost),
        "scenario_contribution_gbp": float(scenario_contribution),
        "maximum_possible_contribution_gbp": float(maximum_contribution),
        "minimum_response_probability_for_break_even": required_response,
        "minimum_purchase_uplift_if_responded_for_break_even": (
            required_uplift_threshold
        ),
        "individual_feasible_contact_count": feasible_count,
        "median_required_purchase_probability_increment": (
            float(required_increment.median())
            if required_increment.notna().any()
            else None
        ),
        "median_required_purchase_uplift_if_responded": (
            float(median_required_uplift.median())
            if median_required_uplift.notna().any()
            else None
        ),
        "interpretation": (
            "Thresholds solve the supplied hypothetical revenue and margin equations; "
            "they are not measured response rates or treatment effects."
        ),
    }


def simulate_retention_scenario(
    selected_customers: pd.DataFrame,
    scenario: RetentionScenario,
) -> dict[str, object]:
    """Calculate hypothetical incremental revenue under explicit assumptions."""
    if not isinstance(scenario, RetentionScenario):
        raise TypeError("scenario must be a RetentionScenario.")
    required = [
        "customer_id",
        "purchase_probability",
        "conditional_expected_spending_gbp",
    ]
    missing = [column for column in required if column not in selected_customers]
    if missing:
        raise ValueError(f"selected_customers is missing required columns: {missing}")
    if selected_customers["customer_id"].duplicated().any():
        raise ValueError("selected_customers must have unique customer_id values.")
    if len(selected_customers) > scenario.maximum_contacts:
        raise ValueError("Selected customer count exceeds maximum_contacts.")
    pence = _money_to_pence(
        scenario.contact_cost_gbp, name="contact_cost_gbp"
    )
    total_cost_pence = len(selected_customers) * pence
    budget_pence = _money_to_pence(
        scenario.campaign_budget_gbp, name="campaign_budget_gbp"
    )
    if total_cost_pence > budget_pence:
        raise ValueError("Selected contact costs exceed the campaign budget.")
    probability = _finite_column(
        selected_customers, "purchase_probability", minimum=0, maximum=1
    )
    conditional = _finite_column(
        selected_customers, "conditional_expected_spending_gbp", minimum=0
    )
    increment = np.minimum(
        1.0 - probability,
        scenario.assumed_response_probability
        * scenario.assumed_purchase_uplift_if_responded,
    )
    hypothetical_revenue = float(np.dot(increment, conditional))
    contact_cost = total_cost_pence / 100.0
    contribution = (
        float(scenario.assumed_gross_margin_rate) * hypothetical_revenue
        - contact_cost
        if scenario.assumed_gross_margin_rate is not None
        else None
    )
    break_even = _scenario_break_even_summary(selected_customers, scenario)
    selected_ids = selected_customers["customer_id"].astype(int).tolist()
    return {
        "assumptions": {
            "horizon_days": scenario.horizon_days,
            "campaign_budget_gbp": budget_pence / 100.0,
            "contact_cost_gbp": pence / 100.0,
            "maximum_contacts": scenario.maximum_contacts,
            "assumed_response_probability": float(
                scenario.assumed_response_probability
            ),
            "assumed_purchase_uplift_if_responded": float(
                scenario.assumed_purchase_uplift_if_responded
            ),
            "assumed_gross_margin_rate": scenario.assumed_gross_margin_rate,
        },
        "selected_customer_count": len(selected_ids),
        "selected_customer_ids": selected_ids,
        "campaign_cost_gbp": contact_cost,
        "budget_remaining_gbp": (budget_pence - total_cost_pence) / 100.0,
        "budget_utilization": (
            total_cost_pence / budget_pence if budget_pence else 0.0
        ),
        "hypothetical_incremental_revenue_gbp": hypothetical_revenue,
        "hypothetical_incremental_contribution_gbp": contribution,
        "break_even_information": break_even,
        "causal_estimate": False,
        "selection_method": "user-defined ranking and hypothetical scenario assumptions",
        "limitations": [
            "Response probability and conditional purchase uplift are hypothetical assumptions, not learned treatment effects.",
            "No randomized intervention data are available; selected customers are not proven persuadable.",
            "Without a gross-margin assumption, incremental revenue is not net profit or contribution.",
            "Conditional expected spending in a nonpurchase scenario is a screening simplification.",
        ],
    }


def compare_retention_strategies(
    forecasts: pd.DataFrame,
    scenarios: list[RetentionScenario],
    strategies: tuple[str, ...] = RANKING_STRATEGIES,
) -> pd.DataFrame:
    """Compare ranking orders under explicit scenarios without refitting models."""
    if not scenarios:
        raise ValueError("At least one RetentionScenario is required.")
    unknown = sorted(set(strategies).difference(RANKING_STRATEGIES))
    if unknown:
        raise ValueError(f"Unknown ranking strategies: {unknown}")
    rankings = {
        strategy: rank_retention_candidates(forecasts, strategy)
        for strategy in strategies
    }
    rows: list[dict[str, object]] = []
    for scenario_index, scenario in enumerate(scenarios):
        if not isinstance(scenario, RetentionScenario):
            raise TypeError("scenarios must contain RetentionScenario objects.")
        for strategy in strategies:
            ranked = rankings[strategy]
            allocation = allocate_contact_budget(
                ranked,
                scenario.campaign_budget_gbp,
                scenario.contact_cost_gbp,
                scenario.maximum_contacts,
            )
            simulated = simulate_retention_scenario(allocation, scenario)
            rows.append(
                {
                    "scenario_index": scenario_index,
                    "horizon_days": scenario.horizon_days,
                    "ranking_strategy": strategy,
                    "selected_customer_count": simulated["selected_customer_count"],
                    "campaign_cost_gbp": simulated["campaign_cost_gbp"],
                    "budget_remaining_gbp": simulated["budget_remaining_gbp"],
                    "budget_utilization": simulated["budget_utilization"],
                    "hypothetical_incremental_revenue_gbp": simulated[
                        "hypothetical_incremental_revenue_gbp"
                    ],
                    "hypothetical_incremental_contribution_gbp": simulated[
                        "hypothetical_incremental_contribution_gbp"
                    ],
                    "causal_estimate": False,
                }
            )
    return pd.DataFrame(rows)


def calculate_break_even_conditions(
    forecasts: pd.DataFrame,
    contact_costs: float | pd.Series | str,
    margin_assumptions: float | pd.Series | str | None,
    *,
    assumed_response_probability: float | None = None,
) -> pd.DataFrame:
    """Calculate scenario break-even requirements, never empirical uplift.

    With a supplied gross margin, the method reports the purchase-probability
    increment needed to cover contact cost. If response probability is supplied,
    it also reports the required conditional uplift. Without margin, contribution
    break-even is explicitly unavailable.
    """
    required = [
        "customer_id",
        "purchase_probability",
        "conditional_expected_spending_gbp",
    ]
    missing = [column for column in required if column not in forecasts]
    if missing:
        raise ValueError(f"forecasts is missing required columns: {missing}")
    if isinstance(contact_costs, str):
        costs = _finite_column(forecasts, contact_costs, minimum=0)
    elif isinstance(contact_costs, pd.Series):
        if not contact_costs.index.equals(forecasts.index):
            raise ValueError("contact_costs Series must align with forecasts.")
        costs = pd.to_numeric(contact_costs, errors="raise").to_numpy(dtype=float)
    else:
        costs = np.full(len(forecasts), float(contact_costs), dtype=float)
    if not np.isfinite(costs).all() or (costs <= 0).any():
        raise ValueError("Contact costs must be finite and positive.")
    probability = _finite_column(
        forecasts, "purchase_probability", minimum=0, maximum=1
    )
    spending = _finite_column(
        forecasts, "conditional_expected_spending_gbp", minimum=0
    )
    result = forecasts.loc[:, ["customer_id"]].copy()
    result["contact_cost_gbp"] = costs
    if margin_assumptions is None:
        result["status"] = "not_estimable_without_margin"
        result["required_purchase_probability_increment"] = np.nan
        result["maximum_feasible_purchase_probability_increment"] = 1 - probability
        result["required_purchase_uplift_if_responded"] = np.nan
        result["break_even_feasible_under_supplied_assumptions"] = pd.NA
        return result
    if isinstance(margin_assumptions, str):
        margins = _finite_column(
            forecasts, margin_assumptions, minimum=0, maximum=1
        )
    elif isinstance(margin_assumptions, pd.Series):
        if not margin_assumptions.index.equals(forecasts.index):
            raise ValueError("margin_assumptions Series must align with forecasts.")
        margins = pd.to_numeric(
            margin_assumptions, errors="raise"
        ).to_numpy(dtype=float)
    else:
        margins = np.full(len(forecasts), float(margin_assumptions), dtype=float)
    if not np.isfinite(margins).all() or ((margins < 0) | (margins > 1)).any():
        raise ValueError("Gross margin assumptions must be finite and within [0, 1].")
    denominator = margins * spending
    required_increment = np.divide(
        costs,
        denominator,
        out=np.full(len(costs), np.nan, dtype=float),
        where=denominator > 0,
    )
    max_increment = 1.0 - probability
    feasible = np.isfinite(required_increment) & (required_increment <= max_increment)
    result["status"] = np.where(
        feasible,
        "mathematically_feasible_under_assumptions",
        "infeasible_or_zero_expected_margin",
    )
    result["assumed_gross_margin_rate"] = margins
    result["required_purchase_probability_increment"] = required_increment
    result["maximum_feasible_purchase_probability_increment"] = max_increment
    result["break_even_feasible_under_supplied_assumptions"] = feasible
    if assumed_response_probability is not None:
        response = float(assumed_response_probability)
        if not np.isfinite(response) or not 0 <= response <= 1:
            raise ValueError("assumed_response_probability must be within [0, 1].")
        result["required_purchase_uplift_if_responded"] = np.divide(
            required_increment,
            response,
            out=np.full(len(costs), np.nan, dtype=float),
            where=response > 0,
        )
        required_uplift = result[
            "required_purchase_uplift_if_responded"
        ].to_numpy(dtype=float)
        result["break_even_feasible_under_supplied_assumptions"] = (
            feasible & np.isfinite(required_uplift) & (required_uplift <= 1)
        )
        result["assumed_response_probability"] = response
    else:
        result["required_purchase_uplift_if_responded"] = np.nan
    result["limitations"] = (
        "Break-even is algebraic under supplied margin and response assumptions; it is not an observed conversion rate."
    )
    return result
