from __future__ import annotations

import base64
from pathlib import Path

import pytest

from imagencli.errors import ValidationError
from imagencli.services.image_encoder import encode_image_to_data_url


def test_encode_image_to_data_url_png(tmp_path: Path) -> None:
    image_path = tmp_path / "input.png"
    image_bytes = b"png-bytes"
    image_path.write_bytes(image_bytes)

    data_url = encode_image_to_data_url(image_path)

    expected = base64.b64encode(image_bytes).decode("utf-8")
    assert data_url == f"data:image/png;base64,{expected}"


def test_encode_image_to_data_url_rejects_unknown_mime(tmp_path: Path) -> None:
    image_path = tmp_path / "input.unknown"
    image_path.write_bytes(b"bytes")

    with pytest.raises(ValidationError, match="Could not determine MIME type"):
        encode_image_to_data_url(image_path)
