#!/usr/bin/env bash
# LaunchFolio — one-command setup for Mac / Linux
set -e

echo ""
echo "  LaunchFolio — Setup"
echo "  ─────────────────────────────────────────"
echo ""

# 1. Check Python 3
if ! command -v python3 &>/dev/null; then
  echo "  ERROR: Python 3 is not installed."
  echo ""
  echo "  Mac:   Download from https://www.python.org/downloads/"
  echo "  Linux: sudo apt install python3 python3-pip"
  echo ""
  exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "  Python: $PYTHON_VERSION"

# 2. Install dependencies
echo "  Installing dependencies..."
pip3 install -r backend/requirements.txt --quiet

echo "  Dependencies installed."
echo ""
echo "  ─────────────────────────────────────────"
echo "  Starting LaunchFolio at http://localhost:5000"
echo "  Press Ctrl+C to stop."
echo "  ─────────────────────────────────────────"
echo ""

# 3. Start the server
python3 backend/generate.py --serve
