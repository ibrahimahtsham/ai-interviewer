from dataclasses import dataclass
import os
from typing import Literal


# New, user-friendly profile labels
PCProfile = Literal["low-end pc", "mid specs", "high end pc"]


@dataclass(frozen=True)
class Config:
    pc_profile: PCProfile = "low-end pc"
    llm_backend: str = "ollama"
    llm_model: str = "llama3:8b"
    tts_voice: str = "default"


def _map_legacy_profile(value: str) -> str:
    v = (value or "").strip().lower()
    legacy_map = {
        "low-cpu": "low-end pc",
        "cpu": "mid specs",
        "gpu": "high end pc",
        "low-end": "low-end pc",
        "mid": "mid specs",
        "high": "high end pc",
    }
    if v in {"low-end pc", "mid specs", "high end pc"}:
        return v
    return legacy_map.get(v, "low-end pc")


def load_config() -> Config:
    return Config(
        pc_profile=_map_legacy_profile(os.getenv("PC_PROFILE", "low-end pc")),
        llm_backend=os.getenv("LLM_BACKEND", "ollama"),
        llm_model=os.getenv("LLM_MODEL", "llama3:8b"),
        tts_voice=os.getenv("TTS_VOICE", "default"),
    )
