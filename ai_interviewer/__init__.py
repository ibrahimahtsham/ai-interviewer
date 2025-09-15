"""AI Interviewer package (MVP).

Exposes simple stubbed backend helpers used by the Streamlit UI.
"""

from .backend import (
    make_transcript_stub,
    make_reply_stub,
    make_beep_wav_bytes,
    ping_test,
)

__all__ = [
    "make_transcript_stub",
    "make_reply_stub",
    "make_beep_wav_bytes",
    "ping_test",
]
