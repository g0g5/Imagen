from __future__ import annotations

import pytest

from imagen.cli import parse_args
from imagen.constants import DEFAULT_MODEL


def test_parse_args_defaults_without_subcommand() -> None:
    args = parse_args(["--prompt", "A cinematic sunset over mountains"])

    assert args.command == "generate"
    assert args.prompt == "A cinematic sunset over mountains"
    assert args.image == []
    assert args.model == DEFAULT_MODEL
    assert args.ratio is None
    assert args.resolution is None
    assert args.output_dir == "./outputs"


def test_parse_args_accepts_multi_image_values() -> None:
    args = parse_args(
        [
            "--prompt",
            "Blend these references",
            "--image",
            "./a.png",
            "./b.jpg",
            "--ratio",
            "16:9",
            "--resolution",
            "2K",
            "--output_dir",
            "./custom-out",
        ]
    )

    assert args.command == "generate"
    assert args.image == ["./a.png", "./b.jpg"]
    assert args.ratio == "16:9"
    assert args.resolution == "2K"
    assert args.output_dir == "./custom-out"


def test_parse_args_auth_subcommand() -> None:
    args = parse_args(["auth"])

    assert args.command == "auth"


def test_parse_args_install_subcommand() -> None:
    args = parse_args(["install", "--skills"])

    assert args.command == "install"
    assert args.skills is True


def test_parse_args_install_requires_skills_flag() -> None:
    with pytest.raises(SystemExit):
        parse_args(["install"])


def test_parse_args_rejects_missing_prompt() -> None:
    with pytest.raises(SystemExit):
        parse_args([])
