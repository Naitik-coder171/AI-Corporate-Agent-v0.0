from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any, Tuple
import uuid
import os
import json
import numpy as np
import httpx
from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore

from app.config import load_config
from app.text_extractor import extract_text_with_metadata
from app.llm import LLMClient


class VectorStore:
    def __init__(self, persist_prefix: str) -> None:
        self.persist_prefix = persist_prefix
        self.emb_path = Path(f"{persist_prefix}.embeddings.npy")
        self.meta_path = Path(f"{persist_prefix}.metadatas.jsonl")
        self.text_path = Path(f"{persist_prefix}.texts.jsonl")
        self.embeddings: np.ndarray | None = None
        self.metadatas: List[Dict[str, Any]] = []
        self.texts: List[str] = []
        self._loaded = False

    def _load(self) -> None:
        if self.emb_path.exists():
            self.embeddings = np.load(self.emb_path)
        if self.meta_path.exists():
            self.metadatas = [json.loads(l) for l in self.meta_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        if self.text_path.exists():
            self.texts = [l for l in self.text_path.read_text(encoding="utf-8").splitlines()]
        self._loaded = True

    def _save(self) -> None:
        if self.embeddings is not None:
            np.save(self.emb_path, self.embeddings)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            for m in self.metadatas:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")
        with open(self.text_path, "w", encoding="utf-8") as f:
            for t in self.texts:
                f.write(t + "\n")

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._load()

    def _embed_with_openai(self, texts: List[str], api_key: str, base_url: str | None, model: str) -> np.ndarray:
        from openai import OpenAI  # type: ignore
        oc = OpenAI(api_key=api_key, base_url=base_url)
        vecs: List[List[float]] = []
        batch_size = 64
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            resp = oc.embeddings.create(model=model, input=batch)
            vecs.extend([d.embedding for d in resp.data])
        arr = np.asarray(vecs, dtype=np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
        return arr / norms

    def _embed_with_ollama(self, texts: List[str], base_url: str, model: str) -> np.ndarray:
        # Ollama embeddings endpoint typically expects single prompt per call
        vecs: List[List[float]] = []
        with httpx.Client(timeout=120) as client:
            for t in texts:
                payload = {"model": model, "prompt": t}
                r = client.post(f"{base_url.rstrip('/')}/api/embeddings", json=payload)
                r.raise_for_status()
                data = r.json()
                emb = data.get("embedding") or data.get("data", [{}])[0].get("embedding")
                if not emb:
                    raise RuntimeError("Ollama embedding response missing 'embedding'")
                vecs.append(emb)
        arr = np.asarray(vecs, dtype=np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
        return arr / norms

    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        cfg = load_config()
        api_key = cfg.openai_api_key or os.getenv("OPENAI_API_KEY")
        base_url = cfg.openai_api_base or os.getenv("OPENAI_API_BASE")
        ollama_base = os.getenv("OLLAMA_BASE_URL", cfg.ollama_base_url)
        emb_model = (cfg.embedding_model or "text-embedding-3-small").strip()

        try:
            if api_key:
                return self._embed_with_openai(texts, api_key, base_url, emb_model)
            # Use Ollama embeddings if available and requested
            if ollama_base and ("nomic" in emb_model or "embed" in emb_model or emb_model.startswith("ollama:")):
                model_name = emb_model.replace("ollama:", "")
                return self._embed_with_ollama(texts, ollama_base, model_name)
        except Exception:
            pass

        # Fallback: deterministic random vectors (demo only)
        rng = np.random.RandomState(42)
        return rng.rand(len(texts), 384).astype(np.float32)

    def build_from_directory(self, reference_dir: str, chunk_size: int = 1200, chunk_overlap: int = 150) -> None:
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        docs: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ref = Path(reference_dir)
        assert ref.exists(), f"Reference dir not found: {ref}"
        for file in sorted(ref.glob("**/*")):
            if not file.is_file():
                continue
            if file.suffix.lower() not in {".docx", ".pdf", ".md", ".txt"}:
                continue
            text, meta = extract_text_with_metadata(str(file))
            if not text.strip():
                continue
            chunks = splitter.split_text(text)
            for i, chunk in enumerate(chunks):
                docs.append(chunk)
                metadatas.append({**meta, "chunk_index": i})
        if not docs:
            return
        embs = self._embed_texts(docs)
        self.embeddings = embs
        self.metadatas = metadatas
        self.texts = docs
        self._save()

    def similarity_search(self, query: str, k: int = 6) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        if self.embeddings is None or not len(self.texts):
            return []
        q_emb = self._embed_texts([query])
        q = q_emb[0]
        sims = (self.embeddings @ q)
        topk_idx = np.argsort(-sims)[:k]
        results: List[Dict[str, Any]] = []
        for idx in topk_idx:
            meta = self.metadatas[idx]
            results.append({"score": float(sims[idx]), **meta, "text": self.texts[idx]})
        return results


essentially_no_op = None

def ensure_index() -> VectorStore:
    cfg = load_config()
    prefix = cfg.vector_db_path or "./data/vector"
    vs = VectorStore(prefix)
    vs._ensure_loaded()
    if vs.embeddings is None or len(vs.texts) == 0:
        vs.build_from_directory(cfg.reference_dir)
    return vs 