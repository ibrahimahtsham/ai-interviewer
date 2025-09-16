# Simple Streamlit App

This is a minimal Streamlit app with a few interactive modes (Echo, Chart, Timer).

## Quick start

1. Create and activate a virtual environment (optional but recommended)
2. Install dependencies
3. Run the app

### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL that Streamlit prints (usually http://localhost:8501).

## Features added
- Interview flow with memory across turns
- LLM Setup tab for Ollama management and model selection
- STT Setup tab for Whisper model selection and a mic test
- Transcript tab to review and clear the entire conversation

Notes:
- STT uses faster-whisper and may require ffmpeg installed on your system for some audio formats.
	- Linux (Debian/Ubuntu): `sudo apt-get install ffmpeg`
	- macOS (Homebrew): `brew install ffmpeg`

## Customize
Open `app.py` and edit. Streamlit auto-reloads on save.
