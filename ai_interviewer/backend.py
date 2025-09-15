from __future__ import annotations

import io
import math
import struct
import wave
import platform
import subprocess
import time
from typing import Dict, Optional


def make_transcript_stub() -> str:
    """Return a fixed sample transcript to simulate STT output.

    Keep this simple for MVP.
    """
    return (
        "Good morning, thanks for meeting with me today. "
        "I have five years of experience in backend development, "
        "mostly with Python and cloud-native services."
    )


def make_reply_stub(transcript: str) -> str:
    """Return a fixed interviewer-style reply based on the transcript.

    For MVP we don't parse deeply; just echo a friendly response.
    """
    return (
        "Thanks for sharing. Could you walk me through a project where you "
        "designed an API end-to-end and what trade-offs you made?"
    )


def make_beep_wav_bytes(duration_s: float = 0.35, freq_hz: float = 880.0) -> bytes:
    """Generate a simple sine-wave beep and return WAV bytes.

    Pure-Python WAV generation; no external dependencies.
    """
    sample_rate = 16000  # 16 kHz mono
    amplitude = 0.3  # relative (0.0 - 1.0)
    n_samples = int(duration_s * sample_rate)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sample_rate)

        for n in range(n_samples):
            t = n / sample_rate
            sample = amplitude * math.sin(2.0 * math.pi * freq_hz * t)
            # Convert to 16-bit signed integer
            val = int(max(-1.0, min(1.0, sample)) * 32767)
            wf.writeframes(struct.pack("<h", val))

    return buf.getvalue()


def ping_test(host: str = "8.8.8.8", count: int = 1, timeout_s: float = 5.0) -> Dict[str, Optional[str]]:
    """Run a simple system ping and return its outputs.

    This is intended as a safe, bounded demonstration of executing a system
    command and surfacing its output back to the UI. It uses a hard-coded
    command template and enforces a process timeout.

    Returns a dict with keys: ok, command, returncode, stdout, stderr, error, duration_s.
    """
    is_windows = platform.system().lower().startswith("win")
    if is_windows:
        cmd = ["ping", "-n", str(int(count)), host]
    else:
        cmd = ["ping", "-c", str(int(count)), host]

    started = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        duration = time.time() - started
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        # Trim extremely long outputs for safety
        max_len = 8000
        if len(stdout) > max_len:
            stdout = stdout[:max_len] + "\n... (truncated)"
        if len(stderr) > max_len:
            stderr = stderr[:max_len] + "\n... (truncated)"
        return {
            "ok": str(proc.returncode == 0),
            "command": " ".join(cmd),
            "returncode": str(proc.returncode),
            "stdout": stdout,
            "stderr": stderr,
            "error": None,
            "duration_s": f"{duration:.3f}",
        }
    except subprocess.TimeoutExpired as e:
        duration = time.time() - started
        return {
            "ok": "False",
            "command": " ".join(cmd),
            "returncode": None,
            "stdout": e.stdout if isinstance(e.stdout, str) else None,
            "stderr": e.stderr if isinstance(e.stderr, str) else None,
            "error": f"Timeout after {timeout_s}s",
            "duration_s": f"{duration:.3f}",
        }
    except FileNotFoundError:
        duration = time.time() - started
        return {
            "ok": "False",
            "command": " ".join(cmd),
            "returncode": None,
            "stdout": None,
            "stderr": None,
            "error": "'ping' command not found on this system.",
            "duration_s": f"{duration:.3f}",
        }
    except Exception as e:  # generic safety net
        duration = time.time() - started
        return {
            "ok": "False",
            "command": " ".join(cmd),
            "returncode": None,
            "stdout": None,
            "stderr": None,
            "error": f"Unexpected error: {e}",
            "duration_s": f"{duration:.3f}",
        }
