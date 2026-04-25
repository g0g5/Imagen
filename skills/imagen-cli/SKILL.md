---
name: imagen-cli
description: Generate images with Imagen CLI using OpenRouter models and local image inputs.
allowed-tools: Bash(imagen:*)
---

# Imagen CLI

Use `imagen` to generate images from prompt text or a prompt file, optionally with reference images.

## Core usage

```bash
imagen --prompt "A cinematic sunset over mountains"
imagen --prompt-file ./prompt.txt
imagen --prompt "Blend these references" --image ./a.png ./b.jpg
imagen --prompt "A magazine cover photo" --ratio 4:5 --resolution 2K --output_dir ./outputs --model openai/gpt-image-1.5
```

## Parameters

```bash
--prompt "your prompt text"                 # required unless --prompt-file is provided
--prompt-file ./prompt.txt                   # optional, reads prompt from .txt or .json
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

The CLI rejects empty prompts, empty prompt files, missing image files, unsupported image types, and invalid `--ratio` or `--resolution` values for the selected model.

`--prompt-file` supports `.txt` and `.json` files only. Files are read as UTF-8 text, including `.json` files, and are not parsed or semantically validated. When `--prompt-file` is provided, it takes priority over `--prompt`.

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
* **Generate from prompt file**: `imagen --prompt-file ./prompt.txt`
* **Generate from references**: add `--image`
* **Control shape and size**: add `--ratio` and `--resolution`
* **Choose output folder**: add `--output_dir`
