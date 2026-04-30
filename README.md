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

Run the auth command and follow the prompts to store your OpenRouter API key:

```bash
imagen auth
```

The key is encrypted and saved in `~/.config/imagen/keys`. Credentials saved
with `imagen auth` take priority over environment variables.

You can also set your OpenRouter API key in the environment as a fallback.

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

Text-to-image from a prompt file:

```bash
imagen --prompt-file ./prompt.txt
```

Image-to-image with multiple inputs:

```bash
imagen --prompt "Blend these references" --image "./a.png" "./b.jpg" --ratio 16:9 --resolution 2K --output_dir ./outputs
```

Store or update your OpenRouter API key:

```bash
imagen auth
```

Install the bundled Claude skill:

```bash
imagen install --skills
```

`imagen auth` currently supports OpenRouter.ai.

## MCP Server

`imagen-mcp` starts a FastMCP server over stdio and exposes one tool, `generate_image`.

The tool uses the same options as the CLI:

- `prompt` maps to `--prompt`
- `prompt_file` maps to `--prompt-file`
- `image` maps to `--image`
- `model` maps to `--model`
- `ratio` maps to `--ratio`
- `resolution` maps to `--resolution`
- `output_dir` maps to `--output_dir`

`prompt_file` supports `.txt` and `.json` files only. Files are read as UTF-8
text, including `.json` files, and are not parsed or semantically validated.
When `prompt_file` is provided, it takes priority over `prompt`. Prompt file
content must be non-empty.

The MCP server uses the same saved credentials as the CLI. If no saved key is
available, it falls back to `OPENROUTER_API_KEY`.

Example MCP client configuration when using an environment variable:

```json
{
  "mcpServers": {
    "imagen": {
      "command": "imagen-mcp",
      "env": {
        "OPENROUTER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

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
