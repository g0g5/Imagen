# Implementation Plan

## Phase 1: Project Setup and Packaging

1. Update `pyproject.toml` so the package exposes an installable `imagen` console script and declares the required runtime and test dependencies.
2. Replace the placeholder entrypoint with the package layout under `imagencli/`, including `__main__.py`, CLI modules, provider modules, service modules, models, and utilities.
3. Establish shared constants for the default model, OpenRouter endpoint, supported MIME types, and static capability data used by validation.

### Completion Log

- 2026-04-11 23:20:18: Updated `pyproject.toml` with build metadata, runtime/test dependencies, and the `imagen` console script.
- 2026-04-11 23:20:18: Replaced the placeholder top-level entrypoint by creating the `imagencli/` package layout with CLI, commands, providers, services, models, and utils modules.
- 2026-04-11 23:20:18: Added shared constants for OpenRouter endpoint, default model, supported image MIME types, and static model capability data.

## Phase 2: CLI and Command Flow

1. Implement `build_parser()` and `parse_args(argv=None)` with `argparse`, covering the main generate flow and the `imagen auth` subcommand stub.
2. Add argument definitions for `--prompt`, `--image`, `--model`, `--ratio`, `--resolution`, and `--output_dir`, preserving the expected defaults and multi-image behavior.
3. Implement `main(argv=None) -> int` to dispatch commands, surface concise user-facing errors, and return non-zero exit codes on failure.
4. Implement the `imagen auth` stub so it exits successfully and explains that `OPENROUTER_API_KEY` is currently required.

### Completion Log

- 2026-04-11 23:24:49: Implemented `build_parser()` with `generate` and `auth` subcommands and added `parse_args(argv=None)` normalization so `imagen --prompt ...` maps to the generate flow.
- 2026-04-11 23:24:49: Added CLI arguments for `--prompt`, `--image`, `--model`, `--ratio`, `--resolution`, and `--output_dir` with defaults and multi-image input support.
- 2026-04-11 23:24:49: Implemented `main(argv=None) -> int` command dispatch with `ImagenError` handling and non-zero exits on failures.
- 2026-04-11 23:24:49: Implemented `imagen auth` stub output indicating `OPENROUTER_API_KEY` is currently required.

## Phase 3: Validation and Request Modeling

1. Define request and response models that carry prompt text, image paths, model selection, optional image settings, and output location.
2. Implement configuration loading for `OPENROUTER_API_KEY` and fail early when it is missing.
3. Add validation helpers for trimmed non-empty prompts, supported image paths, supported MIME types, and model-specific ratio and resolution rules.
4. Keep the capability matrix in a static module so unsupported combinations are rejected before any network call.

### Completion Log

- 2026-04-11 23:26:29: Updated request modeling so `GenerateRequest` carries normalized `Path` image inputs and output location for downstream provider/services integration.
- 2026-04-11 23:26:29: Implemented strict runtime config loading for `OPENROUTER_API_KEY` with early `ConfigError` when the key is missing or blank.
- 2026-04-11 23:26:29: Added centralized validation helpers for prompt trimming, image file existence/type checks, and model-aware ratio/resolution validation backed by static capabilities.
- 2026-04-11 23:26:29: Added capability accessor usage in validation flow and wired `run_generate` to build a validated request before any later-phase provider network call.

## Phase 4: Image Encoding, Payload Building, and Provider Integration

1. Implement local image encoding to convert supported input files into base64 data URLs for OpenRouter image-to-image requests.
2. Build a payload builder that produces the correct OpenRouter request body for both prompt-only and prompt-plus-image flows, including text-first ordering for mixed content.
3. Implement a provider base interface and an OpenRouter provider that isolates HTTP behavior from CLI parsing and file system concerns.
4. Use `requests` to send `POST` calls to the OpenRouter chat completions endpoint with the required headers, timeouts, and Gemini image modalities.
5. Map timeout, HTTP, network, and malformed-response failures into clear CLI-safe error messages.

### Completion Log

- 2026-04-11 23:28:55: Implemented local image encoding utilities to convert validated image files into base64 data URLs for OpenRouter image-to-image inputs.
- 2026-04-11 23:28:55: Added OpenRouter payload builder support for prompt-only and prompt-plus-image requests with required Gemini modalities, text-first mixed content ordering, and conditional image config fields.
- 2026-04-11 23:28:55: Implemented the OpenRouter provider over the base provider interface, isolating HTTP request/response handling from CLI argument parsing and filesystem operations.
- 2026-04-11 23:28:55: Wired provider calls to `requests.post` with OpenRouter endpoint, auth/content headers, user agent, and configured connect/read timeouts.
- 2026-04-11 23:28:55: Added explicit error mapping for timeout, HTTP, network, invalid JSON, missing image response fields, and malformed image entries into `ProviderError`/`ResponseFormatError` messages safe for CLI output.

## Phase 5: Response Handling and File Output

1. Parse generated image data from `choices[0].message.images[*].image_url.url` and validate that image content is present.
2. Decode returned data URLs and save the images into the requested output directory, creating the directory when needed.
3. Apply the timestamp-plus-index naming convention so multiple returned images are written predictably.
4. Add output helpers that report success paths cleanly without leaking raw API response details.

### Completion Log

- 2026-04-11 23:31:04: Kept provider response parsing aligned to `choices[0].message.images[*].image_url.url` and enforced non-empty image URL data before save flow.
- 2026-04-11 23:31:04: Implemented image data URL decoding and output persistence with automatic output directory creation.
- 2026-04-11 23:31:04: Added timestamp-plus-index output naming in the format `imagen-YYYYMMDD-HHMMSS-01.<ext>` for predictable multi-image writes.
- 2026-04-11 23:31:04: Added CLI output helper formatting and wired generate command success output to print saved file paths only.

## Phase 6: Tests and Documentation

1. Add `pytest` coverage for parser defaults, supported and unsupported CLI values, missing API key handling, invalid image paths, payload builder behavior, image encoding, image saving, and `imagen auth` stub output.
2. Structure tests around pure functions where possible so parser, validation, and payload construction remain easy to verify without live API calls.
3. Update `README.md` with installation steps, `OPENROUTER_API_KEY` setup, text-to-image and multi-image examples, supported ratio and resolution values, and the current `imagen auth` limitation.
4. Run the local test suite and fix any implementation gaps needed to satisfy the acceptance criteria.

### Completion Log

- 2026-04-11 23:35:50: Added `pytest` coverage for CLI parsing defaults, validation failures, missing `OPENROUTER_API_KEY`, invalid image paths, payload building, image encoding, image saving, and `imagen auth` stub output.
- 2026-04-11 23:35:50: Structured tests around pure units (`validation`, `payload_builder`, `image_encoder`, `image_saver`) and command entrypoints to avoid live OpenRouter API calls.
- 2026-04-11 23:35:50: Updated `README.md` with install commands, environment setup, text-to-image and multi-image examples, supported ratio/resolution values, and `imagen auth` limitation notes.
- 2026-04-11 23:35:50: Ran local test suite and verified all tests pass.
