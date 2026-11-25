from __future__ import annotations

import gzip
import json

import pytest

from api import trajectory_service
from src.trajectory_serving_snapshot import dataframe_records
from src.trajectory_snapshot_format import (
    SNAPSHOT_SCHEMA_VERSION,
    source_manifest,
)


def test_trajectory_snapshot_has_current_provenance_and_no_future_targets() -> None:
    with gzip.open(trajectory_service._SNAPSHOT_PATH, "rt", encoding="utf-8") as stream:
        payload = json.load(stream)

    assert payload["schema_version"] == SNAPSHOT_SCHEMA_VERSION
    assert payload["source_manifest"] == source_manifest(
        trajectory_service.PROJECT_ROOT
    )
    bundle = payload["bundle"]
    assert bundle["cutoff_date"] == "2010-09-10"
    assert len(bundle["features"]) == 3373
    assert len(bundle["matrix"]) > len(bundle["features"])
    feature_columns = set(bundle["features"][0])
    assert not any(
        column.lower().startswith(("futureorders_", "futurerevenue_", "purchased_"))
        for column in feature_columns
    )


def test_trajectory_snapshot_loader_rejects_stale_sources(monkeypatch) -> None:
    trajectory_service._get_trajectory_bundle.cache_clear()
    monkeypatch.setattr(trajectory_service, "source_manifest", lambda _root: [])
    try:
        with pytest.raises(ValueError, match="stale"):
            trajectory_service._get_trajectory_bundle()
    finally:
        trajectory_service._get_trajectory_bundle.cache_clear()


def test_snapshot_float_serialization_normalizes_sub_precision_drift() -> None:
    import pandas as pd

    first = dataframe_records(
        pd.DataFrame({"value": [8.289667508417503]})
    )
    second = dataframe_records(
        pd.DataFrame({"value": [8.289667508417505]})
    )

    assert first == second == [{"value": 8.289667508418}]
