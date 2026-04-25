"""Base provider interface."""

from __future__ import annotations

from imagen.models.request import GenerateRequest
from imagen.models.response import GenerateResponse


class ImageProvider:
    def generate(self, request: GenerateRequest) -> GenerateResponse:
        raise NotImplementedError
