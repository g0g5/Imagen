"""Shared image generation workflow."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from imagencli.config import load_config
from imagencli.providers.openrouter import OpenRouterProvider
from imagencli.services.image_saver import save_generated_images
from imagencli.validation import build_generate_request


def generate_and_save_images(
    *,
    prompt: str,
    image_paths: Sequence[str] | None,
    model: str,
    ratio: str | None,
    resolution: str | None,
    output_dir: str,
) -> list[Path]:
    config = load_config()
    request = build_generate_request(
        prompt=prompt,
        image_paths=image_paths,
        model=model,
        ratio=ratio,
        resolution=resolution,
        output_dir=output_dir,
    )
    provider = OpenRouterProvider(api_key=config.openrouter_api_key)
    response = provider.generate(request)
    return save_generated_images(response.images, request.output_dir)
