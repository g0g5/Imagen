from __future__ import annotations

from pathlib import Path

import pytest
from fastmcp.exceptions import ToolError

from imagencli import mcp_server
from imagencli.constants import DEFAULT_MODEL
from imagencli.errors import ValidationError


def test_generate_image_returns_structured_result(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured_kwargs: dict[str, object] = {}

    def fake_generate_and_save_images(**kwargs: object) -> list[Path]:
        captured_kwargs.update(kwargs)
        return [tmp_path / "first.png", tmp_path / "second.webp"]

    monkeypatch.setattr(
        mcp_server, "generate_and_save_images", fake_generate_and_save_images
    )

    result = mcp_server.generate_image(
        prompt="Blend these references",
        image=["./a.png", "./b.jpg"],
        model="sourceful/riverflow-v2-pro",
        ratio="16:9",
        resolution="2K",
        output_dir="./custom-out",
    )

    assert captured_kwargs == {
        "prompt": "Blend these references",
        "image_paths": ["./a.png", "./b.jpg"],
        "model": "sourceful/riverflow-v2-pro",
        "ratio": "16:9",
        "resolution": "2K",
        "output_dir": "./custom-out",
    }
    assert result.count == 2
    assert result.saved_paths == [
        str(tmp_path / "first.png"),
        str(tmp_path / "second.webp"),
    ]
    assert "Saved 2 image(s):" in result.message


def test_generate_image_uses_cli_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_kwargs: dict[str, object] = {}

    def fake_generate_and_save_images(**kwargs: object) -> list[Path]:
        captured_kwargs.update(kwargs)
        return []

    monkeypatch.setattr(
        mcp_server, "generate_and_save_images", fake_generate_and_save_images
    )

    result = mcp_server.generate_image(prompt="A cinematic sunset over mountains")

    assert captured_kwargs == {
        "prompt": "A cinematic sunset over mountains",
        "image_paths": None,
        "model": DEFAULT_MODEL,
        "ratio": None,
        "resolution": None,
        "output_dir": "./outputs",
    }
    assert result.count == 0
    assert result.saved_paths == []
    assert result.message == "No images were saved."


def test_generate_image_converts_imagen_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_generate_and_save_images(**kwargs: object) -> list[Path]:
        raise ValidationError("Prompt must be non-empty.")

    monkeypatch.setattr(
        mcp_server, "generate_and_save_images", fake_generate_and_save_images
    )

    with pytest.raises(ToolError, match="Prompt must be non-empty"):
        mcp_server.generate_image(prompt="")
