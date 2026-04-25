from __future__ import annotations

from pathlib import Path

import pytest

from imagen.cli import main
from imagen.commands.auth import run_auth
from imagen.commands import generate as generate_command
from imagen.config import load_config
from imagen.constants import DEFAULT_MODEL
from imagen.errors import ConfigError, ValidationError
from imagen.validation import build_generate_request
from imagen.validation import validate_ratio, validate_resolution


def test_load_config_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(ConfigError, match="OPENROUTER_API_KEY is required"):
        load_config()


def test_main_returns_error_for_missing_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    exit_code = main(["--prompt", "a cat"])

    assert exit_code == 1


def test_main_generate_prints_saved_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    saved_path = tmp_path / "imagen-test.png"

    def fake_generate_and_save_images(**kwargs: object) -> list[Path]:
        return [saved_path]

    monkeypatch.setattr(
        generate_command, "generate_and_save_images", fake_generate_and_save_images
    )

    exit_code = main(["--prompt", "a cat"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert f"- {saved_path}" in captured.out


def test_build_generate_request_rejects_missing_image_path(tmp_path: Path) -> None:
    missing_path = tmp_path / "does-not-exist.png"
    with pytest.raises(ValidationError, match="Image file does not exist"):
        build_generate_request(
            prompt="a cat",
            image_paths=[str(missing_path)],
            model=DEFAULT_MODEL,
            ratio=None,
            resolution=None,
            output_dir="./outputs",
        )


def test_validate_ratio_rejects_unsupported_value() -> None:
    with pytest.raises(ValidationError, match="Unsupported aspect ratio"):
        validate_ratio(DEFAULT_MODEL, "7:5")


def test_validate_resolution_rejects_extended_value_for_other_models() -> None:
    with pytest.raises(ValidationError, match="Unsupported resolution"):
        validate_resolution("openai/unknown-model", "0.5K")


def test_run_auth_prints_stub_message(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run_auth()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "not implemented yet" in captured.out
    assert "OPENROUTER_API_KEY" in captured.out
