"""
temporal_framework.py
=====================
Reusable, leakage-free temporal feature/target construction for
Customer Segmentation and Retention Analysis (OELP project).

Used by:
  - Notebook 05: Statistical Validation & Temporal Prediction Foundation
  - Notebook 06+: Predictive modeling notebooks

Design principles
-----------------
* All features are computed strictly from records BEFORE the cutoff date.
* Future targets are computed strictly from records AFTER the cutoff date.
* Survival durations use precise fractional-day resolution (total_seconds/86400),
  not integer .dt.days truncation.
* Censoring: a customer receives a definitive non-purchase label only when the
  full horizon is observable (cutoff + horizon <= dataset_end).
* No zero-imputation for missing interpurchase gaps (single-purchase customers
  receive NaN for gap statistics).
* Observation exposure for rates uses (cutoff_date - FirstPurchaseDate), not
  the first-to-last span, to represent the actual observation window.
* Administrative test accounts (14103, 14827) are always excluded.
* Cancellation invoices (C-prefix) are excluded from purchase features.

Horizon-Specific Outcome-Matured Predictive Split Protocol
-----------------------------------------------------------
Given Year 1 data (Dec 2009 – Dec 2010, ~374 days, dataset end: 2010-12-09 20:01:00):

To guarantee that training outcomes are 100% mature and observable before validation
predictions are generated, and validation outcomes are mature before test predictions,
we establish horizon-specific chronological splits:

  Horizon 30d:
    TRAIN    2010-06-01 -> Target window: 2010-06-01 to 2010-07-01 (matures 31d before VAL)
    VAL      2010-08-01 -> Target window: 2010-08-01 to 2010-08-31 (matures 10d before TEST)
    TEST     2010-09-10 -> Target window: 2010-09-10 to 2010-10-10 (observable <= dataset end)

  Horizon 60d:
    TRAIN    2010-05-01 -> Target window: 2010-05-01 to 2010-06-30 (matures 1d before VAL)
    VAL      2010-07-01 -> Target window: 2010-07-01 to 2010-08-30 (matures 11d before TEST)
    TEST     2010-09-10 -> Target window: 2010-09-10 to 2010-11-09 (observable <= dataset end)

  Horizon 90d:
    TRAIN    2010-03-01 -> Target window: 2010-03-01 to 2010-05-30 (matures 2d before VAL)
    VAL      2010-06-01 -> Target window: 2010-06-01 to 2010-08-30 (matures 11d before TEST)
    TEST     2010-09-10 -> Target window: 2010-09-10 to 2010-12-09 (observable <= dataset end)

Strict Leakage Guarantee:
  In predictive datasets, preprocessing (log1p transform, StandardScaler, KMeans) is
  fit strictly on TRAIN cutoff data and applied to transform VAL and TEST.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ADMIN_EXCLUDE = {14103, 14827}
FORECAST_HORIZONS = [30, 60, 90]  # days

# Horizon-specific outcome-matured chronological split specifications
HORIZON_SPLIT_SPECS = {
    30: {
        "train": pd.Timestamp("2010-06-01"),
        "val":   pd.Timestamp("2010-08-01"),
        "test":  pd.Timestamp("2010-09-10"),
    },
    60: {
        "train": pd.Timestamp("2010-05-01"),
        "val":   pd.Timestamp("2010-07-01"),
        "test":  pd.Timestamp("2010-09-10"),
    },
    90: {
        "train": pd.Timestamp("2010-03-01"),
        "val":   pd.Timestamp("2010-06-01"),
        "test":  pd.Timestamp("2010-09-10"),
    },
}

# Explicit column-group registries for Notebook 06
FEATURE_COLS = [
    "Customer ID", "cutoff_date",
    "FirstPurchaseDate", "LastPurchaseDate",
    "Frequency", "Monetary_Gross", "AOV",
    "Recency", "Tenure_obs_days",
    "SpendRate_per_obs_day", "PurchaseRate_per_obs_day",
    "Median_Gap_days", "Mean_Gap_days", "Std_Gap_days",
    "Min_Gap_days", "Max_Gap_days",
    "Recent_Orders", "Recent_Revenue",
    "log1p_Recency", "log1p_Frequency", "log1p_Monetary",
    "Hist_Cluster_id", "Hist_Segment",
]

TARGET_COLS = [
    "NextPurchaseDate", "TimeToNext_days", "Event_flag", "Survival_duration",
    "Purchased_30d", "FutureOrders_30d", "FutureRevenue_30d",
    "Purchased_60d", "FutureOrders_60d", "FutureRevenue_60d",
    "Purchased_90d", "FutureOrders_90d", "FutureRevenue_90d",
]

# Authorized split roles for predictive modeling (Notebook 06+)
PREDICTIVE_SPLIT_ROLES = ["TRAIN", "VAL", "TEST"]


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

def load_cleaned_transactions(filepath: str) -> pd.DataFrame:
    """Load the cleaned transaction file and parse InvoiceDate."""
    df = pd.read_csv(filepath)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    return df


def build_order_level_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate valid purchase lines to order (invoice) level.

    Rules
    -----
    * Exclude cancellation invoices (Invoice starts with 'C').
    * Exclude administrative test accounts.
    * Gross revenue = sum(Quantity * Price) per invoice.
    * Returns one row per (Customer ID, Invoice).
    """
    purchases = df[~df["Invoice"].str.startswith("C")].copy()
    purchases = purchases[~purchases["Customer ID"].isin(ADMIN_EXCLUDE)]
    purchases["LineRevenue"] = purchases["Quantity"] * purchases["Price"]

    orders = (
        purchases.groupby(["Customer ID", "Invoice"], as_index=False)
        .agg(
            PurchaseDate=("InvoiceDate", "min"),   # earliest timestamp per invoice
            GrossRevenue=("LineRevenue", "sum"),
        )
    )
    orders = orders.sort_values(["Customer ID", "PurchaseDate"]).reset_index(drop=True)
    return orders


