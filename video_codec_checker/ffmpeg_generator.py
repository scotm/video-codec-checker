"""FFmpeg command generation for video codec conversion."""

from pathlib import Path


def _single_quote(path: str) -> str:
    """Return path wrapped in single quotes with internal quotes escaped.

    Uses the POSIX-safe pattern: ' -> '\'' inside single-quoted strings.
    Always returns a single-quoted string to keep output consistent.
    """
    return "'" + path.replace("'", "'\"'\"'") + "'"


def get_audio_bitrate(channels: int) -> str:
    """Determine optimal Opus bitrate based on audio channels.

    Uses a safe default of 128k when channels are unknown or <= 0.
    """
    if channels <= 0:
        return "128k"  # Unknown; default to stereo bitrate
    if channels == 1:
        return "48k"  # Mono
    if channels == 2:
        return "128k"  # Stereo
    if 3 <= channels <= 6:
        return "256k"  # 5.1 surround
    return "320k"  # 7.1 or higher


def generate_ffmpeg_command(input_file: Path, channels: int) -> str:
    """Generate FFmpeg command to convert video to AV1 and audio to Opus."""
    output_file = input_file.with_stem(input_file.stem + "_av1").with_suffix(".mkv")
    audio_bitrate = get_audio_bitrate(channels)

    q_input = _single_quote(str(input_file))
    q_output = _single_quote(str(output_file))

    cmd_parts = [
        "ffmpeg",
        "-i",
        q_input,
        "-map_metadata",
        "-1",
        "-c:v",
        "libsvtav1",
        "-preset",
        "4",
        "-crf",
        "32",
        "-c:a",
        "libopus",
        "-b:a",
        audio_bitrate,
        q_output,
    ]

    return " ".join(cmd_parts)
