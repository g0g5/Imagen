"""Static model capability data for local validation."""

from __future__ import annotations

from imagen.constants import MODEL_CAPABILITIES


def get_model_capabilities(model: str) -> dict[str, set[str]]:
    return MODEL_CAPABILITIES.get(model, MODEL_CAPABILITIES["default"])


__all__ = ["MODEL_CAPABILITIES", "get_model_capabilities"]
