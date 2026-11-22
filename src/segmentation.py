"""Reusable full-period descriptive customer segmentation.

This is intentionally separate from ``temporal_framework``'s TRAIN-only
historical segmentation transform. It reproduces Notebook 04's descriptive
full-Year-1 RFM analysis and must not be used as a predictive cutoff transform.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

RFM_COLUMNS = ("Recency", "Frequency", "Monetary_Gross")
LOG_COLUMNS = ("log1p_Recency", "log1p_Frequency", "log1p_Monetary")
RANDOM_STATE = 42
N_INIT = 20
MAX_ITER = 500
DEFAULT_INACTIVITY_THRESHOLD_DAYS = 101.9


@dataclass
class DescriptiveSegmentation:
    """Descriptive labels, profiles, and fitted RFM transform."""

    customers: pd.DataFrame
    profiles: pd.DataFrame
    scaler: StandardScaler
    kmeans: KMeans
    segment_names: dict[int, str]
    metrics: dict[str, float]


def _validated_rfm(features: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(features, pd.DataFrame) or features.empty:
        raise ValueError("customer_features must be a non-empty DataFrame.")
    required = ["Customer ID", *RFM_COLUMNS]
    missing = [column for column in required if column not in features]
    if missing:
        raise ValueError(f"customer_features is missing required columns: {missing}")
    data = features.copy()
    if data["Customer ID"].isna().any() or data["Customer ID"].duplicated().any():
        raise ValueError("Customer ID must be present and unique for descriptive segmentation.")
    for column in RFM_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="raise")
        values = data[column].to_numpy(dtype=float)
        if not np.isfinite(values).all() or (values < 0).any():
            raise ValueError(f"{column} must contain finite non-negative values.")
    if data["Recency"].lt(1).any() or data["Frequency"].lt(1).any():
        raise ValueError("Recency and Frequency must be at least one.")
    return data.reset_index(drop=True)


def evaluate_kmeans_candidates(
    customer_features: pd.DataFrame,
    cluster_counts: Iterable[int] = range(2, 11),
    *,
    random_state: int = RANDOM_STATE,
    n_init: int = N_INIT,
    max_iter: int = MAX_ITER,
) -> pd.DataFrame:
    """Evaluate the Notebook 04 log1p-RFM K-Means candidates."""
    data = _validated_rfm(customer_features)
    values = data.loc[:, RFM_COLUMNS].to_numpy(dtype=float)
    log_values = np.log1p(values)
    scaler = StandardScaler().fit(log_values)
    scaled = scaler.transform(log_values)
    rows = []
    for k in cluster_counts:
        if int(k) != k or k < 2 or k >= len(data):
            raise ValueError(f"Each cluster count must be an integer in [2, n-1]; got {k}.")
        model = KMeans(
            n_clusters=int(k),
            random_state=random_state,
            n_init=n_init,
            max_iter=max_iter,
        )
        labels = model.fit_predict(scaled)
        rows.append(
            {
                "K": int(k),
                "Inertia": round(float(model.inertia_), 2),
                "Silhouette": round(
                    float(silhouette_score(scaled, labels, random_state=random_state)), 6
                ),
                "DaviesBouldin": round(float(davies_bouldin_score(scaled, labels)), 6),
                "CalinskiHarabasz": round(
                    float(calinski_harabasz_score(scaled, labels)), 2
                ),
            }
        )
    if not rows:
        raise ValueError("At least one cluster count must be evaluated.")
    return pd.DataFrame(rows)


def select_cluster_count(
    metrics: pd.DataFrame,
    customer_features: pd.DataFrame,
    *,
    minimum_cluster_pct: float = 2.0,
    random_state: int = RANDOM_STATE,
    n_init: int = N_INIT,
    max_iter: int = MAX_ITER,
) -> int:
    """Apply Notebook 04's metric-vote and minimum-cluster-size rule."""
    required = {"K", "Silhouette", "DaviesBouldin", "CalinskiHarabasz"}
    missing = sorted(required.difference(metrics.columns))
    if missing:
        raise ValueError(f"metrics is missing required columns: {missing}")
    if not 0 < minimum_cluster_pct < 50:
        raise ValueError("minimum_cluster_pct must be between 0 and 50.")
    data = _validated_rfm(customer_features)
    if len(metrics) < 1:
        raise ValueError("metrics must contain at least one candidate.")
    candidates = set(pd.to_numeric(metrics["K"], errors="raise").astype(int))
    best_sil = int(metrics.loc[metrics["Silhouette"].idxmax(), "K"])
    best_db = int(metrics.loc[metrics["DaviesBouldin"].idxmin(), "K"])
    best_ch = int(metrics.loc[metrics["CalinskiHarabasz"].idxmax(), "K"])
    votes = [best_sil, best_db, best_ch]
    majority_k = Counter(votes).most_common(1)[0][0]
    values = np.log1p(data.loc[:, RFM_COLUMNS].to_numpy(dtype=float))
    scaled = StandardScaler().fit_transform(values)

    def minimum_pct(k: int) -> float:
        labels = KMeans(
            n_clusters=k,
            random_state=random_state,
            n_init=n_init,
            max_iter=max_iter,
        ).fit_predict(scaled)
        return 100.0 * pd.Series(labels).value_counts().min() / len(labels)

    if minimum_pct(majority_k) >= minimum_cluster_pct:
        return majority_k
    alternatives = sorted(candidates.union({3, 4}))
    for alternative in alternatives:
        if alternative < len(data) and minimum_pct(alternative) >= minimum_cluster_pct:
            return alternative
    raise ValueError("No evaluated cluster count satisfies the minimum cluster-size rule.")


