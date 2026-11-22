from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
METRICS_DIR = PROJECT_ROOT / "data" / "metrics"

PREDICTION_CUTOFF = "2010-09-10"
PREDICTION_HORIZONS = (30, 60, 90)
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
