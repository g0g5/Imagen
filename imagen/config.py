"""Configuration loading helpers."""

from __future__ import annotations

from dataclasses import dataclass
from os import getenv

from imagen.auth_store import OPENROUTER_PROVIDER, load_api_key
from imagen.errors import ConfigError


@dataclass(frozen=True)
class RuntimeConfig:
    openrouter_api_key: str


def load_config() -> RuntimeConfig:
    api_key = load_api_key(OPENROUTER_PROVIDER)
    if api_key:
        return RuntimeConfig(openrouter_api_key=api_key)

    api_key = (getenv("OPENROUTER_API_KEY") or "").strip()
    if not api_key:
        raise ConfigError(
            "OpenRouter API key is required. Run `imagen auth` or set "
            "OPENROUTER_API_KEY and try again."
        )
    return RuntimeConfig(openrouter_api_key=api_key)
