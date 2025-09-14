"""Video processing functionality for codec checking."""

import json
import subprocess
import time
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

    files = [p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in allowed]

    return sorted(set(files))  # Remove duplicates and sort


# ---- ffprobe helpers (kept small to reduce complexity in the main API) ----

def _ensure_stats(stats: dict | None) -> dict:
    if stats is None:
        return {
            "fast_attempted": 0,
            "fast_succeeded": 0,
            "fast_fallbacks": 0,
            "fast_time": 0.0,
            "full_probes": 0,
            "full_time": 0.0,
        }
    stats.setdefault("fast_attempted", 0)
    stats.setdefault("fast_succeeded", 0)
    stats.setdefault("fast_fallbacks", 0)
    stats.setdefault("fast_time", 0.0)
    stats.setdefault("full_probes", 0)
    stats.setdefault("full_time", 0.0)
    return stats


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def _probe_full(
    base: list[str],
    file_path: Path,
    stats: dict | None,
) -> subprocess.CompletedProcess[str]:
    if stats is not None:
        stats["full_probes"] += 1
    t0 = time.perf_counter()
    result = _run(base + [str(file_path)])
    if stats is not None:
        stats["full_time"] += (time.perf_counter() - t0)
    return result


def _probe_fast(
    base: list[str], file_path: Path, ffprobe_args: list[str], stats: dict | None
) -> subprocess.CompletedProcess[str] | None:
    if stats is not None:
        stats["fast_attempted"] += 1
    t0 = time.perf_counter()
    result = _run(base + ffprobe_args + [str(file_path)])
    if stats is not None:
        stats["fast_time"] += (time.perf_counter() - t0)
    if result.returncode != 0 or not result.stdout:
        if stats is not None:
            stats["fast_fallbacks"] += 1
        return None
    if stats is not None:
        stats["fast_succeeded"] += 1
    return result


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


def probe_video_metadata(
    file_path: Path,
    ffprobe_args: list[str] | None = None,
    stats: dict | None = None,
) -> tuple[str | None, int]:
    """Probe both video codec and audio channels using a single ffprobe call.

    Returns a tuple of (video_codec or None, audio_channels as int).
    """
    try:
        base = [
            "ffprobe",
            "-v",
            "quiet",
            "-show_entries",
            "stream=index,codec_type,codec_name,channels",
            "-of",
            "json",
        ]
        s = _ensure_stats(stats) if stats is not None else None
        result: subprocess.CompletedProcess[str] | None
        if ffprobe_args:
            result = _probe_fast(base, file_path, ffprobe_args, s)
            if result is None:
                result = _probe_full(base, file_path, s)
                if result.returncode != 0 or not result.stdout:
                    return None, 0
        else:
            result = _probe_full(base, file_path, s)
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
