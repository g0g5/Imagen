"""Image generation command."""

from __future__ import annotations

from argparse import Namespace

from imagencli.config import load_config
from imagencli.providers.openrouter import OpenRouterProvider
from imagencli.services.image_saver import save_generated_images
from imagencli.utils.output import format_saved_image_paths
from imagencli.validation import build_generate_request


def run_generate(args: Namespace) -> int:
    config = load_config()
    request = build_generate_request(
        prompt=args.prompt,
        image_paths=args.image,
        model=args.model,
        ratio=args.ratio,
        resolution=args.resolution,
        output_dir=args.output_dir,
    )
    provider = OpenRouterProvider(api_key=config.openrouter_api_key)
    response = provider.generate(request)
    saved_paths = save_generated_images(response.images, request.output_dir)
    print(format_saved_image_paths(saved_paths))
    return 0
