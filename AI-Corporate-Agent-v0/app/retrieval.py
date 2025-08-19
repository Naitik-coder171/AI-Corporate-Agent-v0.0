from __future__ import annotations
from typing import List, Dict
from pathlib import Path

from app.ingest import ensure_index


def retrieve_context(question: str, k: int = 6) -> List[Dict]:
    vs = ensure_index()
    hits = vs.similarity_search(question, k=k)
    contexts: List[Dict] = []
    for h in hits:
        contexts.append({
            "source": h.get("source", "unknown"),
            "score": h["score"],
            "text": h.get("text", "")[:3000],
        })
    return contexts


def build_rag_prompt(user_task: str, contexts: List[Dict]) -> str:
    header = (
        "You are an expert ADGM corporate paralegal. Use only the provided context to assess compliance.\n"
        "Cite the exact regulation or the source document name where relevant.\n"
    )
    ctx_blocks = []
    for i, c in enumerate(contexts, 1):
        name = Path(str(c.get('source','context'))).name
        ctx_blocks.append(f"[Source {i}: {name}]\n{c['text']}")
    return header + "\n\n" + "\n\n".join(ctx_blocks) + "\n\nUser task:\n" + user_task 