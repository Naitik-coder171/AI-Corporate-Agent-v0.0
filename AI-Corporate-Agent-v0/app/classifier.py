from __future__ import annotations
import re
from pathlib import Path
from typing import Tuple


PATTERNS = [
    (re.compile(r"articles? of association|\bAOA\b", re.I), "Articles of Association"),
    (re.compile(r"memorandum of association|\bMOA\b|\bMOU\b", re.I), "Memorandum of Association"),
    (re.compile(r"board resolution", re.I), "Board Resolution"),
    (re.compile(r"shareholder resolution|shareholders' resolution", re.I), "Shareholder Resolution"),
    (re.compile(r"register of members|register of directors", re.I), "Register of Members and Directors"),
    (re.compile(r"incorporation application|application form", re.I), "Incorporation Application Form"),
    (re.compile(r"beneficial owner|UBO", re.I), "UBO Declaration"),
    (re.compile(r"change of registered address", re.I), "Change of Registered Address Notice"),
]


def classify(path: str, text: str) -> Tuple[str, float]:
    name = Path(path).name
    haystack = f"{name}\n{text[:4000]}"
    for pattern, label in PATTERNS:
        if pattern.search(haystack):
            return label, 0.9
    return "Unknown", 0.2 