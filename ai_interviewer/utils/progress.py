from __future__ import annotations

import re


def parse_percent(line: str) -> int | None:
    m = re.search(r"(\d{1,3})\s*%", line or "")
    if not m:
        return None
    p = int(m.group(1))
    return max(0, min(100, p))
