## Project Overview
ImagenCLI is a Python 3.12 CLI package that validates image-generation inputs, calls OpenRouter image models via `requests`, and saves generated images locally.

## Structure Map
imagencli/
|- imagencli/                 # Core application package for CLI flow and provider integration
|  |- commands/               # CLI subcommands (`generate`, `auth` stub)
|  |- models/                 # Typed request/response and model capability data
|  |- providers/              # Provider interface and OpenRouter API implementation
|  |- services/               # Payload building, image encoding, and image persistence
|  |- utils/                  # Shared MIME, path, and CLI output helpers
|  |- cli.py                  # Argument parsing and command dispatch entrypoint
|  |- config.py               # Environment-based runtime configuration loading
|  |- constants.py            # Default model, API URL, and supported option constants
|  |- errors.py               # Application error hierarchy for user-safe failures
|  \- validation.py           # Prompt/image/option validation and request assembly
|- tests/                     # Pytest suite for CLI args and core service behavior
|- README.md                  # User-facing setup and usage guide
\- pyproject.toml             # Package metadata, dependencies, and `imagen` script

## Development Guide
- Build/install (editable): `python -m pip install -e .[test]`
- Run tests: `pytest`
- Run typecheck-level sanity check: `python -m compileall imagencli tests`
- Verify changes quickly: `pytest && python -m imagencli --help`
