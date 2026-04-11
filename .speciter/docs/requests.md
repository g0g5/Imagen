# Requests for CLI Image Clients

Sources: Requests 2.33.1 docs (`quickstart`, `advanced`, `api`) - https://docs.python-requests.org/en/master/

## Install

```bash
python -m pip install requests
```

## POST JSON

```python
import requests

payload = {
    "prompt": "cinematic snowy mountain at sunrise",
    "width": 1024,
    "height": 1024,
}

r = requests.post(
    "https://api.example.com/v1/images/generate",
    json=payload,
    headers={"Authorization": f"Bearer {api_key}"},
    timeout=(3.05, 60),
)
r.raise_for_status()
data = r.json()
image_url = data["data"][0]["url"]
```

## Session Reuse

```python
import requests

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {api_key}",
    "User-Agent": "imagen-cli/1.0",
})

r = session.post(
    "https://api.example.com/v1/images/generate",
    json={"prompt": prompt},
    timeout=(3.05, 60),
)
r.raise_for_status()
```

## Timeouts

```python
requests.post(url, json=payload, timeout=10)          # connect + read
requests.post(url, json=payload, timeout=(3.05, 60))  # connect, read
```

```python
try:
    requests.post(url, json=payload, timeout=(3.05, 60))
except requests.ConnectTimeout:
    print("connect timeout")
except requests.ReadTimeout:
    print("read timeout")
```

Notes:
- Always set `timeout`; Requests does not time out by default.
- Timeout is socket inactivity, not total wall-clock request time.

## Error Handling

```python
import requests

try:
    r = requests.post(url, json=payload, timeout=(3.05, 60))
    r.raise_for_status()
    result = r.json()
except requests.HTTPError as e:
    body = e.response.text if e.response is not None else ""
    print(f"http error: {e} :: {body[:500]}")
except requests.Timeout:
    print("timeout")
except requests.ConnectionError:
    print("network error")
except requests.JSONDecodeError:
    print("invalid json response")
except requests.RequestException as e:
    print(f"request failed: {e}")
```

## Download Generated Image

```python
import requests

with requests.get(image_url, stream=True, timeout=(3.05, 120)) as r:
    r.raise_for_status()
    with open("out.png", "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
```

## Download Bytes In Memory

```python
import requests

r = requests.get(image_url, timeout=(3.05, 120))
r.raise_for_status()
image_bytes = r.content
```

## Stream JSON/Event-like Output

```python
import json
import requests

with requests.get(events_url, stream=True, timeout=(3.05, 120)) as r:
    r.raise_for_status()
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if line:
            event = json.loads(line)
            print(event)
```

## Upload File

```python
import requests

with open("input.png", "rb") as f:
    r = requests.post(
        upload_url,
        files={"image": ("input.png", f, "image/png")},
        data={"prompt": prompt},
        timeout=(3.05, 120),
    )
    r.raise_for_status()
```

## Large Request Body Streaming

```python
with open("huge-input.bin", "rb") as f:
    r = requests.post(upload_url, data=f, timeout=(3.05, 120))
    r.raise_for_status()
```

## Retries for Transient Errors

```python
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

session = Session()
retry = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 502, 503, 504],
    allowed_methods={"GET", "POST"},
)
session.mount("https://", HTTPAdapter(max_retries=retry))

r = session.post(url, json=payload, timeout=(3.05, 60))
r.raise_for_status()
```

## Minimal Helper

```python
import requests


def post_json(url, payload, api_key):
    try:
        r = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "imagen-cli/1.0",
            },
            timeout=(3.05, 60),
        )
        r.raise_for_status()
        return r.json()
    except requests.JSONDecodeError as e:
        raise RuntimeError("server returned non-JSON") from e
    except requests.RequestException as e:
        raise RuntimeError(f"request failed: {e}") from e
```

## Key Doc Points

- Use `json=` for JSON bodies; `data=` does not set `application/json` for you.
- `json=` is ignored if `data=` or `files=` is also provided.
- Use `raise_for_status()` for HTTP 4xx/5xx.
- `r.json()` can succeed even when HTTP status is an error.
- Use `stream=True` + `iter_content()` for large image downloads.
- Open upload files in binary mode.
- Sessions reuse connections and persist default headers/cookies.
