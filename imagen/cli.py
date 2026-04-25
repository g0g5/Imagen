"""CLI parser and command dispatch for imagen."""

from __future__ import annotations

from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from sys import argv as sys_argv, stderr

from imagen.commands.auth import run_auth
from imagen.commands.generate import run_generate
from imagen.commands.install import run_install
from imagen.constants import DEFAULT_MODEL
from imagen.errors import ImagenError

_KNOWN_COMMANDS = {"generate", "auth", "install"}


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="imagen", description="Generate images with OpenRouter"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser(
        "generate", help="Generate images using OpenRouter"
    )
    generate_parser.add_argument("--prompt", required=True)
    generate_parser.add_argument("--image", nargs="+", default=[])
    generate_parser.add_argument("--model", default=DEFAULT_MODEL)
    generate_parser.add_argument("--ratio")
    generate_parser.add_argument("--resolution")
    generate_parser.add_argument("--output_dir", default="./outputs")

    subparsers.add_parser("auth", help="Manage provider authentication (stub)")

    install_parser = subparsers.add_parser(
        "install", help="Install local integrations such as Claude skills"
    )
    install_parser.add_argument(
        "--skills",
        action="store_true",
        required=True,
        help="Install the bundled imagen-cli Claude skill",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> Namespace:
    parser = build_parser()
    normalized_argv = list(sys_argv[1:] if argv is None else argv)
    if not normalized_argv or normalized_argv[0] not in _KNOWN_COMMANDS:
        normalized_argv = ["generate", *normalized_argv]
    return parser.parse_args(normalized_argv)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        if args.command == "auth":
            return run_auth()
        if args.command == "install":
            return run_install(args)
        return run_generate(args)
    except ImagenError as exc:
        print(f"Error: {exc}", file=stderr)
        return 1
    except SystemExit as exc:
        code = exc.code
        return code if isinstance(code, int) else 1
