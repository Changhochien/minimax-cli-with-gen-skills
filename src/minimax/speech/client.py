"""MiniMax TTS API client."""
from __future__ import annotations

from typing import Any

from ..api.client import MiniMaxClient


class SpeechClient:
    """Client for MiniMax Text-to-Speech API (speech-2.8-hd etc.)."""

    T2A_ENDPOINT = "/t2a_v2"
    ASYNC_ENDPOINT = "/t2a_async_v2"
    QUERY_ENDPOINT = "/query/t2a_async_query_v2"
    UPLOAD_ENDPOINT = "/files/upload"
    CLONE_ENDPOINT = "/voice_clone"
    DESIGN_ENDPOINT = "/voice_design"

    def __init__(self, client: MiniMaxClient) -> None:
        self._client = client

    async def synthesize(
        self,
        text: str,
        voice_id: str,
        *,
        model: str = "speech-2.8-hd",
        speed: float = 1.0,
        pitch: int = 0,
        vol: float = 1.0,
        emotion: str | None = None,
        language_boost: str | None = None,
        audio_format: str = "mp3",
        sample_rate: int | None = None,
        bitrate: int | None = None,
        channel: int = 1,
        stream: bool = False,
        voice_modify: dict[str, Any] | None = None,
        text_normalization: bool = False,
        latex_read: bool = False,
        output_format: str = "hex",
    ) -> dict[str, Any]:
        """Synchronous TTS — texts up to 10,000 characters."""
        payload: dict[str, Any] = {
            "model": model,
            "text": text,
            "voice_id": voice_id,
            "speed": speed,
            "pitch": pitch,
            "vol": vol,
            "audio_format": audio_format,
            "channel": channel,
            "stream": stream,
            "text_normalization": text_normalization,
            "latex_read": latex_read,
            "output_format": output_format,
        }
        if emotion:
            payload["emotion"] = emotion
        if language_boost:
            payload["language_boost"] = language_boost
        if sample_rate:
            payload["sample_rate"] = sample_rate
        if bitrate:
            payload["bitrate"] = bitrate
        if voice_modify:
            payload["voice_modify"] = voice_modify

        result = await self._client.post(self.T2A_ENDPOINT, json=payload)
        return result

    async def create_long_speech_task(
        self,
        text: str,
        voice_id: str,
        *,
        model: str = "speech-2.8-hd",
        audio_format: str = "mp3",
        sample_rate: int | None = None,
        bitrate: int | None = None,
    ) -> dict[str, Any]:
        """Create async long-form TTS task — for texts 10,000–50,000 chars."""
        payload: dict[str, Any] = {
            "model": model,
            "text": text,
            "voice_id": voice_id,
            "audio_format": audio_format,
        }
        if sample_rate:
            payload["sample_rate"] = sample_rate
        if bitrate:
            payload["bitrate"] = bitrate

        result = await self._client.post(self.ASYNC_ENDPOINT, json=payload)
        return result

    async def query_long_speech_task(self, task_id: str) -> dict[str, Any]:
        """Poll status of an async TTS task."""
        result = await self._client.get(
            self.QUERY_ENDPOINT, params={"task_id": task_id}
        )
        return result

    async def upload_audio(
        self,
        audio: str,
        purpose: str = "voice_clone",
    ) -> dict[str, Any]:
        """Upload an audio file for voice cloning.

        Args:
            audio: URL or base64 data URL of the audio file (mp3/m4a/wav, 10s–5min).
            purpose: Always "voice_clone" for now.
        """
        if audio.startswith("data:"):
            # base64 data URL — decode and upload as file
            return await self._upload_base64_audio(audio, purpose)
        # URL-based upload
        result = await self._client.upload_file(
            self.UPLOAD_ENDPOINT,
            files={
                "file": (
                    "audio.mp3",
                    audio,
                    "application/octet-stream",
                )
            },
            data={"purpose": purpose},
        )
        return result

    async def _upload_base64_audio(
        self, data_url: str, purpose: str
    ) -> dict[str, Any]:
        import base64

        mime, b64 = data_url.split(",", 1)
        ext = mime.split("/")[1].split(";")[0]  # e.g. "mp3", "wav"
        raw = base64.b64decode(b64)
        result = await self._client.upload_file(
            self.UPLOAD_ENDPOINT,
            files={"file": (f"audio.{ext}", raw, mime)},
            data={"purpose": purpose},
        )
        return result

    async def clone_voice(
        self,
        file_id: str,
        voice_id: str,
    ) -> dict[str, Any]:
        """Clone a voice from an uploaded audio file."""
        payload = {"file_id": file_id, "voice_id": voice_id}
        result = await self._client.post(self.CLONE_ENDPOINT, json=payload)
        return result

    async def design_voice(
        self,
        prompt: str,
        preview_text: str,
        voice_id: str,
        *,
        model: str = "speech-2.8-hd",
    ) -> dict[str, Any]:
        """Generate a custom voice from a text description."""
        payload = {
            "model": model,
            "prompt": prompt,
            "preview_text": preview_text,
            "voice_id": voice_id,
        }
        result = await self._client.post(self.DESIGN_ENDPOINT, json=payload)
        return result

    async def get_voice(self, voice_id: str) -> dict[str, Any]:
        """Get details of a voice."""
        result = await self._client.get(f"/voices/{voice_id}")
        return result

    async def delete_voice(self, voice_id: str) -> dict[str, Any]:
        """Delete a cloned or designed voice."""
        result = await self._client.post(f"/voices/{voice_id}/delete", json={})
        return result

    async def list_voices(self) -> dict[str, Any]:
        """List popular preset voices."""
        result = await self._client.get("/voices")
        return result
