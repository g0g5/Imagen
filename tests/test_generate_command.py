from __future__ import annotations

import stat
from pathlib import Path

import pytest

from imagen.auth_store import OPENROUTER_PROVIDER, save_api_key
from imagen.cli import main
from imagen.commands.auth import run_auth
from imagen.commands import generate as generate_command
from imagen.config import load_config
from imagen.constants import DEFAULT_MODEL
from imagen.errors import ConfigError, ValidationError
from imagen.validation import build_generate_request
from imagen.validation import validate_ratio, validate_resolution


def test_load_config_requires_api_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(ConfigError, match="OpenRouter API key is required"):
        load_config()


def test_load_config_uses_environment_when_no_saved_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("OPENROUTER_API_KEY", "env-secret")

    config = load_config()

    assert config.openrouter_api_key == "env-secret"


def test_load_config_prefers_saved_key_over_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("OPENROUTER_API_KEY", "env-secret")
    save_api_key(OPENROUTER_PROVIDER, "saved-secret")

    config = load_config()

    assert config.openrouter_api_key == "saved-secret"


def test_main_returns_error_for_missing_api_key(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
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


def test_main_generate_passes_prompt_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("a cat from a file", encoding="utf-8")
    captured_kwargs: dict[str, object] = {}

    def fake_generate_and_save_images(**kwargs: object) -> list[Path]:
        captured_kwargs.update(kwargs)
        return []

    monkeypatch.setattr(
        generate_command, "generate_and_save_images", fake_generate_and_save_images
    )

    exit_code = main(["--prompt-file", str(prompt_file)])

    assert exit_code == 0
    assert captured_kwargs["prompt"] is None
    assert captured_kwargs["prompt_file"] == str(prompt_file)


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


def test_build_generate_request_reads_prompt_file_and_ignores_prompt(
    tmp_path: Path,
) -> None:
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("file prompt\n", encoding="utf-8")

    request = build_generate_request(
        prompt="ignored prompt",
        prompt_file=str(prompt_file),
        image_paths=None,
        model=DEFAULT_MODEL,
        ratio=None,
        resolution=None,
        output_dir="./outputs",
    )

    assert request.prompt == "file prompt\n"


def test_build_generate_request_reads_json_prompt_file_as_text(tmp_path: Path) -> None:
    prompt_file = tmp_path / "prompt.json"
    prompt_file.write_text('{"prompt": "a cat"}', encoding="utf-8")

    request = build_generate_request(
        prompt=None,
        prompt_file=str(prompt_file),
        image_paths=None,
        model=DEFAULT_MODEL,
        ratio=None,
        resolution=None,
        output_dir="./outputs",
    )

    assert request.prompt == '{"prompt": "a cat"}'


def test_build_generate_request_rejects_empty_prompt_file(tmp_path: Path) -> None:
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("  \n", encoding="utf-8")

    with pytest.raises(ValidationError, match="Prompt file must be non-empty"):
        build_generate_request(
            prompt=None,
            prompt_file=str(prompt_file),
            image_paths=None,
            model=DEFAULT_MODEL,
            ratio=None,
            resolution=None,
            output_dir="./outputs",
        )


def test_build_generate_request_rejects_unsupported_prompt_file_type(
    tmp_path: Path,
) -> None:
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("a cat", encoding="utf-8")

    with pytest.raises(ValidationError, match="Unsupported prompt file type"):
        build_generate_request(
            prompt=None,
            prompt_file=str(prompt_file),
            image_paths=None,
            model=DEFAULT_MODEL,
            ratio=None,
            resolution=None,
            output_dir="./outputs",
        )


def test_build_generate_request_rejects_missing_prompt_file(tmp_path: Path) -> None:
    prompt_file = tmp_path / "missing.txt"

    with pytest.raises(ValidationError, match="Prompt file does not exist"):
        build_generate_request(
            prompt=None,
            prompt_file=str(prompt_file),
            image_paths=None,
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


def test_run_auth_saves_encrypted_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    inputs = iter(["1", "stored-secret"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(inputs))

    exit_code = run_auth()

    captured = capsys.readouterr()
    config_dir = tmp_path / ".config" / "imagen"
    keys_file = config_dir / "keys"
    encryption_key_file = config_dir / ".encryption_key"

    assert exit_code == 0
    assert "Saved OpenRouter.ai API key" in captured.out
    assert keys_file.exists()
    assert encryption_key_file.exists()
    assert b"stored-secret" not in keys_file.read_bytes()
    assert stat.S_IMODE(config_dir.stat().st_mode) == 0o700
    assert stat.S_IMODE(keys_file.stat().st_mode) == 0o600
    assert stat.S_IMODE(encryption_key_file.stat().st_mode) == 0o600
    assert load_config().openrouter_api_key == "stored-secret"
