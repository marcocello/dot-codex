"""Audio transcription services."""

from telegram_to_agents.transcription.openai_audio import (
    AudioTranscriptionError,
    transcribe_openai_audio,
)

__all__ = ["AudioTranscriptionError", "transcribe_openai_audio"]
