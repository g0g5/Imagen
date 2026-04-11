"""Path normalization and filesystem helpers."""

from __future__ import annotations

from pathlib import Path


def normalize_path(path: str) -> Path:
    return Path(path).expanduser()
