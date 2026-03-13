from __future__ import annotations

from pathlib import Path


class SpeechToText:
    """
    Speech-to-text adapter.

    This backend is production-structured but keeps STT optional because different
    deployments use different providers (Whisper, Azure, Deepgram, etc.).
    """

    def transcribe(self, audio_path: str) -> str:
        p = Path(audio_path)
        if not p.exists():
            raise FileNotFoundError(audio_path)
        raise NotImplementedError(
            "Speech-to-text is not configured in this reference implementation. "
            "Use transcript upload or integrate your preferred STT provider."
        )

