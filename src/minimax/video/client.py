"""MiniMax video generation API client (Hailuo)."""
from __future__ import annotations

from typing import Any

from ..api.client import MiniMaxClient


class VideoClient:
    """Client for MiniMax video generation API (Hailuo models)."""

    GENERATE_ENDPOINT = "/video_generation"
    QUERY_ENDPOINT = "/query/video_generation"
    FILE_RETRIEVE_ENDPOINT = "/files/retrieve"

    def __init__(self, client: MiniMaxClient) -> None:
        self._client = client

    async def generate(
        self,
        prompt: str,
        model: str = "MiniMax-Hailuo-02",
        duration: int = 6,
        resolution: str = "1080P",
        *,
        first_frame_image: str | None = None,
        last_frame_image: str | None = None,
        subject_references: list[dict[str, Any]] | None = None,
        # S2V-01 specific
        subject_reference_mode: bool = False,
    ) -> dict[str, Any]:
        """
        Create a video generation task.

        Modes:
        - Text-to-Video:     provide prompt only
        - Image-to-Video:    provide prompt + first_frame_image
        - First-Last-Frame:   provide prompt + first_frame_image + last_frame_image
        - Subject-consistent: provide subject_references (S2V-01 model)
        """
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution,
        }
        if first_frame_image:
            payload["first_frame_image"] = first_frame_image
        if last_frame_image:
            payload["last_frame_image"] = last_frame_image
        if subject_references:
            payload["subject_reference"] = subject_references
        if subject_reference_mode:
            payload["subject_reference_mode"] = True

        result = await self._client.post(self.GENERATE_ENDPOINT, json=payload)
        return result

    async def query(self, task_id: str) -> dict[str, Any]:
        """Poll the status of a video generation task."""
        result = await self._client.get(
            self.QUERY_ENDPOINT, params={"task_id": task_id}
        )
        return result

    async def retrieve_file(self, file_id: str) -> dict[str, Any]:
        """Retrieve a generated video file."""
        result = await self._client.get(
            self.FILE_RETRIEVE_ENDPOINT, params={"file_id": file_id}
        )
        return result
