#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

python_cmd="python3"

if [ ! -d "$VENV_DIR" ]; then
  echo "[setup] Creating virtual environment at $VENV_DIR"
  $python_cmd -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "[setup] Upgrading pip"
python -m pip install --upgrade pip >/dev/null

echo "[setup] Installing requirements"
pip install -r "$ROOT_DIR/requirements.txt"

echo "[run] Starting Streamlit app"
exec streamlit run "$ROOT_DIR/app.py"
