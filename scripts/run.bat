@echo off
setlocal ENABLEDELAYEDEXPANSION

REM -------------------------------------------------------------
REM Windows launcher for AI Interviewer (mirrors scripts/run.sh)
REM 1. Create/activate venv
REM 2. Install/upgrade deps
REM 3. Launch Streamlit app
REM -------------------------------------------------------------

REM Detect Python
where python >NUL 2>&1
if errorlevel 1 (
  echo [error] Python not found in PATH. Install Python 3.10+ and retry.
  exit /b 1
)

if not exist .venv (
  echo [setup] Creating virtual environment (.venv)
  python -m venv .venv || (
    echo [error] Failed to create virtual environment
    exit /b 1
  )
)

call .venv\Scripts\activate || (
  echo [error] Failed to activate virtual environment
  exit /b 1
)

echo [setup] Upgrading pip
python -m pip install --upgrade pip >NUL

echo [setup] Installing / updating dependencies
pip install -r requirements.txt || (
  echo [error] Dependency installation failed
  exit /b 1
)

echo.
echo [info] If Ollama is not installed on Windows run: winget install Ollama.Ollama

echo [run] Starting Streamlit application
streamlit run app.py

endlocal
