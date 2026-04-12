"""Install subcommand for local integrations."""

from __future__ import annotations

import shutil
from argparse import Namespace
from pathlib import Path

from imagencli.errors import InstallError
from imagencli.utils.paths import normalize_path


def get_bundled_skill_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "skills" / "imagen-cli"


def get_claude_skills_dir() -> Path:
    return normalize_path("~/.claude/skills")


def run_install(args: Namespace) -> int:
    if not args.skills:
        raise InstallError("`imagen install` currently requires `--skills`.")

    source_dir = get_bundled_skill_dir()
    if not source_dir.is_dir():
        raise InstallError(f"Bundled skill directory was not found: {source_dir}")

    target_root = get_claude_skills_dir()
    target_root.mkdir(parents=True, exist_ok=True)
    target_dir = target_root / source_dir.name

    try:
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
    except OSError as exc:
        raise InstallError(f"Failed to install Claude skill: {exc}") from exc

    print(f"Installed Claude skill to {target_dir}")
    return 0
