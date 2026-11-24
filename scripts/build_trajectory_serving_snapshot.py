"""Build or verify the immutable precomputed trajectory API snapshot."""

from __future__ import annotations

import argparse
import gzip
import json
import os
from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.trajectory_serving_snapshot import (  # noqa: E402
    build_trajectory_bundle_from_sources,
    create_snapshot_payload,
)

OUTPUT_PATH = PROJECT_ROOT / "data/serving/trajectory_snapshot.json.gz"


def build_bytes() -> bytes:
    bundle = build_trajectory_bundle_from_sources(PROJECT_ROOT)
    payload = create_snapshot_payload(bundle, root=PROJECT_ROOT)
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return gzip.compress(encoded, compresslevel=9, mtime=0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the checked-in snapshot differs from current historical inputs.",
    )
    args = parser.parse_args()
    expected = build_bytes()
    if args.check:
        if not OUTPUT_PATH.is_file():
            parser.error(f"Trajectory serving snapshot is missing: {OUTPUT_PATH}")
        if OUTPUT_PATH.read_bytes() != expected:
            print("Trajectory serving snapshot is stale; rebuild it before serving.")
            return 1
        print(
            f"Trajectory serving snapshot is reproducible: "
            f"{OUTPUT_PATH.relative_to(PROJECT_ROOT)} ({len(expected)} bytes)"
        )
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=OUTPUT_PATH.parent,
        prefix=f".{OUTPUT_PATH.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary:
        temporary.write(expected)
        temporary.flush()
        os.fsync(temporary.fileno())
        temporary_path = temporary.name
    os.chmod(temporary_path, 0o644)
    os.replace(temporary_path, OUTPUT_PATH)
    print(
        f"Wrote {OUTPUT_PATH.relative_to(PROJECT_ROOT)} "
        f"({len(expected)} compressed bytes)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
