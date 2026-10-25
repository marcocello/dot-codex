"""OpenAI-backed audio transcription for messaging ingress."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from openai import AsyncOpenAI

from telegram_to_agents.config import TranscriptionConfig
from telegram_to_agents.infra.env_secrets import load_env_secrets

logger = logging.getLogger(__name__)


class AudioTranscriptionError(RuntimeError):
    """A safe, user-actionable transcription boundary failure."""


def _api_key(env_file: Path) -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        key = load_env_secrets(env_file).get("OPENAI_API_KEY", "").strip()
    if not key:
        raise AudioTranscriptionError("OPENAI_API_KEY is not configured")
    return key


async def transcribe_openai_audio(
    path: Path,
    config: TranscriptionConfig,
    env_file: Path,
) -> str:
    """Return a non-empty transcript for *path* using OpenAI's audio API."""
    client = AsyncOpenAI(api_key=_api_key(env_file))
    try:
        async with asyncio.timeout(config.timeout_seconds):
            with path.open("rb") as audio_file:
                response = await client.audio.transcriptions.create(
                    model=config.model,
                    file=audio_file,
                )
    except TimeoutError as exc:
        raise AudioTranscriptionError("OpenAI transcription timed out") from exc
    except Exception as exc:
        logger.warning("OpenAI transcription failed: %s", type(exc).__name__)
        raise AudioTranscriptionError("OpenAI transcription failed") from exc

    transcript = response.text.strip()
    if not transcript:
        raise AudioTranscriptionError("OpenAI returned an empty transcript")
    return transcript
