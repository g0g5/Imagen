"""OpenRouter provider implementation."""

from __future__ import annotations

from dataclasses import dataclass

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
_OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models?output_modalities=image"


@dataclass(frozen=True)
class OpenRouterModelMetadata:
    id: str
    modality: str
    input_modalities: tuple[str, ...]
    output_modalities: tuple[str, ...]


_DEFAULT_IMAGE_MODELS: tuple[OpenRouterModelMetadata, ...] = (
    OpenRouterModelMetadata(
        id="google/gemini-3.1-flash-image-preview",
        modality="text+image->text+image",
        input_modalities=("image", "text"),
        output_modalities=("image", "text"),
    ),
    OpenRouterModelMetadata(
        id="sourceful/riverflow-v2-pro",
        modality="text+image->image",
        input_modalities=("text", "image"),
        output_modalities=("image",),
    ),
    OpenRouterModelMetadata(
        id="sourceful/riverflow-v2-fast",
        modality="text+image->image",
        input_modalities=("text", "image"),
        output_modalities=("image",),
    ),
    OpenRouterModelMetadata(
        id="black-forest-labs/flux.2-klein-4b",
        modality="text+image->image",
        input_modalities=("text", "image"),
        output_modalities=("image",),
    ),
    OpenRouterModelMetadata(
        id="bytedance-seed/seedream-4.5",
        modality="text+image->image",
        input_modalities=("image", "text"),
        output_modalities=("image",),
    ),
    OpenRouterModelMetadata(
        id="black-forest-labs/flux.2-max",
        modality="text+image->image",
        input_modalities=("text", "image"),
        output_modalities=("image",),
    ),
    OpenRouterModelMetadata(
        id="sourceful/riverflow-v2-max-preview",
        modality="text+image->image",
        input_modalities=("text", "image"),
        output_modalities=("image",),
    ),
    OpenRouterModelMetadata(
        id="sourceful/riverflow-v2-standard-preview",
        modality="text+image->image",
        input_modalities=("text", "image"),
        output_modalities=("image",),
    ),
    OpenRouterModelMetadata(
        id="sourceful/riverflow-v2-fast-preview",
        modality="text+image->image",
        input_modalities=("text", "image"),
        output_modalities=("image",),
    ),
    OpenRouterModelMetadata(
        id="black-forest-labs/flux.2-flex",
        modality="text+image->image",
        input_modalities=("text", "image"),
        output_modalities=("image",),
    ),
    OpenRouterModelMetadata(
        id="black-forest-labs/flux.2-pro",
        modality="text+image->image",
        input_modalities=("text", "image"),
        output_modalities=("image",),
    ),
    OpenRouterModelMetadata(
        id="google/gemini-3-pro-image-preview",
        modality="text+image->text+image",
        input_modalities=("image", "text"),
        output_modalities=("image", "text"),
    ),
    OpenRouterModelMetadata(
        id="openai/gpt-5-image-mini",
        modality="text+image+file->text+image",
        input_modalities=("file", "image", "text"),
        output_modalities=("image", "text"),
    ),
    OpenRouterModelMetadata(
        id="openai/gpt-5-image",
        modality="text+image+file->text+image",
        input_modalities=("image", "text", "file"),
        output_modalities=("image", "text"),
    ),
    OpenRouterModelMetadata(
        id="google/gemini-2.5-flash-image",
        modality="text+image->text+image",
        input_modalities=("image", "text"),
        output_modalities=("image", "text"),
    ),
)


class OpenRouterProvider(ImageProvider):
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._model_metadata_cache: dict[str, OpenRouterModelMetadata] = {}
        self._model_metadata_cache_populated = False

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        data_urls = encode_images_to_data_urls(request.image_paths)
        model_metadata = self._get_model_metadata(request.model)
        if "image" not in model_metadata.output_modalities:
            raise ProviderError(
                f"Model '{request.model}' does not support image output."
            )
        payload = build_openrouter_payload(
            request,
            data_urls,
            modalities=list(model_metadata.output_modalities),
        )
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

    def _get_model_metadata(self, model_id: str) -> OpenRouterModelMetadata:
        cached = self._model_metadata_cache.get(model_id)
        if cached is not None:
            return cached

        if not self._model_metadata_cache_populated:
            self._populate_model_metadata_cache()
            cached = self._model_metadata_cache.get(model_id)
            if cached is not None:
                return cached

        raise ProviderError(f"Model metadata unavailable for '{model_id}'.")

    def _populate_model_metadata_cache(self) -> None:
        remote_models = self._fetch_remote_image_models()
        if remote_models is not None:
            for model in remote_models:
                self._model_metadata_cache[model.id] = model

        for model in _DEFAULT_IMAGE_MODELS:
            self._model_metadata_cache.setdefault(model.id, model)

        self._model_metadata_cache_populated = True

    def _fetch_remote_image_models(
        self,
    ) -> list[OpenRouterModelMetadata] | None:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "User-Agent": _USER_AGENT,
        }

        try:
            response = requests.get(
                _OPENROUTER_MODELS_URL,
                headers=headers,
                timeout=_HTTP_TIMEOUT,
            )
            response.raise_for_status()
            response_data = response.json()
        except (requests.RequestException, ValueError):
            return None

        try:
            models = response_data["data"]
        except (KeyError, TypeError):
            return None
        if not isinstance(models, list):
            return None

        parsed_models: list[OpenRouterModelMetadata] = []
        for model_data in models:
            parsed = _parse_model_metadata(model_data)
            if parsed is not None:
                parsed_models.append(parsed)
        return parsed_models


def _parse_model_metadata(model_data: object) -> OpenRouterModelMetadata | None:
    if not isinstance(model_data, dict):
        return None

    model_id = model_data.get("id")
    architecture = model_data.get("architecture")
    if not isinstance(model_id, str) or model_id == "openrouter/auto":
        return None
    if not isinstance(architecture, dict):
        return None

    input_modalities = _normalize_modalities(architecture.get("input_modalities"))
    output_modalities = _normalize_modalities(architecture.get("output_modalities"))
    if "image" not in output_modalities:
        return None

    modality = architecture.get("modality")
    if not isinstance(modality, str):
        modality = ""

    return OpenRouterModelMetadata(
        id=model_id,
        modality=modality,
        input_modalities=input_modalities,
        output_modalities=output_modalities,
    )


def _normalize_modalities(raw_modalities: object) -> tuple[str, ...]:
    if not isinstance(raw_modalities, list):
        return ()

    modalities: list[str] = []
    for raw_modality in raw_modalities:
        if isinstance(raw_modality, str) and raw_modality not in modalities:
            modalities.append(raw_modality)
    return tuple(modalities)


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
