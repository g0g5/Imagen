"""Image encoding utilities."""

from __future__ import annotations

import base64
from pathlib import Path

from imagen.errors import ValidationError
from imagen.utils.mime import detect_mime_type


def encode_image_to_data_url(path: Path) -> str:
    mime_type = detect_mime_type(path)
    if mime_type is None:
        raise ValidationError(f"Could not determine MIME type for image: {path}")
    raw_bytes = path.read_bytes()
    encoded = base64.b64encode(raw_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def encode_images_to_data_urls(paths: list[Path]) -> list[str]:
    return [encode_image_to_data_url(path) for path in paths]
