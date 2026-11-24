"""Generate or verify the deterministic 11-notebook research summary."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import PROJECT_ROOT
from src.final_evaluation import OUTPUT_PATH, build_final_evaluation, encode_final_evaluation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the checked-in summary differs from the current source evidence.",
    )
    args = parser.parse_args()

    output_path = OUTPUT_PATH
    expected = encode_final_evaluation(build_final_evaluation(PROJECT_ROOT))
    if args.check:
        if not output_path.is_file():
            parser.error(f"Generated research summary is missing: {output_path}")
        actual = output_path.read_bytes()
        if actual != expected:
            print("Final research summary is stale; run python scripts/build_final_evaluation.py.")
            return 1
        print(f"Final research summary is reproducible: {output_path.relative_to(PROJECT_ROOT)}")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=output_path.parent,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary:
        temporary.write(expected)
        temporary.flush()
        os.fsync(temporary.fileno())
        temporary_path = temporary.name
    os.chmod(temporary_path, 0o644)
    os.replace(temporary_path, output_path)
    print(f"Wrote {output_path.relative_to(PROJECT_ROOT)} ({len(expected)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
