Param(
    [string]$PythonBin = "python"
)

$ErrorActionPreference = "Stop"

$VenvDir = ".venv"
if (!(Test-Path $VenvDir)) {
    Write-Host "[setup] Creating venv in $VenvDir"
    & $PythonBin -m venv $VenvDir
}

$Activate = Join-Path $VenvDir "Scripts/Activate.ps1"
if (!(Test-Path $Activate)) {
    Write-Error "[error] Could not find activate script at $Activate"
    exit 1
}

. $Activate

Write-Host "[setup] Upgrading pip"
python -m pip install --upgrade pip wheel

Write-Host "[setup] Installing requirements"
pip install -r requirements.txt

Write-Host "[run] Launching Streamlit app"
python -m streamlit run app.py --server.headless=$false
