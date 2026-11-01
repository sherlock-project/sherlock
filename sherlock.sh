#!/usr/bin/env bash

# -------------------------------------------------------------
# Sherlock Launcher for Linux / macOS / Unix / Git Bash
# -------------------------------------------------------------

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Locate virtual environment or system Python (handles both Linux/macOS and Windows Git Bash)
if [ -f "$SCRIPT_DIR/venv/bin/sherlock" ]; then
    RUNNER="$SCRIPT_DIR/venv/bin/sherlock"
elif [ -f "$SCRIPT_DIR/venv/Scripts/sherlock.exe" ]; then
    RUNNER="$SCRIPT_DIR/venv/Scripts/sherlock.exe"
elif [ -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    RUNNER="$SCRIPT_DIR/venv/bin/python3 -m sherlock_project"
elif [ -f "$SCRIPT_DIR/venv/Scripts/python.exe" ]; then
    RUNNER="$SCRIPT_DIR/venv/Scripts/python.exe -m sherlock_project"
elif command -v python3 >/dev/null 2>&1; then
    RUNNER="python3 -m sherlock_project"
elif command -v python >/dev/null 2>&1; then
    RUNNER="python -m sherlock_project"
else
    echo "[ERROR] Python 3 was not found on your system!"
    echo "Please install Python 3.9+ to run Sherlock."
    exit 1
fi

# If CLI arguments are provided, execute directly
if [ "$#" -gt 0 ]; then
    exec $RUNNER "$@"
fi

# Interactive mode when executed without arguments
clear
echo "============================================================"
echo "                    SHERLOCK LAUNCHER                       "
echo "        Hunt down social media accounts by username         "
echo "============================================================"
echo ""

read -rp "Enter username(s) to search (or 'q' to quit): " TARGET_USER

if [ -z "$TARGET_USER" ]; then
    echo "[!] No username entered."
    exit 1
fi

case "$TARGET_USER" in
    q|Q|exit|quit)
        exit 0
        ;;
esac

echo ""
echo "Optional flags:"
echo "  1. Standard search (default)"
echo "  2. Save to CSV file (--csv)"
echo "  3. Save to Excel spreadsheet (--xlsx)"
echo "  4. Show only found accounts (--print-found)"
echo "  5. Include NSFW sites (--nsfw)"
echo "  6. Custom arguments"
echo ""
read -rp "Select an option [1-6, default=1]: " FLAG_CHOICE

EXTRA_FLAGS=""
case "$FLAG_CHOICE" in
    2) EXTRA_FLAGS="--csv" ;;
    3) EXTRA_FLAGS="--xlsx" ;;
    4) EXTRA_FLAGS="--print-found" ;;
    5) EXTRA_FLAGS="--nsfw" ;;
    6)
        read -rp "Enter custom flags (e.g. --csv --print-found --timeout 30): " EXTRA_FLAGS
        ;;
    *)
        EXTRA_FLAGS=""
        ;;
esac

echo ""
echo "[*] Running Sherlock for: $TARGET_USER $EXTRA_FLAGS"
echo ""

$RUNNER $TARGET_USER $EXTRA_FLAGS

echo ""
echo "============================================================"
echo "Search finished! Results (if any) are saved in the current folder."
echo "============================================================"
echo ""
