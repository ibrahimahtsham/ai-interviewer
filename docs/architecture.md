AI Interviewer — Project Structure (Concise)

What it is

- A local Streamlit app that acts like an “AI interviewer”. You speak, it transcribes (STT), sends the transcript to a local LLM for an interviewer-style reply, then speaks the reply back (TTS). English only.

How it’s deployed (local-only)

- Single Streamlit app the user runs locally with a simple command.
- Everything runs on the user’s machine (no cloud required).
- No CORS/TLS complexity because UI and logic are in one app.

Core flow

1) Record audio in browser (start/stop single answer).
2) STT → English transcript.
3) LLM → interviewer-style reply (English only, enforced by system prompt).
4) TTS → synthesize reply audio.
5) Show reply text and play audio in the UI.

Controls in the UI

- Choose STT model size (lighter vs heavier for CPU/GPU).
- Choose LLM model from local Ollama.
- Choose TTS voice (English voices).

English-only behavior

- STT: language='en' (no auto-detect/translation).
- LLM: system prompt enforces English-only responses.
- TTS: English voice (en_US or en_GB, etc.).

Tools & technologies (concise)

- Python 3.10+
- Streamlit (UI)
- Mic capture: streamlit-webrtc or streamlit-mic-recorder
- STT: faster-whisper (CTranslate2) + ffmpeg
- LLM: Ollama (local models: llama3, mistral, qwen2.5, phi4)
- TTS: piper-tts (English voices)
- Optional: CUDA for GPU acceleration

Project structure (baseline)

root/
- app.py                        # Streamlit entrypoint (UI wiring)
- ai_interviewer/               # Python package
	- __init__.py
	- config.py                  # Config helpers (env, defaults)
	- preflight.py               # Environment checks (ffmpeg, ollama, piper)
	- audio/
		- io_utils.py              # WAV helpers, conversions
	- stt/
		- __init__.py
		- faster_whisper.py        # STT implementation (en, model selection)
	- llm/
		- __init__.py
		- ollama_client.py         # Local LLM calls with system prompt
	- tts/
		- __init__.py
		- piper_tts.py             # Piper integration (voice selection)
	- ui/
		- __init__.py
		- components.py            # Reusable Streamlit UI pieces
- scripts/
	- run.sh                     # Create venv, install deps, run app (Linux/macOS)
	- run.ps1                    # Same for Windows PowerShell
- requirements.txt             # Runtime deps (streamlit, requests, etc.)
- requirements-dev.txt         # Dev extras (pytest, black, mypy) [optional]
- .env.example                 # Example environment variables
- .streamlit/
	- config.toml                # Theme, runOnSave, telemetry settings
- tests/
	- test_stubs.py              # Smoke tests and core unit tests
- README.md                    # Quickstart, usage, troubleshooting
- LICENSE                      # Project license

Configuration & defaults

- .env (not committed) defines STT_MODEL, LLM_MODEL, PIPER_VOICE, etc.
- .streamlit/config.toml sets theme, runOnSave, headless.
- app.py reads config via ai_interviewer.config.

Preflight checks (optional but recommended)

- On first run, check availability: ffmpeg, ollama, piper, model files.
- Show friendly guidance if missing (install steps, env hints).

Coding guidelines

- Keep app.py thin: UI and orchestration only.
- Put integrations in ai_interviewer/stt|llm|tts modules with clear function contracts (pure functions where practical).
- Prefer dependency injection (e.g., pass model/voice names from UI to services).
- Handle errors with clear messages surfaced in the UI.

Testing

- Add smoke tests for basic imports and simple functions.
- Unit-test parsing/wrapping logic for STT/LLM/TTS modules (mock external binaries/services).

Next steps (implementation roadmap, high level)

1) Build mic capture UI and wire to STT (English).
2) Add Ollama call with system prompt enforcing English reply.
3) Add Piper TTS output and playback.
4) Add model/voice selectors with persisted defaults.
5) Add onboarding/setup to download recommended models.