from __future__ import annotations
import re
from typing import List


def _normalize_profile(profile: str) -> str:
    p = (profile or "").strip().lower()
    alias = {
        "low-cpu": "low-end pc",
        "cpu": "mid specs",
        "gpu": "high end pc",
        "low-end": "low-end pc",
        "mid": "mid specs",
        "high": "high end pc",
    }
    return alias.get(p, p or "low-end pc")


def pc_profile_model_candidates(profile: str) -> List[str]:
    p = _normalize_profile(profile)
    # For now, only one model is actively used
    return ["llama3:8b"]


def choose_model_for_profile(profile: str, installed: list[str]) -> str:
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
