from __future__ import annotations

from pathlib import Path

from imagen.models.request import GenerateRequest
from imagen.services.payload_builder import build_openrouter_payload


def test_build_payload_text_only_with_image_config() -> None:
    request = GenerateRequest(
        prompt="A cinematic sunset over mountains",
        image_paths=[],
        model="google/gemini-3.1-flash-image-preview",
        ratio="16:9",
        resolution="2K",
        output_dir=Path("./outputs"),
    )

    payload = build_openrouter_payload(
        request,
        image_data_urls=[],
        modalities=["image", "text"],
    )

    assert payload["model"] == request.model
    assert payload["modalities"] == ["image", "text"]
    assert payload["messages"] == [{"role": "user", "content": request.prompt}]
    assert payload["image_config"] == {"aspect_ratio": "16:9", "image_size": "2K"}


def test_build_payload_multi_image_orders_text_first() -> None:
    request = GenerateRequest(
        prompt="Blend these references",
        image_paths=[Path("a.png"), Path("b.jpg")],
        model="google/gemini-3.1-flash-image-preview",
        output_dir=Path("./outputs"),
    )
    data_urls = ["data:image/png;base64,aaa", "data:image/jpeg;base64,bbb"]

    payload = build_openrouter_payload(
        request,
        image_data_urls=data_urls,
        modalities=["image"],
    )

    content = payload["messages"][0]["content"]
    assert content[0] == {"type": "text", "text": request.prompt}
    assert content[1] == {"type": "image_url", "image_url": {"url": data_urls[0]}}
    assert content[2] == {"type": "image_url", "image_url": {"url": data_urls[1]}}
    assert payload["modalities"] == ["image"]
    assert "image_config" not in payload
