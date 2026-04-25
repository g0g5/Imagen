from __future__ import annotations

import io
from pathlib import Path

import pytest

from imagen.cli import main
from imagen.commands.install import run_install


def test_run_install_copies_bundled_skill(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    source_dir = tmp_path / "bundled" / "imagen-cli"
    source_dir.mkdir(parents=True)
    (source_dir / "SKILL.md").write_text("name: imagen-cli\n", encoding="utf-8")

    target_root = tmp_path / "home" / ".claude" / "skills"

    monkeypatch.setattr(
        "imagen.commands.install.get_bundled_skill_dir", lambda: source_dir
    )
    monkeypatch.setattr(
        "imagen.commands.install.get_claude_skills_dir", lambda: target_root
    )

    exit_code = run_install(type("Args", (), {"skills": True})())

    captured = capsys.readouterr()
    installed_file = target_root / "imagen-cli" / "SKILL.md"
    assert exit_code == 0
    assert installed_file.exists()
    assert installed_file.read_text(encoding="utf-8") == "name: imagen-cli\n"
    assert str(target_root / "imagen-cli") in captured.out


def test_run_install_overwrites_existing_skill_contents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_dir = tmp_path / "bundled" / "imagen-cli"
    source_dir.mkdir(parents=True)
    (source_dir / "SKILL.md").write_text("new contents\n", encoding="utf-8")

    target_root = tmp_path / "home" / ".claude" / "skills"
    existing_dir = target_root / "imagen-cli"
    existing_dir.mkdir(parents=True)
    (existing_dir / "SKILL.md").write_text("old contents\n", encoding="utf-8")

    monkeypatch.setattr(
        "imagen.commands.install.get_bundled_skill_dir", lambda: source_dir
    )
    monkeypatch.setattr(
        "imagen.commands.install.get_claude_skills_dir", lambda: target_root
    )

    exit_code = run_install(type("Args", (), {"skills": True})())

    assert exit_code == 0
    assert (existing_dir / "SKILL.md").read_text(encoding="utf-8") == "new contents\n"


def test_main_install_succeeds_without_api_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    source_dir = tmp_path / "bundled" / "imagen-cli"
    source_dir.mkdir(parents=True)
    (source_dir / "SKILL.md").write_text("name: imagen-cli\n", encoding="utf-8")

    target_root = tmp_path / "home" / ".claude" / "skills"

    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(
        "imagen.commands.install.get_bundled_skill_dir", lambda: source_dir
    )
    monkeypatch.setattr(
        "imagen.commands.install.get_claude_skills_dir", lambda: target_root
    )

    exit_code = main(["install", "--skills"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Installed Claude skill to" in captured.out
    assert (target_root / "imagen-cli" / "SKILL.md").exists()


def test_main_install_returns_error_when_source_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stderr_buffer = io.StringIO()

    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(
        "imagen.commands.install.get_bundled_skill_dir",
        lambda: tmp_path / "missing" / "imagen-cli",
    )
    monkeypatch.setattr(
        "imagen.commands.install.get_claude_skills_dir",
        lambda: tmp_path / "home" / ".claude" / "skills",
    )
    monkeypatch.setattr("imagen.cli.stderr", stderr_buffer)

    exit_code = main(["install", "--skills"])

    assert exit_code == 1
    assert "Bundled skill directory was not found" in stderr_buffer.getvalue()
