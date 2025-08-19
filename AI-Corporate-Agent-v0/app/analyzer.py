from __future__ import annotations
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path

from app.classifier import classify
from app.checklists import REQUIRED_DOCS_BY_PROCESS, detect_process_from_docs
from app.retrieval import retrieve_context, build_rag_prompt
from app.llm import LLMClient
from app.official_check import is_official_adgm_format


def detect_basic_red_flags(text: str) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    # Jurisdiction mentions not ADGM
    if re.search(r"Dubai Courts|UAE Federal Courts|onshore UAE", text, re.I):
        issues.append({
            "issue": "Document references non-ADGM jurisdiction",
            "section_hint": "Jurisdiction/Dispute Resolution",
            "severity": "High",
            "suggestion": "Specify ADGM Courts or ADGM Arbitration as applicable.",
        })
    # Ambiguous language
    if re.search(r"may\s+at its discretion|best efforts|endeavour to", text, re.I):
        issues.append({
            "issue": "Ambiguous or non-binding language detected",
            "section_hint": "Obligations/Definitions",
            "severity": "Medium",
            "suggestion": "Replace with clear, binding obligations (e.g., 'shall').",
        })
    # Missing signatures
    if not re.search(r"Signed by|Signature|Authorised Signatory|Director", text, re.I):
        issues.append({
            "issue": "No signatory/signature section detected",
            "section_hint": "Execution/Signatures",
            "severity": "High",
            "suggestion": "Add execution blocks for authorised signatories.",
        })
    return issues


def analyze_documents(docs: List[Tuple[str, str]]) -> Dict[str, Any]:
    # docs: list of (path, text)
    detected_types: List[str] = []
    per_doc_results: List[Dict[str, Any]] = []

    for path, text in docs:
        doc_type, confidence = classify(path, text)

        # Official ADGM format check
        is_official, reason = is_official_adgm_format(text)
        format_issue: List[Dict[str, Any]] = []
        if not is_official:
            format_issue.append({
                "issue": "Document does not appear to be in official ADGM format",
                "section_hint": "Formatting/Template",
                "severity": "High",
                "suggestion": (
                    "Please use the official ADGM template as per ADGM rules and regulations. "
                    "Download the correct form from the official ADGM website."
                ),
                "citation": "ADGM official forms/templates (see ADGM Registration Authority).",
            })

        base_issues = detect_basic_red_flags(text)
        rag_contexts = retrieve_context(
            f"Identify ADGM compliance red flags for a {doc_type} and cite rules.")
        prompt = build_rag_prompt(
            user_task=(
                f"Document type: {doc_type}. Provide a short list of issues with citations and suggestions.\n"
                f"Use JSON with fields: section_hint, issue, severity (High/Medium/Low), suggestion, citation."
            ),
            contexts=rag_contexts,
        )
        ai_issues: List[Dict[str, Any]] = []
        try:
            llm = LLMClient()
            llm_output = llm.generate([
                {"role": "system", "content": "Return only valid JSON array."},
                {"role": "user", "content": prompt},
            ], temperature=0.1, max_tokens=700)
            import json
            parsed = json.loads(llm_output)
            if isinstance(parsed, list):
                for item in parsed:
                    ai_issues.append({
                        "section_hint": item.get("section_hint") or "",
                        "issue": item.get("issue") or "",
                        "severity": item.get("severity") or "Medium",
                        "suggestion": item.get("suggestion") or "",
                        "citation": item.get("citation") or "",
                    })
        except Exception:
            ai_issues = []

        issues = format_issue + base_issues + ai_issues
        per_doc_results.append({
            "file": Path(path).name,
            "type": doc_type,
            "confidence": confidence,
            "issues": issues,
        })
        detected_types.append(doc_type)

    process = detect_process_from_docs(detected_types)
    required = REQUIRED_DOCS_BY_PROCESS.get(process, [])
    present_set = set(dt for dt in detected_types if dt != "Unknown")
    missing = [d for d in required if d not in present_set]

    report: Dict[str, Any] = {
        "process": process,
        "documents_uploaded": len(docs),
        "required_documents": len(required),
        "missing_documents": missing,
        "files": per_doc_results,
    }
    return report 