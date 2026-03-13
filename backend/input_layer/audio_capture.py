from __future__ import annotations

from pathlib import Path


class AudioCapture:
    """
    Minimal audio capture/storage helper.

    In production this could stream from a device; here we focus on accepting uploads
    and persisting them for later speech-to-text.
    """

    def save_upload(self, *, content: bytes, filename: str, dest_dir: str) -> str:
        Path(dest_dir).mkdir(parents=True, exist_ok=True)
        safe = filename.replace("\\", "_").replace("/", "_")
        out = Path(dest_dir) / safe
        out.write_bytes(content)
        return str(out)

