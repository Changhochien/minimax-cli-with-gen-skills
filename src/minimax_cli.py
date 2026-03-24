#!/usr/bin/env python3
"""MiniMax CLI — image, speech, video, and music generation."""
from __future__ import annotations

import asyncio
import base64
import json
import os
import sys
from pathlib import Path
from typing import Any

import typer
from typing_extensions import Annotated

from minimax.api.client import MiniMaxClient
from minimax.image.client import ImageClient
from minimax.music.client import MusicClient
from minimax.speech.client import SpeechClient
from minimax.video.client import VideoClient

__version__ = "0.2.0"

# ── App scaffolding ────────────────────────────────────────────────────────────

app = typer.Typer(
    name="minimax",
    help="MiniMax CLI — image, speech, video, and music generation.",
    add_completion=False,
)
image_app = typer.Typer()
speech_app = typer.Typer()
video_app = typer.Typer()
music_app = typer.Typer()
app.add_typer(image_app, name="image", help="Image generation (T2I / I2I)")
app.add_typer(speech_app, name="speech", help="Text-to-speech and voice management")
app.add_typer(video_app, name="video", help="Video generation (Hailuo)")
app.add_typer(music_app, name="music", help="Music generation")


def get_client() -> MiniMaxClient:
    return MiniMaxClient()


def json_output(result: dict[str, Any]) -> None:
    typer.echo(json.dumps(result, indent=2, ensure_ascii=False))


def _save_hex_to_file(hex_data: str, output: Path) -> None:
    audio_bytes = bytes.fromhex(hex_data)
    Path(output).write_bytes(audio_bytes)
    typer.echo(f"Saved {len(audio_bytes):,} bytes to {output}")


def _resolve_output_path(default_name: str, output: Path | None) -> Path:
    """Resolve output path, creating parent directories if needed."""
    if output is None:
        return Path(default_name)
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


# ── Image subcommands ──────────────────────────────────────────────────────────

@image_app.command()
def generate(
    prompt: str = typer.Option(..., "--prompt", "-p", help="Image description"),
    aspect_ratio: str = typer.Option(None, "--aspect-ratio", "-r",
                                      help="1:1, 16:9, 9:16, 4:3, 3:2, 2:3, 3:4, 21:9"),
    width: int = typer.Option(None, "--width", help="Custom width (512–2048, divisible by 8)"),
    height: int = typer.Option(None, "--height", help="Custom height (512–2048, divisible by 8)"),
    model: str = typer.Option("image-01", "--model", "-m"),
    response_format: str = typer.Option("base64", "--response-format", "-f",
                                        help="base64 or url"),
    number: int = typer.Option(1, "--number", "-n", help="Number of images (1–9)"),
    image: str = typer.Option(None, "--image", "-i",
                              help="Reference image URL or base64 for I2I"),
    subject_ref: str = typer.Option(None, "--subject-ref",
                                     help="Subject reference image URL or base64"),
    seed: int = typer.Option(None, "--seed", "-s"),
    optimizer: bool = typer.Option(False, "--optimizer/--no-optimizer"),
    output: Path = typer.Option(None, "--output", "-o",
                                help="Write first image to file"),
) -> None:
    """Generate an image (T2I or I2I)."""
    subject_references = None
    if subject_ref:
        subject_references = [{"type": "character", "image_file": subject_ref}]

    async def run() -> None:
        client = get_client()
        img = ImageClient(client)
        result = await img.generate(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            width=width,
            height=height,
            model=model,
            response_format=response_format,
            number_of_images=number,
            image=image,
            subject_references=subject_references,
            seed=seed,
            prompt_optimizer=optimizer,
        )
        images = result.get("data", {}).get("image_base64") or []
        status_ok = result.get("base_resp", {}).get("status_code") == 0
        if output and status_ok and images:
            data = images[0]
            out_path = _resolve_output_path("output.png", output)
            if data.startswith("data:"):
                _, b64 = data.split(",", 1)
                out_path.write_bytes(base64.b64decode(b64))
            else:
                out_path.write_bytes(base64.b64decode(data))
            typer.echo(f"Saved to {out_path}")
        else:
            json_output(result)

    asyncio.run(run())


# ── Speech subcommands ─────────────────────────────────────────────────────────