def fit_descriptive_segmentation(
    customer_features: pd.DataFrame,
    *,
    n_clusters: int = 2,
    inactivity_threshold_days: float = DEFAULT_INACTIVITY_THRESHOLD_DAYS,
    random_state: int = RANDOM_STATE,
    n_init: int = N_INIT,
    max_iter: int = MAX_ITER,
) -> DescriptiveSegmentation:
    """Fit Notebook 04's descriptive log1p-RFM StandardScaler + K-Means model.

    Average order value, inter-purchase gaps, cancellations, and the at-risk
    flag are not clustering inputs. Segment names are assigned after fitting,
    in ascending median-recency order.
    """
    data = _validated_rfm(customer_features)
    if n_clusters < 2 or n_clusters >= len(data):
        raise ValueError("n_clusters must be between 2 and the number of customers - 1.")
    if not np.isfinite(inactivity_threshold_days) or inactivity_threshold_days < 0:
        raise ValueError("inactivity_threshold_days must be finite and non-negative.")

    log_frame = pd.DataFrame(
        np.log1p(data.loc[:, RFM_COLUMNS].to_numpy(dtype=float)),
        columns=LOG_COLUMNS,
        index=data.index,
    )
    scaler = StandardScaler()
    scaled = scaler.fit_transform(log_frame)
    model = KMeans(
        n_clusters=int(n_clusters),
        random_state=random_state,
        n_init=n_init,
        max_iter=max_iter,
    )
    raw_labels = model.fit_predict(scaled)
    result = data.copy()
    result["Cluster"] = raw_labels.astype(int)
    result["At_Risk_Flag"] = (
        result["Recency"] > float(inactivity_threshold_days)
    ).astype(int)

    profile_columns = [
        "Cluster",
        "N_customers",
        "Pct_customers",
        "Median_Recency",
        "Mean_Recency",
        "Median_Frequency",
        "Mean_Frequency",
        "Median_Monetary_Gross",
        "Mean_Monetary_Gross",
        "Total_Revenue",
        "Revenue_Share_Pct",
        "Median_AOV",
        "Mean_Cancellation_Rate",
        "Median_InterPurchase_Days",
        "N_with_InterPurchase",
    ]
    overall_revenue = float(result["Monetary_Gross"].sum())
    profile_rows = []
    for cluster in sorted(result["Cluster"].unique()):
        group = result.loc[result["Cluster"].eq(cluster)]
        gap_column = "Median_InterPurchase_Days"
        gaps = (
            pd.to_numeric(group[gap_column], errors="coerce").dropna()
            if gap_column in group
            else pd.Series(dtype=float)
        )
        cancellations = (
            pd.to_numeric(group["Cancellation_Rate"], errors="coerce")
            if "Cancellation_Rate" in group
            else pd.Series(np.nan, index=group.index)
        )
        revenue = float(group["Monetary_Gross"].sum())
        profile_rows.append(
            {
                "Cluster": int(cluster),
                "N_customers": int(len(group)),
                "Pct_customers": round(100 * len(group) / len(result), 2),
                "Median_Recency": round(float(group["Recency"].median()), 1),
                "Mean_Recency": round(float(group["Recency"].mean()), 1),
                "Median_Frequency": round(float(group["Frequency"].median()), 1),
                "Mean_Frequency": round(float(group["Frequency"].mean()), 1),
                "Median_Monetary_Gross": round(
                    float(group["Monetary_Gross"].median()), 2
                ),
                "Mean_Monetary_Gross": round(
                    float(group["Monetary_Gross"].mean()), 2
                ),
                "Total_Revenue": round(revenue, 2),
                "Revenue_Share_Pct": round(
                    100 * revenue / overall_revenue, 2
                ) if overall_revenue else np.nan,
                "Median_AOV": round(
                    float(pd.to_numeric(group["AOV"], errors="coerce").median()), 2
                ) if "AOV" in group else np.nan,
                "Mean_Cancellation_Rate": round(float(cancellations.mean()), 4),
                "Median_InterPurchase_Days": (
                    round(float(gaps.median()), 1) if len(gaps) else np.nan
                ),
                "N_with_InterPurchase": int(len(gaps)),
            }
        )
    profiles = pd.DataFrame(profile_rows, columns=profile_columns)
    ordered = profiles.sort_values("Median_Recency").reset_index(drop=True)
    names_by_k = {
        2: ["Recent / Active Customers", "Lapsed / At-Risk Customers"],
        3: [
            "Recent / Active Customers",
            "Regular Customers",
            "Lapsed / At-Risk Customers",
        ],
        4: [
            "Champions (High-Value, Recent)",
            "Loyal Regular Customers",
            "At-Risk / Declining Customers",
            "Lapsed Customers",
        ],
        5: [
            "Champions (High-Value)",
            "Loyal Regulars",
            "New / Occasional Customers",
            "At-Risk Customers",
            "Lapsed Customers",
        ],
    }
    rank_names = names_by_k.get(
        int(n_clusters), [f"Segment {rank + 1}" for rank in range(int(n_clusters))]
    )
    segment_names = {
        int(row["Cluster"]): rank_names[rank]
        for rank, row in enumerate(ordered.to_dict("records"))
    }
    profiles["Segment_Name"] = profiles["Cluster"].map(segment_names)
    result["Segment_Name"] = result["Cluster"].map(segment_names)

    metric_values = {
        "inertia": float(model.inertia_),
        "silhouette_score": float(
            silhouette_score(scaled, raw_labels, random_state=random_state)
        ),
        "davies_bouldin_index": float(davies_bouldin_score(scaled, raw_labels)),
        "calinski_harabasz_score": float(
            calinski_harabasz_score(scaled, raw_labels)
        ),
    }
    return DescriptiveSegmentation(
        customers=result,
        profiles=profiles,
        scaler=scaler,
        kmeans=model,
        segment_names=segment_names,
        metrics=metric_values,
    )
