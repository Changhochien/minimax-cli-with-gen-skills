"""MiniMax API shared HTTP client."""
from __future__ import annotations

import os
from typing import Any

import httpx


class MiniMaxClient:
    """Thread-safe shared HTTP client for MiniMax API."""

    BASE_URL = "https://api.minimax.io/v1"

    def __init__(self, api_key: str | None = None, timeout: float = 120.0) -> None:
        self.api_key = api_key or os.environ.get("MINIMAX_API_KEY", "")
        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY is required")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "MiniMaxClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers=self._headers(),
                timeout=self.timeout,
            )
        return self._client

    async def post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        client = await self._get_client()
        response = await client.post(path, json=json, params=params)
        response.raise_for_status()
        return response.json()

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        client = await self._get_client()
        response = await client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    async def upload_file(
        self,
        path: str,
        files: dict[str, Any],
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Upload a file using multipart/form-data."""
        client = await self._get_client()
        # Remove Content-Type header for multipart uploads
        headers = {k: v for k, v in self._headers().items() if k != "Content-Type"}
        async with httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=self.timeout,
        ) as c:
            response = await c.post(path, files=files, data=data)
        response.raise_for_status()
        return response.json()
