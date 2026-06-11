"""
OllamaService — calls a local Ollama instance (llama3.1:8b) for lightweight
summarisation tasks. All methods return None gracefully if Ollama is offline
or the model is unavailable, allowing the pipeline to continue without summaries.
"""
import json
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_MODEL = "llama3.1:8b"
_TIMEOUT = 120.0  # seconds — local models can be slow on first token


class OllamaService:
    def __init__(self) -> None:
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._available: bool | None = None  # lazily checked

    # ── Public API ────────────────────────────────────────────────────────────

    def summarize_readme(self, readme_text: str) -> str | None:
        """
        Summarise a README in 3–4 sentences describing what the project does,
        its main purpose, and its primary audience.
        """
        if not readme_text or not readme_text.strip():
            return None
        truncated = readme_text[:6000]  # keep prompt manageable
        prompt = (
            "You are a technical writer. Read the following README and produce a "
            "concise 3–4 sentence summary describing: what the project does, its "
            "primary purpose, and who it is for. Base your answer ONLY on the text "
            "provided. Do not invent features.\n\n"
            f"README:\n{truncated}\n\nSummary:"
        )
        return self._generate(prompt, max_tokens=256)

    def summarize_module(self, module_name: str, file_names: list[str]) -> str | None:
        """
        Given a top-level module/directory and its contained file names,
        produce a one-sentence description of the module's likely responsibility.
        """
        if not file_names:
            return None
        files_str = ", ".join(file_names[:30])
        prompt = (
            f"You are a senior software engineer reviewing a codebase. "
            f"The directory '{module_name}' contains these files: {files_str}. "
            f"In one sentence, describe what this module is responsible for. "
            f"Answer with only the sentence, no preamble."
        )
        return self._generate(prompt, max_tokens=80)

    def summarize_chunk(self, code_chunk: str, context: str = "") -> str | None:
        """
        Summarise a small code snippet in one sentence.
        Used for components/controllers when full code analysis is needed.
        """
        if not code_chunk or not code_chunk.strip():
            return None
        ctx = f"Context: {context}\n\n" if context else ""
        prompt = (
            f"{ctx}Summarise what the following code does in one sentence.\n\n"
            f"```\n{code_chunk[:3000]}\n```\n\nSummary:"
        )
        return self._generate(prompt, max_tokens=80)

    def is_available(self) -> bool:
        """Check whether the Ollama server is reachable."""
        if self._available is not None:
            return self._available
        try:
            resp = httpx.get(f"{self._base_url}/api/tags", timeout=5.0)
            self._available = resp.status_code == 200
        except Exception:
            self._available = False
        if not self._available:
            logger.warning(
                "Ollama not reachable at %s — module/README summaries will be skipped",
                self._base_url,
            )
        return self._available

    # ── Internal ──────────────────────────────────────────────────────────────

    def _generate(self, prompt: str, max_tokens: int = 256) -> str | None:
        if not self.is_available():
            return None
        try:
            payload = {
                "model": _MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": max_tokens, "temperature": 0.2},
            }
            resp = httpx.post(
                f"{self._base_url}/api/generate",
                json=payload,
                timeout=_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data.get("response", "").strip()
            return text if text else None
        except httpx.TimeoutException:
            logger.warning("Ollama request timed out after %.0fs", _TIMEOUT)
            return None
        except Exception as exc:
            logger.warning("Ollama generate failed: %s", exc)
            return None
