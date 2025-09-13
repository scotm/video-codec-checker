"""Video processing functionality for codec checking."""

import subprocess
from pathlib import Path


def get_video_files(directory=".", video_extensions=None):
    """Find all video files recursively in the given directory."""
    if video_extensions is None:
        video_extensions = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg", ".3gp", ".ogv"}
    
    path = Path(directory)
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(path.rglob(f"*{ext}"))
        video_files.extend(path.rglob(f"*{ext.upper()}"))
    
    return sorted(set(video_files))  # Remove duplicates and sort


def get_video_codec(file_path):
    """Extract video codec from file using ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_name",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def get_audio_channels(file_path):
    """Extract audio channels from file using ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-select_streams", "a:0",
            "-show_entries", "stream=channels",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        channels = result.stdout.strip()
        return int(channels) if channels.isdigit() else 0
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        return 0