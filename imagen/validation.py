"""Input validation and request construction helpers."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from imagen.errors import ValidationError
from imagen.models.capabilities import get_model_capabilities
from imagen.models.request import GenerateRequest
from imagen.utils.mime import detect_mime_type, is_supported_image_mime_type
from imagen.utils.paths import normalize_path

_SUPPORTED_PROMPT_FILE_EXTENSIONS = {".json", ".txt"}


def validate_prompt(prompt: str | None) -> str:
    normalized = (prompt or "").strip()
    if not normalized:
        raise ValidationError("Prompt must be non-empty.")
    return normalized


def read_prompt_file(prompt_file: str) -> str:
    path = normalize_path(prompt_file)
    if path.suffix.lower() not in _SUPPORTED_PROMPT_FILE_EXTENSIONS:
        allowed = ", ".join(sorted(_SUPPORTED_PROMPT_FILE_EXTENSIONS))
        raise ValidationError(
            f"Unsupported prompt file type for '{prompt_file}'. "
            f"Supported extensions: {allowed}."
        )
    if not path.exists():
        raise ValidationError(f"Prompt file does not exist: {prompt_file}")
    if not path.is_file():
        raise ValidationError(f"Prompt file path is not a file: {prompt_file}")
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValidationError(f"Could not read prompt file '{prompt_file}': {exc}") from exc
    if not content.strip():
        raise ValidationError("Prompt file must be non-empty.")
    return content


def resolve_prompt(prompt: str | None, prompt_file: str | None) -> str:
    if prompt_file is not None:
        return read_prompt_file(prompt_file)
    return validate_prompt(prompt)


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
    prompt: str | None,
    image_paths: Sequence[str] | None,
    model: str,
    ratio: str | None,
    resolution: str | None,
    output_dir: str,
    prompt_file: str | None = None,
) -> GenerateRequest:
    return GenerateRequest(
        prompt=resolve_prompt(prompt, prompt_file),
        image_paths=validate_image_paths(image_paths),
        model=model,
        ratio=validate_ratio(model, ratio),
        resolution=validate_resolution(model, resolution),
        output_dir=normalize_path(output_dir),
    )
