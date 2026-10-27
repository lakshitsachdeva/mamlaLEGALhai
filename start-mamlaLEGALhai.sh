#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"
port="${MAMLALEGALHAI_PORT:-${REGULATRACE_PORT:-8000}}"
url="http://127.0.0.1:$port"
if command -v curl >/dev/null 2>&1; then
  health="$(curl -fsS --max-time 2 "$url/api/health" 2>/dev/null || true)"
  if [ -n "$health" ]; then
    case "$health" in
      *'"service":"mamlalegalhai-api"'*) printf 'mamlaLEGALhai is already running: %s/#executive\n' "$url"; exit 0 ;;
      *) printf 'Port %s is occupied by another service.\n' "$port" >&2; exit 1 ;;
    esac
  fi
fi
if [ ! -x .venv/bin/python ]; then
  if command -v python3.12 >/dev/null 2>&1; then
    python3.12 -m venv .venv
  else
    python3 -m venv .venv
  fi
fi

.venv/bin/python -m pip install -r requirements.txt
printf 'Starting mamlaLEGALhai: %s/#executive\n' "$url"
exec .venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port "$port"
