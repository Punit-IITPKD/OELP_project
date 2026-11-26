#!/usr/bin/env python3
"""Capture or verify checksums for canonical OELP research and model artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOTS = (
    "models/",
    "notebooks/",
    "data/raw/",
    "data/processed/",
    "data/metrics/",
    "data/serving/",
)


def tracked_artifacts() -> list[dict[str, int | str]]:
    tracked = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout.split(b"\0")
    artifacts = []

    for raw_path in tracked:
        if not raw_path:
            continue
        path = raw_path.decode("utf-8")
        if not path.startswith(ARTIFACT_ROOTS):
            continue

        file_path = ROOT / path
        if not file_path.is_file():
            continue

        digest = hashlib.sha256()
        size = 0
        with file_path.open("rb") as artifact:
            for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
        artifacts.append({"path": path, "sha256": digest.hexdigest(), "bytes": size})

    return sorted(artifacts, key=lambda item: str(item["path"]))


def capture(destination: Path) -> int:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    manifest = {
        "schema_version": 1,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "commit": commit,
        "artifact_roots": list(ARTIFACT_ROOTS),
        "artifacts": tracked_artifacts(),
    }
    destination = destination if destination.is_absolute() else ROOT / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Captured {len(manifest['artifacts'])} artifacts at {commit}")
    print(f"Manifest: {destination.relative_to(ROOT)}")
    return 0


def verify(source: Path) -> int:
    source = source if source.is_absolute() else ROOT / source
    expected = json.loads(source.read_text(encoding="utf-8"))
    expected_by_path = {entry["path"]: entry for entry in expected["artifacts"]}
    actual_by_path = {entry["path"]: entry for entry in tracked_artifacts()}

    missing = sorted(set(expected_by_path) - set(actual_by_path))
    added = sorted(set(actual_by_path) - set(expected_by_path))
    changed = sorted(
        path
        for path in set(expected_by_path) & set(actual_by_path)
        if expected_by_path[path]["sha256"] != actual_by_path[path]["sha256"]
    )

    if not (missing or added or changed):
        print(f"PASS: {len(actual_by_path)} canonical artifacts match {expected['commit']}")
        return 0

    print("FAIL: canonical artifact integrity differs from the baseline", file=sys.stderr)
    for label, paths in (("missing", missing), ("added", added), ("changed", changed)):
        for path in paths:
            print(f"{label}: {path}", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    capture_parser = commands.add_parser("capture", help="write a baseline checksum manifest")
    capture_parser.add_argument("destination", type=Path)
    verify_parser = commands.add_parser("verify", help="compare artifacts to a baseline manifest")
    verify_parser.add_argument("source", type=Path)
    args = parser.parse_args()

    if args.command == "capture":
        return capture(args.destination)
    return verify(args.source)


if __name__ == "__main__":
    raise SystemExit(main())
