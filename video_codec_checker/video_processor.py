"""Video processing functionality for codec checking."""

import json
import subprocess
from pathlib import Path


def get_video_files(
    directory: str = ".", video_extensions: set[str] | None = None
) -> list[Path]:
    """Find all video files recursively in the given directory.

    Uses a single directory walk and filters by suffix for performance.
    """
    if video_extensions is None:
        video_extensions = {
            ".mp4",
            ".avi",
            ".mkv",
            ".mov",
            ".wmv",
            ".flv",
            ".webm",
            ".m4v",
            ".mpg",
            ".mpeg",
            ".3gp",
            ".ogv",
        }

    allowed = {ext.lower() for ext in video_extensions}
    path = Path(directory)

    files = [
        p
        for p in path.rglob("*")
        if p.is_file() and p.suffix.lower() in allowed
    ]

    return sorted(set(files))  # Remove duplicates and sort


def get_video_codec(file_path: Path) -> str | None:
    """Extract video codec from file using ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(file_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def get_audio_channels(file_path: Path) -> int:
    """Extract audio channels from file using ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=channels",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(file_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        channels = result.stdout.strip()
        return int(channels) if channels.isdigit() else 0
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        return 0


def probe_video_metadata(file_path: Path) -> tuple[str | None, int]:
    """Probe both video codec and audio channels using a single ffprobe call.

    Returns a tuple of (video_codec or None, audio_channels as int).
    """
    try:
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-show_entries",
            "stream=index,codec_type,codec_name,channels",
            "-of",
            "json",
            str(file_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0 or not result.stdout:
            return None, 0

        data = json.loads(result.stdout)
        streams = data.get("streams", [])
        v_codec: str | None = None
        a_channels: int = 0
        for s in streams:
            stype = s.get("codec_type")
            if stype == "video" and v_codec is None:
                v_codec = s.get("codec_name")
            elif stype == "audio" and a_channels == 0:
                try:
                    a_channels = int(s.get("channels", 0) or 0)
                except (TypeError, ValueError):
                    a_channels = 0
        return v_codec, a_channels
    except (json.JSONDecodeError, subprocess.TimeoutExpired, FileNotFoundError):
        return None, 0
