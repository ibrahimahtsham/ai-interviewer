#!/usr/bin/env bash
set -euo pipefail

# Minimal runner for Linux/macOS
PYTHON_BIN=${PYTHON_BIN:-python3}
VENV_DIR=.venv

if [ ! -d "$VENV_DIR" ]; then
  echo "[setup] Creating venv in $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

ACTIVATE="${VENV_DIR}/bin/activate"
if [ ! -f "$ACTIVATE" ]; then
  echo "[error] Could not find activate script at $ACTIVATE"
  exit 1
fi

source "$ACTIVATE"

PYTHON="python"
PIP="pip"

echo "[setup] Upgrading pip"
$PYTHON -m pip install --upgrade pip wheel

echo "[setup] Installing requirements"
$PIP install -r requirements.txt

echo "[run] Launching Streamlit app"
exec $PYTHON -m streamlit run app.py --server.headless=false
