from __future__ import annotations

from enum import Enum
from typing import Any, List


class PCProfile(Enum):
    LOW = "Low-end PC"
    HIGH = "High-end PC"


# Ordered labels for UI widgets
PROFILE_LABELS: List[str] = [p.value for p in PCProfile]


def normalize_profile(value: Any) -> PCProfile:
    """Normalize to one of the two supported profiles without aliases.

    Accepts:
      - PCProfile enum values
      - Enum names: "LOW", "HIGH" (case-insensitive)
      - Labels: "Low-end PC", "High-end PC" (case-insensitive)

    Falls back to PCProfile.LOW if not recognized.
    """
    if isinstance(value, PCProfile):
        return value

    s = (str(value) if value is not None else "").strip()
    if not s:
        return PCProfile.LOW

    s_lower = s.lower()
    # Match by enum name (LOW/HIGH)
    for p in PCProfile:
        if s_lower == p.name.lower():
            return p
    # Match by label value (Low-end PC / High-end PC)
    for p in PCProfile:
        if s_lower == p.value.lower():
            return p

    return PCProfile.LOW


def to_label(profile: PCProfile | str) -> str:
    """Return the user-facing label for a profile (enum or string)."""
    return normalize_profile(profile).value
