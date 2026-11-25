#!/usr/bin/env python3
"""Measure cold and warm Phase 7 API requests using fresh Uvicorn processes."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENDPOINTS = {
    "research_summary": "/api/research/summary",
    "trajectory_summary": "/api/trajectories/summary",
    "trajectory_customer": "/api/customers/18102/trajectory",
}


def _available_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _rss_bytes(pid: int) -> int | None:
    status_path = Path(f"/proc/{pid}/status")
    if not status_path.is_file():
        return None
    for line in status_path.read_text().splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) * 1024
    return None


def _request(url: str, timeout: float = 15) -> tuple[int, bytes, float]:
    started = time.perf_counter()
    try:
        with urlopen(url, timeout=timeout) as response:
            body = response.read()
            return response.status, body, (time.perf_counter() - started) * 1000
    except URLError as error:
        raise RuntimeError(f"Request failed: {url}: {error}") from error


def _start_server() -> tuple[subprocess.Popen[bytes], str, float]:
    port = _available_port()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "error",
        ],
        cwd=PROJECT_ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base_url = f"http://127.0.0.1:{port}"
    started = time.perf_counter()
    deadline = started + 60
    while time.perf_counter() < deadline:
        if process.poll() is not None:
            raise RuntimeError("Uvicorn exited before the health check became ready.")
        try:
            status, _, _ = _request(f"{base_url}/api/health", timeout=1)
            if status == 200:
                return process, base_url, (time.perf_counter() - started) * 1000
        except RuntimeError:
            pass
        time.sleep(0.1)
    process.terminate()
    raise TimeoutError("Uvicorn did not become healthy within 60 seconds.")


def _stop_server(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def _summarize(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    p95_index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return {
        "samples": len(values),
        "median_ms": ordered[len(ordered) // 2] if len(ordered) % 2 else (ordered[len(ordered) // 2 - 1] + ordered[len(ordered) // 2]) / 2,
        "p95_ms": ordered[p95_index],
        "min_ms": ordered[0],
        "max_ms": ordered[-1],
    }


def _cold_trials(endpoint: str, count: int) -> tuple[list[float], list[float], int]:
    latencies: list[float] = []
    startup: list[float] = []
    response_bytes = 0
    for _ in range(count):
        process, base_url, ready_ms = _start_server()
        startup.append(ready_ms)
        try:
            status, body, elapsed_ms = _request(base_url + ENDPOINTS[endpoint])
            if status != 200:
                raise RuntimeError(f"{endpoint} returned HTTP {status}.")
            latencies.append(elapsed_ms)
            response_bytes = len(body)
        finally:
            _stop_server(process)
    return latencies, startup, response_bytes


def _warm_trials(endpoint: str, count: int) -> tuple[list[float], int, int | None]:
    process, base_url, _ = _start_server()
    try:
        status, body, _ = _request(base_url + ENDPOINTS[endpoint])
        if status != 200:
            raise RuntimeError(f"Warm-up {endpoint} returned HTTP {status}.")
        rss = _rss_bytes(process.pid)
        latencies: list[float] = []
        for _ in range(count):
            status, body, elapsed_ms = _request(base_url + ENDPOINTS[endpoint])
            if status != 200:
                raise RuntimeError(f"{endpoint} returned HTTP {status}.")
            latencies.append(elapsed_ms)
        return latencies, len(body), rss
    finally:
        _stop_server(process)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--warm-samples", type=int, default=20)
    args = parser.parse_args()
    if args.trials < 1 or args.warm_samples < 1:
        parser.error("trial and warm-sample counts must be positive.")

    output: dict[str, object] = {
        "python_version": sys.version.split()[0],
        "cpu_count": os.cpu_count(),
        "fresh_process_trials": args.trials,
        "warm_samples_per_endpoint": args.warm_samples,
        "measurements": {},
    }
    measurements: dict[str, object] = output["measurements"]  # type: ignore[assignment]
    startup_samples: list[float] = []
    for endpoint in ENDPOINTS:
        cold, startup, response_bytes = _cold_trials(endpoint, args.trials)
        startup_samples.extend(startup)
        warm, warm_bytes, rss = _warm_trials(endpoint, args.warm_samples)
        measurements[endpoint] = {
            "cold": _summarize(cold),
            "warm": _summarize(warm),
            "response_bytes": response_bytes,
            "warm_response_bytes": warm_bytes,
            "process_rss_bytes_after_warmup": rss,
        }
    output["process_start_to_health_ready"] = _summarize(startup_samples)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
