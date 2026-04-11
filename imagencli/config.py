"""Configuration loading helpers."""

from __future__ import annotations

from dataclasses import dataclass
from os import getenv

from imagencli.errors import ConfigError


@dataclass(frozen=True)
class RuntimeConfig:
    openrouter_api_key: str


def load_config() -> RuntimeConfig:
    api_key = (getenv("OPENROUTER_API_KEY") or "").strip()
    if not api_key:
        raise ConfigError(
            "OPENROUTER_API_KEY is required. Set it in your environment and try again."
        )
    return RuntimeConfig(openrouter_api_key=api_key)
