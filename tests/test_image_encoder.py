from __future__ import annotations

import base64
from pathlib import Path

import pytest

from imagen.errors import ValidationError
from imagen.services.image_encoder import encode_image_to_data_url
from imagen.utils import mime as mime_utils


def test_encode_image_to_data_url_png(tmp_path: Path) -> None:
    image_path = tmp_path / "input.png"
    image_bytes = b"png-bytes"
    image_path.write_bytes(image_bytes)

    data_url = encode_image_to_data_url(image_path)

    expected = base64.b64encode(image_bytes).decode("utf-8")
    assert data_url == f"data:image/png;base64,{expected}"


def test_detect_mime_type_normalizes_application_jpg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        mime_utils,
        "guess_type",
        lambda _: ("application/jpg", None),
    )

    assert mime_utils.detect_mime_type(Path("input.jpg")) == "image/jpeg"


def test_encode_image_to_data_url_normalizes_application_jpg(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image_path = tmp_path / "input.jpg"
    image_bytes = b"jpg-bytes"
    image_path.write_bytes(image_bytes)
    monkeypatch.setattr(
        mime_utils,
        "guess_type",
        lambda _: ("application/jpg", None),
    )

    data_url = encode_image_to_data_url(image_path)

    expected = base64.b64encode(image_bytes).decode("utf-8")
    assert data_url == f"data:image/jpeg;base64,{expected}"


def test_encode_image_to_data_url_rejects_unknown_mime(tmp_path: Path) -> None:
    image_path = tmp_path / "input.unknown"
    image_path.write_bytes(b"bytes")

    with pytest.raises(ValidationError, match="Could not determine MIME type"):
        encode_image_to_data_url(image_path)
