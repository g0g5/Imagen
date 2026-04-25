"""Response models produced by provider clients."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedImage:
    data_url: str


@dataclass(frozen=True)
class GenerateResponse:
    images: list[GeneratedImage]
