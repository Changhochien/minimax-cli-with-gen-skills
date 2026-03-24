"""MiniMax unified Python package — image, speech, and video generation."""
from __future__ import annotations

from minimax.api.client import MiniMaxClient
from minimax.image.client import ImageClient
from minimax.speech.client import SpeechClient
from minimax.video.client import VideoClient

__version__ = "0.1.0"
__all__ = ["MiniMaxClient", "ImageClient", "SpeechClient", "VideoClient"]
