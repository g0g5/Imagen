"""Base provider interface."""

from __future__ import annotations

from imagencli.models.request import GenerateRequest
from imagencli.models.response import GenerateResponse


class ImageProvider:
    def generate(self, request: GenerateRequest) -> GenerateResponse:
        raise NotImplementedError
