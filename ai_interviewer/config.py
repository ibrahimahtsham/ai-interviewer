from dataclasses import dataclass
import os
from typing import Literal


PCProfile = Literal["low-cpu", "cpu", "gpu"]


@dataclass(frozen=True)
class Config:
    pc_profile: PCProfile = "low-cpu"
    llm_backend: str = "dummy"  # "dummy" or "ollama"
    llm_model: str = "llama3"
    tts_voice: str = "default"


def load_config() -> Config:
    return Config(
        pc_profile=os.getenv("PC_PROFILE", "cpu"),
        llm_backend=os.getenv("LLM_BACKEND", "dummy"),
        llm_model=os.getenv("LLM_MODEL", "llama3"),
        tts_voice=os.getenv("TTS_VOICE", "default"),
    )
