"""Minimal TTS using pyttsx3 (offline, cross-platform).

Contract:
    synthesize(text: str, voice: str | None, out_path: str) -> str
Returns the path to the audio file if successful; raises or returns empty string on failure.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


def _init_engine():
    try:
        import pyttsx3  # type: ignore
    except Exception as e:  # pragma: no cover - optional import at runtime
        raise RuntimeError("pyttsx3 is required for TTS but not installed") from e
    engine = pyttsx3.init()
    return engine


def synthesize(text: str, voice: Optional[str], out_path: str) -> str:
    engine = _init_engine()
    try:
        if voice and isinstance(voice, str) and voice != "default":
            # best-effort: set by name id substring
            try:
                for v in engine.getProperty("voices"):
                    if voice.lower() in (v.id or "").lower() or voice.lower() in (v.name or "").lower():
                        engine.setProperty("voice", v.id)
                        break
            except Exception:
                pass

        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        engine.save_to_file(text, str(out))
        engine.runAndWait()
        return str(out)
    finally:
        try:
            engine.stop()
        except Exception:
            pass
