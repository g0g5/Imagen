"""FastMCP server entrypoint for Imagen."""

from __future__ import annotations

from dataclasses import dataclass

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from imagen.constants import DEFAULT_MODEL
from imagen.errors import ImagenError
from imagen.services.generation import generate_and_save_images
from imagen.utils.output import format_saved_image_paths


@dataclass(frozen=True)
class GenerateImageResult:
    count: int
    saved_paths: list[str]
    message: str


mcp = FastMCP(
    "Imagen",
    mask_error_details=True,
    on_duplicate="error",
)


@mcp.tool(
    name="generate_image",
    description="Generate images with OpenRouter using the same options as the imagen CLI.",
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
    timeout=180.0,
)
def generate_image(
    prompt: str | None = None,
    prompt_file: str | None = None,
    image: list[str] | None = None,
    model: str = DEFAULT_MODEL,
    ratio: str | None = None,
    resolution: str | None = None,
    output_dir: str = "./outputs",
) -> GenerateImageResult:
    """Generate image files and return the saved paths."""
    try:
        saved_paths = generate_and_save_images(
            prompt=prompt,
            prompt_file=prompt_file,
            image_paths=image,
            model=model,
            ratio=ratio,
            resolution=resolution,
            output_dir=output_dir,
        )
    except ImagenError as exc:
        raise ToolError(str(exc)) from exc

    message = format_saved_image_paths(saved_paths)
    return GenerateImageResult(
        count=len(saved_paths),
        saved_paths=[str(path) for path in saved_paths],
        message=message,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
