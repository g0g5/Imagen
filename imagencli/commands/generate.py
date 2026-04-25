"""Image generation command."""

from __future__ import annotations

from argparse import Namespace

from imagencli.services.generation import generate_and_save_images
from imagencli.utils.output import format_saved_image_paths


def run_generate(args: Namespace) -> int:
    saved_paths = generate_and_save_images(
        prompt=args.prompt,
        image_paths=args.image,
        model=args.model,
        ratio=args.ratio,
        resolution=args.resolution,
        output_dir=args.output_dir,
    )
    print(format_saved_image_paths(saved_paths))
    return 0
