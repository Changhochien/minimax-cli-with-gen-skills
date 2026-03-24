"""MiniMax image generation API client."""
from __future__ import annotations

import base64
from typing import Any

from ..api.client import MiniMaxClient


class ImageClient:
    """Client for MiniMax image generation API (image-01)."""

    ENDPOINT = "/image_generation"

    def __init__(self, client: MiniMaxClient) -> None:
        self._client = client

    async def generate(
        self,
        prompt: str,
        *,
        aspect_ratio: str | None = None,
        width: int | None = None,
        height: int | None = None,
        model: str = "image-01",
        response_format: str = "base64",
        number_of_images: int = 1,
        image: str | None = None,
        subject_references: list[dict[str, Any]] | None = None,
        seed: int | None = None,
        prompt_optimizer: bool = False,
    ) -> dict[str, Any]:
        """
        Generate images via MiniMax image-01 model.

        T2I: provide only prompt.
        I2I: provide prompt + image (URL or base64).
        Character-consistent I2I: add subject_references.
        """
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "response_format": response_format,
            "number_of_images": number_of_images,
        }

        if aspect_ratio:
            payload["aspect_ratio"] = aspect_ratio
        if width:
            payload["width"] = width
        if height:
            payload["height"] = height
        if image:
            payload["image"] = image
        if subject_references:
            payload["subject_reference"] = subject_references
        if seed is not None:
            payload["seed"] = seed
        if prompt_optimizer:
            payload["prompt_optimizer"] = True

        result = await self._client.post(self.ENDPOINT, json=payload)
        return result

    def parse_base64_image(self, data_url: str) -> bytes:
        """Extract raw bytes from a base64 data URL."""
        _, b64 = data_url.split(",", 1)
        return base64.b64decode(b64)
