"""CLI output formatting helpers."""

from __future__ import annotations

from pathlib import Path


def format_saved_image_paths(paths: list[Path]) -> str:
    if not paths:
        return "No images were saved."

    lines = [f"Saved {len(paths)} image(s):"]
    lines.extend(f"- {path}" for path in paths)
    return "\n".join(lines)
