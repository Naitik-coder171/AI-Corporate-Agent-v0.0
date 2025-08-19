from __future__ import annotations
import re
from typing import Tuple

ADGM_MARKERS = [
    r"\bAbu Dhabi Global Market\b",
    r"\bADGM\b",
    r"\bRegistration Authority\b",
    r"\bCompanies Regulations\b",
]

ADGM_URL_MARKERS = [
    r"adgm\.com",
    r"registrationauthority@adgm\.com",
]


def is_official_adgm_format(text: str) -> Tuple[bool, str]:
    sample = text[:8000]
    hits = 0
    for pat in ADGM_MARKERS:
        if re.search(pat, sample, re.I):
            hits += 1
    url_hits = 0
    for pat in ADGM_URL_MARKERS:
        if re.search(pat, sample, re.I):
            url_hits += 1
    # Heuristic: require at least two core markers OR one core + one url/contact marker
    if hits >= 2 or (hits >= 1 and url_hits >= 1):
        return True, "Detected ADGM header markers"
    return False, "No clear ADGM official markers found"

