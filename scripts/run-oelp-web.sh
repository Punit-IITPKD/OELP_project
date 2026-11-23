#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"
export PORT="${PORT:-5000}"
export BASE_PATH="${BASE_PATH:-/}"

uv run --no-project --python 3.11 --with-requirements requirements-ci.txt uvicorn api.main:app --host 127.0.0.1 --port 8000 &
API_PID=$!

cleanup() {
  kill "$API_PID" 2>/dev/null || true
  wait "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

ready=0
for _ in $(seq 1 60); do
  if curl --silent --fail http://127.0.0.1:8000/api/health >/dev/null; then
    ready=1
    break
  fi
  if ! kill -0 "$API_PID" 2>/dev/null; then
    wait "$API_PID"
    echo "FastAPI exited before its health check passed." >&2
    exit 1
  fi
  sleep 1
done

if [[ "$ready" -ne 1 ]]; then
  echo "FastAPI did not become healthy within 60 seconds." >&2
  exit 1
fi

pnpm --filter @workspace/oelp-customer-intelligence run dev:vite
