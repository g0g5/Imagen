"""MIME-related helper functions."""

from __future__ import annotations

from mimetypes import guess_type
from pathlib import Path

from imagen.constants import SUPPORTED_IMAGE_MIME_TYPES


_MIME_TYPE_ALIASES = {
    "application/jpg": "image/jpeg",
}


def detect_mime_type(path: Path) -> str | None:
    mime_type, _ = guess_type(path.name)
    if mime_type is None:
        return None
    return _MIME_TYPE_ALIASES.get(mime_type, mime_type)


def is_supported_image_mime_type(mime_type: str | None) -> bool:
    return mime_type in SUPPORTED_IMAGE_MIME_TYPES
