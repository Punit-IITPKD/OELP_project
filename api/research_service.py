"""Read-only access to the precomputed final research evaluation."""

from __future__ import annotations

import json
from functools import lru_cache

from app.config import METRICS_DIR, PROJECT_ROOT
from api.schemas import FinalResearchSummary
from src.final_evaluation import ARTIFACT_VERSION, current_source_manifest

_SUMMARY_PATH = METRICS_DIR / "final_project_evaluation.json"


@lru_cache(maxsize=1)
def _load_summary() -> dict:
    if not _SUMMARY_PATH.is_file():
        raise FileNotFoundError("The final research summary has not been generated.")
    try:
        payload = json.loads(_SUMMARY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("The final research summary cannot be read.") from error
    if not isinstance(payload, dict) or payload.get("artifact_version") != ARTIFACT_VERSION:
        raise ValueError("The final research summary has an unsupported version.")
    if payload.get("source_manifest") != current_source_manifest(PROJECT_ROOT):
        raise ValueError("The final research summary is stale for the current evidence.")
    return FinalResearchSummary.model_validate(payload).model_dump(mode="json")


def get_research_summary() -> dict:
    """Return the read-only aggregate summary; never load customers or models."""
    return _load_summary()
