"""Application-facing, inference-only customer intelligence service."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from src import purchase_clock as pc
from src import spending_model as sm
from src import temporal_framework as tf
from src.data_preparation import validate_transaction_history

PREDICTIVE_TEST_CUTOFF = pd.Timestamp("2010-09-10")
_DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _validate_transform(transform: Mapping, *, name: str) -> None:
    expected_columns = ["Recency", "Frequency", "Monetary_Gross"]
    if transform.get("transform_version") != "historical-rfm-kmeans-v1":
        raise ValueError(f"{name} has an unsupported historical segmentation version.")
    if list(transform.get("feature_columns", [])) != expected_columns:
        raise ValueError(f"{name} has an incompatible segmentation feature schema.")
    if transform.get("fit_role") != "TRAIN":
        raise ValueError(f"{name} segmentation must be fitted on TRAIN only.")
    if transform.get("scaler") is None or transform.get("kmeans") is None:
        raise ValueError(f"{name} segmentation transform is incomplete.")
    labels = transform.get("label_map")
    if not isinstance(labels, Mapping) or len(labels) != 2:
        raise ValueError(f"{name} segmentation must contain the two saved segment labels.")
    if set(labels.values()) != {"Recent / Active", "Lapsed / At-Risk"}:
        raise ValueError(f"{name} segment label mapping is incompatible.")
    active_cluster = transform.get("active_cluster")
    if active_cluster is None or int(active_cluster) not in {
        int(label) for label in labels
    }:
        raise ValueError(f"{name} active-cluster mapping is invalid.")


def _validate_purchase_bundle(bundle: Mapping, *, name: str) -> None:
    if bundle.get("metadata", {}).get("model_version") != pc.MODEL_VERSION:
        raise ValueError(f"{name} has an unsupported purchase-clock model version.")
    missing = {
        "global",
        "segment",
        "personalized_pipeline",
        "metadata",
        "segment_transform",
    }.difference(bundle)
    if missing:
        raise ValueError(f"{name} is missing model entries: {sorted(missing)}")
    _validate_transform(bundle["segment_transform"], name=name)
    hazards = np.asarray(bundle["global"].get("hazards"), dtype=float)
    if hazards.shape != (pc.N_INTERVALS,) or not np.isfinite(hazards).all():
        raise ValueError(f"{name} global hazard schema must contain nine finite values.")
    if bundle.get("personalized_pipeline") is None:
        raise ValueError(f"{name} personalized hazard pipeline is missing.")
    gap = bundle["metadata"].get("population_median_gap_days")
    if gap is None or not np.isfinite(float(gap)) or float(gap) <= 0:
        raise ValueError(f"{name} population median gap must be finite and positive.")


def _normalize_customer_ids(customer_ids: Iterable | int | str | None) -> list[int] | None:
    if customer_ids is None:
        return None
    if isinstance(customer_ids, (str, int, float, np.integer, np.floating)):
        values = [customer_ids]
    else:
        values = list(customer_ids)
    if not values:
        raise ValueError("customer_ids cannot be an empty collection.")
    numeric = pd.to_numeric(pd.Series(values), errors="raise")
    if numeric.isna().any() or not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError("customer_ids must contain finite numeric identifiers.")
    if not np.equal(numeric, np.floor(numeric)).all():
        raise ValueError("customer_ids must contain whole-number identifiers.")
    normalized = numeric.astype("int64").tolist()
    if len(set(normalized)) != len(normalized):
        raise ValueError("customer_ids cannot contain duplicates.")
    return normalized


class CustomerIntelligence:
    """Load saved Notebook 06/07 artifacts and make historical forecasts.

    The service does not fit, tune, or retrain models. It builds features from
    transactions strictly before an approved Year 1 cutoff, applies each
    artifact's own saved segmentation transform, and returns predictions only.
    """

    def __init__(
        self,
        purchase_bundle: Mapping,
        spending_bundle: Mapping,
        *,
        dataset_end: pd.Timestamp,
        validation_purchase_bundle: Mapping | None = None,
        dataset_start: pd.Timestamp | None = None,
    ) -> None:
        _validate_purchase_bundle(purchase_bundle, name="purchase-clock bundle")
        if validation_purchase_bundle is not None:
            _validate_purchase_bundle(
                validation_purchase_bundle, name="validation-vintage purchase bundle"
            )
            vintage = validation_purchase_bundle["metadata"].get(
                "validation_vintage", {}
            )
            if vintage.get("test_outcomes_used") is not False:
                raise ValueError(
                    "Validation-vintage purchase model must declare test_outcomes_used=false."
                )
        if spending_bundle.get("metadata", {}).get("model_version") != sm.MODEL_VERSION:
            raise ValueError("Unsupported spending-model bundle version.")
        horizons = {
            int(horizon) for horizon in spending_bundle.get("horizon_models", {})
        }
        if not horizons or not horizons.issubset(set(sm.HORIZONS)):
            raise ValueError("Spending bundle has no supported forecast horizons.")
        transforms = spending_bundle.get("segment_transforms")
        if not isinstance(transforms, Mapping):
            raise ValueError("Spending bundle has no horizon-specific segment transforms.")
        for horizon in horizons:
            key = horizon if horizon in transforms else str(horizon)
            if key not in transforms:
                raise ValueError(f"Spending bundle is missing its {horizon}-day transform.")
            _validate_transform(
                transforms[key], name=f"{horizon}-day spending transform"
            )
        declared_purchase_version = spending_bundle["metadata"].get(
            "purchase_probability_source_model", {}
        ).get("model_version")
        if declared_purchase_version not in (None, pc.MODEL_VERSION):
            raise ValueError(
                "Spending and purchase-clock artifact versions are incompatible."
            )

        self.purchase_bundle = dict(purchase_bundle)
        self.spending_bundle = dict(spending_bundle)
        self.validation_purchase_bundle = (
            dict(validation_purchase_bundle)
            if validation_purchase_bundle is not None
            else None
        )
        self.dataset_end = pd.Timestamp(dataset_end)
        self.dataset_start = (
            pd.Timestamp(dataset_start) if dataset_start is not None else None
        )
        if pd.isna(self.dataset_end):
            raise ValueError("dataset_end must be a valid timestamp.")
        self.supported_horizons = tuple(sorted(horizons))
        self._protocol = self.spending_bundle["metadata"].get(
            "joint_validation_protocol", {}
        )
        self._test_cutoff = pd.Timestamp(
            self.purchase_bundle["metadata"].get(
                "first_test_cutoff", PREDICTIVE_TEST_CUTOFF
            )
        )

    @classmethod
    def from_artifacts(
        cls,
        project_root: str | Path | None = None,
    ) -> "CustomerIntelligence":
        """Load the committed model files and Year 1 order-date boundaries."""
        root = Path(project_root) if project_root is not None else _DEFAULT_PROJECT_ROOT
        purchase_dir = root / "models" / "purchase_clock"
        spending_dir = root / "models" / "spending_model"
        orders_path = root / "data" / "processed" / "temporal" / "orders.csv"
        if not orders_path.is_file():
            raise FileNotFoundError(f"Year 1 order data not found: {orders_path}")
        orders = pd.read_csv(orders_path, usecols=["PurchaseDate"], parse_dates=["PurchaseDate"])
        if orders.empty:
            raise ValueError(f"Year 1 order data is empty: {orders_path}")
        purchase_bundle = pc.load_purchase_clock_artifacts(purchase_dir)
        spending_bundle = sm.load_spending_artifacts(spending_dir)
        validation_dir = purchase_dir / "validation_vintage"
        validation_bundle = (
            pc.load_purchase_clock_artifacts(validation_dir)
            if (validation_dir / "purchase_clock.joblib").is_file()
            else None
        )
        return cls(
            purchase_bundle,
            spending_bundle,
            validation_purchase_bundle=validation_bundle,
            dataset_start=orders["PurchaseDate"].min(),
            dataset_end=orders["PurchaseDate"].max(),
        )

    def _eligible_horizons(self, cutoff: pd.Timestamp) -> dict[int, str]:
        eligible: dict[int, str] = {}
        if cutoff == self._test_cutoff:
            for horizon in self.supported_horizons:
                eligible[horizon] = "out-of-time TEST (historical; not real-time)"
            return eligible
        for horizon in self.supported_horizons:
            entry = self._protocol.get(str(horizon), {})
            try:
                protocol_cutoff = pd.Timestamp(entry["cutoff"])
            except (KeyError, TypeError, ValueError):
                continue
            if cutoff == protocol_cutoff:
                status = str(entry.get("status", "")).lower()
                if status in {"prospective", "retrospective/exploratory"}:
                    eligible[horizon] = str(entry["status"])
        return eligible

    def predict_customers(
        self,
        transactions: pd.DataFrame,
        cutoff_date: pd.Timestamp,
        *,
        customer_ids: Iterable | int | str | None = None,
        horizons: Sequence[int] | None = None,
    ) -> pd.DataFrame:
        """Predict purchase and expected-spending outcomes for one cutoff.

        Only historically authorized Notebook 07 cutoff/horizon pairs are
        accepted: validation forecasts use their declared vintage; the
        September 2010 test cutoff supports all model horizons. June 2010's
        90-day joint forecast is marked retrospective/exploratory in metadata.
        No future target or evaluation label is read or returned.
        """
        cutoff = pd.Timestamp(cutoff_date)
        if pd.isna(cutoff) or cutoff.tz is not None or cutoff != cutoff.normalize():
            raise ValueError("cutoff_date must be a timezone-naive date at midnight.")
        if cutoff + pd.Timedelta(days=min(self.supported_horizons)) > self.dataset_end:
            raise ValueError("cutoff_date is outside the observable Year 1 data window.")

        eligible = self._eligible_horizons(cutoff)
        if not eligible:
            raise ValueError(
                "No saved Notebook 06/07 model is historically eligible at "
                f"cutoff {cutoff.date()}."
            )
        requested_horizons = (
            sorted(eligible)
            if horizons is None
            else sorted({int(horizon) for horizon in horizons})
        )
        if not requested_horizons:
            raise ValueError("At least one forecast horizon must be requested.")
        unsupported = sorted(set(requested_horizons).difference(self.supported_horizons))
        if unsupported:
            raise ValueError(f"Unsupported forecast horizons: {unsupported}")
        unobservable = [
            horizon
            for horizon in requested_horizons
            if cutoff + pd.Timedelta(days=horizon) > self.dataset_end
        ]
        if unobservable:
            raise ValueError(
                f"Forecast horizons {unobservable} are not fully observable by "
                f"the Year 1 data end ({self.dataset_end})."
            )
        ineligible = sorted(set(requested_horizons).difference(eligible))
        if ineligible:
            raise ValueError(
                f"Horizons {ineligible} are not validated for cutoff {cutoff.date()}; "
                f"eligible horizons are {sorted(eligible)}."
            )
        if self.dataset_start is not None and cutoff <= self.dataset_start:
            raise ValueError("cutoff_date must follow the start of the Year 1 history.")

        clean = validate_transaction_history(transactions, cutoff)
        if clean["InvoiceDate"].max() > self.dataset_end:
            raise ValueError(
                "Transactions extend beyond the Year 1 model scope; these artifacts "
                "cannot be applied to Year 2 or later data."
            )
        if self.dataset_start is not None and clean["InvoiceDate"].min() < self.dataset_start:
            raise ValueError("Transactions begin before the Year 1 model scope.")

        # Future transaction rows are intentionally discarded before aggregation.
        historical = clean.loc[clean["InvoiceDate"] < cutoff].copy()
        orders = tf.build_order_level_dataset(historical)
        if orders.empty:
            raise ValueError("No valid historical purchase orders exist before cutoff_date.")
        feature_frame = tf.compute_historical_features(orders, cutoff)
        if feature_frame.empty:
            raise ValueError("No customers have an eligible pre-cutoff purchase history.")
        selected_ids = _normalize_customer_ids(customer_ids)
        if selected_ids is not None:
            found_ids = set(feature_frame["Customer ID"].astype(int))
            absent = sorted(set(selected_ids).difference(found_ids))
            if absent:
                raise ValueError(
                    f"Requested customers have no valid pre-cutoff purchase history: {absent}"
                )
            feature_frame = feature_frame.loc[
                feature_frame["Customer ID"].isin(selected_ids)
            ].copy()
        if feature_frame.empty:
            raise ValueError("No eligible customer features remain for inference.")

        model = self.purchase_bundle
        # The June/July/August validation forecasts use the Jan-Apr vintage.
        if cutoff != self._test_cutoff:
            if cutoff == pd.Timestamp("2010-06-01"):
                # Notebook 07 explicitly labels this 90-day forecast retrospective.
                model = self.purchase_bundle
            elif self.validation_purchase_bundle is not None:
                model = self.validation_purchase_bundle
            else:
                raise ValueError(
                    "A validation-vintage purchase-clock artifact is required for "
                    f"prospective cutoff {cutoff.date()}."
                )

        feature_columns = list(sm.BASE_FEATURE_COLUMNS)
        missing = [column for column in feature_columns if column not in feature_frame]
        if missing:
            raise ValueError(f"Historical feature construction omitted model fields: {missing}")
        model_features = feature_frame.loc[:, feature_columns].reset_index(drop=True)
        purchase_predictions = pc.predict_purchase_clock(model, model_features)
        revenue_predictions = sm.predict_expected_revenue(
            self.spending_bundle,
            model_features,
            purchase_predictions,
        )

        base = model_features.loc[:, [sm.CUSTOMER_ID, sm.CUTOFF_COL]].reset_index(drop=True)
        output = base.copy()
        for horizon in requested_horizons:
            probability_column = f"personalized_P{horizon}"
            output[f"prediction_protocol_{horizon}d"] = eligible[horizon]
            output[f"global_purchase_probability_{horizon}d"] = purchase_predictions[
                f"global_P{horizon}"
            ].to_numpy(dtype=float)
            output[f"segment_purchase_probability_{horizon}d"] = purchase_predictions[
                f"segment_P{horizon}"
            ].to_numpy(dtype=float)
            output[f"purchase_probability_{horizon}d"] = purchase_predictions[
                probability_column
            ].to_numpy(dtype=float)
            for source, target in (
                (
                    f"historical_rate_expected_{horizon}d",
                    f"historical_rate_expected_revenue_{horizon}d",
                ),
                (
                    f"segment_conditional_revenue_{horizon}d",
                    f"segment_conditional_revenue_{horizon}d",
                ),
                (
                    f"segment_expected_revenue_{horizon}d",
                    f"segment_expected_revenue_{horizon}d",
                ),
                (
                    f"personalized_conditional_revenue_{horizon}d",
                    f"personalized_conditional_revenue_{horizon}d",
                ),
                (
                    f"personalized_expected_revenue_{horizon}d",
                    f"personalized_expected_revenue_{horizon}d",
                ),
            ):
                output[target] = revenue_predictions[source].to_numpy(dtype=float)

        if output.duplicated([sm.CUSTOMER_ID, sm.CUTOFF_COL]).any():
            raise AssertionError("Inference returned duplicate customer/cutoff rows.")
        if set(output.columns).intersection(pc.TARGET_COLUMNS):
            raise AssertionError("Inference output contains future targets or labels.")
        predicted_columns = [
            column for column in output.columns
            if column not in {sm.CUSTOMER_ID, sm.CUTOFF_COL}
            and not column.startswith("prediction_protocol_")
        ]
        values = output[predicted_columns].to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise ValueError("Inference produced non-finite predictions.")
        return output.reset_index(drop=True)


def predict_customers(
    transactions: pd.DataFrame,
    cutoff_date: pd.Timestamp,
    *,
    customer_ids: Iterable | int | str | None = None,
    horizons: Sequence[int] | None = None,
    project_root: str | Path | None = None,
) -> pd.DataFrame:
    """Convenience function that loads saved artifacts and predicts once."""
    service = CustomerIntelligence.from_artifacts(project_root)
    return service.predict_customers(
        transactions,
        cutoff_date,
        customer_ids=customer_ids,
        horizons=horizons,
    )
