import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class GroqClient:
    """Thin wrapper around the Groq SDK — used only for high-level reasoning."""

    def __init__(self) -> None:
        try:
            from groq import Groq
            self._client = Groq(api_key=settings.groq_api_key)
            logger.info("Groq client initialised (model: llama-3.1-8b-instant)")
        except Exception as exc:
            logger.warning("Failed to initialise Groq client: %s", exc)
            self._client = None

    def complete(self, prompt: str, max_tokens: int = 2048) -> str | None:
        """Send a prompt to Groq and return the text response, or None on failure."""
        if not self._client:
            logger.warning("Groq client unavailable — skipping completion")
            return None
        try:
            chat = self._client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                max_tokens=max_tokens,
            )
            return chat.choices[0].message.content.strip()
        except Exception as exc:
            logger.warning("Groq API call failed: %s", exc)
            return None
