from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from telegram_to_agents.config import TranscriptionConfig
from telegram_to_agents.transcription.openai_audio import (
    AudioTranscriptionError,
    transcribe_openai_audio,
)


@pytest.mark.asyncio
async def test_transcribes_with_secret_file_and_configured_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    audio = tmp_path / "voice.ogg"
    audio.write_bytes(b"audio")
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=file-key\n")
    observed: dict[str, object] = {}

    class FakeTranscriptions:
        async def create(self, *, model: str, file: object) -> object:
            observed.update(model=model, payload=file.read())
            return SimpleNamespace(text="  hello world  ")

    class FakeOpenAI:
        def __init__(self, *, api_key: str) -> None:
            observed["api_key"] = api_key
            self.audio = SimpleNamespace(transcriptions=FakeTranscriptions())

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("telegram_to_agents.transcription.openai_audio.AsyncOpenAI", FakeOpenAI)

    result = await transcribe_openai_audio(
        audio,
        TranscriptionConfig(automatic_audio=True, model="gpt-4o-transcribe"),
        env_file,
    )

    assert result == "hello world"
    assert observed == {
        "api_key": "file-key",
        "model": "gpt-4o-transcribe",
        "payload": b"audio",
    }


@pytest.mark.asyncio
async def test_missing_key_fails_before_provider_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    audio = tmp_path / "voice.ogg"
    audio.write_bytes(b"audio")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(AudioTranscriptionError, match="OPENAI_API_KEY"):
        await transcribe_openai_audio(audio, TranscriptionConfig(), tmp_path / "missing.env")
