"""MiniMax MCP server — exposes all MiniMax tools via Model Context Protocol."""
from __future__ import annotations

from ..api.client import MiniMaxClient
from ..image.client import ImageClient
from ..speech.client import SpeechClient
from ..video.client import VideoClient


def create_mcp_server() -> "FastMCP":
    """Create and configure the FastMCP server with all MiniMax tools."""
    from fastmcp import FastMCP

    mcp = FastMCP("minimax")

    # Shared client instance
    client = MiniMaxClient()
    image_client = ImageClient(client)
    speech_client = SpeechClient(client)
    video_client = VideoClient(client)

    # ── Image tools ────────────────────────────────────────────────

    @mcp.tool()
    async def generate_image(
        prompt: str,
        *,
        aspect_ratio: str | None = None,
        width: int | None = None,
        height: int | None = None,
        model: str = "image-01",
        response_format: str = "base64",
        number_of_images: int = 1,
        image: str | None = None,
        subject_references: list[dict[str, str]] | None = None,
        seed: int | None = None,
        prompt_optimizer: bool = False,
    ) -> dict:
        """Generate images via MiniMax image-01 (T2I, I2I, character-consistent I2I)."""
        return await image_client.generate(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            width=width,
            height=height,
            model=model,
            response_format=response_format,
            number_of_images=number_of_images,
            image=image,
            subject_references=subject_references,
            seed=seed,
            prompt_optimizer=prompt_optimizer,
        )

    # ── Speech / TTS tools ─────────────────────────────────────────

    @mcp.tool()
    async def synthesize_speech(
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
        voice_modify: dict | None = None,
        text_normalization: bool = False,
        latex_read: bool = False,
        output_format: str = "hex",
    ) -> dict:
        """Synthesize speech from text (up to 10,000 chars)."""
        return await speech_client.synthesize(
            text=text,
            voice_id=voice_id,
            model=model,
            speed=speed,
            pitch=pitch,
            vol=vol,
            emotion=emotion,
            language_boost=language_boost,
            audio_format=audio_format,
            sample_rate=sample_rate,
            bitrate=bitrate,
            channel=channel,
            stream=stream,
            voice_modify=voice_modify,
            text_normalization=text_normalization,
            latex_read=latex_read,
            output_format=output_format,
        )

    @mcp.tool()
    async def create_long_speech_task(
        text: str,
        voice_id: str,
        *,
        model: str = "speech-2.8-hd",
        audio_format: str = "mp3",
        sample_rate: int | None = None,
        bitrate: int | None = None,
    ) -> dict:
        """Create async long-form TTS task (10,000–50,000 chars)."""
        return await speech_client.create_long_speech_task(
            text=text,
            voice_id=voice_id,
            model=model,
            audio_format=audio_format,
            sample_rate=sample_rate,
            bitrate=bitrate,
        )

    @mcp.tool()
    async def query_long_speech_task(task_id: str) -> dict:
        """Poll status of an async TTS task."""
        return await speech_client.query_long_speech_task(task_id)

    @mcp.tool()
    async def upload_audio(audio: str, purpose: str = "voice_clone") -> dict:
        """Upload audio file (URL or base64) for voice cloning."""
        return await speech_client.upload_audio(audio=audio, purpose=purpose)

    @mcp.tool()
    async def clone_voice(file_id: str, voice_id: str) -> dict:
        """Clone a voice using an uploaded audio file."""
        return await speech_client.clone_voice(file_id=file_id, voice_id=voice_id)

    @mcp.tool()
    async def design_voice(
        prompt: str,
        preview_text: str,
        voice_id: str,
        *,
        model: str = "speech-2.8-hd",
    ) -> dict:
        """Generate a custom voice from a text description."""
        return await speech_client.design_voice(
            prompt=prompt,
            preview_text=preview_text,
            voice_id=voice_id,
            model=model,
        )

    @mcp.tool()
    async def get_voice(voice_id: str) -> dict:
        """Get details of a cloned or designed voice."""
        return await speech_client.get_voice(voice_id)

    @mcp.tool()
    async def delete_voice(voice_id: str) -> dict:
        """Delete a cloned or designed voice."""
        return await speech_client.delete_voice(voice_id)

    @mcp.tool()
    async def list_voices() -> dict:
        """List popular preset voices."""
        return await speech_client.list_voices()

    # ── Video tools ────────────────────────────────────────────────

    @mcp.tool()
    async def generate_video(
        prompt: str,
        *,
        model: str = "MiniMax-Hailuo-02",
        duration: int = 6,
        resolution: str = "1080P",
        first_frame_image: str | None = None,
        last_frame_image: str | None = None,
        subject_references: list[dict[str, str]] | None = None,
        subject_reference_mode: bool = False,
    ) -> dict:
        """Generate video via MiniMax Hailuo (T2V, I2V, first-last-frame, subject-consistent)."""
        return await video_client.generate(
            prompt=prompt,
            model=model,
            duration=duration,
            resolution=resolution,
            first_frame_image=first_frame_image,
            last_frame_image=last_frame_image,
            subject_references=subject_references,
            subject_reference_mode=subject_reference_mode,
        )

    @mcp.tool()
    async def query_video_task(task_id: str) -> dict:
        """Poll status of a video generation task."""
        return await video_client.query(task_id)

    @mcp.tool()
    async def retrieve_video_file(file_id: str) -> dict:
        """Retrieve a generated video file."""
        return await video_client.retrieve_file(file_id)

    return mcp


def run() -> None:
    """Entry point for the MCP server."""
    mcp = create_mcp_server()
    mcp.run()


if __name__ == "__main__":
    run()
