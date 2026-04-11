"""MIME-related helper functions."""

from __future__ import annotations

from mimetypes import guess_type
from pathlib import Path

from imagencli.constants import SUPPORTED_IMAGE_MIME_TYPES


def detect_mime_type(path: Path) -> str | None:
    mime_type, _ = guess_type(path.name)
    return mime_type


def is_supported_image_mime_type(mime_type: str | None) -> bool:
    return mime_type in SUPPORTED_IMAGE_MIME_TYPES
