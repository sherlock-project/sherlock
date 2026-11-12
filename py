#!/usr/bin/env bash
set -e
if ! command -v python >/dev/null 2>&1; then
  echo "python is not on PATH" >&2
  exit 1
fi
exec python "$@"
