# Imagen CLI OpenRouter MVP

## Goal

Build a lightweight Python CLI named `imagen` for text-to-image and image-to-image generation using OpenRouter only, while keeping provider abstractions ready for future backends.

## Scope

- Deliver a package entry so users can run `imagen`
- Implement OpenRouter-backed image generation flow
- Support prompt-only and prompt+one-or-more-image inputs
- Read API key from `OPENROUTER_API_KEY`
- Add `imagen auth` as a documented stub that is not implemented yet
- Add basic tests for CLI parsing, validation, and payload building
- Add README usage for install and examples

## Non-Goals

- No local API key storage yet
- No provider switching CLI yet
- No streaming responses in this iteration
- No model auto-discovery from OpenRouter API
- No remote image URL input as a first-class CLI feature

## User-Facing Commands

### Main Command

```bash
imagen --prompt "A cinematic sunset over mountains"
imagen --prompt "Turn this into anime key art" --image "./input.png"
imagen --prompt "Blend these references" --image "./a.png" "./b.jpg" --ratio 16:9 --resolution 2K --output_dir ./outputs
```

### Required / Optional Args

- `--prompt`: required string
- `--image`: optional, one or more image paths, supports quoted paths with spaces
- `--model`: optional, default `google/gemini-3.1-flash-image-preview`
- `--ratio`: optional, validated against supported aspect ratios
- `--resolution`: optional, validated against supported image sizes
- `--output_dir`: optional, default `./outputs`

### Subcommand Stub

```bash
imagen auth
```

Behavior: print a short message that provider API key storage is a future feature and current auth uses `OPENROUTER_API_KEY`.

## Supported Values

### Aspect Ratios

Base set:

`1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`

Extended set for `google/gemini-3.1-flash-image-preview` only:

`1:4`, `4:1`, `1:8`, `8:1`

### Resolutions

Base set:

`1K`, `2K`, `4K`

Extended for `google/gemini-3.1-flash-image-preview` only:

`0.5K`

## External Dependencies

- `requests`: synchronous HTTP client for OpenRouter API calls
- `pytest`: unit tests for parser, validation, payload builder, and command behavior

## Proposed Project Structure

```text
imagencli/
  __init__.py
  __main__.py
  cli.py
  config.py
  constants.py
  errors.py
  commands/
    __init__.py
    generate.py
    auth.py
  providers/
    __init__.py
    base.py
    openrouter.py
  models/
    __init__.py
    request.py
    response.py
    capabilities.py
  services/
    __init__.py
    image_encoder.py
    image_saver.py
    payload_builder.py
  utils/
    __init__.py
    mime.py
    paths.py
    output.py
tests/
  test_cli_args.py
  test_generate_command.py
  test_payload_builder.py
  test_image_encoder.py
  test_image_saver.py
```

## Architecture

### CLI Layer

- Use `argparse`
- Keep parser construction pure: `build_parser()` and `parse_args(argv=None)`
- `main(argv=None) -> int` should orchestrate command dispatch and return exit codes

Minimal pattern:

```python
from argparse import ArgumentParser


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="imagen")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--image", nargs="+")
    parser.add_argument("--model", default="google/gemini-3.1-flash-image-preview")
    parser.add_argument("--ratio")
    parser.add_argument("--resolution")
    parser.add_argument("--output_dir", default="./outputs")
    return parser
```

### Provider Abstraction

- Define one base provider interface for future backends
- OpenRouter implementation should inherit the same base class that future providers will use
- Keep provider logic isolated from CLI parsing and file I/O

Suggested interface:

```python
class ImageProvider:
    def generate(self, request: "GenerateRequest") -> "GenerateResponse":
        raise NotImplementedError
```

### Request Model

Suggested fields:

- `prompt: str`
- `image_paths: list[str]`
- `model: str`
- `ratio: str | None`
- `resolution: str | None`
- `output_dir: Path`

### OpenRouter Request Rules

- Endpoint: `POST https://openrouter.ai/api/v1/chat/completions`
- Header: `Authorization: Bearer <OPENROUTER_API_KEY>`
- Header: `Content-Type: application/json`
- For Gemini image models, send `modalities: ["image", "text"]`
- For prompt-only generation, `messages` may be a plain text user message
- For image input generation, `messages[0].content` must be an array with text first, then one or more `image_url` items
- Local images must be converted to base64 data URLs before sending

Text-to-image payload shape:

```python
payload = {
    "model": request.model,
    "messages": [
        {
            "role": "user",
            "content": request.prompt,
        }
    ],
    "modalities": ["image", "text"],
    "image_config": {
        "aspect_ratio": request.ratio,
        "image_size": request.resolution,
    },
}
```

Image-to-image payload shape:

