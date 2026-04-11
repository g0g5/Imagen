"""OpenRouter provider implementation."""

from __future__ import annotations

import requests

from imagencli.constants import OPENROUTER_CHAT_COMPLETIONS_URL
from imagencli.errors import ProviderError, ResponseFormatError
from imagencli.models.request import GenerateRequest
from imagencli.models.response import GenerateResponse, GeneratedImage
from imagencli.providers.base import ImageProvider
from imagencli.services.image_encoder import encode_images_to_data_urls
from imagencli.services.payload_builder import build_openrouter_payload

_HTTP_TIMEOUT = (3.05, 120)
_USER_AGENT = "imagen-cli/0.1.0"


class OpenRouterProvider(ImageProvider):
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        data_urls = encode_images_to_data_urls(request.image_paths)
        payload = build_openrouter_payload(request, data_urls)
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "User-Agent": _USER_AGENT,
        }

        try:
            response = requests.post(
                OPENROUTER_CHAT_COMPLETIONS_URL,
                json=payload,
                headers=headers,
                timeout=_HTTP_TIMEOUT,
            )
            response.raise_for_status()
        except requests.Timeout as exc:
            raise ProviderError("OpenRouter request timed out.") from exc
        except requests.HTTPError as exc:
            body = ""
            if exc.response is not None and exc.response.text:
                body = exc.response.text.strip()[:500]
            message = "OpenRouter HTTP error."
            if body:
                message = f"OpenRouter HTTP error: {body}"
            raise ProviderError(message) from exc
        except requests.RequestException as exc:
            raise ProviderError("OpenRouter request failed.") from exc

        try:
            response_data = response.json()
        except ValueError as exc:
            raise ResponseFormatError(
                "OpenRouter response was not valid JSON."
            ) from exc

        return _parse_generate_response(response_data)


def _parse_generate_response(response_data: dict) -> GenerateResponse:
    try:
        choices = response_data["choices"]
        first_choice = choices[0]
        message = first_choice["message"]
        images = message["images"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ResponseFormatError(
            "OpenRouter response missing choices[0].message.images."
        ) from exc

    generated_images: list[GeneratedImage] = []
    for image in images:
        try:
            data_url = image["image_url"]["url"]
        except (KeyError, TypeError) as exc:
            raise ResponseFormatError(
                "OpenRouter response image entry is malformed."
            ) from exc
        if not isinstance(data_url, str) or not data_url.strip():
            raise ResponseFormatError(
                "OpenRouter response image URL must be a non-empty string."
            )
        generated_images.append(GeneratedImage(data_url=data_url))

    if not generated_images:
        raise ResponseFormatError("OpenRouter response did not include image data.")
    return GenerateResponse(images=generated_images)
