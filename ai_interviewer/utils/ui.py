from __future__ import annotations
import re
from typing import List, Dict, Optional

from ai_interviewer.profiles import PCProfile, normalize_profile

# Approximate download sizes for common Ollama models (GB, quantized defaults).
# These are estimates and can vary by quantization/build. Used for UI only.
MODEL_CATALOG: Dict[str, float] = {
    # Ultra-small
    "tinyllama:1.1b": 0.6,
    "llama3.2:1b": 0.9,
    # Small (~2-4GB)
    "llama3.2:3b": 2.3,
    "phi3:3.8b": 2.8,
    "qwen2.5:3b": 2.6,
    "gemma2:2b": 1.6,
    # Medium (~4-8GB)
    "mistral:7b": 4.2,
    "qwen2:7b": 5.0,
    "llama3:8b": 4.7,
    # Large
    "llama2:13b": 8.0,
    "llama3.1:70b": 40.0,
}


def pc_profile_model_candidates(profile: PCProfile | str) -> List[str]:
    """Return a list of model names ordered by size for the profile.

    - LOW: ascending by approximate size (smallest first)
    - HIGH: descending by approximate size (largest first)
    Unknown sizes (not in catalog) are appended at the end in arbitrary order.
    """
    p = normalize_profile(profile)
    known = sorted(MODEL_CATALOG.items(), key=lambda kv: kv[1])  # ascending by GB
    known_names = [name for name, _ in known]
    # In case there are models outside the catalog, list them last (none at the moment)
    unknown_names: List[str] = []
    names = known_names + unknown_names
    if p == PCProfile.HIGH:
        names = list(reversed(names))
    return names


def choose_model_for_profile(profile: PCProfile | str, installed: list[str]) -> str:
    suggestions = pc_profile_model_candidates(profile)
    for s in suggestions:
        if s in installed:
            return s
    return suggestions[0] if suggestions else "llama3:8b"


def append_console(line: str, session_state) -> None:
    lines = session_state.setdefault("console", [])
    lines.append(line)
    session_state["console"] = lines


def parse_percent(line: str) -> int | None:
    m = re.search(r"(\d{1,3})\s*%", line)
    if not m:
        return None
    p = int(m.group(1))
    return max(0, min(100, p))


def get_model_size_gb(name: str) -> Optional[float]:
    return MODEL_CATALOG.get(name)


def format_size_gb(gb: float) -> str:
    if gb < 1.0:
        # Show in MB for tiny models
        return f"≈ {int(gb * 1024)} MB"
    # One decimal is enough for readability
    return f"≈ {gb:.1f} GB"


def get_model_size_label(name: str) -> Optional[str]:
    size = get_model_size_gb(name)
    if size is None:
        return None
    return format_size_gb(size)
