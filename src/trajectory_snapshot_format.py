"""Lightweight contract shared by the offline snapshot builder and API loader."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

SNAPSHOT_SCHEMA_VERSION = "trajectory-serving-v1"
SOURCE_RELATIVE_PATHS = (
    "data/processed/temporal/orders.csv",
    "data/processed/temporal/predictive_splits_30d.csv",
    "data/metrics/trajectory_analysis_evaluation.json",
    "models/trajectory_analysis/metadata.json",
    "models/trajectory_analysis/summary_clusters.joblib",
    "models/trajectory_analysis/shape_clusters.joblib",
    "models/trajectory_analysis/functional_pca.joblib",
)


def source_manifest(root: Path) -> list[dict[str, Any]]:
    manifest = []
    for relative in SOURCE_RELATIVE_PATHS:
        path = Path(root) / relative
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        manifest.append({"path": relative, "sha256": digest})
    return manifest