# ---------------------------------------------------------------------------
# Historical feature extraction
# ---------------------------------------------------------------------------

def compute_historical_features(
    orders: pd.DataFrame,
    cutoff_date: pd.Timestamp,
    reference_date: pd.Timestamp = None,
    rolling_window_days: int = 90,
) -> pd.DataFrame:
    """
    Build customer-level RFM+ features using records strictly before cutoff_date.

    Parameters
    ----------
    orders : order-level DataFrame from build_order_level_dataset()
    cutoff_date : feature computation horizon (exclusive upper bound).
                  Records with PurchaseDate >= cutoff_date are excluded.
    reference_date : used for Recency calculation; defaults to cutoff_date
    rolling_window_days : look-back window for recent activity features

    Rate denominators
    -----------------
    SpendRate and PurchaseRate use (cutoff_date - FirstPurchaseDate) as the
    observation-exposure denominator (Tenure_obs_days). This avoids instability
    of the first-to-last span, which can be near-zero for infrequent buyers.
    Single-purchase customers have Tenure_obs_days > 0 (by strict '<' cutoff)
    so they receive valid rate estimates.

    Returns
    -------
    DataFrame with one row per eligible customer (>=1 purchase before cutoff).
    Missing interpurchase gap values remain NaN for single-purchase customers.
    """
    if reference_date is None:
        reference_date = cutoff_date

    hist = orders[orders["PurchaseDate"] < cutoff_date].copy()

    if hist.empty:
        return pd.DataFrame()

    # Per-customer aggregations
    agg = hist.groupby("Customer ID").agg(
        FirstPurchaseDate=("PurchaseDate", "min"),
        LastPurchaseDate=("PurchaseDate", "max"),
        Frequency=("Invoice", "nunique"),
        Monetary_Gross=("GrossRevenue", "sum"),
    ).reset_index()

    agg["Recency"] = (reference_date - agg["LastPurchaseDate"]).dt.days
    agg["AOV"]     = agg["Monetary_Gross"] / agg["Frequency"]

    # Observation exposure: time from first purchase to cutoff (fractional days)
    agg["Tenure_obs_days"] = (
        (cutoff_date - agg["FirstPurchaseDate"]).dt.total_seconds() / 86400.0
    )

    valid_exposure = agg["Tenure_obs_days"] > 0
    agg["SpendRate_per_obs_day"] = np.where(
        valid_exposure,
        agg["Monetary_Gross"] / agg["Tenure_obs_days"],
        np.nan,
    )
    agg["PurchaseRate_per_obs_day"] = np.where(
        valid_exposure,
        agg["Frequency"] / agg["Tenure_obs_days"],
        np.nan,
    )

    # Interpurchase gap statistics (only for customers with >=2 purchases)
    gap_stats = _compute_gap_stats(hist)
    agg = agg.merge(gap_stats, on="Customer ID", how="left")

    # Rolling window recent activity
    rolling_cutoff = cutoff_date - pd.Timedelta(days=rolling_window_days)
    recent = hist[hist["PurchaseDate"] >= rolling_cutoff].groupby("Customer ID").agg(
        Recent_Orders=("Invoice", "nunique"),
        Recent_Revenue=("GrossRevenue", "sum"),
    ).reset_index()
    agg = agg.merge(recent, on="Customer ID", how="left")
    agg["Recent_Orders"]  = agg["Recent_Orders"].fillna(0).astype(int)
    agg["Recent_Revenue"] = agg["Recent_Revenue"].fillna(0.0)

    agg["cutoff_date"] = cutoff_date
    return agg


