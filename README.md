# Imagen CLI

`imagen` is a lightweight Python CLI for OpenRouter image generation.

## Installation

```bash
uv tool install .
```

To include test tooling:

```bash
uv sync --dev
```

## Authentication

Set your OpenRouter API key in the environment before running commands.

```bash
export OPENROUTER_API_KEY="your_api_key_here"
```

On Windows PowerShell:

```powershell
$env:OPENROUTER_API_KEY = "your_api_key_here"
```

## Usage

Text-to-image:

```bash
imagen --prompt "A cinematic sunset over mountains"
```

Image-to-image with multiple inputs:

```bash
imagen --prompt "Blend these references" --image "./a.png" "./b.jpg" --ratio 16:9 --resolution 2K --output_dir ./outputs
```

Auth stub command:

```bash
imagen auth
```

Install the bundled Claude skill:

```bash
imagen install --skills
```

`imagen auth` is currently a stub and does not store credentials yet. This MVP uses `OPENROUTER_API_KEY` only.

## Supported Values

Aspect ratios:

- Base: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`
- Extended (`google/gemini-3.1-flash-image-preview` only): `1:4`, `4:1`, `1:8`, `8:1`

Resolutions:

- Base: `1K`, `2K`, `4K`
- Extended (`google/gemini-3.1-flash-image-preview` only): `0.5K`

## Run Tests

```bash
uv run pytest
```

## Development

```bash
uv sync --dev
```

Run the CLI locally:

```bash
uv run imagen --help
```
