"""Image output persistence utilities."""

from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path

from imagen.errors import ResponseFormatError
from imagen.models.response import GeneratedImage

_MIME_EXTENSION_MAP = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def save_generated_images(images: list[GeneratedImage], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    saved_paths: list[Path] = []

    for index, image in enumerate(images, start=1):
        extension, payload = _decode_image_data_url(image.data_url)
        filename = f"imagen-{timestamp}-{index:02d}{extension}"
        path = output_dir / filename
        path.write_bytes(payload)
        saved_paths.append(path)

    return saved_paths


def _decode_image_data_url(data_url: str) -> tuple[str, bytes]:
    if not data_url.startswith("data:"):
        raise ResponseFormatError("Generated image URL is not a data URL.")

    try:
        header, encoded_payload = data_url.split(",", 1)
    except ValueError as exc:
        raise ResponseFormatError("Generated image data URL is malformed.") from exc

    if ";base64" not in header:
        raise ResponseFormatError("Generated image data URL must be base64 encoded.")

    mime_type = header[5:].split(";", 1)[0]
    extension = _MIME_EXTENSION_MAP.get(mime_type)
    if extension is None:
        raise ResponseFormatError(
            f"Generated image MIME type is unsupported: {mime_type}"
        )

    try:
        payload = base64.b64decode(encoded_payload, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ResponseFormatError(
            "Generated image payload is not valid base64."
        ) from exc

    if not payload:
        raise ResponseFormatError("Generated image payload was empty.")
    return extension, payload