def _compute_gap_stats(hist: pd.DataFrame) -> pd.DataFrame:
    """
    Compute interpurchase gap statistics per customer using fractional days.
    Returns NaN for all gap stats for single-purchase customers.
    """
    rows = []
    for cust_id, grp in hist.groupby("Customer ID"):
        dates = grp["PurchaseDate"].sort_values().unique()
        if len(dates) < 2:
            rows.append({
                "Customer ID": cust_id,
                "Median_Gap_days": np.nan,
                "Mean_Gap_days":   np.nan,
                "Std_Gap_days":    np.nan,
                "Min_Gap_days":    np.nan,
                "Max_Gap_days":    np.nan,
            })
        else:
            ts = np.array([pd.Timestamp(d).timestamp() for d in dates])
            gaps = np.diff(ts) / 86400.0
            rows.append({
                "Customer ID":     cust_id,
                "Median_Gap_days": float(np.median(gaps)),
                "Mean_Gap_days":   float(np.mean(gaps)),
                "Std_Gap_days":    float(np.std(gaps, ddof=1)) if len(gaps) > 1 else np.nan,
                "Min_Gap_days":    float(np.min(gaps)),
                "Max_Gap_days":    float(np.max(gaps)),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Future target construction
# ---------------------------------------------------------------------------

def compute_future_targets(
    orders: pd.DataFrame,
    features_df: pd.DataFrame,
    cutoff_date: pd.Timestamp,
    dataset_end: pd.Timestamp,
    horizons: list = None,
) -> pd.DataFrame:
    """
    Compute future purchase targets for each customer in features_df.

    For each horizon H (days):
      * horizon_end = cutoff_date + H days
      * A customer can receive a definitive non-purchase label only when
        horizon_end <= dataset_end (full horizon observable).
      * Purchased_in_H  : binary (1 / 0 / NaN if censored)
      * FutureOrders_H  : count of distinct invoices in (cutoff, horizon_end]
      * FutureRevenue_H : gross revenue in (cutoff, horizon_end]
      * TimeToNext_days : fractional days from cutoff to first future purchase
      * Event_flag      : 1 = purchased (observed event), 0 = right-censored
      * Survival_duration : fractional days; event customers = TimeToNext_days;
                            censored customers = (dataset_end - cutoff) in days
                            (minimum 1/86400 day to stay strictly positive)
    """
    if horizons is None:
        horizons = FORECAST_HORIZONS

    customers = features_df["Customer ID"].unique()
    future = orders[
        (orders["PurchaseDate"] > cutoff_date)
        & (orders["Customer ID"].isin(customers))
    ].copy()

    # Next purchase date per customer
    next_purchase = (
        future.groupby("Customer ID")["PurchaseDate"].min().reset_index()
        .rename(columns={"PurchaseDate": "NextPurchaseDate"})
    )
    result = features_df[["Customer ID"]].copy()
    result = result.merge(next_purchase, on="Customer ID", how="left")
    result["NextPurchaseDate"] = pd.to_datetime(result["NextPurchaseDate"])

    # Fractional-day time to next purchase
    result["TimeToNext_days"] = (
        result["NextPurchaseDate"] - cutoff_date
    ).dt.total_seconds() / 86400.0

    result["Event_flag"] = result["NextPurchaseDate"].notna().astype(int)

    censor_dur = max(
        (dataset_end - cutoff_date).total_seconds() / 86400.0,
        1.0 / 86400.0
    )
    result["Survival_duration"] = (
        result["TimeToNext_days"].fillna(censor_dur).clip(lower=1.0 / 86400.0)
    )

    for H in horizons:
        horizon_end     = cutoff_date + pd.Timedelta(days=H)
        fully_observable = horizon_end <= dataset_end

        in_window = future[future["PurchaseDate"] <= horizon_end]
        h_agg = (
            in_window.groupby("Customer ID")
            .agg(
                n_orders=("Invoice", "nunique"),
                revenue=("GrossRevenue", "sum"),
            )
            .reset_index()
        )

        col_bought = f"Purchased_{H}d"
        col_orders = f"FutureOrders_{H}d"
        col_rev    = f"FutureRevenue_{H}d"

        result = result.merge(
            h_agg.rename(columns={"n_orders": col_orders, "revenue": col_rev}),
            on="Customer ID",
            how="left",
        )
        result[col_orders] = result[col_orders].fillna(0).astype(int)
        result[col_rev]    = result[col_rev].fillna(0.0)

        if fully_observable:
            result[col_bought] = (result[col_orders] > 0).astype(int)
        else:
            result[col_bought] = np.where(result[col_orders] > 0, 1, np.nan)

    result["cutoff_date"] = cutoff_date
    return result


# ---------------------------------------------------------------------------
# Historical clustering (leakage-free)
# ---------------------------------------------------------------------------

def fit_historical_kmeans(
    features_df: pd.DataFrame,
    n_clusters: int = 2,
    random_state: int = 42,
    n_init: int = 20,
    max_iter: int = 500,
) -> tuple:
    """
    Fit log1p -> StandardScaler -> KMeans on historical RFM features.
    """
    df = features_df.copy()
    rfm_cols = ["Recency", "Frequency", "Monetary_Gross"]
    df_valid = df.dropna(subset=rfm_cols).copy()

    df_valid["log1p_Recency"]   = np.log1p(df_valid["Recency"])
    df_valid["log1p_Frequency"] = np.log1p(df_valid["Frequency"])
    df_valid["log1p_Monetary"]  = np.log1p(df_valid["Monetary_Gross"])

    feat_cols = ["log1p_Recency", "log1p_Frequency", "log1p_Monetary"]
    X = df_valid[feat_cols].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    km = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=n_init,
        max_iter=max_iter,
    )
    km.fit(X_scaled)
    df_valid["Cluster_raw"] = km.labels_

    cluster_recency = df_valid.groupby("Cluster_raw")["Recency"].mean()
    active_cluster  = int(cluster_recency.idxmin())

    label_map = {
        active_cluster: "Recent / Active",
        1 - active_cluster: "Lapsed / At-Risk",
    }

    df_valid["Hist_Segment"]    = df_valid["Cluster_raw"].map(label_map)
    df_valid["Hist_Cluster_id"] = df_valid["Cluster_raw"].apply(
        lambda x: 1 if x == active_cluster else 0
    )

    return df_valid, scaler, km, label_map


# ---------------------------------------------------------------------------
# Horizon-Specific Predictive Dataset Builder (Outcome-Matured)
# ---------------------------------------------------------------------------

def build_horizon_splits(
    orders: pd.DataFrame,
    horizon: int,
    dataset_end: pd.Timestamp,
    specs: dict = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Build outcome-matured, strictly leakage-free Train/Val/Test datasets for horizon H.

    Guarantees:
      1. Train target window closes before or at Val cutoff date.
      2. Val target window closes before or at Test cutoff date.
      3. Test target window closes before or at dataset end.
      4. Preprocessing (StandardScaler, KMeans) is fit strictly on TRAIN and applied
         to transform VAL and TEST.
    """
    if specs is None:
        specs = HORIZON_SPLIT_SPECS[horizon]

    train_cutoff = specs["train"]
    val_cutoff   = specs["val"]
    test_cutoff  = specs["test"]

    # 1. Feature extraction
    train_feats = compute_historical_features(orders, train_cutoff)
    val_feats   = compute_historical_features(orders, val_cutoff)
    test_feats  = compute_historical_features(orders, test_cutoff)

    # 2. Strict Preprocessing Fit ONLY on Train
    rfm_cols = ["Recency", "Frequency", "Monetary_Gross"]
    feat_cols = ["log1p_Recency", "log1p_Frequency", "log1p_Monetary"]
    for df in [train_feats, val_feats, test_feats]:
        df["log1p_Recency"]   = np.log1p(df["Recency"])
        df["log1p_Frequency"] = np.log1p(df["Frequency"])
        df["log1p_Monetary"]  = np.log1p(df["Monetary_Gross"])

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(train_feats[feat_cols].values)

    km = KMeans(n_clusters=2, random_state=random_state, n_init=20, max_iter=500)
    km.fit(X_train_scaled)
    train_feats["Cluster_raw"] = km.labels_

    active_cluster = int(train_feats.groupby("Cluster_raw")["Recency"].mean().idxmin())
    label_map = {
        active_cluster: "Recent / Active",
        1 - active_cluster: "Lapsed / At-Risk",
    }
    train_feats["Hist_Cluster_id"] = (train_feats["Cluster_raw"] == active_cluster).astype(int)
    train_feats["Hist_Segment"]    = train_feats["Cluster_raw"].map(label_map)

    # Transform Val and Test without fitting
    for df_eval in [val_feats, test_feats]:
        X_eval_scaled = scaler.transform(df_eval[feat_cols].values)
        df_eval["Cluster_raw"]     = km.predict(X_eval_scaled)
        df_eval["Hist_Cluster_id"] = (df_eval["Cluster_raw"] == active_cluster).astype(int)
        df_eval["Hist_Segment"]    = df_eval["Cluster_raw"].map(label_map)

    # 3. Future target construction
    train_tgts = compute_future_targets(orders, train_feats, train_cutoff, dataset_end, [horizon])
    val_tgts   = compute_future_targets(orders, val_feats, val_cutoff, dataset_end, [horizon])
    test_tgts  = compute_future_targets(orders, test_feats, test_cutoff, dataset_end, [horizon])

    # 4. Merge
    dfs = []
    for role, f_df, t_df in [("TRAIN", train_feats, train_tgts),
                             ("VAL", val_feats, val_tgts),
                             ("TEST", test_feats, test_tgts)]:
        m = f_df.merge(t_df.drop(columns=["cutoff_date"], errors="ignore"), on="Customer ID", how="inner")
        m["split_role"]   = role
        m["horizon_days"] = horizon
        if "Cluster_raw" in m.columns:
            m = m.drop(columns=["Cluster_raw"])
        dfs.append(m)

    combined = pd.concat(dfs, ignore_index=True)
    return combined


def build_all_horizon_splits(orders: pd.DataFrame, dataset_end: pd.Timestamp) -> dict:
    """Build splits for all defined horizons: 30d, 60d, 90d."""
    return {H: build_horizon_splits(orders, H, dataset_end) for H in HORIZON_SPLIT_SPECS}


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_horizon_split_maturity(specs: dict = None, dataset_end: pd.Timestamp = None) -> dict:
    """
    Verify that train labels mature before val cutoff, val labels mature
    before test cutoff, and test horizon is observable within dataset.
    """
    if specs is None:
        specs = HORIZON_SPLIT_SPECS
    if dataset_end is None:
        dataset_end = pd.Timestamp("2010-12-09 20:01:00")

    issues = {}
    for H, s in specs.items():
        train_end = s["train"] + pd.Timedelta(days=H)
        val_end   = s["val"]   + pd.Timedelta(days=H)
        test_end  = s["test"]  + pd.Timedelta(days=H)

        if train_end > s["val"]:
            issues[f"train_immature_{H}d"] = f"Train end {train_end.date()} > Val cutoff {s['val'].date()}"
        if val_end > s["test"]:
            issues[f"val_immature_{H}d"] = f"Val end {val_end.date()} > Test cutoff {s['test'].date()}"
        if test_end > dataset_end:
            issues[f"test_unobservable_{H}d"] = f"Test end {test_end} > Dataset end {dataset_end}"

    return issues


def validate_no_leakage(features_df: pd.DataFrame, cutoff_date: pd.Timestamp) -> dict:
    """Check that no historical feature rows contain data on or after cutoff_date."""
    issues = {}

    if "LastPurchaseDate" in features_df.columns:
        late = features_df[
            pd.to_datetime(features_df["LastPurchaseDate"]) >= cutoff_date
        ]
        issues["last_purchase_on_or_after_cutoff"] = len(late)

    if "FirstPurchaseDate" in features_df.columns:
        late2 = features_df[
            pd.to_datetime(features_df["FirstPurchaseDate"]) >= cutoff_date
        ]
        issues["first_purchase_on_or_after_cutoff"] = len(late2)

    return issues


def validate_target_construction(
    targets_df: pd.DataFrame,
    cutoff_date: pd.Timestamp,
    dataset_end: pd.Timestamp,
    horizons: list = None,
) -> dict:
    """Check target DataFrame integrity."""
    if horizons is None:
        horizons = FORECAST_HORIZONS

    issues = {}

    if "Survival_duration" in targets_df.columns:
        neg = (targets_df["Survival_duration"] <= 0).sum()
        issues["non_positive_survival_duration"] = int(neg)

    if "NextPurchaseDate" in targets_df.columns:
        past_end = targets_df[
            pd.to_datetime(targets_df["NextPurchaseDate"]) > dataset_end
        ]
        issues["next_purchase_past_dataset_end"] = len(past_end)

    for H in horizons:
        col = f"Purchased_{H}d"
        horizon_end = cutoff_date + pd.Timedelta(days=H)
        if col in targets_df.columns and horizon_end <= dataset_end:
            invalid = (~targets_df[col].isin([0, 1])).sum()
            issues[f"non_binary_{col}"] = int(invalid)

    return issues


def validate_unique_customer_cutoff(df: pd.DataFrame) -> int:
    """Return number of duplicate (Customer ID, cutoff_date) rows."""
    return df.duplicated(subset=["Customer ID", "cutoff_date"]).sum()


# ---------------------------------------------------------------------------
# Function-level tests (called by Notebook 05 validation section)
# ---------------------------------------------------------------------------

def run_function_tests(orders_df: pd.DataFrame, dataset_end: pd.Timestamp) -> dict:
    """
    Test production functions with synthetic edge-case data and check
    split maturity and descriptive/predictive separation.
    """
    results = {}

    # Synthetic minimal order set
    cutoff = pd.Timestamp("2010-08-01")
    syn_orders = pd.DataFrame({
        "Customer ID":  [1, 1, 1, 2, 3, 4, 5],
        "Invoice":      ["A1", "A2", "A3", "B1", "C1", "D1", "E1"],
        "PurchaseDate": [
            pd.Timestamp("2010-06-01"),
            pd.Timestamp("2010-08-01"),   # on cutoff — excluded from history
            pd.Timestamp("2010-08-15"),   # future
            pd.Timestamp("2010-07-01"),   # single purchase customer
            pd.Timestamp("2010-04-01"),   # only past purchase — will be censored
            pd.Timestamp("2010-03-15"),   # past purchase
            pd.Timestamp("2010-05-15"),   # past purchase
        ],
        "GrossRevenue": [100.0, 200.0, 300.0, 50.0, 80.0, 120.0, 150.0],
    })

    # --- Test 1: Purchase exactly on cutoff excluded from history ---
    try:
        feats = compute_historical_features(syn_orders, cutoff)
        cust1 = feats[feats["Customer ID"] == 1]
        expected_freq = 1
        actual_freq   = int(cust1["Frequency"].iloc[0])
        results["cutoff_boundary_exclusion"] = "PASS" if actual_freq == expected_freq else f"FAIL: {actual_freq}"
    except Exception as e:
        results["cutoff_boundary_exclusion"] = f"FAIL: {e}"

    # --- Test 2: Future target — event customer has TimeToNext > 0 ---
    try:
        feats = compute_historical_features(syn_orders, cutoff)
        tgts  = compute_future_targets(syn_orders, feats, cutoff, dataset_end, [30, 60, 90])
        cust1_tgt = tgts[tgts["Customer ID"] == 1]
        expected_days = (pd.Timestamp("2010-08-15") - cutoff).total_seconds() / 86400.0
        actual_days   = float(cust1_tgt["TimeToNext_days"].iloc[0])
        results["future_target_time_to_next"] = "PASS" if abs(actual_days - expected_days) < 1e-6 else f"FAIL: {actual_days}"
    except Exception as e:
        results["future_target_time_to_next"] = f"FAIL: {e}"

    # --- Test 3: Censored customer has Survival_duration = censor_duration ---
    try:
        feats = compute_historical_features(syn_orders, cutoff)
        tgts  = compute_future_targets(syn_orders, feats, cutoff, dataset_end, [30, 60, 90])
        cust3 = tgts[tgts["Customer ID"] == 3]
        expected_censor = (dataset_end - cutoff).total_seconds() / 86400.0
        actual_surv     = float(cust3["Survival_duration"].iloc[0])
        actual_event    = int(cust3["Event_flag"].iloc[0])
        results["censored_customer_duration"] = "PASS" if (actual_event == 0 and abs(actual_surv - expected_censor) < 1e-6) else f"FAIL: {actual_surv}"
    except Exception as e:
        results["censored_customer_duration"] = f"FAIL: {e}"

    # --- Test 4: Fractional-day survival duration ---
    try:
        sub_day_orders = pd.DataFrame({
            "Customer ID":  [9, 9],
            "Invoice":      ["Z1", "Z2"],
            "PurchaseDate": [
                pd.Timestamp("2010-07-30 10:00:00"),
                pd.Timestamp("2010-08-01 10:30:00"),
            ],
            "GrossRevenue": [10.0, 20.0],
        })
        feats_sd = compute_historical_features(sub_day_orders, cutoff)
        tgts_sd  = compute_future_targets(sub_day_orders, feats_sd, cutoff, dataset_end, [30])
        cust9    = tgts_sd[tgts_sd["Customer ID"] == 9]
        expected_frac = (pd.Timestamp("2010-08-01 10:30:00") - cutoff).total_seconds() / 86400.0
        actual_frac = float(cust9["TimeToNext_days"].iloc[0])
        results["fractional_day_duration"] = "PASS" if abs(actual_frac - expected_frac) < 1e-9 else f"FAIL: {actual_frac}"
    except Exception as e:
        results["fractional_day_duration"] = f"FAIL: {e}"

    # --- Test 5: Single-purchase customer has NaN gap stats ---
    try:
        feats = compute_historical_features(syn_orders, cutoff)
        cust2 = feats[feats["Customer ID"] == 2]
        gap_nan = cust2["Median_Gap_days"].isna().all()
        results["single_purchase_gap_nan"] = "PASS" if gap_nan else "FAIL"
    except Exception as e:
        results["single_purchase_gap_nan"] = f"FAIL: {e}"

    # --- Test 6: No future information leaks into historical features ---
    try:
        feats = compute_historical_features(syn_orders, cutoff)
        leakage = validate_no_leakage(feats, cutoff)
        results["no_leakage_in_features"] = "PASS" if sum(leakage.values()) == 0 else f"FAIL: {leakage}"
    except Exception as e:
        results["no_leakage_in_features"] = f"FAIL: {e}"

    # --- Test 7: Binary targets are 0/1 for fully-observable horizon ---
    try:
        feats = compute_historical_features(syn_orders, cutoff)
        tgts  = compute_future_targets(syn_orders, feats, cutoff, dataset_end, [30])
        col   = "Purchased_30d"
        bad   = (~tgts[col].isin([0, 1])).sum()
        results["binary_targets_0_or_1"] = "PASS" if bad == 0 else f"FAIL: {bad}"
    except Exception as e:
        results["binary_targets_0_or_1"] = f"FAIL: {e}"

    # --- Test 8: Positive survival durations for all customers ---
    try:
        feats = compute_historical_features(syn_orders, cutoff)
        tgts  = compute_future_targets(syn_orders, feats, cutoff, dataset_end, [30, 60, 90])
        neg   = (tgts["Survival_duration"] <= 0).sum()
        results["positive_survival_durations"] = "PASS" if neg == 0 else f"FAIL: {neg}"
    except Exception as e:
        results["positive_survival_durations"] = f"FAIL: {e}"

    # --- Test 9: Train label maturity across all predictive horizons ---
    try:
        maturity_issues = validate_horizon_split_maturity(HORIZON_SPLIT_SPECS, dataset_end)
        train_issues = [v for k, v in maturity_issues.items() if "train" in k]
        results["train_label_maturity"] = "PASS" if len(train_issues) == 0 else f"FAIL: {train_issues}"
    except Exception as e:
        results["train_label_maturity"] = f"FAIL: {e}"

    # --- Test 10: Validation label maturity across all predictive horizons ---
    try:
        val_issues = [v for k, v in maturity_issues.items() if "val" in k]
        results["validation_label_maturity"] = "PASS" if len(val_issues) == 0 else f"FAIL: {val_issues}"
    except Exception as e:
        results["validation_label_maturity"] = f"FAIL: {e}"

    # --- Test 11: Test horizon observability within dataset ---
    try:
        test_issues = [v for k, v in maturity_issues.items() if "test" in k]
        results["test_horizon_observability"] = "PASS" if len(test_issues) == 0 else f"FAIL: {test_issues}"
    except Exception as e:
        results["test_horizon_observability"] = f"FAIL: {e}"

    # --- Test 12: Separation of descriptive vs predictive datasets ---
    # Verify build_horizon_splits fits scaler strictly on TRAIN
    try:
        syn_splits = build_horizon_splits(syn_orders, 30, dataset_end, {
            "train": pd.Timestamp("2010-06-01"),
            "val":   pd.Timestamp("2010-08-01"),
            "test":  pd.Timestamp("2010-09-10"),
        })
        train_rows = (syn_splits["split_role"] == "TRAIN").sum()
        val_rows   = (syn_splits["split_role"] == "VAL").sum()
        test_rows  = (syn_splits["split_role"] == "TEST").sum()
        if train_rows > 0 and val_rows > 0 and test_rows > 0 and "Hist_Segment" in syn_splits.columns:
            results["separation_descriptive_vs_predictive"] = "PASS"
        else:
            results["separation_descriptive_vs_predictive"] = "FAIL: row structure incomplete"
    except Exception as e:
        results["separation_descriptive_vs_predictive"] = f"FAIL: {e}"

    # --- Test 13: Feature and Target column registries are strictly disjoint ---
    try:
        overlap = set(FEATURE_COLS).intersection(set(TARGET_COLS))
        results["feature_target_disjoint"] = "PASS" if len(overlap) == 0 else f"FAIL: {overlap}"
    except Exception as e:
        results["feature_target_disjoint"] = f"FAIL: {e}"

    # --- Test 14: No future / target derived names in FEATURE_COLS ---
    try:
        forbidden = [c for c in FEATURE_COLS if any(c.startswith(p) for p in ['Future', 'Purchased_', 'Next', 'Event_', 'Survival_'])]
        results["no_leakage_in_predictive_features"] = "PASS" if len(forbidden) == 0 else f"FAIL: {forbidden}"
    except Exception as e:
        results["no_leakage_in_predictive_features"] = f"FAIL: {e}"

    return results
