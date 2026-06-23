"""Runtime configuration. Values come from the environment (optionally via a .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass

try:  # load .env if python-dotenv is installed; harmless if absent
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover
    pass

# Default to the most capable Claude model. Override with DEAL_AGENT_MODEL.
DEFAULT_MODEL = "claude-opus-4-8"


@dataclass(frozen=True)
class Settings:
    model: str = os.getenv("DEAL_AGENT_MODEL", DEFAULT_MODEL)
    # Effort controls thinking depth + token spend: low | medium | high | xhigh | max
    effort: str = os.getenv("DEAL_AGENT_EFFORT", "high")
    max_tokens: int = int(os.getenv("DEAL_AGENT_MAX_TOKENS", "16000"))
    # Cheaper model for the vision sub-call inside the map tool
    vision_model: str = os.getenv("DEAL_AGENT_VISION_MODEL", DEFAULT_MODEL)


settings = Settings()
