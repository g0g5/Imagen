"""Request models used by provider clients."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from imagencli.constants import DEFAULT_MODEL


@dataclass(frozen=True)
class GenerateRequest:
    prompt: str
    image_paths: list[Path]
    model: str = DEFAULT_MODEL
    ratio: str | None = None
    resolution: str | None = None
    output_dir: Path = Path("./outputs")
