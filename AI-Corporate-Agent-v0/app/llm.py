from __future__ import annotations
import httpx
from typing import List, Dict, Any
from app.config import load_config

try:
    from openai import OpenAI  # type: ignore
    _has_openai = True
except Exception:
    _has_openai = False


class LLMClient:
    def __init__(self) -> None:
        self.cfg = load_config()
        self._client = None
        if self.cfg.openai_api_key and _has_openai:
            self._client = OpenAI(api_key=self.cfg.openai_api_key, base_url=self.cfg.openai_api_base)

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 800) -> str:
        if self._client:
            resp = self._client.chat.completions.create(
                model=self.cfg.openai_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content or ""
        # Fallback to Ollama
        payload: Dict[str, Any] = {
            "model": self.cfg.ollama_model,
            "messages": messages,
            "options": {"temperature": temperature},
        }
        with httpx.Client(timeout=120) as client:
            r = client.post(f"{self.cfg.ollama_base_url}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
            # Ollama may stream, but final content is often in 'message'
            if "message" in data and data["message"].get("content"):
                return data["message"]["content"]
            # If it's a chunked array, join contents
            if isinstance(data, list):
                return "".join(chunk.get("message", {}).get("content", "") for chunk in data)
            return "" 