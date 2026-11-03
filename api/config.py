"""Runtime settings for document classification."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _first_env(*names: str, default: str) -> str:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return default


@dataclass(frozen=True)
class Settings:
    ollama_url: str
    model: str
    timeout_seconds: float = 120.0
    max_text_chars: int = 12_000
    max_upload_bytes: int = 15 * 1024 * 1024


def load_settings() -> Settings:
    """Read `.env` and process environment variables.

    Existing process variables win. `ollama_url` and `LLM_MODEL` match the
    project `.env`. `OLLAMA_URL` is accepted as well.
    """
    root = Path(__file__).resolve().parents[1]
    _load_dotenv(root / ".env")
    return Settings(
        ollama_url=_first_env("OLLAMA_URL", "ollama_url", default="http://localhost:11435").rstrip("/"),
        model=_first_env("LLM_MODEL", "llm_model", default="qwen:7b"),
    )
