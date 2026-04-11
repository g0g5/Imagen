# pytest for a Python CLI image client

Official docs:
- pytest stable docs: https://docs.pytest.org/en/stable/
- parametrization: https://docs.pytest.org/en/stable/how-to/parametrize.html
- assertions / `pytest.raises`: https://docs.pytest.org/en/stable/how-to/assert.html
- monkeypatch: https://docs.pytest.org/en/stable/how-to/monkeypatch.html
- output capture: https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html
- `pytest-httpx`: https://colin-b.github.io/pytest_httpx/

## Install

```bash
pip install pytest httpx pytest-httpx
```

## CLI argument parsing

Keep parsing pure: `parse_args(argv=None)`.

```python
# client/cli.py
from argparse import ArgumentParser

def build_parser() -> ArgumentParser:
    p = ArgumentParser()
    p.add_argument("prompt")
    p.add_argument("--model", choices=["fast", "quality"], default="fast")
    p.add_argument("--steps", type=int, default=20)
    return p

def parse_args(argv=None):
    return build_parser().parse_args(argv)
```

```python
# tests/test_cli_args.py
import pytest
from client.cli import parse_args

def test_parse_args_happy_path():
    ns = parse_args(["a cat", "--model", "quality", "--steps", "30"])
    assert ns.prompt == "a cat"
    assert ns.model == "quality"
    assert ns.steps == 30

def test_parse_args_defaults():
    ns = parse_args(["a cat"])
    assert ns.model == "fast"
    assert ns.steps == 20

def test_parse_args_rejects_bad_choice():
    with pytest.raises(SystemExit):
        parse_args(["a cat", "--model", "broken"])
```

## Testing `main()` with `monkeypatch` and `capsys`

```python
# client/cli.py
import sys

def main(argv=None) -> int:
    args = parse_args(argv)
    print(f"generating: {args.prompt}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

```python
# tests/test_cli_main.py
from client import cli

def test_main_uses_sys_argv(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["prog", "sunset", "--model", "fast"])
    code = cli.main()
    out = capsys.readouterr().out
    assert code == 0
    assert "generating: sunset" in out
```

## Function-level validation

Use `@pytest.mark.parametrize` for valid/invalid inputs and `pytest.raises(..., match=...)` for exact failure intent.

```python
# client/validate.py
def validate_request(prompt: str, steps: int, width: int, height: int) -> None:
    if not prompt.strip():
        raise ValueError("prompt must not be empty")
    if not 1 <= steps <= 100:
        raise ValueError("steps must be between 1 and 100")
    if width % 64 or height % 64:
        raise ValueError("size must be divisible by 64")
```

```python
# tests/test_validate.py
import pytest
from client.validate import validate_request

@pytest.mark.parametrize(
    "prompt,steps,width,height",
    [
        ("cat", 1, 512, 512),
        ("cat", 50, 1024, 768),
    ],
)
def test_validate_request_accepts_valid_inputs(prompt, steps, width, height):
    validate_request(prompt, steps, width, height)

@pytest.mark.parametrize(
    "prompt,steps,width,height,msg",
    [
        (" ", 20, 512, 512, "prompt must not be empty"),
        ("cat", 0, 512, 512, "steps must be between 1 and 100"),
        ("cat", 20, 500, 512, "size must be divisible by 64"),
    ],
)
def test_validate_request_rejects_bad_inputs(prompt, steps, width, height, msg):
    with pytest.raises(ValueError, match=msg):
        validate_request(prompt, steps, width, height)
```

## HTTP client mocking with `pytest-httpx`

Best fit when the CLI uses `httpx` to call an image API.

```python
# client/api.py
import httpx

def generate_image(base_url: str, payload: dict) -> str:
    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        r = client.post("/images/generations", json=payload)
        r.raise_for_status()
        return r.json()["data"][0]["url"]
```

```python
# tests/test_api.py
import httpx
import pytest
from client.api import generate_image

def test_generate_image_success(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://img.example.com/images/generations",
        match_json={"prompt": "cat", "model": "fast"},
        json={"data": [{"url": "https://cdn.example.com/cat.png"}]},
    )

    url = generate_image(
        "https://img.example.com",
        {"prompt": "cat", "model": "fast"},
    )

    assert url == "https://cdn.example.com/cat.png"

def test_generate_image_timeout(httpx_mock):
    httpx_mock.add_exception(httpx.ReadTimeout("timed out"))
    with pytest.raises(httpx.ReadTimeout):
        generate_image("https://img.example.com", {"prompt": "cat"})

def test_generate_image_sent_expected_request(httpx_mock):
    httpx_mock.add_response(json={"data": [{"url": "x"}]})
    generate_image("https://img.example.com", {"prompt": "cat"})
    req = httpx_mock.get_request()
    assert req.method == "POST"
    assert str(req.url) == "https://img.example.com/images/generations"
```

## Minimal layout suggestion

```text
client/
  cli.py          # argparse only
  validate.py     # pure validation helpers
  api.py          # httpx calls only
tests/
  test_cli_args.py
  test_cli_main.py
  test_validate.py
  test_api.py
```

## Run

```bash
pytest -q
```
