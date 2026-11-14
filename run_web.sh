#!/bin/sh
# Chạy giao diện web của Sherlock: sh run_web.sh
cd "$(dirname "$0")" || exit 1
PY=python3
command -v $PY >/dev/null 2>&1 || PY=python
if ! command -v $PY >/dev/null 2>&1; then
  echo "Không tìm thấy Python. Hãy cài Python 3.9+ từ https://www.python.org/downloads/"
  exit 1
fi
if [ ! -d .venv ]; then
  echo "Lần đầu chạy: đang tạo môi trường và cài thư viện..."
  $PY -m venv .venv || exit 1
  .venv/bin/python -m pip install -q --upgrade pip
  .venv/bin/python -m pip install -q -e . || exit 1
fi
exec .venv/bin/python web/server.py --open "$@"
