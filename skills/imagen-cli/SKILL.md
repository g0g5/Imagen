---
name: imagen-cli
description: Generate images with Imagen CLI using OpenRouter models and local image inputs.
allowed-tools: Bash(imagen:*)
---

# Imagen CLI

Use `imagen` to generate images from a prompt, optionally with reference images.

## Prerequisite

Set `OPENROUTER_API_KEY` before running commands.

```bash
export OPENROUTER_API_KEY="your_api_key_here"
```

## Core usage

`generate` is the default command.

```bash
imagen --prompt "A cinematic sunset over mountains"
imagen --prompt "Blend these references" --image ./a.png ./b.jpg
imagen --prompt "A magazine cover photo" --ratio 4:5 --resolution 2K --output_dir ./outputs --model openai/gpt-image-1.5
imagen generate --prompt "A watercolor fox in a forest"
```

## Parameters

```bash
--prompt "your prompt text"                 # required
--image ./input.png ./reference.jpg         # optional, one or more files
--model google/gemini-3.1-flash-image-preview
--ratio 16:9
--resolution 2K
--output_dir ./outputs
```

## Supported values

Aspect ratios:

```text
Base: 1:1 2:3 3:2 3:4 4:3 4:5 5:4 9:16 16:9 21:9
Gemini extra: 1:4 4:1 1:8 8:1
```

Resolutions:

```text
Base: 1K 2K 4K
Gemini extra: 0.5K
```

Supported input image types:

```text
image/png
image/jpeg
image/webp
image/gif
```

## Validation

The CLI rejects empty prompts, missing image files, unsupported image types, and invalid `--ratio` or `--resolution` values for the selected model.

## Output

Generated images are saved locally and printed as paths.

```text
Saved 2 image(s):
- outputs/generated-1.png
- outputs/generated-2.png
```

## Auth command

`imagen auth` is a stub and does not store credentials.

```bash
imagen auth
```

## Agent tasks

* **Generate from text**: `imagen --prompt ...`
* **Generate from references**: add `--image`
* **Control shape and size**: add `--ratio` and `--resolution`
* **Choose output folder**: add `--output_dir`
