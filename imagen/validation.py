"""Input validation and request construction helpers."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from imagen.errors import ValidationError
from imagen.models.capabilities import get_model_capabilities
from imagen.models.request import GenerateRequest
from imagen.utils.mime import detect_mime_type, is_supported_image_mime_type
from imagen.utils.paths import normalize_path


def validate_prompt(prompt: str) -> str:
    normalized = prompt.strip()
    if not normalized:
        raise ValidationError("Prompt must be non-empty.")
    return normalized


def validate_ratio(model: str, ratio: str | None) -> str | None:
    if ratio is None:
        return None
    normalized = ratio.strip()
    if not normalized:
        raise ValidationError("Aspect ratio cannot be empty.")
    supported = get_model_capabilities(model)["aspect_ratios"]
    if normalized not in supported:
        allowed = ", ".join(sorted(supported))
        raise ValidationError(
            f"Unsupported aspect ratio '{normalized}' for model '{model}'. "
            f"Supported values: {allowed}."
        )
    return normalized


def validate_resolution(model: str, resolution: str | None) -> str | None:
    if resolution is None:
        return None
    normalized = resolution.strip()
    if not normalized:
        raise ValidationError("Resolution cannot be empty.")
    supported = get_model_capabilities(model)["resolutions"]
    if normalized not in supported:
        allowed = ", ".join(sorted(supported))
        raise ValidationError(
            f"Unsupported resolution '{normalized}' for model '{model}'. "
            f"Supported values: {allowed}."
        )
    return normalized


def validate_image_paths(image_paths: Sequence[str] | None) -> list[Path]:
    if not image_paths:
        return []
    validated_paths: list[Path] = []
    for raw_path in image_paths:
        path = normalize_path(raw_path)
        if not path.exists():
            raise ValidationError(f"Image file does not exist: {raw_path}")
        if not path.is_file():
            raise ValidationError(f"Image path is not a file: {raw_path}")
        mime_type = detect_mime_type(path)
        if not is_supported_image_mime_type(mime_type):
            raise ValidationError(
                f"Unsupported image type for '{raw_path}': {mime_type or 'unknown'}"
            )
        validated_paths.append(path)
    return validated_paths


def build_generate_request(
    *,
    prompt: str,
    image_paths: Sequence[str] | None,
    model: str,
    ratio: str | None,
    resolution: str | None,
    output_dir: str,
) -> GenerateRequest:
    return GenerateRequest(
        prompt=validate_prompt(prompt),
        image_paths=validate_image_paths(image_paths),
        model=model,
        ratio=validate_ratio(model, ratio),
        resolution=validate_resolution(model, resolution),
        output_dir=normalize_path(output_dir),
    )
