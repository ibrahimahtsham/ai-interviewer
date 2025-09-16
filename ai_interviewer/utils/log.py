from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Any

# Log levels and mapping to numeric values
_LOG_LEVELS = {"DEBUG": 10, "INFO": 20, "SUCCESS": 25, "WARN": 30, "WARNING": 30, "ERROR": 40}
_MIN_LEVEL = _LOG_LEVELS.get(os.getenv("LOG_LEVEL", "INFO").upper(), 20)

# ANSI colors
_RESET = "\x1b[0m"
_COLORS = {
    "DEBUG": "\x1b[90m",    # bright black (gray)
    "INFO": "\x1b[36m",     # cyan
    "SUCCESS": "\x1b[32m",  # green
    "WARN": "\x1b[33m",     # yellow
    "ERROR": "\x1b[31m",    # red
}


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _use_color(stream) -> bool:
    if os.getenv("NO_COLOR"):
        return False
    if os.getenv("FORCE_COLOR"):
        return True
    try:
        return stream.isatty()
    except Exception:
        return False


def set_level(level: str) -> None:
    global _MIN_LEVEL
    _MIN_LEVEL = _LOG_LEVELS.get((level or "").upper(), _MIN_LEVEL)


def log(message: Any, level: str = "INFO") -> None:
    lvl = (level or "INFO").upper()
    value = _LOG_LEVELS.get(lvl, 20)
    if value < _MIN_LEVEL:
        return

    text = "" if message is None else str(message)
    lines = text.splitlines() or [""]

    stream = sys.stderr if lvl in ("WARN", "WARNING", "ERROR") else sys.stdout
    color_on = _use_color(stream)
    color = _COLORS.get(lvl, "")
    prefix = f"[{_now()}] [{lvl}] "

    for line in lines:
        out = prefix + line
        if color_on and color:
            out = f"{color}{out}{_RESET}"
        print(out, file=stream, flush=True)


def debug(msg: Any) -> None:
    log(msg, "DEBUG")


def info(msg: Any) -> None:
    log(msg, "INFO")


def success(msg: Any) -> None:
    log(msg, "SUCCESS")


def warn(msg: Any) -> None:
    log(msg, "WARN")


def error(msg: Any) -> None:
    log(msg, "ERROR")