@speech_app.command()
def synthesize(
    text: str = typer.Option(..., "--text", "-t", help="Text to synthesize (max 10,000 chars)"),
    voice_id: str = typer.Option(..., "--voice-id", "-v", help="Voice ID"),
    model: str = typer.Option("speech-2.8-hd", "--model", "-m"),
    speed: float = typer.Option(1.0, "--speed"),
    pitch: int = typer.Option(0, "--pitch"),
    vol: float = typer.Option(1.0, "--vol"),
    emotion: str = typer.Option(None, "--emotion", "-e",
                               help="happy, sad, angry, fearful, disgusted, surprised, calm, fluent, whisper"),
    language_boost: str = typer.Option(None, "--language-boost"),
    audio_format: str = typer.Option("mp3", "--audio-format", "-f"),
    sample_rate: int = typer.Option(None, "--sample-rate"),
    bitrate: int = typer.Option(None, "--bitrate"),
    channel: int = typer.Option(1, "--channel"),
    output_format: str = typer.Option("hex", "--output-format"),
    output: Path = typer.Option(None, "--output", "-o",
                                help="Save decoded audio to file"),
) -> None:
    """Synthesize speech (sync, up to 10,000 chars)."""
    async def run() -> None:
        client = get_client()
        speech = SpeechClient(client)
        result = await speech.synthesize(
            text=text, voice_id=voice_id, model=model, speed=speed,
            pitch=pitch, vol=vol, emotion=emotion, language_boost=language_boost,
            audio_format=audio_format, sample_rate=sample_rate, bitrate=bitrate,
            channel=channel, output_format=output_format,
        )
        status_ok = result.get("base_resp", {}).get("status_code") == 0
        audio_data = result.get("data", {}).get("audio") or result.get("audio")
        if output and status_ok and audio_data:
            _save_hex_to_file(audio_data, _resolve_output_path("output.mp3", output))
        else:
            json_output(result)

    asyncio.run(run())


@speech_app.command("long-create")
def long_speech_create(
    text: str = typer.Option(..., "--text", "-t", help="Long text (10,000–50,000 chars)"),
    voice_id: str = typer.Option(..., "--voice-id", "-v"),
    model: str = typer.Option("speech-2.8-hd", "--model", "-m"),
    audio_format: str = typer.Option("mp3", "--audio-format", "-f"),
    sample_rate: int = typer.Option(None, "--sample-rate"),
    bitrate: int = typer.Option(None, "--bitrate"),
) -> None:
    """Create an async long-form TTS task."""
    async def run() -> None:
        client = get_client()
        speech = SpeechClient(client)
        result = await speech.create_long_speech_task(
            text=text, voice_id=voice_id, model=model,
            audio_format=audio_format, sample_rate=sample_rate, bitrate=bitrate,
        )
        json_output(result)

    asyncio.run(run())


@speech_app.command("long-query")
def long_speech_query(
    task_id: str = typer.Argument(...),
) -> None:
    """Poll status of an async TTS task."""
    async def run() -> None:
        client = get_client()
        speech = SpeechClient(client)
        result = await speech.query_long_speech_task(task_id)
        json_output(result)

    asyncio.run(run())


@speech_app.command()
def upload(
    audio: str = typer.Option(..., "--audio", "-a",
                              help="Audio URL or base64 data URL (mp3/m4a/wav, 10s–5min)"),
    purpose: str = typer.Option("voice_clone", "--purpose", "-p"),
) -> None:
    """Upload an audio file for voice cloning."""
    async def run() -> None:
        client = get_client()
        speech = SpeechClient(client)
        result = await speech.upload_audio(audio=audio, purpose=purpose)
        json_output(result)

    asyncio.run(run())


@speech_app.command()
def clone(
    file_id: str = typer.Option(..., "--file-id"),
    voice_id: str = typer.Option(..., "--voice-id", "-v"),
) -> None:
    """Clone a voice from an uploaded audio file."""
    async def run() -> None:
        client = get_client()
        speech = SpeechClient(client)
        result = await speech.clone_voice(file_id=file_id, voice_id=voice_id)
        json_output(result)

    asyncio.run(run())


@speech_app.command()
def design(
    prompt: str = typer.Option(..., "--prompt", "-p",
                               help="Voice description, e.g. 'Excited male product reviewer'"),
    preview_text: str = typer.Option(..., "--preview", "-t",
                                     help="Short text for preview audio"),
    voice_id: str = typer.Option(..., "--voice-id", "-v"),
    model: str = typer.Option("speech-2.8-hd", "--model", "-m"),
) -> None:
    """Generate a custom voice from a text description."""
    async def run() -> None:
        client = get_client()
        speech = SpeechClient(client)
        result = await speech.design_voice(
            prompt=prompt, preview_text=preview_text,
            voice_id=voice_id, model=model,
        )
        json_output(result)

    asyncio.run(run())


@speech_app.command()
def list_voices() -> None:
    """List popular preset voices."""
    async def run() -> None:
        client = get_client()
        speech = SpeechClient(client)
        result = await speech.list_voices()
        json_output(result)

    asyncio.run(run())


# ── Video subcommands ─────────────────────────────────────────────────────────

