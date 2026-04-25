"""OpenRouter payload construction utilities."""

from __future__ import annotations

from imagen.models.request import GenerateRequest


def build_openrouter_payload(
    request: GenerateRequest,
    image_data_urls: list[str],
    modalities: list[str],
) -> dict:
    payload: dict[str, object] = {
        "model": request.model,
        "modalities": modalities,
    }

    if image_data_urls:
        content: list[dict[str, object]] = [{"type": "text", "text": request.prompt}]
        for data_url in image_data_urls:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": data_url},
                }
            )
        payload["messages"] = [{"role": "user", "content": content}]
    else:
        payload["messages"] = [{"role": "user", "content": request.prompt}]

    image_config: dict[str, str] = {}
    if request.ratio is not None:
        image_config["aspect_ratio"] = request.ratio
    if request.resolution is not None:
        image_config["image_size"] = request.resolution
    if image_config:
        payload["image_config"] = image_config

    return payload