```python
payload = {
    "model": request.model,
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": request.prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": data_url_1},
                },
                {
                    "type": "image_url",
                    "image_url": {"url": data_url_2},
                },
            ],
        }
    ],
    "modalities": ["image", "text"],
}
```

Implementation note: omit `image_config` keys when CLI args are not provided.

## Data Handling

### Input Images

- Accept one or more filesystem paths from `--image`
- Verify each path exists before provider call
- Support MIME types: `image/png`, `image/jpeg`, `image/webp`, `image/gif`
- Convert files to `data:<mime>;base64,<encoded>`

Minimal pattern:

```python
import base64
from pathlib import Path


def encode_image(path: Path, mime_type: str) -> str:
    raw = path.read_bytes()
    return f"data:{mime_type};base64,{base64.b64encode(raw).decode('utf-8')}"
```

### Output Images

- Parse `choices[0].message.images[*].image_url.url`
- Expect data URLs, typically PNG
- Decode and save into `--output_dir`
- Auto-create output directory if needed
- Default filename format: `imagen-YYYYMMDD-HHMMSS-01.png`

## Validation Rules

- `--prompt` must be non-empty after trimming
- `OPENROUTER_API_KEY` must exist in environment before making requests
- Each `--image` path must exist and be a supported image type
- `--ratio` must be in the allowed set for the selected model
- `--resolution` must be in the allowed set for the selected model
- Reject `0.5K` unless model is `google/gemini-3.1-flash-image-preview`
- Reject extended aspect ratios unless model is `google/gemini-3.1-flash-image-preview`

Store the capability matrix in a static module for this iteration.

## Error Handling

- Distinguish config errors, validation errors, network errors, HTTP errors, and malformed response errors
- Surface concise user messages in CLI output
- Return non-zero exit code on failure
- If API returns non-2xx, include trimmed response text when safe
- If response lacks image data, fail with a clear response-format error

Requests usage pattern from library research:

```python
import requests


response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    json=payload,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "imagen-cli/0.1.0",
    },
    timeout=(3.05, 120),
)
response.raise_for_status()
data = response.json()
```

Recommended exception mapping:

```python
try:
    response = requests.post(url, json=payload, headers=headers, timeout=(3.05, 120))
    response.raise_for_status()
    data = response.json()
except requests.Timeout as exc:
    raise RuntimeError("OpenRouter request timed out") from exc
except requests.HTTPError as exc:
    body = exc.response.text if exc.response is not None else ""
    raise RuntimeError(f"OpenRouter HTTP error: {body[:500]}") from exc
except requests.RequestException as exc:
    raise RuntimeError("OpenRouter request failed") from exc
```

## Testing Requirements

Use `pytest`.

Required test coverage for this iteration:

- CLI argument parsing happy path and defaults
- CLI parser rejects unsupported values
- Validation for missing API key and bad file paths
- Payload builder for text-only request
- Payload builder for multi-image request with text-first content ordering
- Image saver decodes data URL and writes files
- `imagen auth` stub prints future-feature message

Testing patterns from library research:

```python
import pytest


@pytest.mark.parametrize(
    "ratio",
    ["1:1", "16:9", "21:9"],
)
def test_ratio_accepts_supported_values(ratio):
    assert validate_ratio(ratio, "google/gemini-3.1-flash-image-preview") is None


def test_ratio_rejects_unsupported_value():
    with pytest.raises(ValueError, match="Unsupported aspect ratio"):
        validate_ratio("7:5", "google/gemini-3.1-flash-image-preview")
```

```python
def test_parse_args_defaults():
    ns = parse_args(["--prompt", "a cat"])
    assert ns.model == "google/gemini-3.1-flash-image-preview"
    assert ns.output_dir == "./outputs"
```

## README Requirements

Document:

- install steps
- environment variable setup for `OPENROUTER_API_KEY`
- text-to-image example
- image-to-image example with multiple `--image` inputs
- supported ratio/resolution values
- note that `imagen auth` is not implemented yet

## Implementation Checklist

- Update packaging so `imagen` is an installable console script
- Create package layout under `imagencli/`
- Implement parser and command dispatch
- Implement request validation and static capability matrix
- Implement OpenRouter provider using `requests`
- Implement local image encoding and output image saving
- Add `imagen auth` stub
- Add tests with `pytest`
- Write README

## Acceptance Criteria

- Running `imagen --prompt "..."` sends a valid OpenRouter image-generation request and saves at least one returned image when API credentials are valid
- Running `imagen --prompt "..." --image "./a.png" "./b.jpg"` sends prompt text first and all images as `image_url` entries
- Invalid ratio/resolution combinations fail locally before network I/O
- Missing `OPENROUTER_API_KEY` fails with a clear message
- Generated files are written under `--output_dir` using timestamp-plus-index naming
- `imagen auth` exits successfully with an explicit future-feature message
- Basic tests pass locally
