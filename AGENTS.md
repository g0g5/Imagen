## Project Overview
Imagen is a Python 3.12 CLI and FastMCP server for validating image-generation inputs, calling OpenRouter image models with `requests`, and saving generated images locally.

## Structure Map
imagen/
|- imagen/                    # Core Python package for CLI, MCP, validation, providers, and shared services
|  |- __main__.py             # `python -m imagen` entrypoint
|  |- cli.py                  # Argparse setup, default command normalization, and command dispatch
|  |- mcp_server.py           # `imagen-mcp` FastMCP stdio server exposing image generation
|  |- config.py               # Environment-based runtime configuration loading
|  |- constants.py            # Defaults, OpenRouter URL, supported options, MIME types, and model capabilities
|  |- errors.py               # Shared user-safe application exceptions
|  |- validation.py           # Prompt/image/option validation and request assembly
|  |- commands/               # CLI subcommands
|  |  |- generate.py          # Generate command using the shared generation workflow
|  |  |- auth.py              # Auth stub that directs users to `OPENROUTER_API_KEY`
|  |  \- install.py           # Installs bundled Claude skill assets
|  |- models/                 # Dataclass contracts shared across validation, services, providers, CLI, and MCP
|  |- providers/              # Provider interface and OpenRouter integration boundary
|  |- services/               # Shared generation orchestration, payload building, image encoding, and image saving
|  |  \- generation.py        # Central workflow reused by CLI and MCP
|  \- utils/                  # Shared MIME, path, and output formatting helpers
|- skills/                    # Bundled local integration assets
|  \- imagen-cli/             # Claude skill installed by `imagen install --skills`
|- tests/                     # Pytest suite for CLI, MCP, provider, command, and service behavior
|- README.md                  # User-facing setup, usage, MCP, and development guide
|- pyproject.toml             # Package metadata, Hatchling build config, dependencies, and console scripts
\- uv.lock                    # Locked dependency graph for uv workflows

## Development Guide
- Build package: `uv build`
- Sync dev environment: `uv sync --dev`
- Run tests: `uv run pytest`
- Run typecheck-level sanity check: `uv run python -m compileall imagen tests`
- Verify changes quickly: `uv run pytest && uv run python -m imagen --help`
