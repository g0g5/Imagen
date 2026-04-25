from __future__ import annotations

from pathlib import Path

import pytest
import requests

from imagen.errors import ProviderError
from imagen.models.request import GenerateRequest
from imagen.providers.openrouter import OpenRouterProvider


class _FakeResponse:
    def __init__(self, payload: dict, *, text: str = "") -> None:
        self._payload = payload
        self.text = text

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def test_generate_uses_remote_model_modalities_and_caches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = GenerateRequest(
        prompt="A studio product photo of a camera",
        image_paths=[],
        model="sourceful/riverflow-v2-pro",
        output_dir=Path("./outputs"),
    )
    provider = OpenRouterProvider(api_key="test-key")
    get_calls = 0
    captured_payloads: list[dict] = []

    def fake_get(*args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal get_calls
        get_calls += 1
        return _FakeResponse(
            {
                "data": [
                    {
                        "id": "sourceful/riverflow-v2-pro",
                        "architecture": {
                            "modality": "text+image->image",
                            "input_modalities": ["text", "image"],
                            "output_modalities": ["image"],
                        },
                    },
                    {
                        "id": "openrouter/auto",
                        "architecture": {
                            "modality": "text+image+file+audio+video->text+image",
                            "input_modalities": ["text", "image", "audio"],
                            "output_modalities": ["text", "image"],
                        },
                    },
                ]
            }
        )

    def fake_post(*args, **kwargs):  # type: ignore[no-untyped-def]
        captured_payloads.append(kwargs["json"])
        return _FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "images": [
                                {"image_url": {"url": "data:image/png;base64,aaa"}}
                            ]
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(requests, "post", fake_post)

    first_response = provider.generate(request)
    second_response = provider.generate(request)

    assert first_response.images[0].data_url == "data:image/png;base64,aaa"
    assert second_response.images[0].data_url == "data:image/png;base64,aaa"
    assert get_calls == 1
    assert captured_payloads[0]["modalities"] == ["image"]
    assert captured_payloads[1]["modalities"] == ["image"]


def test_generate_falls_back_to_default_model_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = GenerateRequest(
        prompt="A cinematic sunset over mountains",
        image_paths=[],
        model="google/gemini-3.1-flash-image-preview",
        output_dir=Path("./outputs"),
    )
    provider = OpenRouterProvider(api_key="test-key")
    captured_payloads: list[dict] = []

    def fake_get(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise requests.Timeout()

    def fake_post(*args, **kwargs):  # type: ignore[no-untyped-def]
        captured_payloads.append(kwargs["json"])
        return _FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "images": [
                                {"image_url": {"url": "data:image/png;base64,bbb"}}
                            ]
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(requests, "post", fake_post)

    response = provider.generate(request)

    assert response.images[0].data_url == "data:image/png;base64,bbb"
    assert captured_payloads[0]["modalities"] == ["image", "text"]


def test_generate_raises_when_model_metadata_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = GenerateRequest(
        prompt="A watercolor landscape",
        image_paths=[],
        model="example/unknown-image-model",
        output_dir=Path("./outputs"),
    )
    provider = OpenRouterProvider(api_key="test-key")

    def fake_get(*args, **kwargs):  # type: ignore[no-untyped-def]
        return _FakeResponse({"data": []})

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(ProviderError, match="Model metadata unavailable"):
        provider.generate(request)
