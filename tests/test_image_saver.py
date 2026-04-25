from __future__ import annotations

import base64
from pathlib import Path

import pytest

from imagen.errors import ResponseFormatError
from imagen.models.response import GeneratedImage
from imagen.services.image_saver import save_generated_images


def test_save_generated_images_writes_files(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    images = [
        GeneratedImage(
            data_url=f"data:image/png;base64,{base64.b64encode(b'first').decode('utf-8')}"
        ),
        GeneratedImage(
            data_url=f"data:image/jpeg;base64,{base64.b64encode(b'second').decode('utf-8')}"
        ),
    ]

    saved_paths = save_generated_images(images, output_dir)

    assert len(saved_paths) == 2
    assert output_dir.exists()
    assert saved_paths[0].name.startswith("imagen-")
    assert saved_paths[0].name.endswith("-01.png")
    assert saved_paths[1].name.endswith("-02.jpg")
    assert saved_paths[0].read_bytes() == b"first"
    assert saved_paths[1].read_bytes() == b"second"


def test_save_generated_images_rejects_malformed_data_url(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    images = [GeneratedImage(data_url="not-a-data-url")]

    with pytest.raises(ResponseFormatError, match="not a data URL"):
        save_generated_images(images, output_dir)