@video_app.command()
def generate(
    prompt: str = typer.Option(..., "--prompt", "-p", help="Video description"),
    model: str = typer.Option("MiniMax-Hailuo-02", "--model", "-m"),
    duration: int = typer.Option(6, "--duration", "-d"),
    resolution: str = typer.Option("1080P", "--resolution", "-r"),
    first_frame: str = typer.Option(None, "--first-frame", "-f",
                                    help="First frame image URL or base64 (I2V)"),
    last_frame: str = typer.Option(None, "--last-frame", "-l",
                                   help="Last frame image URL or base64 (first-last-frame)"),
    subject_ref: str = typer.Option(None, "--subject-ref",
                                    help="Subject reference image URL or base64 (S2V-01)"),
    subject_mode: bool = typer.Option(False, "--subject-mode"),
) -> None:
    """Generate video (T2V, I2V, first-last-frame, or subject-consistent)."""
    subject_references = None
    if subject_ref:
        subject_references = [{"type": "character", "image_file": subject_ref}]

    async def run() -> None:
        client = get_client()
        video = VideoClient(client)
        result = await video.generate(
            prompt=prompt, model=model, duration=duration,
            resolution=resolution, first_frame_image=first_frame,
            last_frame_image=last_frame, subject_references=subject_references,
            subject_reference_mode=subject_mode,
        )
        json_output(result)

    asyncio.run(run())


@video_app.command()
def query(
    task_id: str = typer.Argument(...),
) -> None:
    """Poll status of a video generation task."""
    async def run() -> None:
        client = get_client()
        video = VideoClient(client)
        result = await video.query(task_id)
        json_output(result)

    asyncio.run(run())


@video_app.command()
def retrieve(
    file_id: str = typer.Argument(...),
) -> None:
    """Retrieve a generated video file."""
    async def run() -> None:
        client = get_client()
        video = VideoClient(client)
        result = await video.retrieve_file(file_id)
        json_output(result)

    asyncio.run(run())


# ── Music subcommands ─────────────────────────────────────────────────────────

@music_app.command()
def generate(
    prompt: str = typer.Option(..., "--prompt", "-p",
                               help="Music style/mood description (max 2000 chars)"),
    lyrics: str = typer.Option(None, "--lyrics", "-l",
                               help="Song lyrics with [Verse], [Chorus], etc. tags (1–3500 chars)"),
    model: str = typer.Option("music-2.5+", "--model", "-m"),
    instrumental: bool = typer.Option(False, "--instrumental/--no-instrumental",
                                       help="Generate instrumental only (music-2.5+)"),
    auto_lyrics: bool = typer.Option(False, "--auto-lyrics/--no-auto-lyrics",
                                      help="Auto-generate lyrics from prompt"),
    audio_format: str = typer.Option("mp3", "--audio-format", "-f",
                                     help="mp3, wav, pcm"),
    sample_rate: int = typer.Option(44100, "--sample-rate"),
    bitrate: int = typer.Option(256000, "--bitrate"),
    output: Path = typer.Option(None, "--output", "-o",
                                 help="Save decoded audio to file"),
) -> None:
    """Generate a music track (music-2.5+)."""
    audio_setting = {"sample_rate": sample_rate, "bitrate": bitrate, "format": audio_format}

    async def run() -> None:
        client = get_client()
        music = MusicClient(client)
        result = await music.generate(
            prompt=prompt,
            lyrics=lyrics,
            model=model,
            is_instrumental=instrumental,
            lyrics_optimizer=auto_lyrics,
            audio_setting=audio_setting,
            output_format="hex",
        )
        if output and result.get("base_resp", {}).get("status_code") == 0:
            data = result.get("data", {})
            if data.get("status") == 2 and data.get("audio"):
                out_path = _resolve_output_path("output.mp3", output)
                _save_hex_to_file(data["audio"], out_path)
            else:
                typer.echo(f"Status: {data.get('status')} — audio may still be generating")
                json_output(result)
        else:
            json_output(result)

    asyncio.run(run())


@music_app.command()
def lyrics(
    prompt: str = typer.Option(..., "--prompt", "-p",
                               help="Theme or idea for the song (max 2000 chars)"),
    mode: str = typer.Option("write_full_song", "--mode",
                             help="Mode: write_full_song (default)"),
) -> None:
    """Generate song lyrics from a text description.

    Use the output as the --lyrics argument for 'minimax music generate'.
    """
    async def run() -> None:
        client = get_client()
        music = MusicClient(client)
        result = await music.generate_lyrics(prompt=prompt, mode=mode)
        json_output(result)

    asyncio.run(run())


# ── Entry points ─────────────────────────────────────────────────────────────

@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v",
                                 is_eager=True, help="Show version"),
) -> None:
    if version:
        typer.echo(f"minimax {__version__}")


if __name__ == "__main__":
    app()
