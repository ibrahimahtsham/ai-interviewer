from __future__ import annotations

"""Speech-to-Text (STT) utilities using faster-whisper.

Contract:
- STTConfig: configuration for transcribe functions
- transcribe_file(path: str, cfg: STTConfig | None) -> str
- transcribe_bytes(data: bytes, cfg: STTConfig | None) -> str

Also exposes simple model selection helpers keyed to the existing PC profiles.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path
import tempfile

from ai_interviewer.profiles import PCProfile, normalize_profile


# Approx sizes (GB) for UI ordering only
STT_MODEL_CATALOG: Dict[str, float] = {
    "tiny.en": 0.1,
    "base.en": 0.15,
    "small.en": 0.5,
    "medium.en": 1.5,
}

_loaded_models: Dict[str, object] = {}


def stt_model_candidates(profile: PCProfile | str) -> List[str]:
    p = normalize_profile(profile)
    names = sorted(STT_MODEL_CATALOG.items(), key=lambda kv: kv[1])
    ordered = [n for n, _ in names]
    if p == PCProfile.HIGH:
        ordered = list(reversed(ordered))
    return ordered


def choose_stt_model_for_profile(profile: PCProfile | str) -> str:
    cands = stt_model_candidates(profile)
    return cands[0] if cands else "tiny.en"


@dataclass
class STTConfig:
    model: str = "tiny.en"
    language: str = "en"
    vad_filter: bool = True
    compute_type: str = "int8"  # light default; override via env if needed


def _get_model(name: str, compute_type: str = "int8"):
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError("faster-whisper is required for STT but not installed") from e

    if name in _loaded_models:
        return _loaded_models[name]
    # Try auto (GPU if available); gracefully fallback to CPU if CUDA/cuBLAS missing
    try:
        m = WhisperModel(name, device="auto", compute_type=compute_type)
    except Exception as e:  # pragma: no cover - environment specific
        msg = str(e).lower()
        if ("cublas" in msg) or ("cuda" in msg):
            try:
                from ai_interviewer.utils.log import warn
                warn("CUDA/cuBLAS not available; falling back to CPU for STT.")
            except Exception:
                pass
            m = WhisperModel(name, device="cpu", compute_type=compute_type)
        else:
            raise
    _loaded_models[name] = m
    return m


def transcribe_file(path: str, cfg: Optional[STTConfig] = None) -> str:
    """Transcribe a WAV/MP3/etc file to text (English)."""
    c = cfg or STTConfig()
    model = _get_model(c.model, compute_type=c.compute_type)
    segments, _info = model.transcribe(
        path,
        language=c.language,
        vad_filter=c.vad_filter,
    )
    text_parts: list[str] = []
    for seg in segments:
        try:
            text_parts.append(seg.text)
        except Exception:
            pass
    return " ".join(t.strip() for t in text_parts if t and t.strip())


def transcribe_bytes(data: bytes, cfg: Optional[STTConfig] = None) -> str:
    """Write bytes to a temp wav and transcribe."""
    tmpdir = tempfile.mkdtemp(prefix="ai-intvw-")
    wav_path = str(Path(tmpdir) / "audio.wav")
    Path(wav_path).write_bytes(data)
    return transcribe_file(wav_path, cfg)
