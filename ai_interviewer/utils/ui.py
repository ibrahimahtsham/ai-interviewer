from __future__ import annotations
import re
import sys
import subprocess
import shutil
import platform
from pathlib import Path
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
    # Mirror to server stdout (useful when running in a terminal)
    try:
        print(line, file=sys.stdout, flush=True)
    except Exception:
        pass
    # Persist to log file for external console viewers
    try:
        log_path = session_state.get("console_log_path") or get_console_log_path(session_state)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line.rstrip() + "\n")
    except Exception:
        pass


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


def get_console_log_path(session_state=None) -> str:
    base = Path(".cache") / "logs"
    base.mkdir(parents=True, exist_ok=True)
    log_path = base / "ollama_console.log"
    if session_state is not None:
        session_state["console_log_path"] = str(log_path)
    return str(log_path)


def open_external_console(log_path: Optional[str] = None) -> tuple[bool, str]:
    """Open a native terminal window that tails the console log.

    Returns (ok, message).
    """
    p = log_path or get_console_log_path(None)
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).touch(exist_ok=True)

    system = platform.system().lower()
    tail_cmd = f"tail -n +1 -f '{p}'"
    try:
        if system == "windows":
            ps_cmd = f"Get-Content -Path '{p}' -Wait -Tail 20"
            cmd = f'start "" powershell -NoExit -Command "{ps_cmd}"'
            subprocess.Popen(cmd, shell=True)
            return True, "Opened external console (PowerShell)."
        elif system == "darwin":
            osa = f'tell application "Terminal" to do script "{tail_cmd}"'
            subprocess.Popen(["osascript", "-e", osa])
            return True, "Opened external console (Terminal.app)."
        else:
            candidates = [
                ("x-terminal-emulator", ["-e", "bash", "-lc", tail_cmd]),
                ("gnome-terminal", ["--", "bash", "-lc", tail_cmd]),
                ("konsole", ["-e", "bash", "-lc", tail_cmd]),
                ("xfce4-terminal", ["-e", "bash", "-lc", tail_cmd]),
                ("lxterminal", ["-e", "bash", "-lc", tail_cmd]),
                ("mate-terminal", ["-e", "bash", "-lc", tail_cmd]),
                ("alacritty", ["-e", "bash", "-lc", tail_cmd]),
                ("xterm", ["-e", "bash", "-lc", tail_cmd]),
            ]
            for exe, args in candidates:
                if shutil.which(exe):
                    subprocess.Popen([exe, *args])
                    return True, f"Opened external console ({exe})."
            return False, "No supported terminal emulator found (install xterm/gnome-terminal/etc.)."
    except Exception as e:
        return False, f"Failed to open external console: {e}"
