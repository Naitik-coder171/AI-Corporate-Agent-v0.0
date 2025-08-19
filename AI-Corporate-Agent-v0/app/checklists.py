from __future__ import annotations
from typing import List, Dict

REQUIRED_DOCS_BY_PROCESS: Dict[str, List[str]] = {
    "Company Incorporation": [
        "Articles of Association",
        "Memorandum of Association",
        "Board Resolution",
        "Shareholder Resolution",
        "Incorporation Application Form",
        "UBO Declaration",
        "Register of Members and Directors",
        "Change of Registered Address Notice",
    ],
}


def detect_process_from_docs(detected_types: List[str]) -> str:
    # Simple heuristic: if any formation doc present, assume incorporation
    formation_markers = {
        "Articles of Association",
        "Memorandum of Association",
        "Board Resolution",
        "Shareholder Resolution",
        "Register of Members and Directors",
    }
    if any(dt in formation_markers for dt in detected_types):
        return "Company Incorporation"
    return "Unknown" 