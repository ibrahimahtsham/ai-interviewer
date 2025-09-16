from dataclasses import dataclass
import os

from ai_interviewer.profiles import PCProfile, normalize_profile


@dataclass(frozen=True)
class Config:
    pc_profile: PCProfile = PCProfile.LOW
    llm_backend: str = "ollama"
    llm_model: str = "tinyllama:1.1b"
    tts_voice: str = "default"


def _map_legacy_profile(value: str) -> PCProfile:
    # Delegate to central normalizer for all legacy strings and labels
    return normalize_profile(value)


def load_config() -> Config:
    return Config(
        pc_profile=_map_legacy_profile(os.getenv("PC_PROFILE", PCProfile.LOW.value)),
        llm_backend=os.getenv("LLM_BACKEND", "ollama"),
        llm_model=os.getenv("LLM_MODEL", "tinyllama:1.1b"),
        tts_voice=os.getenv("TTS_VOICE", "default"),
    )
