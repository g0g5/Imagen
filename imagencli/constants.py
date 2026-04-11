"""Static constants and capability data."""

from __future__ import annotations

DEFAULT_MODEL = "google/gemini-3.1-flash-image-preview"
OPENROUTER_CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"

SUPPORTED_IMAGE_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
}

BASE_ASPECT_RATIOS = {
    "1:1",
    "2:3",
    "3:2",
    "3:4",
    "4:3",
    "4:5",
    "5:4",
    "9:16",
    "16:9",
    "21:9",
}

EXTENDED_ASPECT_RATIOS = {
    "1:4",
    "4:1",
    "1:8",
    "8:1",
}

BASE_RESOLUTIONS = {
    "1K",
    "2K",
    "4K",
}

EXTENDED_RESOLUTIONS = {
    "0.5K",
}

MODEL_CAPABILITIES = {
    DEFAULT_MODEL: {
        "aspect_ratios": BASE_ASPECT_RATIOS | EXTENDED_ASPECT_RATIOS,
        "resolutions": BASE_RESOLUTIONS | EXTENDED_RESOLUTIONS,
    },
    "default": {
        "aspect_ratios": BASE_ASPECT_RATIOS,
        "resolutions": BASE_RESOLUTIONS,
    },
}
