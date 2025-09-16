from __future__ import annotations

import re


def extract_first_question(text: str) -> str:
    """Extract a single interview question from arbitrary model output.

    Rules:
    - trim code fences/quotes and common speaker labels
    - prefer a quoted question if present
    - otherwise return up to the first '?'
    - if no question mark, return the trimmed text
    """
    t = (text or "").strip().strip("`")
    # Remove common speaker/label/filler prefixes
    t = re.sub(
        r"^[>*\s]*?(Interviewer|Assistant|AI|System|Question|Output|Prompt|Role|Task)\s*:\s*",
        "",
        t,
        flags=re.I,
    )
    t = re.sub(
        r"^(Sure|Okay|Certainly|Absolutely|Great|Here(?: is|'s)|Let's|Of course)[!,:-]*\s+",
        "",
        t,
        flags=re.I,
    )
    # Prefer quoted question if present
    m = re.search(r'"([^"\n\r]+\?)"', t)
    if m:
        return m.group(1).strip().strip('\"“”')
    m = re.search(r"“([^”\n\r]+\?)”", t)
    if m:
        return m.group(1).strip()
    # Fallback: up to first question mark
    qpos = t.find("?")
    if qpos != -1:
        return t[: qpos + 1].strip().strip('"“”')
    return t
